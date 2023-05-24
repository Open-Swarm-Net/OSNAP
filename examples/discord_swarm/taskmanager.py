"""
This is a separate discord bot that handles the task management for the swarm
"""
import random
import sys, os, time
import discord
from dotenv import load_dotenv
from discord.ext import commands
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select

# adding the lates version of the osnap_client to the path
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent.parent))

from osnap_client.protocol import AgentCommand, AgentCommandType

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='$', intents=intents)

engine = create_engine('sqlite:///tasks.db', echo=True)
metadata = MetaData()

# Define the tables
tasks = Table(
    'tasks', metadata,
    Column('id', Integer, primary_key=True),
    Column('type', String),
    Column('description', String),
    Column('status', String)
)

agents = Table(
    'agents', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('task_types', String)
)

commands_table = Table(
    'commands_table', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('capable_users', String)
)

# Create the tables
metadata.create_all(engine)

conn = engine.connect()

@bot.event
async def on_ready():
    log(f'We have logged in as {bot.user}')
    available_commands = [command.name for command in bot.commands]
    listening_on_channels = [channel.name for channel in bot.get_all_channels()]
    intro = f'Hello, I am {bot.user.name}. I am ready to manage your tasks. Available commands:{available_commands}.\nListening on channels:{listening_on_channels}'
    # send a message to chenel intros
    target_channel = "intros"

    for channel in bot.get_all_channels():
        if channel.name == target_channel and isinstance(channel, discord.TextChannel):
            await channel.send(intro)
            return

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    # Handle custom commands
    if message.content.startswith('$'):
        command = message.content[1:].split(' ')[0].lower()
        result = conn.execute(select(commands_table).where(commands_table.c.name == command)).fetchone()
        if result is None:
            custom_manager_commands = [command.name for command in bot.commands]
            if command not in custom_manager_commands:
                await message.reply(f'There is no such bot who can do ${command}')

        else:
            # add the task to the tasks table
            task_type = command
            task_description = ' '.join(message.content[1:].split(' ')[1:])
            conn.execute(tasks.insert().values(type=task_type, description=task_description, status='pending'))
            await message_relevant_agents(task_type, task_description)

    await bot.process_commands(message)

async def message_relevant_agents(task_type, task_description):
    # Query the list of agents and their tasks
    log(f'Querying agents for {task_type}')
    result = conn.execute(select(agents)).fetchall()
    username_idx = agents.c.keys().index('name')
    task_types_idx = agents.c.keys().index('task_types')
    for row in result:
        if task_type in row[task_types_idx].lower().replace(' ', '').split(','):
            username = row[username_idx]
            for user in bot.users:
                if user.name == username:
                    command = AgentCommand(
                        sender="Task Manager",
                        receiver=user.name,
                        command_type=AgentCommandType.TASK,
                        task_name=task_type,
                        data=task_description
                    ).json()
                    message = f'$available_task {command}'
                    await user.send(message)

@bot.command()
async def add_command(ctx, *, command_name):
    # Add a custom command
    conn.execute(commands_table.insert().values(name=command_name, user=ctx.author.name))
    await ctx.send(f'Command ${command_name} added.')

@bot.command()
async def subscribe(ctx, *, task_types):
    # Store the agent and its task types
    # Check if the agent already exists
    result = conn.execute(select(agents).where(agents.c.name == ctx.author.name)).fetchone()
    

    # split the list of task types
    if ";" in task_types:
        task_types = task_types.replace(';', ',')
    task_types = task_types.replace(' ', '').lower()
    task_types = task_types.split(',')

    if result is None:
        conn.execute(agents.insert().values(name=ctx.author.name, task_types=','.join(task_types)))
        log(f'Added {ctx.author.name} with {task_types}')
    else:
        conn.execute(agents.update().where(agents.c.name == ctx.author.name).values(task_types=task_types))
        log(f'Updated {ctx.author.name} with {task_types}')

    
    for task_type in task_types:
        # Check if the task type exists and add it to the table if it doesn't
        result = conn.execute(select(commands_table).where(commands_table.c.name == task_type)).fetchone()
        if result is None:
            conn.execute(commands_table.insert().values(name=task_type, capable_users=ctx.author.name))
            log(f'Added {task_type} with {ctx.author.name}')
        else:
            # result is tuple, so we need the id of the key capable_users
            cu_idx = commands_table.c.keys().index('capable_users')
            existing_users = result[cu_idx].split(',')
            if ctx.author.name in existing_users:
                continue
            new_users = ','.join([ctx.author.name] + existing_users)
            conn.execute(commands_table.update().where(commands_table.c.name == task_type).values(capable_users=new_users))
            log(f'Updated {task_type} with {new_users}')

    await ctx.reply(f'Subscription successful.')

@bot.command()
async def who(ctx):
    # Query the list of agents and their tasks
    log('Querying agents')
    result = conn.execute(select(agents)).fetchall()
    username_idx = agents.c.keys().index('name')
    task_types_idx = agents.c.keys().index('task_types')
    for row in result:
        await ctx.reply(f'Agent: {row[username_idx]}, Task types: {row[task_types_idx]}')

@bot.command()
async def what(ctx):
    # Query the list of agents and their tasks
    log('Querying commands')
    result = conn.execute(select(commands_table)).fetchall()
    """
        Column('name', String),
    Column('capable_users', String)
    """
    command_name_idx = commands_table.c.keys().index('name')
    capable_users_idx = commands_table.c.keys().index('capable_users')
    for row in result:
        await ctx.reply(f'Command: {row[command_name_idx]}, Capable users: {row[capable_users_idx]}')

@bot.command()
async def whats_going(ctx):
    # Query the list of tasks and their statuses
    log('Querying tasks')
    result = conn.execute(select(tasks)).fetchall()

    type_idx = tasks.c.keys().index('type')
    descr_idx = tasks.c.keys().index('description')
    status_idx = tasks.c.keys().index('status')

    for row in result:
        await ctx.reply(f'Task: {row[type_idx]} {row[descr_idx]}, Status: {row[status_idx]}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # find commands in the tasks table
        result = conn.execute(select(commands_table).where(commands_table.c.name == ctx.message.content[1:])).fetchone()
        if result is None:
            await ctx.reply('Invalid command.')
    else:
        log(f'Error occurred: {error}')

def log(message):
    print(message)

# Continue implementing the remaining commands...

bot.run(os.getenv("TASK_MANAGER_TOKEN"))

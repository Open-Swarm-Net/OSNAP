"""
This is a separate discord bot that handles the task management for the swarm
"""
import os
import sys
import discord
from dotenv import load_dotenv
from discord.ext import commands
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select
from pathlib import Path

# Adding the latest version of the osnap_client to the path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))

from osnap_client.protocol import AgentCommand, AgentCommandType


class SwarmManager:
    def __init__(self):
        load_dotenv()
        intents = discord.Intents.default()
        intents.members = intents.guilds = intents.messages = intents.message_content = intents.reactions = True

        self.client = discord.Client(intents=intents)
        self.engine = create_engine('sqlite:///tasks.db', echo=True)
        self.metadata = MetaData()

        # Define the tables
        self.tasks_table = Table(
            'tasks', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('type', String),
            Column('description', String),
            Column('status', String)
        )

        self.agents_table = Table(
            'agents_table', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('description', String),
            Column('task_types', String)
        )

        self.commands_table = Table(
            'commands_table', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('capable_users', String)
        )

        self.special_commands = {
            'who': self.who,
            'what': self.what,
            'whats_going': self.whats_going
        }

        # Create the tables
        self.metadata.create_all(self.engine)
        self.conn = self.engine.connect()

        # Define event handlers
        @self.client.event
        async def on_ready():
            await self.on_ready()

        @self.client.event
        async def on_message(message: discord.Message):
            await self.on_message(message)

    async def on_ready(self):
        self.log(f'We have logged in as {self.client.user}')
        available_commands = self.special_commands.keys()
        listening_on_channels = [channel.name for channel in self.client.get_all_channels()]
        intro = f'Hello, I am {self.client.user.name}. I am ready to manage your tasks. Available commands:{available_commands}.\nListening on channels:{listening_on_channels}'
        target_channel = "intros"

        await self.client.change_presence(status=discord.Status.online)

        for channel in self.client.get_all_channels():
            if channel.name == target_channel and isinstance(channel, discord.TextChannel):
                await channel.send(intro)
                return

    async def on_message(self, message: discord.Message):
        if message.author == self.client.user:
            return

        # handle special commands (subscribe, who, what, whats_going)
        for command in self.special_commands:
            if message.content.startswith(f'${command}'):
                data = message.content.split(' ')[1:]
                data = ' '.join(data)
                await self.special_commands[command](message, data)
                return

        # Handle custom commands to the bots
        if message.content.startswith('$'):
            command = message.content[1:].split(' ')[0].lower()
            result = self.conn.execute(select(self.commands_table).where(self.commands_table.c.name == command)).fetchone()
            if result is None:
                custom_manager_commands = [command.name for command in self.client.commands]
                if command not in custom_manager_commands:
                    await message.reply(f'There is no such bot who can do ${command}')
                else:
                    # add the task to the tasks table
                    task_type = command
                    task_description = ' '.join(message.content[1:].split(' ')[1:])
                    self.conn.execute(self.tasks_table.insert().values(type=task_type, description=task_description, status='pending'))
                    await self.message_relevant_agents(task_type, task_description)

        # handle bot to Swarm communication
        if message.content.startswith('{'):
            try:
                agent_command = AgentCommand.parse_raw(message.content)
                if agent_command.command_type == AgentCommandType.REGISTER:
                    await self.register_bot(message_obj=message, data=agent_command)
            except Exception as e:
                self.log(f"Error parsing message: {e}")
                await message.reply('Failed to parse message. Use the following format:\n{ "sender": "agent", "receiver": "discord_adapter", "command": "request", "task_name": "hello", "data": "xxx" }')

    async def message_relevant_agents(self, task_type, task_description):
        self.log(f'Querying agents for {task_type}')
        result = self.conn.execute(select(self.agents_table)).fetchall()
        username_idx = self.agents_table.c.keys().index('name')
        task_types_idx = self.agents_table.c.keys().index('task_types')
        for row in result:
            if task_type in row[task_types_idx].lower().replace(' ', '').split(','):
                username = row[username_idx]
                for user in self.client.users:
                    if user.name == username:
                        command = AgentCommand(
                            sender="Task Manager",
                            receiver=user.name,
                            command_type=AgentCommandType.TASK,
                            task_name=task_type,
                            payload=task_description
                        ).json()
                        message = f'$available_task {command}'
                        await user.send(message)

    async def register_bot(self, message_obj: discord.Message, data: AgentCommand):
        author_name = message_obj.author.name
        if author_name != data.sender:
            await message_obj.reply(f'You ({author_name}) are not allowed to register {data.sender}.')
            return
        
        result = self.conn.execute(select(self.agents_table).where(self.agents_table.c.name == author_name)).fetchone()

        task_types = data.payload['available_commands']
        description = data.payload['description']

        if result is None:
            self.conn.execute(self.agents_table.insert().values(name=author_name, description=description, task_types=','.join(task_types)))
            self.log(f'Added {author_name} with {task_types} and {description}')
        else:
            self.conn.execute(self.agents_table.update().where(self.agents_table.c.name == author_name).values(task_types=task_types))
            self.conn.execute(self.agents_table.update().where(self.agents_table.c.name == author_name).values(description=description))
            self.log(f'Updated {author_name} with {task_types} and {description}')

        for task_type in task_types:
            result = self.conn.execute(select(self.commands_table).where(self.commands_table.c.name == task_type)).fetchone()
            if result is None:
                self.conn.execute(self.commands_table.insert().values(name=task_type, capable_users=author_name))
                self.log(f'Added {task_type} with {author_name}')
            else:
                cu_idx = self.commands_table.c.keys().index('capable_users')
                existing_users = result[cu_idx].split(',')
                if author_name in existing_users:
                    continue
                new_users = ','.join([author_name] + existing_users)
                self.conn.execute(self.commands_table.update().where(self.commands_table.c.name == task_type).values(capable_users=new_users))
                self.log(f'Updated {task_type} with {new_users}')

        await message_obj.reply(f'Subscription successful.')

    async def who(self, message_obj: discord.Message, data: str):
        self.log('Querying agents')
        result = self.conn.execute(select(self.agents_table)).fetchall()
        username_idx = self.agents_table.c.keys().index('name')
        description_idx = self.agents_table.c.keys().index('description')
        task_types_idx = self.agents_table.c.keys().index('task_types')
        users_dict = {}
        for row in result:
            users_dict[row[username_idx]] = {
                'description': row[description_idx],
                'task_types': row[task_types_idx]
            }
        
        response = AgentCommand(
            sender="swarm",
            receiver=message_obj.author.name,
            command_type=AgentCommandType.INFO,
            task_name="who",
            payload_type = 'dict',
            payload=users_dict
        ).json()


        await message_obj.reply(response)

    async def what(self, message_obj: discord.Message, data: str):
        self.log('Querying commands')
        result = self.conn.execute(select(self.commands_table)).fetchall()
        command_name_idx = self.commands_table.c.keys().index('name')
        capable_users_idx = self.commands_table.c.keys().index('capable_users')
        commands_dict = {}
        for row in result:
            commands_dict[row[command_name_idx]] = row[capable_users_idx].split(',')

        response = AgentCommand(
            sender="swarm",
            receiver=message_obj.author.name,
            command_type=AgentCommandType.INFO,
            task_name="what",
            payload_type = 'dict',
            payload=commands_dict
        ).json()

        await message_obj.reply(response)

    async def whats_going(self, message_obj: discord.Message, data: str):
        self.log('Querying tasks')
        result = self.conn.execute(select(self.tasks_table)).fetchall()[:100]
        type_idx = self.tasks_table.c.keys().index('type')
        descr_idx = self.tasks_table.c.keys().index('description')
        status_idx = self.tasks_table.c.keys().index('status')
        tasks = {}
        for row in result:
            tasks[row[type_idx]] = (row[descr_idx], row[status_idx])

        response = AgentCommand(
            sender="swarm",
            receiver=message_obj.author.name,
            command_type=AgentCommandType.INFO,
            task_name="whats_going",
            payload_type = 'dict',
            payload=tasks
        ).json()

        await message_obj.reply(response)

    def run(self):
        self.client.run(os.getenv("TASK_MANAGER_TOKEN"))

    def log(self, message):
        print(message)

if __name__ == "__main__":
    swarm_manager = SwarmManager()
    swarm_manager.run()

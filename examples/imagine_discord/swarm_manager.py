import sys, os, time
from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select

# adding the lates version of the osnap_client to the path
from pathlib import Path
file_path = Path(__file__).absolute()
sys.path.append(str(file_path.parent.parent.parent))

from osnap_client.adapters import DiscordAdapter
from osnap_client.agents import SwarmAgentBase
from osnap_client.protocol import AgentCommand, AgentCommandType
from osnap_client.utils.ai_engines import DalleEngine

class SwarmManager(SwarmAgentBase):
    def __init__(self, name, description, swarm_adapter):
        super().__init__(name, description, swarm_adapter)

        @self.command(name="register")
        async def register(message: AgentCommand):
            await self.register_agent(message)
            print(f"Registered agent {message.sender}")

        @self.command(name="who")
        async def who(message: AgentCommand):
            await self.who_is_available(message)

        @self.command(name="what")
        async def what(message: AgentCommand):
            await self.what_is_available(message)

        @self.command(name="whats_going")
        async def whats_going(message: AgentCommand):
            await self.whats_going_on(message)

        @self.command(name="task")
        async def task(message: AgentCommand):
            await self.handle_task(message)

        self._init_db()
        self._self_register()

    async def register_agent(self, data: AgentCommand):
        author_name = data.sender
        
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

        response = AgentCommand(
            sender=self.name,
            receiver="agent",
            command_type=AgentCommandType.REGISTER,
            task_type="register",
            payload_type = 'str',
            payload=f"200: OK",
        )

        await self.swarm_adapter.send_dm(response, author_name)

    async def who_is_available(self, data: AgentCommand):
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
            receiver=data.sender,
            command_type=AgentCommandType.INFO,
            task_type="who",
            payload_type = 'dict',
            payload=users_dict
        )

        await self.swarm_adapter.send_dm(response, data.sender)
    
    async def what_is_available(self, data: AgentCommand):
        self.log('Querying commands')
        result = self.conn.execute(select(self.commands_table)).fetchall()
        command_name_idx = self.commands_table.c.keys().index('name')
        capable_users_idx = self.commands_table.c.keys().index('capable_users')
        commands_dict = {}
        for row in result:
            commands_dict[row[command_name_idx]] = row[capable_users_idx].split(',')

        response = AgentCommand(
            sender="swarm",
            receiver=data.sender,
            command_type=AgentCommandType.INFO,
            task_type="what",
            payload_type = 'dict',
            payload=commands_dict
        )

        await self.swarm_adapter.send_dm(response, data.sender)

    async def whats_going_on(self, data: AgentCommand):
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
            receiver=data.sender,
            command_type=AgentCommandType.INFO,
            task_type="whats_going",
            payload_type = 'dict',
            payload=tasks
        )

        await self.swarm_adapter.send_dm(response, data.sender)       

    async def handle_task(self, data: AgentCommand):
        """Agents in the swarm exchange tasks with each other.
        1. Extract task from the payload: task = Task.from_json(data.payload) if data.payload_type == 'task' else error
        2. Check if the given task is in the database
        3. if yes, update the status of the task and send it to the relevant agent 
        4. if no, add the task to the database and send it to the relevant agent
        """
        self.log('Handling task')

    def _init_db(self):
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
        # Create the tables
        self.metadata.create_all(self.engine)
        self.conn = self.engine.connect()

    def _self_register(self):
        self.log('Registering self')
        task_types = [command for command in self.command_map.keys() if command != "on_ready"]
        description = self.description
        author_name = self.name

        result = self.conn.execute(select(self.agents_table).where(self.agents_table.c.name == author_name)).fetchone()

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

    def log(self, message):
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {message}')

def main():
    """
    On a mac, go to Macintosh HD > Applications > Python3.x folder (x being your python3 version) > double click on "Install Certificates.command" file
    """
    load_dotenv()

    intents_list = ["message_content", "members", "guilds", "messages", "reactions"]
    adapter = DiscordAdapter(
        start_server=os.getenv("START_SERVER_NAME"),
        intents_list=intents_list,
        token=os.getenv("TASK_MANAGER_TOKEN"),
    )

    agent = SwarmManager(
        name="SwarmManager",
        description="I manager the swarm: I keep track of who is capable of doing what and who is doing what.",
        swarm_adapter=adapter
    )
    agent.run()


if __name__ == "__main__":
    main()

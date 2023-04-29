import uuid
from .agents.PersonalAgent import (TaskStatus, TaskType)

class ForeverRunningAgent(PersonalAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.should_run = True

    def run(self):
        while self.should_run:
            user_input = input("Enter a prompt (type 'exit' to stop): ")
            
            if user_input.lower() == 'exit':
                self.should_run = False
                continue

            self.process_prompt(user_input)
            response = self.generate_final_response()
            print(f"Response: {response}")

    def breakdown_prompt(self, prompt):
        # Stub logic for breaking down the prompt into tasks
        tasks = [
            {
                "id": str(uuid.uuid4()),
                "type": TaskType.LLM,
                "description": "Task 1",
                "status": TaskStatus.OPEN
            },
            {
                "id": str(uuid.uuid4()),
                "type": TaskType.SEARCH,
                "description": "Task 2",
                "status": TaskStatus.OPEN
            }
        ]
        return tasks

    def generate_final_response(self):
        # Implement logic for generating the final response
        response = "This is the final response."
        return response

if __name__ == "__main__":
    forever_running_agent = ForeverRunningAgent()
    forever_running_agent.run()

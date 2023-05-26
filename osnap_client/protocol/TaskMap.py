import uuid
from threading import Lock
import time
import json

class TaskMedia:
    def __init__(self, object_type, object_data):
        self.object_type = object_type
        if not isinstance(object_data, str):
            raise TypeError(f"Expected a string, got {type(object_data)}. Encode the object to ASCII base64 before passing it to TaskMedia: base64.b64encode(object_data).decode('utf-8')")
        self.object_data = object_data

class Task:
    """Class to represent a task in the TaskMap

    Args:
    - task_id (str): A unique identifier for the task
    - created_at (float): A timestamp of when the task was created
    - task_description (str): A description of the task
    - related_media (list): A list of TaskMedia objects that are related to the task
    - subtasks (set): A set of subtask ids that are related to the task
    - status (str): The status of the task, one of "pending", "in_progress", "completed", "failed"
    - result (str): The result of the task, if any
    
    """
    def __init__(self, task_description, related_media: list=[], suptask=None):
        """Constructor for the Task class

        Args:
            task_description (str): A description of the task
            related_media (list, TaskMedia): A list of TaskMedia objects that are related to the task
        """
        self.task_id = str(uuid.uuid4())
        self.created_at = time.time()
        self.task_description = task_description
        for el in related_media:
            if not isinstance(el, TaskMedia):
                raise TypeError(f"Expected a TaskMedia object, got {type(el)}")
        self.related_media = related_media
        self.subtasks = set()
        self.suptask = None
        self.status = "pending"
        self.result = None

    def update(self, status, result=None, related_media=None):
        self.status = status
        self.result = result
        if related_media:
            for el in related_media:
                if not isinstance(el, TaskMedia):
                    raise TypeError(f"Expected a TaskMedia object, got {type(el)}")
            self.related_media.extend(related_media)

    def add_subtask(self, task_id):
        self.subtasks.add(task_id)

    def copy(self):
        out = {}
        for k, v in self.__dict__.items():
            if isinstance(v, set):
                out[k] = list(v)
            else:
                out[k] = v
        return out
    
    def json(self):
        return json.dumps(self.copy())
    
    @staticmethod
    def from_dict(task_dict):
        try:
            task = Task(task_dict["task_description"], task_dict["related_media"])
            task.task_id = task_dict["task_id"]
            task.created_at = task_dict["created_at"]
            task.subtasks = set(task_dict["subtasks"])
            task.suptask = task_dict["suptask"]
            task.status = task_dict["status"]
            task.result = task_dict["result"]
        except KeyError as e:
            raise ValueError("Invalid task dictionary") from e
        return task

    @staticmethod
    def from_json(json_str):
        try:
            task_dict = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string") from e
        return Task.from_dict(task_dict)

class TaskMap:
    """Class to represent a map of tasks.
    Tasks can only be solved if all of their subtasks are solved.    
    """
    def __init__(self):
        self.tasks = {}
        self.lock = Lock()

    def create_task(self, task_info: str, related_media: list=[]):
        """Create a new task

        Args:
        - task_info (str): A description of the task
        - related_media (list, TaskMedia): A list of TaskMedia objects that are related to the task

        Returns:
        - str: The task id of the created task
        - dict: A copy of the created task
        """
        with self.lock:
            task = Task(task_info, related_media)
            self.tasks[task.task_id] = task
            return task.task_id, task

    def update_task(self, task_id: str, status, result=None, related_media=[]):
        with self.lock:
            self.tasks[task_id].update(status, result, related_media)

    def add_subtask(self, task_id, subtask_info, related_media=[]):
        """Add a subtask to an existing task

        Args:
        - task_id (str): The task id of the parent task
        - subtask_info (str): A description of the subtask

        Returns:
        - str: The task id of the created subtask
        - dict: A copy of the created subtask
        """
        with self.lock:
            subtask = Task(subtask_info, related_media, suptask=task_id)
            self.tasks[subtask.task_id] = subtask
            self.tasks[task_id].add_subtask(subtask.task_id)
            return subtask.task_id, subtask

    def get_task(self, task_id):
        with self.lock:
            task_base = self.tasks[task_id].copy()
            subtasks = {}
            for subtask_id in task_base.subtasks:
                subtasks[subtask_id] = self.get_task(subtask_id)
            
            task_base["subtasks"] = subtasks        
        return task_base
    
    def json(self, task_id):
        task_dict = self.get_task(task_id)
        return json.dumps(task_dict, indent=4)

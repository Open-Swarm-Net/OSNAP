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
    def __init__(self, task_description, related_media: list=[]):
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

class TaskMap:
    def __init__(self):
        self.tasks = {}
        self.lock = Lock()

    def create_task(self, task_info: str, related_media: list=[]):
        with self.lock:
            task = Task(task_info, related_media)
            self.tasks[task.task_id] = task
            return task.task_id

    def update_task(self, task_id: str, status, result=None, related_media=[]):
        with self.lock:
            self.tasks[task_id].update(status, result, related_media)

    def add_subtask(self, task_id, subtask_info, related_media=[]):
        with self.lock:
            subtask = Task(subtask_info, related_media)
            self.tasks[subtask.task_id] = subtask
            self.tasks[task_id].add_subtask(subtask.task_id)
            return subtask.task_id

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

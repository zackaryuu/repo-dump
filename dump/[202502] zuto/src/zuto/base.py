import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import List, Dict
from .etc import SequenceUseException
from .model import Task
from zuu.STRUCT.DECOR.track_and_terminate import lifetime, cleanup
from zuu.PKG.importlib import import_file

class Zuto:
    def __init__(self, tasks_folder: str):
        self.tasks_folder = Path(tasks_folder)
        self.pending_queue: List[Task] = []
        self.task_paths: Dict[str, str] = {}  # task_id: file_path
        self.observer = Observer()
        self.setup_functions = {}
        self._setup_file_monitoring()
        
    def _setup_file_monitoring(self):
        class TaskFileHandler(FileSystemEventHandler):
            def __init__(self, processor):
                self.processor = processor
                
            def on_modified(self, event):
                if event.src_path.endswith(('.yml', '.yaml')):
                    self.processor._reload_task(event.src_path)

        self.observer.schedule(
            TaskFileHandler(self), 
            str(self.tasks_folder), 
            recursive=True
        )
        self.observer.start()

    def _load_initial_tasks(self):
        for file_path in self.tasks_folder.glob("*.yml"):
            self._load_task(file_path)
        for file_path in self.tasks_folder.glob("*.yaml"):
            self._load_task(file_path)

    def _load_task(self, file_path: str):
        try:
            task = Task.from_yaml(file_path)
            self.pending_queue.append(task)
            self.task_paths[task.id] = str(file_path)
        except Exception as e:
            logging.error(f"Error loading task {file_path}: {e}")

    def _reload_task(self, file_path: str):
        # Remove existing task if not yet executed
        for idx, task in enumerate(self.pending_queue):
            if self.task_paths.get(task.id) == file_path:
                del self.pending_queue[idx]
                break
                
        # Reload and add back to queue
        self._load_task(file_path)

  

    def _execute_task(self, task: Task):
        def _internal(task: Task):
            # Add your actual task execution logic here
            print(f"Executing task: {task.name}")
            # Example execution: perform steps
            for step in task.steps:
                print(step)
                time.sleep(1)
        
        func = _internal
        if task.meta.lifetime:
            func = lifetime(task.meta.lifetime)(func)

        if task.meta.cleanup:
            func = cleanup(windows=task.meta.cleanup, processes=task.meta.cleanup, new_only=True)(func)

        try:
            func(task)
        except Exception as e:
            logging.error(f"Error executing task {task.name}: {e}")
            raise

    def _should_skip_task(self, task: Task) -> bool:
        if task.meta.cond:
            try:
                return not eval(task.meta.cond)
            except Exception as e:
                logging.error(f"Condition evaluation failed for {task.name}: {e}")
                return True
        return False

    def start(self):
        self._load_initial_tasks()
        try:
            while True:
                try:
                    if not self.pending_queue:
                        raise SequenceUseException()
                    
                    task = self.pending_queue.pop(0)
                    if self._should_skip_task(task):
                        logging.info(f"Skipping task {task.name} due to condition")
                        raise SequenceUseException()

                    self._execute_task(task)

                except SequenceUseException:          
                        time.sleep(1) 
                        continue

        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join() 
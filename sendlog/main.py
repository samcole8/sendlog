from utils.config_handler import ConfigHandler
from utils.workflow_manager import WorkflowManager
from log_monitor import LogMonitor

import threading
import queue
import time

CONFIG_PATH = "/etc/sendlog/sendlog.yml"
PLUGIN_DIR = "plugins"

def process_workflows(workflow_queue):
    while True:
        workflow, msg = workflow_queue.get()
        workflow._execute(msg)
        workflow_queue.task_done()

def main():
    # Load config into ConfigHandler
    config_handler = ConfigHandler(CONFIG_PATH)
    
    # Create WorkflowManager
    workflow_manager = WorkflowManager()

    # Load destinations from config
    for data in config_handler.destinations():
        workflow_manager.load_destinations(*data)

    # Load file workflows from config
    for data in config_handler.files():
        workflow_manager.load_workflow(*data)

    # Set up worker thread
    workflow_queue = queue.Queue()
    worker_thread = threading.Thread(target=process_workflows, args=(workflow_queue,))
    worker_thread.daemon = True
    worker_thread.start()

    # Start file monitoring
    paths = workflow_manager.get_paths()
    log_monitor = LogMonitor(paths)
    for path, msg in log_monitor.monitor():
        workflow = workflow_manager.get_workflow(path)
        workflow_queue.put((workflow, msg))


if __name__ == "__main__":
    main()
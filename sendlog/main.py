from config_handler import ConfigHandler
from workflow_manager import WorkflowManager
from log_monitor import LogMonitor

from utils import log
import logging
import threading
import queue
import time

CONFIG_PATH = "/etc/sendlog/sendlog.yml"

def process_workflows(workflow_queue):
    while True:
        workflow, msg = workflow_queue.get()
        workflow(msg)
        workflow_queue.task_done()

def main():

    # Load config into ConfigHandler
    config_handler = ConfigHandler(CONFIG_PATH)
    
    # Start logging
    log.config(config_handler.log_path)
    logger = logging.getLogger(__name__)

    # Create WorkflowManager
    workflow_manager = WorkflowManager()

    # Load endpoints from config
    for data in config_handler.endpoints():
        workflow_manager.load_endpoint(*data)

    # Load file workflows from config
    for data in config_handler.files():
        workflow_manager.load_file(*data)
    
    workflow_manager.display_worktrees()

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
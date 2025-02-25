from utils.config_handler import ConfigHandler
from utils.workflow_manager import WorkflowManager
from log_monitor import LogMonitor

def main():
    # Load config into ConfigHandler
    config_handler = ConfigHandler("sendlog.yml")
    
    # Create WorkflowManager
    workflow_manager = WorkflowManager()

    # Load destinations from config
    for data in config_handler.destinations():
        workflow_manager.load_destinations(*data)

    # Load file workflows from config
    for data in config_handler.files():
        workflow_manager.load_workflow(*data)
    
    # Start file monitoring
    paths = workflow_manager.get_paths()
    log_monitor = LogMonitor(paths)
    for path, msg in log_monitor.monitor():
        print(f"{path}: {msg}")
        # workflow_manager.get_workflow(path).execute(msg)


if __name__ == "__main__":
    main()
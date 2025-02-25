import inotify.adapters
import os

class LogMonitor:
    """Wrapper for inotify that detects new lines only."""
    def __init__(self, paths):
        self.notifier = inotify.adapters.Inotify()
        self.file_positions = {path: os.path.getsize(path) for path in paths}
        self.add_watches(paths)
    
    def add_watches(self, paths):
        for path in paths:
            self.notifier.add_watch(path)
    
    def monitor(self):
        """Yield log message and origin when a change is detected."""
        while True:
            for event in self.notifier.event_gen(yield_nones=False, timeout_s=1):
                (_, event_types, path, _) = event
                if "IN_MODIFY" in event_types and path in self.file_positions:
                    with open(path, "r") as f:
                        f.seek(self.file_positions[path])
                        new_lines = f.readlines()
                        self.file_positions[path] = f.tell()
                        for line in new_lines:
                            yield path, line.strip()
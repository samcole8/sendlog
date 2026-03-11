class Msg:
    def __init__(self, text):
        self.text = text
        self.context = {}
        self._cache = {}
    
    def match(self, pattern):
        if pattern not in self._cache:
            self._cache[pattern] = re.search(pattern, self.text)
        return self._cache[pattern]

class Sendlog:
    def __init__(self):
        self._watchers = []
    
    def watch(self, source, sinks):
        def decorator(fn):
            self._watchers.append((source, sinks, fn))
            return fn
        return decorator
    
    def run(self):
        pass
# Plugin DSL

*See [Plugin Architecture]() prior to reading this section.*

- [Plugin Modules](#plugin-modules)
- [Plugin Class Basics](#plugin-class-basics)
- [Channel Module](#channel-module)
  - [Channel Class](#channel-class)
  - [Example](#example)
- [Log Module](#log-module)
  - [LogType Class](#logtype-class)
  - [Rule Class](#rule-class)
  - [Transformer Class](#transformer-class)
  - [Example](#example-1)


## Plugin Modules

At the highest level, all plugins are Python modules.

There are two types of plugin module:

- **Channel** modules should define how an alert gets to an endpoint.
- **Log** modules should define how log lines are parsed from a specific source.

Plugin modules should be placed in their respective parent directories within the root `plugins` directory. For example:

```py
sendlog # repository root
└── sendlog
    └── plugins # root plugins directory
        ├── channels # channel plugin modules go in here
        │   ├── file.py
        │   ├── smtp.py
        │   ├── stdout.py
        │   ├── telegram.py
        │   └── twilio_sms.py
        └── logs # log plugin modules go in here
            ├── auth.py
            ├── sendlog.py
            └── systemd.py
```

While modules provide a layer of convenience when managing plugins, the plugin system does not recognise or enforce them beyond the import constraints shown above.

## Plugin Class Basics

Plugin modules contain one or more **plugin class**. These classes represent nodes on a **worktree**: processes that convert a log to a payload or send it to an endpoint.

Generally speaking, plugin classes are created by extending the relevant superclass and implementing the `__call__` method. If plugins do not inherit from the expected base, they will be rejected.

Plugin superclasses can be imported from the `plugin` module. However, plugin superclasses will vary depending on which module you are writing for.

## Channel Module

Channel modules should only define one class: that extending the **Channel superclass**, which defines how an alert gets to an endpoint.

### Channel Class

All custom channel classes must extend the Channel superclass:

```py
class Channel(ABC, metaclass=_ChannelMeta):
    __slots__ = ["name"]
    def __init__(self, name, **kwargs):
        self.name = name

        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def __call__(self, msg):
        pass
```

**Explanation**:

- Channel is an abstract base class. You must implement the `__call__` method in subclasses.
- Extra attributes (e.g. API keys) are passed via the config file and must be declared in `__slots__` within the subclass.

**Constraints**:

- You cannot override the `__init__` method for Channel subclasses.
- The `__call__` method should contain exactly one additional parameter (`msg` is suggested) to accomodate the alert payload.

### Example

Below is an example of a Channel plugin module, which contains a Channel plugin class:

```py
from plugin import Channel # import Channel superclass

import requests

class Telegram(Channel): # must inherit from Channel superclass
    __slots__ = ["chat_id", "token"] # Channel variables

    # entrypoint method
    def __call__(self, msg): # must take an additional parameter
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {"chat_id": self.chat_id, "text": msg}
        requests.post(url, params=params,)
```

**Explanation**

- `Channel` is imported from the `plugin` module.
- `Telegram` extends `Channel`.
- The required attributes `chat_id` and `token` are specified in `__slots__`.
- The `__call__` method is the entrypoint for delivery.
- When this plugin is called (e.g., `telegram("Hello!")`), it sends a message using Telegram’s Bot API.


## Log Module

Log modules define how logs are matched, filtered and transformed by extending the `LogType`, `Rule`, and `Transformer` superclasses.

The DSL allows you to create modular, hierarchical definitions that map directly to components of log processing:

- Log sources (like auth.log)
- Event types (like new login)
- Transformations (like rendering a human-readable format)

The hierarchical constraints of these components are maintained by nesting:

```py
from plugin import LogType, Rule, Transformer

class MyLogType(LogType):                 # Top-level log source plugin

    class MyRule(Rule):                   # A specific type of event

        class MyTransformer(Transformer): # Transforms matched event into payload
            pass
```

Currently, sendlog only permits workflows that consist of a `LogType`, `Rule`, and `Transformer`. If we think of the structure as a tree:

- The top-level node (e.g. `MyLogType`) must extend `LogType`
- The second-level node (e.g. `MyRule`) must extend `Rule`
- The leaves of the tree (e.g. `MyTransformer`) must extend `Transformer`

Like all plugins, the `__call__` method defines how the class performs its' function. The output (`return` value) of one plugin is chained to the subnodes in the tree. However, some of these plugins have default implementations that can simplify the plugin definition.

### LogType Class

The `LogType` superclass defines how logs are matched to a generic structure. It is best used to extract common fields from semi-structured log sources.

```py3
class LogType(ABC, metaclass=_LogTypeMeta):
    """
    Base class for a LogType plugin.
    """

    regex = None

    def __call__(self, log_line: str):
        """
        Convert log_line to structured JSON using regex.
        
        Must return a dictionary with the "message" key.
        """
        if self.__class__.regex:
            match = re.match(self.__class__.regex, log_line)
            if match:
                log_parts = match.groupdict()
                return log_parts
            else:
                raise TypeError("Log line did not match the expected format.")
        else:
            return {"message": log_line}
```

**Explanation**:

- `LogType` contains a default `__call__` method that uses the class-level `regex` variable to create a dictionary from the provided log line.
- The `regex` variable must contain a valid named-group regular expression.
- The `__call__` method can be overriden in a subclass to use a different matching technique.
- Without specifying a regex string, the plugin assumes the entire log line is the message. This maintains compatibility with other plugin defaults.
- If a log does not match the expected format, an error will be raised.

**Constraints**:

- If implemented, the `__init__` method can only contain the `self` parameter.
- The `__call__` method should contain exactly one additional parameter (`log_line` is suggested) to accomodate the log line.
- The `__call__` method must return a value that is compatible with all subnodes.

### Rule Class

`Rule` plugins are similar to `LogType` plugins, but they do not raise errors when the message doesn't match. They extend the `Rule` superclass:

```py
class Rule(ABC, metaclass=_RuleMeta):

    regex = None
    
    def __call__(self, log_parts: dict):
        """Convert log message to structured JSON."""
        if self.__class__.regex:
            match = re.match(self.__class__.regex, log_parts["message"])
            if match:
                message_parts = match.groupdict()
                return {**log_parts, "context": {**message_parts}}
        return False
```

**Explanation**

- `Rule` contains a default `__call__` method that uses the class-level `regex` variable to create a dictionary from the provided log line.
- If the function returns something other than `None` or `False`, the rule will trigger an alert.
- The `regex` variable must contain a valid named-group regular expression.
- The `__call__` method can be overriden in a subclass to use a different matching technique.
- Without specifying a regex string, the plugin always returns `False`, and will never trigger an alert.
- By default, the `Rule` plugin expects a `message` key from the parent `LogType`; this is used for the matching process.

**Constraints**:

- If implemented, the `__init__` method can only contain the `self` parameter.
- The `__call__` method should contain exactly one additional parameter (`log_line` is suggested) to accomodate the log line.
- The `__call__` method must return a value that is compatible with all subnodes.

### Transformer Class

```py
class Transformer(ABC, metaclass=_TransformerMeta):

    def __call__(self, log_parts: dict):
        return log_parts["message"]
```

**Explanation**

- `Transformer` contains a default `__call__` method that simply returns the `message` key from the provided dictionary.
- The `__call__` method can be overriden in a subclass to define a custom transformation.

**Constraints**

- If implemented, the `__init__` method can only contain the `self` parameter.
- The `__call__` method should contain exactly one additional parameter (`log_line` is suggested) to accomodate the log line.

### Example

```py
from plugin import LogType, Rule, Transformer
from datetime import datetime

class Pacman(LogType):
    regex = r"\[(?P<timestamp>.*?)\] \[(?P<application>.*?)\] (?P<message>.*)"

    class RunCommand(Rule):
        regex = r"Running\s+'(?P<command>[^']+)'"

        class HumanReadable(Transformer):
            def __call__(self, parts):
                context = parts["context"]
                timestamp = datetime.strptime(parts["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
                return f"Command '{context["command"]}' detected at {timestamp.strftime("%Y-%m-%d %H:%M")}."
        
        class JSONL(Transformer):
            def __call__(self, parts):
                return parts
```

**Explanation**:

- The `Pacman` LogType produces a dictionary with the `timestamp`, `application`, and `message` keys.
- The `RunCommand` Rule tests whether the `message` matches a regular expression indicating a specific log event.
- The `HumanReadable` Transformer converts the log into a convenient human-readable message using the extracted values.
- The `JSONL` Transformer simply returns the log in dictionary form.
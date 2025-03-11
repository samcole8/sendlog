## Plugins

- [Overview](#overview)
- [Logs](#logs)
  - [Shared Functions](#shared-functions)
  - [Pattern Recognition](#pattern-recognition)
- [Channels](#channels)

### Overview

In sendlog, the term *plugin* refers to any section of code that is imported dynamically based on the contents of the configuration file. They allows users to define custom behaviours for alert handling. There are two broad types:

- **Logs**: Plugins that define how a log line is processed when a new line is added. They are read from `sendlog/plugins/logs/`.
- **Channels**: Plugins that define how an alert is sent to an endpoint. They are read from `sendlog/plugins/channels/`.

### Logs

Log plugins have three components:

- **LogTypes**: Containers for logic relating to a specific log type (e.g., `/var/log/pacman.log`).
- **Rules**: Evaluation logic that controls whether an alert will fire, based on the contents of a log message.
- **Transformers**: Parsing logic that converts a message into another format.

Transformers belong to Rules, which belong to LogTypes. This hierarchy is fundamental to the program's operation, and should be consistently represented in both the [configuration](configuration-file.md) file and the plugins themselves.

These parts are represented as classes, and must inherit from the corresponding `LogType`, `Rule` and `Transformer` base classes. A simple template is shown below:

```py
from plugin import LogType, Rule, Transformer

class MyLogType(LogType):

    class __call__(Rule):
        def evaluate(self, line):
            # Return `True` to send the alert, or `False` to drop it.
            return True 

        class MyTransformer(Transformer):
            def __call__(self, line):
                # Do something with line
                return line
```

- The `__call__` [dunder](https://docs.python.org/3/reference/datamodel.html) method shown above is an entrypoint function that is **required** for each rule or transformer to work. If they are left unimplemented, they will cause an error during runtime.
- The `__call__` method can call other methods within the same scope or access properties. However, it must not contain more than two arguments (including `self`), or the plugin will be rejected.

#### Shared Functions

In some cases, you might want to "share" a function between multiple rules or transformers. This is simple to do with multiple inheritance:

```py
from plugin import LogType, Rule, Transformer

class MyTransformerExtension(): # Must not inherit from Transformer
    def my_shared_function(self, line):
        # Do something with line
        return line

class MyLogType(LogType):

    class MyRule(Rule):
        def __call__(self, line):
            return True 

        class MyTransformer(Transformer, MyTransformerExtension):
            def __call__(self, line):
                # Can use methods of MyTransformerExtension
                self.my_shared_function(line)
                return line

    class MyOtherRule(Rule):
        def __call__(self, line):
            return True 

        class MyOtherTransformer(Transformer, MyTransformerExtension):
            def __call__(self, line):
                # Can also use methods of MyTransformerExtension
                self.my_shared_function(line)
                return line
        
        class MyOtherTransformer2(Transformer):
            def __call__(self, line):
                # Has no access to MyTransformerExtension
                return line
```

- Note that in order to function correctly, the custom transformer must not inherit from the `Transformer` base class. It is not considered a complete transformer and does not need to be part of the hierarchy.

#### Pattern Recognition

sendlog supports basic pattern recognition using properties. You can define an `__init__` method to set these.

```py
class MyLogType(LogType):

    class FailedLogin(Rule):

        def __init__(self):
            self.login_attempts = 0

        def __call__(self, line):
            # Check if login failed or succeeded
            if "Failed login" in line:
                self.login_attempts += 1
            elif "Login success" in line:
                self.login_attempts = 0
            # Trigger after 3 failed attempts
            if self.login_attempts >=3:
                trigger = True
            else:
                trigger = False
            return trigger
```

- The `__init__` method must only contain the `self` argument, or the plugin will be rejected.

### Channels

Channels are represented by classes with a mandatory `__call__` function that acts as an entrypoint for sending the alert. They must inherit from the `Endpoint` superclass.

An example of an endpoint is shown below:

```py
from plugin import Endpoint
import requests

class Telegram(Endpoint):
    # Explicitly state required variables here
    required_vars = ["chat_id", "token"]

    # Entrypoint method
    def __call__(self, msg):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {"chat_id": self.chat_id, "text": msg}
        response = requests.post(url, params=params,)
        if response.status_code == 200:
            print(f"{msg} -> {self}")
```

- Unlike log plugins, Channels can accept additional keyword arguments such as URLs, as long as they are specified in the configuration file (see [destinations](configuration-file.md#destinations)) and the channel itself. They should be explicitly stated (e.g., `required_vars = ["chat_id", "token"]`).
- The `__init__` method cannot be used, or the plugin will be rejected.
- The `__call__` [dunder](https://docs.python.org/3/reference/datamodel.html) method shown above is an entrypoint function that is **required** for each channel to work. If left unimplemented, it will cause an error during runtime.
- The `__call__` method can call other methods within the same scope or access properties. However, it must not contain more than two arguments (including `self`), or the plugin will be rejected.
<hr>

Next: [Configuration file](configuration-file.md)
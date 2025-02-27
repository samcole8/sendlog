## Plugins

- [Overview](#overview)
- [Workflows](#workflows)
  - [Shared Functions](#shared-functions)
- [Endpoints](#endpoints)

### Overview

sendlog allows users to define their own behaviours for alert handling through **plugins**. There are two types:

- **Workflow** plugins define how a log line is processed when a new line is added. They are read from `sendlog/plugins/workflows/`.
- **Endpoint** plugins define how an alert is sent to a destination. They are read from `sendlog/plugins/endpoints/`.

### Workflows

Workflow plugins have three components:

- **LogTypes**: Containers for logic relating to a specific log type (e.g., `/var/log/pacman.log`).
  - **Rules**: Evaluations that control whether an alert will fire, based on the contents of a log message.
    - **Transformer**: Parsers that convert a message into another format.

Transformers belong to Rules, which belong to LogTypes. This hierarchy is fundamental to the program's operation, and should be consistently represented in both the [configuration](configuration-file.md) file and the plugins themselves.

These parts are represented as classes, and must inherit from the `LogType`, `Rule` and `Transformer` base classes. A simple template is shown below:

```py
from plugin import LogType, Rule, Transformer

class MyLogType(LogType):

    class MyRule(Rule):
        def evaluate(self, line):
            # Return `True` to send the alert, or `False` to drop it.
            return True 

        class MyTransformer(Transformer):
            def transform(self, line):
                # Do something with line
                return line
```

The `evaluate` and `transform` functions shown above are entrypoint functions that are **required** for each rule or transformer to work.

#### Shared Functions

In some cases, you might want to "share" a function between multiple rules or transformers. This is simple to do with multi-level inheritance from a shared superclass:

```py
from plugin import LogType, Rule, Transformer

class MyCustomTransformer(Transformer):
    def my_shared_function(self, line):
        # Do something with line
        return line

class MyLogType(LogType):

    class MyRule(Rule):
        def evaluate(self, line):
            return True 

        class MyTransformer(MyCustomTransformer):
            def transform(self, line):
                # Can use methods of MyCustomTransformer
                self.my_shared_function(line)
                return line

    class MyOtherRule(Rule):
        def evaluate(self, line):
            return True 

        class MyOtherTransformer(MyCustomTransformer):
            def transform(self, line):
                # Can also use methods of MyCustomTransformer
                self.my_shared_function(line)
                return line
        
        class MyOtherTransformer2(Transformer):
            def transform(self, line):
                # Has no access to MyCustomTransformer
                return line
```



### Endpoints

Endpoints are represented by classes with a mandatory `send` function that acts as an entrypoint for sending the alert. They must inherit from the `Endpoint` superclass.

An example of an endpoint is shown below:

```py
from plugin import Endpoint
import requests

class Telegram(Endpoint):
    required_vars = ["chat_id", "token"]
    def send(self, msg):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {"chat_id": self.chat_id, "text": msg}
        response = requests.post(url, params=params,)
        if response.status_code == 200:
            print(f"{msg} -> {self}")
```

Unlike workflows, the entrypoint class can accept additional keyword arguments such as URLs, as long as they are specified in the configuration file (see [destinations](configuration-file.md#destinations)). At present, the program does **not** require these to be explicitly stated (e.g., `required_vars = ["chat_id", "token"]`), but it is recommended for clarity.

<hr>

Next: [Configuration file](configuration-file.md)
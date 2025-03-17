## Error Logging

- [Overview](#overview)
- [Error codes](#error-codes)
- [Fallback alerts and error reporting](#fallback-alerts-and-error-reporting)


### Overview

sendlog produces logs for significant events, including startup issues and runtime problems. As shown in the example below, logs use the **JSONL** format , primarily because it makes parsing simpler.

```json
[2025-03-17T16:20:31+0000] [PACMAN] Running 'pacman -Sy' -> <plugins.channels.telegram.Telegram object at 0x7bbff1798590>
{"asctime": "2025-03-17 16:20:32,836", "levelname": "ERROR", "code ": "RUNTIME.ENDPOINT_ERROR", "message": "An error occurred that prevented an alert from sending: Endpoint 'telegram_1' from Channel plugin subclass 'plugins.channels.telegram.Telegram' encountered the following error when processing the alert input '[2025-03-17T16:20:31+0000] [PACMAN] Running 'pacman -Sy'' from file '/var/log/pacman.log': 'ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))'", "data": {"endpoint_name": "telegram_1", "plugin_class_name": "plugins.channels.telegram.Telegram", "log_line": "[2025-03-17T16:20:31+0000] [PACMAN] Running 'pacman -Sy'", "workflow_trace_stack": ["plugins.logs.pacman.Pacman", "plugins.logs.pacman.Pacman.RunCommand", "plugins.logs.pacman.Pacman.RunCommand.Human", "plugins.channels.telegram.Telegram:telegram_1"], "file_path": "/var/log/pacman.log", "exc_info": "ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))"}}
```

In a prettier JSON format, the above log looks like this:

```json
{
  "timestamp": "2025-03-17T16:20:32+0000",
  "level": "ERROR",
  "code": "RUNTIME.ENDPOINT_ERROR",
  "message": "An error occurred that prevented an alert from sending: Endpoint 'telegram_1' from Channel plugin subclass 'plugins.channels.telegram.Telegram' encountered the following error when processing the alert input '[2025-03-17T16:20:31+0000] [PACMAN] Running 'pacman -Sy'' from file '/var/log/pacman.log': 'ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))'",
  "data": {
    "endpoint_name": "telegram_1",
    "plugin_class_name": "plugins.channels.telegram.Telegram",
    "log_line": "[2025-03-17T16:20:31+0000] [PACMAN] Running 'pacman -Sy'",
    "workflow_trace_stack": [
      "plugins.logs.pacman.Pacman",
      "plugins.logs.pacman.Pacman.RunCommand",
      "plugins.logs.pacman.Pacman.RunCommand.Human",
      "plugins.channels.telegram.Telegram:telegram_1"
    ],
    "file_path": "/var/log/pacman.log",
    "exc_info": "ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))"
  }
}
```

The `timestamp`, `level`, `code`, and `message` are static elements that appear in every log message. Anything under `data` will depend on the cause of the event, which can be identified using the `code`.

### Error codes

The table below provides an overview of log codes and their root cause.

| Code                                  | Cause                                                                                                                    |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `WORKFLOW.ENDPOINT_VARIABLE_MISMATCH` | Mismatch between a `Channel` plugin's required variables and the endpoint variables specified in the configuration file. |
| `WORKFLOW.PLUGIN_CLASS_NOT_FOUND`     | The plugin class referenced in the configuration file could not be found in the specified module.                        |
| `WORKFLOW.PLUGIN_MODULE_NOT_FOUND`    | The plugin module referenced in the configuration file could not be found in the specified module.                       |
| `WORKFLOW.PLUGIN_INHERITANCE`         | The plugin class did not inherit from the expected base class (`Logtype`, `Rule`, `Transformer`, or `Channel`).          |
| `WORKFLOW.ENDPOINT_UNDEFINED`         | The endpoint was referenced by a workflow but was not defined in the `endpoints` section of the configuration file.      |
| `CONFIG.KEY`                          | The expected YAML key could not be found in the configuration file.                                                      |
| `CONFIG.TYPE`                         | A value in the configuration file was an unexpected type.                                                                |
| `PLUGIN.OVERRIDE`                     | The plugin attempted to override a core method or attribute, which is not allowed.                                       |
| `PLUGIN.INIT_VALIDATION`              | The plugin's `__init__` method contained a parameter other than `self`, which is not allowed.                            |
| `RUNTIME.RULE_ERROR`                  | An error occurred in the `Rule` plugin while processing a log line.                                                      |
| `RUNTIME.TRANSFORMER_ERROR`           | An error occurred in the `Transformer` plugin while processing a log line.                                               |
| `RUNTIME.ENDPOINT_ERROR`              | An error occurred in the `Endpoint` plugin while processing an alert input.                                              |


### Fallback alerts and error reporting

sendlog can be used to monitor itself. The most useful application of this is detecting runtime errors and reporting them via a fallback alert.

For example, the runtime alert codes will always start with `RUNTIME.`, with `level` = `ERROR`. So, by configuring a Rule plugin to check for these conditions, you can automate fallback alerts from any origin.
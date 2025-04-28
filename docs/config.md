# Configuration File

- [Overview](#overview)
- [Endpoints](#endpoints)
  - [Fields](#fields)
  - [Structure](#structure)
  - [Example](#example)
- [Files](#files)
  - [Fields](#fields-1)
  - [Structure](#structure-1)
  - [Example](#example-1)

## Overview

The configuration file defines active alert workflows and endpoints. At the bare minimum, you must define one endpoint and one file workflow for an alert to function.

## Endpoints

Once instantiated, a Channel is called an endpoint. It represents the destination itself.

Before configuring a workflow, at least one endpoint is required. They can be defined in the `endpoints` section of the configuration file and re-used for different workflows.

### Fields

| Field             | Type   | Required | Description                                                              |
| ----------------- | ------ | -------- | ------------------------------------------------------------------------ |
| `<endpoint_name>` | string | Yes      | Arbitrary unique identifier for the destination.                         |
| `plugin`          | string | Yes      | Module for the endpoint plugin that will handle the alert.               |
| `channel`         | string | Yes      | Channel class within the specified plugin (e.g., `Console`, `Telegram`). |
| `vars`            | map    | No       | Dictionary of custom variables required by the specified Channel.        |

### Structure

```yaml
endpoints:
  <endpoint_name>:
    plugin: <plugin_name>
    channel: <channel_class>
    vars:
      <key>: <value>
```

### Example

```yaml
endpoints:
  telegram_1:
    plugin: telegram
    channel: Telegram
    vars:
      chat_id: <my_chat_id>
      token: <my_token>
```

## Files

The `files` section defines the alert workflows for each of the specified files. Defining a workflow requires at least one endpoint to be configured.

### Fields

| Field                 | Type   | Required | Description                                                   |
| --------------------- | ------ | -------- | ------------------------------------------------------------- |
| `<file_path>`         | string | Yes      | Path to the file that should be monitored.                    |
| `plugin`              | string | Yes      | Name of the module that will handle the alert.                |
| `log_type`            | string | Yes      | Name of the `LogType` subclass within the specified plugin.   |
| `rules`               | map    | Yes      | Dictionary of rules.                                          |
| `<rule_class>`        | string | Yes      | Name of the `Rule` subclass within the specified log type.    |
| `transformers`        | map    | Yes      | Dictionary of transformers.                                   |
| `<transformer_class>` | string | Yes      | Name of the `Transformer` subclass within the specified rule. |
| `endpoints`           | list   | Yes      | List of endpoints to send an alert to.                        |
| `<endpoint_name>`     | string | Yes      | The name of an endpoint specified in the `endpoints` block.   |

You can have multiple files, log types, rules, transformer and endpoints under each parent key.

### Structure

```yaml
files:
  /var/log/pacman.log:
    plugin: <plugin_module>
    log_type: Pacman
    rules:
      <rule_class>:
        transformers:
          <transformer_class>:
            endpoints:
              - <endpoint_name>
```

### Example

```yaml
files:
  /var/log/pacman.log:
    plugin: pacman
    log_type: Pacman
    rules:
      RunCommand:
        transformers:
          Human:
            endpoints:
              - telegram_1
          JSON:
            endpoints:
              - telegram_1
              - telegram_2
```
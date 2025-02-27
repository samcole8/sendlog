## Configuration File

[Back to Contents](..)

- [Overview](#overview)
- [Destinations](#destinations)
  - [Fields](#fields)
  - [Structure](#structure)
  - [Example](#example)
- [Files](#files)
  - [Fields](#fields-1)
  - [Structure](#structure-1)
  - [Example](#example-1)

### Overview

The configuration file defines active alert workflows and endpoint configurations (called destinations). At the bare minimum, you must define one destination and one file for an alert to function.

### Destinations

Before configuring a workflow, at least one destination is required. The `destinations` section defines a place an alert can go, and provides any information it needs to get there.

#### Fields

| Field                | Type   | Required | Description                                                               |
| -------------------- | ------ | -------- | ------------------------------------------------------------------------- |
| `<destination_name>` | string | Yes      | Arbitrary unique identifier for the destination.                          |
| `plugin`             | string | Yes      | Module for the endpoint plugin that will handle the alert.                |
| `endpoint`           | string | Yes      | Endpoint class within the specified plugin (e.g., `Console`, `Telegram`). |
| `vars`               | map    | No       | Dictionary of custom variables required by the specified Endpoint.        |

You can have multiple instances of the same endpoint, for example to send alerts to different accounts or locations.

#### Structure

```yaml
destinations:
  <destination_name>:
    plugin: <plugin_name>
    endpoint: <endpoint_type>
    vars:
      <key>: <value>
```

#### Example

```yaml
destinations:
  telegram_1:
    plugin: telegram
    endpoint: Telegram
    vars:
      chat_id: <my_chat_id>
      token: <my_token>
```

### Files

The `files` section defines the alert workflows for each of the specified files.

#### Fields

| Field                 | Type   | Required | Description                                                      |
| --------------------- | ------ | -------- | ---------------------------------------------------------------- |
| `<file_path>`         | string | Yes      | Path to the file that should be monitored.                       |
| `plugin`              | string | Yes      | Name of the module that will handle the alert.                   |
| `log_type`            | string | Yes      | Name of the `LogType` subclass within the specified plugin.      |
| `rules`               | map    | Yes      | Dictionary of rules.                                             |
| `<rule_class>`        | string | Yes      | Name of the `Rule` subclass within the specified log type.       |
| `transformers`        | map    | Yes      | Dictionary of transformers.                                      |
| `<transformer_class>` | string | Yes      | Name of the `Transformer` subclass within the specified rule.    |
| `destinations`        | list   | Yes      | List of destinations to send an alert to.                        |
| `<destination_name>`  | string | Yes      | The name of a destination specified in the `destinations` block. |

You can have multiple files, log types, rules, transformer and destinations under each respective parent key. Destinations can be re-used.

#### Structure

```yaml
files:
  /var/log/pacman.log:
    plugin: <plugin_module>
    log_type: Pacman
    rules:
      <rule_class>:
        transformers:
          <transformer_class>:
            destinations:
              - <destination_name>
```

#### Example

```yaml
files:
  /var/log/pacman.log:
    plugin: pacman
    log_type: Pacman
    rules:
      RunCommand:
        transformers:
          Human:
            destinations:
              - telegram_1
          JSON:
            destinations:
              - telegram_1
              - telegram_2
```
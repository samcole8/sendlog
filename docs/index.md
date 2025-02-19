
File-based alerts for Linux. 

## Plugins

This software exposes a programmatic interface for extensibly writing log alerts.

Alerts are written using a combination of **Types**, **Triggers**, **Formats**, and **Endpoints**.

### Types

Types represent a specific log format (such as `auth.log`), and must contain one or more Triggers.

### Triggers

Triggers "decide" whether an alert will fire, based on a log message. They must contain one or more formats.

### Formats

Formats convert a log message into a format suitable for one or more Endpoints.

### Endpoints

Endpoints represent the destination for the alert (SMS, email, e.t.c) and handle sending it.

## Configuration File

![Entity relationship diagram for Types, Triggers, Formats, and Endpoints](erd.drawio.png)

```yaml
files:
  /var/auth.log:
    plugin: myplugin
    rules:
      MyRule:
        transformations:
          MyTransformation:
            endpoints:
              - myendpoint
              - myendpoint2
    enabled: true
```
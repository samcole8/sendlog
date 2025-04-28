# Quick Start Guide

- [Installation](#installation)
- [Configuring alerts](#configuring-alerts)
- [Writing Plugins](#writing-plugins)
- [Starting the service](#starting-the-service)


## Installation

This quick start installation guide is designed for Linux distributions running systemd.

1. Clone the repository. You can put it anywhere you want—`/opt` is recommended. Example:
   
   ```sh
   sudo git clone https://github.com/samcole8/sendlog.git /opt/sendlog
   ```

2. Configure a virtual environment and install Python dependencies

   ```sh
   python3 -m venv /opt/sendlog/venv
   source /opt/sendlog/venv/bin/activate
   pip install -r /opt/sendlog/requirements.txt
   ```

3. Copy the systemd service script into your systemd service directory, e.g.:
   ```sh
   sudo cp /opt/sendlog/pkg/sendlog.service /etc/systemd/system/sendlog.service
   ```

## Configuring alerts

Configuration examples are available in `examples/`. For more information on configuring sendlog, see the [Configuration File](config.md) documentation.

## Writing Plugins

You can write plugins to integrate sendlog with custom log structures or endpoints. For more information on writing plugins, see the [Plugin DSL](plugin-dsl.md) documentation.

## Starting the service

1. Start/enable the service:

   ```sh
   sudo systemctl enable --now sendlog
   ```

2. Check if the system is operational:

   ```sh
   sudo systemctl status sendlog
   ```

3. If the configuration file changes, restart the service:

   ```sh
   sudo systemctl restart sendlog
   ```
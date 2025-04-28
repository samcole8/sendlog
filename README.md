# sendlog

[![Release](https://img.shields.io/github/v/release/samcole8/sendlog)](https://github.com/samcole8/sendlog/releases/latest)
![Last Commit](https://img.shields.io/github/last-commit/samcole8/sendlog)
![Repo Size](https://img.shields.io/github/repo-size/samcole8/sendlog)

sendlog is a lightweight, extensible log monitoring framework with rule-based alerting. View the full documentation at [sendlog.samcole.net](https://sendlog.samcole.net/).

*NOTE: Sendlog is in alpha. In its current state, it may be unstable and is subject to significant changes in future releases.*

## Quick Start Guide

### Installation

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

### Configuring alerts

Configuration examples are available in `examples/`. For more information on configuring sendlog, see the [Configuration File](https://sendlog.samcole.net/config) documentation.

## Writing Plugins

You can write plugins to integrate sendlog with custom log structures or endpoints. For more information on writing plugins, see the [Plugin DSL](https://sendlog.samcole.net/plugin-dsl) documentation.

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
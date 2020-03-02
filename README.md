## Description

Simple [Wialon IPs](https://gurtam.com/ru/gps-hardware/soft/wialon-ips) protocol emulator.
Allows you to send Wialon IPs messages (with TCP or UDP) to any available network endpoint that accepts Wialon IPs protocol.

After installing this package, `wialon_ips` console script becomes available in OS-specific user directory.
Run this script to repeatedly send Wialon IPs messages to configurable endpoint with any interval.

This tool supposed to provide facility for quick debugging and not intended to be advanced Wialon IPs emulation tool.
As soon as this tool just for debugging purposes, it is fully interactive, and does not support passing configuration as arguments.
All settings related to communication interactively asked when script runs.

## Presets

You can choose to persist communication configuration for future uses: just save current configuration as preset when you will be prompted. All saved presets stored in to `json`-file `wialon_ips_presets.conf` living in OS-specific user directory (`/home/$USER/.local/share/wialon_ips/wialon_ips_presets.conf` for Ubuntu Linux). It's not recommended to edit this file manually, but also not forbidden(format is quite intuitive) :)
To drop all your presets:

```bash
wialon_ips clear
```

## OS compatibility notes

It tested and works well under Ubuntu 18.04.
It wasn't tested under Windows or other Linux distributions, but unlikely any problems expected there: project structure follows recommendations from [official Python documentation about project packaging and distribution](https://packaging.python.org/tutorials/packaging-projects/), and no platform-specific feautures used. Let me know if you will have issues.

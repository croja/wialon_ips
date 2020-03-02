#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wialon_ips",
    version="0.0.1",
    author="Sergey Shevchik",
    author_email="sergey.shevchik@gmail.com",
    description="Simple Wialon IPs protocol emulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/croja/wialon_ips",
    py_modules=["wialon_ips"],
    python_requires=">=3.6",
    install_requires=['requests', 'PyInquirer', 'appdirs'],
    entry_points={
        "console_scripts": [
            "wialon_ips = wialon_ips"
        ]
    }
)
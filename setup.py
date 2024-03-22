from setuptools import setup, find_packages


setup(
    name="modbusreader",
    version="1.0",
    packages=find_packages(),
    python_requires='>=3.9, <4',
    include_package_data=True,
    setup_requires=['wheel'],
    install_requires=[
        "paho.mqtt",
        "minimalmodbus"
    ]
)

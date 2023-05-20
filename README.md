# Impose CLI

Impose CLI is a simple tool used to generate a CLI tool by using one decorator - @impose.

### How to use
Functions that are meant to be CLI commands should be decorator with @impose
In the main method, the impose_cli(execute=True, target=[COMMAND_DIRECTORY])() method should be called.

If target is None, then the commands will be from the same file. Otherwise, include the directory for your commands.

### How to download
pip install impose-cli

# Impose CLI

Impose CLI is a simple tool used to generate a CLI tool by using one decorator.

### How to use
Functions that are meant to be CLI commands should be decorator with @impose
In the main method, the impose_cli(target=None)() method should be called.

If target is None, then the commands will be from the same file. Otherwise, include the directory for your commands.
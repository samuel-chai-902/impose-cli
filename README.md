# Impose CLI
https://github.com/samuel-chai-902/impose-cli

Impose CLI is a simple tool used to generate a CLI tool by using one decorator.

### How to use
Every function that should be recognized as a commmand can be marked with the @impose decorator. Parameters of 
the function without default values become arguments, while those with default values become options. 

The impose_cli function should be run in the main method of the entrypoint of the project. The impose_cli
function accepts two parameteres: execute, and target. 

If execute is set to true, then impose_cli is a void
function which generates the CLI output. If execute is set to false, then impose_cli returns a click group. 
This could be useful if you want to dynamically edit the functions you have decorated without changing the source
of the impose-cli package.

Target takes a directory as an argument. If target is None, then the only functions scanned are those 
in the same module as the main method is being called. However, if a directory is passed, all of the functions
decorated with @impose in the directory are read into the CLI, and each module that they are found in becomes 
a separate command group.
    
### How to download
pip install impose-cli


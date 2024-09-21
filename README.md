## mycogs

mycogs is collection of redbot plugins I written for our discord server (***our****cogs? *Communist-Bugs-Bunny.png*)

## development process
I use `build.py` script from reloading cogs. My nvim is set to execute build.* scripts from directory of current project. In every project I simply put new `build.py` and change the cogname. Project directory is linked to redbot cogs path. In my right terminal pane, I run redbot with `--rpc` flag, so after pressing reload hotkey, I immediately see all the tracebacks if there are any.

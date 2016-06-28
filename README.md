# znc-pypush
Python Pushover User Plugin for the ZNC IRC Bouncer

## Requirements
ZNC with Python3 support (builtin or modpython loaded)

## Installation
Copy or symlink pypush.py into the modules directory.

## Setup
Load the module and setup the Pushover settings.
```
/msg *status loadmod pypush
/msg *pypush setuser <pushover user key>
/msg *pypush settoken <pushover api token>
```
This will now send Pushover mesages when your nick is mentioned in channel or you are private messaged.
## Other
Add other words in channel to highlight on
```
/msg *pypush sethighlight foo bar
```
Show some debug info
```
/msg *pypush debug
```

IRC Bot
=======
A simple IRC Bot written in Python

Commands
========
* `!search <nick>` - tells \<nick\> to use a search engine (see Config: search)
* `!wiki <search term>` - replies a wikipedia link for \<search term\>
* `!quit` - disconects the bot only if the command is given by the owner(see Config: owner)
* `!answer` or `!42` - you'll find the answer through these commands

Adding commands
===============
1. In `config.py` you must add the name of the command to the `cmds_list`'s
   end(without _!_)
2. In directory `cmds/` you must create a file named after your command
3. Into the newly created file you must define a function named after your
   command that takes one parameter, this
   parameter will contain the command sent by the user, the function must return
   the message to be sent on the channel

E.g:
You want to create a command `!dance` so you follow these steps:
1. Add 'dance' to the `cmds_list` in `config.py`
2. Create `cmds/dance.py`
3. In `cmds/dance.py` define `def dance(param):`, `param` will hold the users
   command in case you must do some checkings or whatever, it must return a
   message for example `return config.privmsg + 'Dance time!\r\n'`

Config
======
* `search` - specifies the reply link for `!search <nick>`
* `owner` - the user(s) who are allowed to `!quit` the bot(_list_ data type)
* `log` - path to the logging directory, all logs are stored here
* `quit_msg` - message to quit with, e.g. PPyBot has left #botwar ("Bye bye")
* `server` - server to connect to(default: chat.freenode.net)
* `port` - port number to use(default: 6667)
* `channel` - channel to connect to
* `nick` - bot's name
* `realName` - bot's "real name"

License
=======

(C) Copyright 2011 PauLLiK

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

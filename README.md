IRC Bot
=======
A simple IRC Bot written in Python
To start it just `cd` to the `src` directory and type `./ircbot.py`, although
before using the bot it's recommended to check the config first.

Commands
========
* `!search <nick>` - tells \<nick\> to use a search engine (see Config: search)
* `!wiki <search term>` - replies a wikipedia link for \<search term\> along
  with the first paragraph from the page
* `!quit` - disconects the bot only if the command is given by the owner(see Config: owner)
* `!answer` - you'll find the answer through this command
* `!weather Sibiu` or `!weather Sibiu, Romania`

Adding commands
===============
1. In `src/config.py` you must add the name of the command to the `cmds_list`'s
   end(without _!_)
2. In directory `src/cmds/` you must create a file named after your command
3. Into the newly created file you must define a function named after your
   command that takes one parameter, this
   parameter will contain the command sent by the user, the function must return
   the message to be sent on the channel

E.g:

You want to create a command `!dance` so you follow these steps:

1. Add 'dance' to the `cmds_list` in `src/config.py`
2. Create `src/cmds/dance.py`
3. In `src/cmds/dance.py` define `def dance(param):`, `param` will hold the users
   command in case you must do some checkings or whatever, it must return a
   message for example `return config.privmsg + 'Dance time!\r\n'`

Config
======
See `src/config.py`:
* `search` - specifies the reply link for `!search <nick>`
* `owner` - the user(s) who are allowed to `!quit` the bot(_list_ data type)
* `log` - path to the logging directory, all logs are stored here
* `quit_msg` - message to quit with, e.g. PPyBot has left #botwar ("Bye bye")
* `server` - server to connect to(default: chat.freenode.net)
* `port` - port number to use(default: 6667)
* `channel` - channel to connect to
* `nick` - bot's name
* `realName` - bot's "real name"

Dependencies
============
* `!weather` and `!wiki` module depends on
  [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/ "BeautifulSoup")

License
=======

(C) Copyright 2011 PauLLiK

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

IRC Bot
=======
A simple IRC Bot written in Python
To start it just `cd` to the `src` directory and type `./ircbot.py`, although
before using the bot it's recommended to check the config first.

The bot can handle multiple channels at a time, also if you want to have a 
_private_ discussion it can be queried (`/query PPyBot`).

IRC Protocol reference: [RFC 1459](http://www.irchelp.org/irchelp/rfc/rfc.html
"IRC Protocol")

Documentation
=============
Sphinx docs to come

Commands
========
* `!google <search term>`
    * returns a link and a short description of the first Google search result
    * see Dependencies: _!google_
* `!wiki <search term>`
    * replies a wikipedia link for \<search term\> along with the first 
    paragraph from the page
* `!quit [#channel ]+`
    * disconnects the bot from the given list of channels
    * if no arguments are given, all connected channels are disconnected
    * if some arguments are provided the bot checks the channel names and 
    disconnects only the valid ones
    * if no channel is "alive" then the bot closes
    * Example: `!quit #foo #bar` - quits from #foo and #bar
    * see Config: _owner_, _channels_
* `!join <#channel >+`
    * the bot joins the given channels, minimum one channel name must be supplied
    * see Config: _owner_
* `!channels`
    * replies a list containing the channels the bot is connected to
    * see Config: _owner_
* `!help`
    * list all available commands
* `!answer`
    * you'll find the answer through this command
* `!weather <city>` or `!weather <city>, <state or country>`
    * replies some info related to the current weather conditions from the
      given location
* `!about`
    * a few words about this software
* `!mball`
    * the famous Magic Ball
* `!uptime`
    * shows current uptime of the bot
* `!so <search term>`
    * replies the first question's title and URL from the search result
    * see Dependencies: _!so_
* `!twitter [username]`
    * replies the latest tweet(along with the tweet date) for the username provided
    * the date will have the following format: DD/MM/YYYY HH:MM
    * if no username is provided then the bot will try to get the latest tweet
      for the IRC-user who issued the command

Total: _13_ commands

Auto-commands
=============
* `email_alert` - the bot sends an email to the owner when somebody talks to him

Total: _1_ auto-command

Adding commands
===============
1. In `src/config.py` you must add the name of the command to the `cmds_list`'s
   end(without _!_)
2. In `src/cmds/` directory you must create a file named after your command
3. Into the newly created file you must define a function named after your
   command that takes one parameter, this parameter will contain the command
   components sent by the user, the function must return either a 
   message(string) to be sent on the channel, either a list, first item being a
   command(other than PRIVMSG which is added automatically if needed) and the 
   second being the command's arguments.

E.g.:

If you want to create a command `!ncmd`, you must follow these steps:

1. Add 'ncmd' to the `cmds_list` in `src/config.py`
2. Create `src/cmds/ncmd.py`
3. In `src/cmds/ncmd.py` define `def dance(param):`, `param` will hold the users
   command components(see `src/parser.py`) in case you must do some checkings, 
   it must return a message(eg. `return 'Dance time!'`, in this
   case `src/ircbot.py` will automatically add `PRIVMSG` at the beginning and 
   `\r\n` at the end) or a list(eg. `return ['JOIN ', '#chan1,#chan2']`, in this
   case the list will be joined and `\r\n` added at the end)

If you want to create a command that the bot should execute if something happens
on the chat (not if the command is manually triggered) you should add the
command name to the `auto_cmds_list` insead of `cmds_list`.

Config
======
See `src/config.py`:

* `owner` - the users who are allowed to send a specific command to the bot
(for example the `!quit` command)
* `log` - path to the logging directory, all logs are stored here
* `server` - server to connect to (default: chat.freenode.net)
* `port` - port number to use (default: 6667)
* `channels` - a list of channels to connect to
* `nicks` - a list of strings, the bot's name will be the first unused nick from
  this list or the first nick in the list and a random sequence appended if all
  nicks are used
* `real_name` - bot's "real name"
* `cmds_list` - a list of strings that the bot knows to answer to
* `auto_cmds_list` - a list of commands defined as regular commands with the
  only difference that they cannot be invoked by users, the bot executes them as
  result of an event

Dependencies
============
* `!weather`, `!twitter` and `!wiki` module depends on
  [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/ "BeautifulSoup")
    * `!weather` and `!twitter` depends on _BeautifulStoneSoup_ (XML)
    * `!wiki` depends on _BeautifulSoup_ (HTML)
* `!google` module depends on 
[Google Custom Search API](http://code.google.com/p/google-api-python-client/ "Custom Search API")
    * before using the bot please see the 
[installation page](http://code.google.com/p/google-api-python-client/wiki/Installation "Custom Search API Installation")
* `!so` module depends on 
[StackExchange API](http://stackapps.com/questions/198/py-stackexchange-an-api-wrapper-for-python "Py-StackExchange")

License
=======

(C) Copyright 2011-2013 Barbu Paul - Gheorghe

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 
this program. If not, see http://www.gnu.org/licenses/.

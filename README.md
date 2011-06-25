IRC Bot
=======
A simple IRC Bot written in Python

Commands
========
* `!search <nick>` - tells \<nick\> to search (see Config: search)
* `!wiki <search term>` - replies a wikipedia link for \<search term\>
* `!quit` - disconects the bot only if the command is given by the owner(see Config: owner)

Config
======
* `search` - specifies the reply link for `!search <nick>`
* `owner` - the user(s) who are allowed to `!quit` the bot(_list_ data type)

License
=======

(C) Copyright 2011 PauLLiK

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

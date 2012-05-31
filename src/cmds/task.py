from functions import is_registered
import config
import sqlite3

#TODO: properly close the conn

#TODO: construct this path
#TODO: if necessarily create the db file
database_filename = 'task.db' #this should be in the src dir

def task(socket, components):
    response = ''
    registered = is_registered(socket, components['sender'])

    if components['sender'] in config.owner and registered:
        try:
            params = components['arguments'].split('!task ')[1]
        except IndexError:
            return 'Please specify a valid action: list, add, del'

        action_delimiter_position = params.find(' ')

        if -1 != action_delimiter_position:
            action = params[:action_delimiter_position]
        else:
            action = params

        if not is_valid_sqlite3(database_filename):
            return 'Invalid database!'

        conn = sqlite3.connect(database_filename)
        db = conn.cursor()

        is_user = user_exists(db, components['sender'])

        if is_user is None:
            return 'Error fetching the database!'

        if 'list' == action:
            if not is_user:
                return 'Could not retrieve any task list!'

            l = list_task(db, components['sender'])

            if not l:
                response = 'Could not retrieve any task list!'
            else:
                response = []
                for t in l:
                    response.append('PRIVMSG {0} :Task {1}: {2}\r\n'.format(
                        components['action_args'][0], t[0], t[1]))
        elif 'add' == action:
            if not is_user and not create_user(db, components['sender']):
                    return 'Error registering the user!'

            try:
                t = params.split(action)[1]
            except IndexError:
                return 'Please provide a task!'

            t = t.strip()

            if not t:
                return 'Please provide a task!'

            id = add_task(db, components['sender'], t)

            if id is False:
                return 'Error adding the task!'

            try:
                conn.commit()
            except sqlite3.Error:
                return 'Error adding the task!'

            response = 'Task with id {0} added!'.format(id)
        elif 'del' == action:
            if not is_user:
                return 'No tasks available!'

            try:
                id = params.split(action)[1]
            except IndexError:
                return 'Please provide a task id!'

            id = id.strip()

            if not id:
                return 'Please provide a task id!'

            no_deleted = del_task(db, components['sender'], id)

            if no_deleted is False:
                return 'An error occurred while deleting'

            try:
                conn.commit()
            except sqlite3.Error:
                return 'Error deleting the task!'

            if no_deleted == 1:
                response = 'Task with id {0} was deleted!'.format(id)
            else:
                response = 'No task with id {0} was found!'.format(id)
        else:
            response = 'Please specify a valid action: list, add, del'

        conn.close()
    else:
        response = 'This command can be run only by the owners!'

    return response

def user_exists(db, nick):
    cmd = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"

    try:
        rv = db.execute(cmd, (nick,))
    except sqlite3.Error:
        return None

    if not rv.fetchone():
        return False

    return True

def create_user(db, nick):
    cmd = 'CREATE TABLE `{0}`(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, task TEXT)'

    try:
        db.execute(cmd.format(nick))
    except sqlite3.Error:
        return False

    return True

def add_task(db, nick, t):
    cmd = 'INSERT INTO `{0}`(task) VALUES(?)'

    try:
        db.execute(cmd.format(nick), (t,))
        return db.execute('SELECT LAST_INSERT_ROWID();').fetchone()[0]
    except sqlite3.Error:
        return False


def list_task(db, nick):
    cmd = 'SELECT * FROM `{0}`'

    try:
        rv = db.execute(cmd.format(nick))
    except sqlite3.Error:
        return False

    return rv.fetchall()

def del_task(db, nick, id):
    cmd = 'DELETE FROM `{0}` WHERE id=?'

    try:
        return db.execute(cmd.format(nick), (id,)).rowcount
    except sqlite3.Error:
        return False

def is_valid_sqlite3(db):
    '''Validates the SQLite3 database file by checking the first bytes
    Check: 1.2.1 Magic Header String of http://www.sqlite.org/fileformat.html
    Note that I'm discarding the last byte, namely: '\0'
    '''

    with open(db, 'r') as f:
        if f.read(15) == 'SQLite format 3':
            return True

        return False

    return False

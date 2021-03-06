from course_reserves import opt
import os
import hashlib
import psycopg2
import database

class User():
    """
    A class necessary for Flask-Login to function. It holds methods
    to log users in from LDAP and add them to a database of users.
    """

    allowed_users = {
        'reserve': '5f4dcc3b5aa765d61d8327deb882cf99'
    }
    
    def __init__(self, username, session_id=None):
        "Returns a User object for Flask-Login"
        if not session_id:
            self.id = os.urandom(24).encode('hex')
        else:
            self.id = session_id
        self.username = username

    @staticmethod
    def try_login(username, password):
        "Tries to log into Laurentian's LDAP servers with the provided info."
        if username in User.allowed_users:
            if hashlib.md5(password).hexdigest() == User.allowed_users[username]:
                u = User(username, os.urandom(24).encode('hex'))
                u.add_to_db()
                return u
        return None
        
    @staticmethod
    def get_by_id(id):
        "Returns a logged-in user with the given id."
        dbh = database.get_db()
        cur = dbh.cursor()
        try:
            cur.execute("SELECT * FROM get_users WHERE id = '%s'" % id)
            return User(cur.fetchone()[1], id)
        except Exception, ex:
            if opt['VERBOSE']:
                print('Couldn\'t query database, or user is expired:')
                print(ex)
        dbh.close()
        return None

    def add_to_db(self):
        "Adds a user to the database."
        dbh = database.get_db()
        cur = dbh.cursor()
        try:
            cur.execute("INSERT INTO users VALUES (%s, %s)",
                (self.id, self.username))
        except Exception, ex:
            print('Could\'t add user to database:')
            print('ex')
        dbh.commit()
        dbh.close()

    def is_authenticated(self):
        """
        Returns the authentication status of a user.
        Because this user always requires a password, this is always true.
        Needed by Flask-Login.
        """
        return True

    def is_active(self):
        "Like above - this is needed by Flask-Login."
        return True

    def is_anonymous(self):
        "Needed by Flask-Login."
        return False

    def get_id(self):
        "Returns the user's UID."
        return self.id

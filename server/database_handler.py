import sqlite3


class DatabaseHandler(object):
    """docstring for DatabaseHandler."""
    def __init__(self, db_name='person'):
        super(DatabaseHandler, self).__init__()
        self.db_name = db_name
        self.conn = sqlite3.connect('{}.db'.format(self.db_name))
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lastname TEXT,
                firstname TEXT,
                middlename TEXT,
                birth_date TEXT
            )""".format(self.db_name))

    def drop_table(self):
        self.cursor.execute('DROP TABLE IF EXISTS persons')

    def add_person(self, person_info):
        self.cursor.execute("""
            INSERT INTO person (lastname, firstname, middlename, birth_date)
            VALUES (?, ?, ?, ?)
        """, person_info)

    def generate_records(self):
        self.cursor.execute('SELECT * FROM person')
        return self.cursor.fetchall()

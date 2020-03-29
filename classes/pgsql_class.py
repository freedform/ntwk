import psycopg2
from ntwk_conf import db_host, db_name, user_name, user_pass

class DatabaseClass:
    def __init__(self):
        try:
            self.connect = psycopg2.connect(dbname=db_name,
                                            user=user_name,
                                            password=user_pass,
                                            host=db_host)
            self.cursor = self.connect.cursor()
        except Exception as error:
            print("Error while connecting to PostgreSQL", error)
        else:
            pass

    def select(self, query):
        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            return records
        except Exception as error:
            print("Error while executing SELECT to PostgreSQL", error)

    def insert(self, query):
        try:
            self.cursor.execute(query)
        except Exception as error:
            print("Error while executing INSERT to PostgreSQL:", error)
        self.connect.commit()

    def update(self, query):
        try:
            self.cursor.execute(query)
            self.connect.commit()
        except Exception as error:
            print("Error while executing UPDATE to PostgreSQL", error)


    def raw_query(self, query):
        try:
            self.cursor.execute(query)
        except Exception as error:
            print("Error while executing QUERY to PostgreSQL", error)
        self.connect.commit()

    def connect_close(self):
        if self.connect:
            self.cursor.close()
            self.connect.close()
        else:
            print('Connection is already CLOSED')

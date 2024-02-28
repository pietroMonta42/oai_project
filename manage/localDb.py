import mysql.connector


class LocalDB:
    def __init__(self):
        self.conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="oai_conversations"
        )

    def get_conn(self):
        return self.conn
    
    def get_assistants(self, max = 100):
        query = f"SELECT * FROM assistants LIMIT {max}"
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()
    
    def new_assistant(self, id, name, model, image):
        query = f"INSERT INTO assistants (id, name, model, image) VALUES ('{id}', '{name}', '{model}', '{image}')"
        cursor = self.conn.cursor()
        print(query)
        cursor.execute(query)
        self.conn.commit()
        return cursor.rowcount
    
    def get_assistant(self, id):
        query = f"SELECT * FROM assistants WHERE id = '{id}'"
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()
    
    def put_assistant(self, id, name=None, model=None, image=None):
        query = f"UPDATE assistants SET "
        if name:
            query = query + f"name = '{name}', "
        if model:
            query = query + f", model = '{model}', "
        if image:
            query = query + f", image = '{image}', "
        query = query[:-2]
        query = query + f" WHERE id = '{id}'"
        cursor = self.conn.cursor()
        cursor.execute(query)
    
    def get_threads(self, max = 50):
        query = f"SELECT * FROM threads LIMIT {max}"
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()
        
    def new_thread(self, id, assistant_id, title):
        query = f"INSERT INTO threads (id, assistant_id, title) VALUES ({id}, {assistant_id}, {title})"
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        return cursor.rowcount
    
    def get_thread(self, id):
        print("log :" + id)
        query = f"SELECT * FROM threads WHERE id = '{id}'"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        print("log :", result)
        return result
    
    def put_thread(self, id, assistant_id, title=None):
        query = f"UPDATE threads SET assistant_id = '{assistant_id}'"
        if title:
            query = query + f", title = '{title}' "
        query = query + f" WHERE id = '{id}'"
        cursor = self.conn.cursor()
        cursor.execute(query)
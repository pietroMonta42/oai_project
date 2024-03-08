import sqlite3


class LocalDB:
    def __init__(self):
        self.conn = sqlite3.connect('oai_data.db')

    def get_conn(self):
        return self.conn
    
    def get_assistants(self, max = 100):
        query = f"SELECT * FROM assistants LIMIT {max}"
        self.conn.row_factory = self.dict_factory
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    def new_assistant(self, id, name, model, image):
        query = "INSERT INTO assistants (id, name, model, image) VALUES ( ?, ?, ?, ?);"
        cursor = self.conn.cursor()
        cursor.execute(query, (id, name, model, image))
        self.conn.commit()
        return cursor.rowcount
    
    def get_assistant(self, id):
        query = f"SELECT * FROM assistants WHERE id = ? ;"
        cursor = self.conn.cursor()
        cursor.execute(query, (id,))
        return cursor.fetchone()
    
    def put_assistant(self, id, name=None, model=None, image=None):
        query = "UPDATE assistants SET "
        param = []
        if name:
            query = query + "name = ?, "
            param.append(name)
        if model:
            query = query + f", model = ?, "
            param.append(model)
        if image:
            query = query + f", image = ?, "
            param.append(image)
        query = query[:-2]
        query = query + " WHERE id = ? ;"
        param = tuple(param)
        cursor = self.conn.cursor()
        cursor.execute(query, param)
    
    def get_threads(self, max = 50):
        query = f"SELECT * FROM threads LIMIT {max};"
        self.conn.row_factory = self.dict_factory
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
        
    def new_thread(self, id, assistant_id, title):
        query = "INSERT INTO threads (id, assistant_id, title) VALUES (?, ?, ?);"
        print("log :", query)
        cursor = self.conn.cursor()
        cursor.execute(query, (id, assistant_id, title))
        self.conn.commit()
        return cursor.rowcount
    
    def get_thread(self, id):
        query = f"SELECT * FROM threads WHERE id = ? ;"
        cursor = self.conn.cursor()
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        return result
    
    def put_thread(self, id, assistant_id, title=None):
        query = f"UPDATE SET assistant_id = ? "
        param = []
        param.append(assistant_id)
        if title:
            query = query + f", title = ? "
            param.append(title)
        query = query + f" WHERE id = ? ;"
        param.append(id)
        param = tuple(param)
        cursor = self.conn.cursor()
        cursor.execute(query, param)
        
    def dict_factory(self,cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
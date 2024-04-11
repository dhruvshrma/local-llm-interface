import sqlite3

def create_sqlite_db_from_schema(db_file, schema_file):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        with open(schema_file, 'r') as f:
            schema = f.read()
        
        cursor.executescript(schema)
        
        conn.commit()
        print(f"SQLite database created from schema: {db_file}")
    except sqlite3.Error as e:
        print(f"Error creating SQLite database: {e}")
    finally:
        if conn:
            conn.close()
            
if __name__ == "__main__":
    db_file = 'conversations.db'
    schema_file = 'schema.sql'
    create_sqlite_db_from_schema(db_file, schema_file)
    
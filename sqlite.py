import sqlite3
import os

def get_data_dir():
        return str(os.path.join(os.getenv("TEMP"), "VeterinaryAssistant","data"))
    
class SQLiteManager:
    DB_PATH = os.path.join(get_data_dir(), "cattle_data.db")
    TABLE_NAME = "animal_data"
    def __init__(self):
        os.makedirs(get_data_dir(), exist_ok=True)
        self.conn = sqlite3.connect(self.DB_PATH,check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            mouth_disease_count INTEGER DEFAULT 0,
            lumpy_skin_count INTEGER DEFAULT 0,
            BCS INTEGER DEFAULT 0
        )
        """)
        self.conn.commit()

    def insert_document(self, document: dict):
        try:
            date = document.get("date")
            mouth_disease_count = document.get("mouth_disease_count", 0)
            lumpy_skin_count = document.get("lumpy_skin_count", 0)
            bcs_score = document.get("BCS", 0)

            # Check if the record for this date already exists
            self.cursor.execute(f"""
                SELECT mouth_disease_count, lumpy_skin_count, BCS
                FROM {self.TABLE_NAME}
                WHERE date = ?
            """, (date,))
            existing = self.cursor.fetchone()

            if existing:
                new_mouth = existing[0] + mouth_disease_count
                new_lumpy = existing[1] + lumpy_skin_count
                new_bcs = existing[2] + bcs_score

                self.cursor.execute(f"""
                    UPDATE {self.TABLE_NAME}
                    SET mouth_disease_count = ?,
                        lumpy_skin_count = ?,
                        BCS = ?
                    WHERE date = ?
                """, (new_mouth, new_lumpy, new_bcs, date))
                print("Document updated successfully")
            else:
                self.cursor.execute(f"""
                    INSERT INTO {self.TABLE_NAME} (date, mouth_disease_count, lumpy_skin_count, BCS)
                    VALUES (?, ?, ?, ?)
                """, (date, mouth_disease_count, lumpy_skin_count, bcs_score))
                print("Document inserted successfully")

            self.conn.commit()

        except Exception as e:
            print("Failed to insert/update document:", e)

    def close(self):
        self.conn.close()

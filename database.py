import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FILE = "passwords.db"

class DatabaseManager:
    def __init__(self):
        self.conn = None

    def init_db(self):
        """Создание таблицы при первом запуске"""
        try:
            self.conn = sqlite3.connect(DB_FILE)
            self.conn.row_factory = sqlite3.Row  # Доступ по имени колонки
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    length INTEGER,
                    use_upper INTEGER,
                    use_digits INTEGER,
                    use_symbols INTEGER,
                    password TEXT NOT NULL,
                    image_path TEXT
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка БД: {e}")

    def get_all(self):
        """Получение всех записей"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM passwords ORDER BY title")
        return cursor.fetchall()

    def insert_record(self, data):
        """Добавление записи (защита от SQL-инъекций через '?')"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO passwords (title, length, use_upper, use_digits, use_symbols, password, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['title'], data['length'], data['use_upper'], 
              data['use_digits'], data['use_symbols'], data['password'], data['image_path']))
        self.conn.commit()

    def update_record(self, data):
        """Обновление записи"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE passwords SET title=?, length=?, use_upper=?, use_digits=?, use_symbols=?, password=?, image_path=?
            WHERE id=?
        """, (data['title'], data['length'], data['use_upper'], 
              data['use_digits'], data['use_symbols'], data['password'], data['image_path'], data['id']))
        self.conn.commit()

    def delete_record(self, item_id):
        """Удаление записи"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM passwords WHERE id=?", (item_id,))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
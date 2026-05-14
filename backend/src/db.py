import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnector:
    def __init__(self):
        self.host = os.environ.get("DB_HOST", "localhost")
        self.user = os.environ.get("DB_USER", "root")
        self.password = os.environ.get("DB_PASSWORD", "Pardo2002")
        self.database = os.environ.get("DB_NAME", "mec_db")
        self.port = int(os.environ.get("DB_PORT", 3306))

    def get_connection(self):
        """Crea una conexión nueva a la base de datos"""
        try:
            return pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.MySQLError as e:
            print(f"❌ Error de conexión: {e}")
            return None

    def test_connection(self):
        """Prueba si la base de datos responde"""
        connection = self.get_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute('SELECT "Conexión exitosa" as mensaje')
                    result = cursor.fetchone()
                    print(f"✅ Base de Datos conectada: {result['mensaje']}")
            finally:
                connection.close()
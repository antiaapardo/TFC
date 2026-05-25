import json
import threading
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

sql_db_host = os.getenv("DB_HOST", "localhost")
sql_db_user = os.getenv("DB_USER", "root")
sql_db_password = os.getenv("DB_PASSWORD", "")
sql_db_name = os.getenv("DB_NAME", "mec_db")
sql_db_port = 3306 

# ==========================================
# GESTIÓN DEL PATRÓN SINGLETON
# ==========================================
_sql_instance = None
_init_lock = threading.Lock()

def get_sql():
    """
    Implementa el patrón Singleton de forma segura (Thread-safe).
    Garantiza que solo exista una instancia de conexión a la base de datos en toda la aplicación.
    """
    global _sql_instance
    if _sql_instance is None:
        with _init_lock:
            if _sql_instance is None:
                _sql_instance = MariaDB()
    return _sql_instance

class _SQLProxy:
    """Proxy para acceder a la instancia única de SQL de forma transparente."""
    def __getattr__(self, item):
        return getattr(get_sql(), item)

sql = _SQLProxy()

# ==========================================
# CLASES DE BASE DE DATOS
# ==========================================

class TransactionResult:
    """
    Clase contenedora que encapsula el resultado de cualquier operación en la base de datos.
    Sigue el estándar del Manual de Arquitectura para el manejo de errores.
    """
    def __init__(self, success, data=None, message=None, status=None, code=None):
        self.success = success
        self.data = data
        self.message = message
        self.status = status
        self.code = code 


class MariaDB:
    """
    Clase principal para la interacción con la base de datos MariaDB/MySQL.
    Maneja las conexiones, transacciones (commit/rollback) y el parseo de resultados.
    """
    def __init__(self):
        pass

    def _get_connection(self):
        """
        Abre y devuelve una nueva conexión a la base de datos usando PyMySQL.
        """
        try:
            return pymysql.connect(
                host=sql_db_host,
                port=sql_db_port,
                user=sql_db_user,
                password=sql_db_password,
                database=sql_db_name
            )
        except Exception as e:
            raise pymysql.OperationalError(f"Database connection failed: {e}")

    def find(self, query, multiple, parameters=None):
        """
        Ejecuta consultas de lectura (SELECT) en la base de datos.

        Parámetros:
            query (str): La consulta SQL a ejecutar.
            multiple (bool): True si se espera una lista de resultados, False para un solo registro.
            parameters (tuple, opcional): Variables a inyectar en la consulta de forma segura.

        Retorna:
            TransactionResult: Objeto con el resultado de la búsqueda o el error capturado.
        """
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(query, parameters)
                data = self.search_wrapper(cursor=cur, multiple=multiple)
                result = TransactionResult(success=True, data=data)
                cur.close()

        except pymysql.Error as e:
            result = self.mariadb_error_handler(e)

        finally:
            if conn: conn.close()

        return result

    def insert(self, query, parameters=None):
        """
        Ejecuta consultas de creación (INSERT) en la base de datos.

        Parámetros:
            query (str): La consulta SQL a ejecutar.
            parameters (tuple, opcional): Valores a insertar de forma segura.

        Retorna:
            TransactionResult: Objeto con el ID generado (lastrowid) o el error capturado.
        """
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(query, parameters)
                lastrowid = cur.lastrowid
                conn.commit() 
                result = TransactionResult(success=True, data=lastrowid)
                cur.close()

        except pymysql.Error as e:
            if conn is not None:
                conn.rollback() 
            result = self.mariadb_error_handler(e)

        finally:
            if conn: conn.close()

        return result

    def modify(self, query, parameters=None):
        """
        Ejecuta consultas de modificación o eliminación (UPDATE, DELETE).

        Parámetros:
            query (str): La consulta SQL a ejecutar.
            parameters (tuple, opcional): Variables a inyectar de forma segura.

        Retorna:
            TransactionResult: Objeto con el número de filas afectadas o el error capturado.
        """
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute(query, parameters)
                rows_affected = cur.rowcount
                conn.commit()
                result = TransactionResult(success=True, data=rows_affected)
                cur.close()

        except pymysql.Error as e:
            if conn is not None:
                conn.rollback()
            result = self.mariadb_error_handler(e)

        finally:
            if conn: conn.close()

        return result

    @staticmethod
    def search_wrapper(cursor, multiple):
        """
        Función helper que convierte el resultado en bruto del cursor SQL 
        en una lista de diccionarios (o un solo diccionario) legibles por Python.
        """
        def parse_json_output(output):
            try:
                parsed = json.loads(output)
            except (ValueError, TypeError):
                return output
            return parsed

        if cursor.rowcount > 0:
            columns = [col[0] for col in cursor.description] 
            if multiple:
                rows_parsed = []
                for row in cursor.fetchall():
                    row_fields = []
                    for field in row:
                        row_fields.append(parse_json_output(field))
                    rows_parsed.append(row_fields)
                return [dict((k, v) for k, v in d.items() if v is not None) 
                        for d in [dict(zip(columns, fields)) for fields in rows_parsed]]
            else:
                row = cursor.fetchone()
                if row is not None:
                    row_fields = []
                    for field in row:
                        row_fields.append(parse_json_output(field))
                    return dict((k, v) for k, v in dict(zip(columns, row_fields)).items() if v is not None)
        return None

    @staticmethod
    def mariadb_error_handler(e: pymysql.Error):
        """
        Captura los errores nativos de PyMySQL y los traduce al formato estandarizado
        TransactionResult para que el DTO pueda interpretarlos fácilmente.
        """
        if isinstance(e, pymysql.IntegrityError):
            return TransactionResult(
                success=False, message=f"Duplicate entry error: {str(e)}", status="112", code=409)
        elif isinstance(e, pymysql.DataError):
            return TransactionResult(
                success=False, message=f"Invalid data error: {str(e)}", status="111", code=400)
        elif isinstance(e, pymysql.OperationalError):
            return TransactionResult(
                success=False, message=f"Operational error: {str(e)}", status="100", code=500)
        else:
            return TransactionResult(
                success=False, message=f"Unknown error: {str(e)}", status="100", code=500)
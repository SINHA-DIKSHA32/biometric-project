import cx_Oracle

def connect_db():
    return cx_Oracle.connect(
        user="system",
        password="hr",
        dsn="localhost/XEPDB1"
    )

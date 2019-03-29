import sqlite3
import sys


def get_connection():
    conn = sqlite3.connect('.coverage')
    return conn

def _process_file(connection, path: str) -> None:
    pass



def main() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    # t = ('RHAT',)
    # select file.path from file order by path;
    # cursor.execute('SELECT file.path FROM file WHERE symbol=?', t)
    # for row in cursor.execute('SELECT file.path FROM file ORDER BY path'):
    for file_id, file_path in cursor.execute('SELECT file.id, file.path FROM file ORDER BY path'):
        print(file_id, file_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())


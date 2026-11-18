from pathlib import Path
from .connection import connection
SQL = Path(__file__).with_name('schema.sql').read_text(encoding='utf-8')
def main():
    with connection() as conn:
        conn.execute(SQL)
    print('Database schema initialized.')
if __name__ == '__main__': main()

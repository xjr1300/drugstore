import os
import sqlite3

# SQLスクリプトディレクトリ
SQL_DIR = os.path.join(os.getcwd(), "sql")

# データベースファイル名
DATABASE_FILE_NAME = "drugstore.db3"


def execute_sql_file(conn: sqlite3.Connection, path: str) -> None:
    """ファイルに記録されたSQL文をデータベースに実行する。

    コミットしないため、この関数の呼び出し元でコミットまたはロールバックすること。

    Args:
        conn (sqlite3.Connection): データベース接続
        path (str): SQLファイルのパス
    """
    with open(path, "rt") as sql_file:
        sql_statements = sql_file.read()
    cursor = conn.cursor()
    cursor.executescript(sql_statements)


def connect_to_database(file_path: str) -> sqlite3.Connection:
    """データベースに接続する。

    データベースが存在しない場合は、データベースを作成する。

    Args:
        file_path (str): データベースファイルのパス

    Returns:
        sqlite3.Connection: データベース接続
    """
    # データベースファイルが存在するか確認
    is_existed = os.path.isfile(file_path)
    # データベースが存在しない場合はデータベースを作成して、データベースに接続
    conn = sqlite3.connect(file_path)
    # 外部参照制約を有効化
    conn.execute("PRAGMA foreign_keys = true")
    # データベースファイルが存在した場合は、テーブルに初期行を挿入せずに、
    # データベース接続を返して終了
    if is_existed:
        return conn
    # テーブル作成SQL文を実行
    sql_path = os.path.join(SQL_DIR, "create_tables.sql")
    execute_sql_file(conn, sql_path)
    # 商品テーブルに行を挿入
    sql_path = os.path.join(SQL_DIR, "insert_item_rows.sql")
    execute_sql_file(conn, sql_path)
    # 会員区分テーブルに行を挿入
    sql_path = os.path.join(SQL_DIR, "insert_membership_type_rows.sql")
    execute_sql_file(conn, sql_path)
    # 顧客テーブルに行を挿入
    sql_path = os.path.join(SQL_DIR, "insert_customer_rows.sql")
    execute_sql_file(conn, sql_path)
    # 消費税テーブルに行を挿入
    sql_path = os.path.join(SQL_DIR, "insert_consumption_tax_rows.sql")
    execute_sql_file(conn, sql_path)
    # データベースをコミット
    conn.commit()
    return conn

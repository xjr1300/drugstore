import os
import sqlite3
import sys
import unittest
import uuid
from glob import glob
from typing import Tuple

from termcolor import colored

DATABASE_DIR = os.path.join(os.getcwd(), "tests", "integrations", "databases")

SQL_DIR = os.path.join(os.getcwd(), "sql")


def remove_test_dbs() -> None:
    """テスト用データベースをすべて削除する。"""
    path = os.path.join(DATABASE_DIR, "test_*.db3")
    db_paths = glob(path, recursive=False)
    for db_path in db_paths:
        try:
            os.remove(db_path)
        except Exception:
            print(f"can't remove {db_path}", file=sys.stderr)


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


def create_test_db() -> Tuple[sqlite3.Connection, str]:
    """テスト用データベースを作成する。

    Returns:
        Tuple[sqlite3.Connection, str]: データベース接続とデータベースのファイルパスを
            格納したタプル
    """
    # データベースを保存するディレクトリを作成
    if not os.path.isdir(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
    # データベースを作成
    db_name = f"test_{uuid.uuid4()}.db3"
    db_path = os.path.join(DATABASE_DIR, db_name)
    conn = sqlite3.connect(db_path)
    # テーブル作成SQL文を実行
    sql_path = os.path.join(SQL_DIR, "create_tables.sql")
    execute_sql_file(conn, sql_path)
    # 会員区分テーブルに行を挿入
    sql_path = os.path.join(SQL_DIR, "insert_membership_type_rows.sql")
    execute_sql_file(conn, sql_path)
    # データベースをコミット
    conn.commit()
    return conn, db_path


class IntegrationTestCase(unittest.TestCase):
    """統合テストクラス

    sqlite3はネストしたトランザクションをサポートしていない。
    よって、setUpClassでSAVEPOINTを作成して、tearDownでSAVEPOINTにロールバックする
    ことで、それぞれテストケースを実行する前の状態にデータベースを戻したいが、sqlite3は
    COMMITすると未処理のトランザクションをコミットして、トランザクションスタックを空にする。
    つまり、作成したSAVEPOINTがすべて削除され、コミット後はSAVEPOINTまでロールバックできない。
    よって、setUpでデータベースを作成して、tearDownでデータベースを削除するように実装した。
    """

    # データベース接続
    conn: sqlite3.Connection
    # データベースのパス
    db_path: str = ""

    def setUp(self) -> None:  # noqa: D102
        result = super().setUp()
        # テスト用データベースをすべて削除
        remove_test_dbs()
        # テースト用データベースを作成
        conn, db_path = create_test_db()
        # メンバ変数を設定
        self.conn = conn
        self.db_path = db_path
        return result

    def tearDown(self) -> None:  # noqa: D102
        # テスト用データベースと切断
        self.conn.close()
        # テスト用データベースを削除
        try:
            os.remove(self.db_path)
        except Exception:
            print(colored(f"can't remove {self.db_path}", "red"), file=sys.stderr)
        return super().tearDown()


class IntegrationTestCaseTest(IntegrationTestCase):
    """統合テストクラスのテスト"""

    def test_can_access_to_database(self) -> None:
        """テスト用のデータベースにアクセスできるか確認"""
        sql = "SELECT COUNT(*) FROM items"
        cursor = self.conn.execute(sql)
        result = cursor.fetchone()[0]
        self.assertEqual(0, result)

    def tearDown(self) -> None:  # noqa: D102
        result = super().tearDown()
        # データベースファイルが削除されていることを確認
        self.assertFalse(os.path.isfile(self.db_path))
        return result


class ExplicitIntegrationTestCase(unittest.TestCase):
    """統合テストクラス

    FIXME: 本テストクラスは適切に機能しないので使用しないこと。

    https://github.com/django/django/blob/02dab94c7b8585c7ae3854465574d768e1df75d3/django/db/backends/sqlite3/base.py#L225
    When 'isolation_level' is not None, sqlite3 commits before each
    savepoint; it's a bug. When it is None, savepoints don't make sense
    because autocommit is enabled. The only exception is inside 'atomic'
    blocks. To work around that bug, on SQLite, 'atomic' starts a
    transaction explicitly rather than simply disable autocommit.
    `isolation_level`がNoneでないとき、sqlite3は前のそれぞれのセーブポイントをコミットする。
    これはバグである。`isolation_level`がNoneのとき、自動コミットが有効になるため、セーブポイントは
    意味をなさない。このバグを回避するために、SQLiteにおいて、`atomic`は単に自動コミットを無効にする
    よりも、明示的にトランザクションを開始する。
    """

    # データベース接続
    conn: sqlite3.Connection
    # データベースのパス
    db_path: str = ""

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D102
        result = super().setUpClass()
        # テスト用データベースをすべて削除
        remove_test_dbs()
        # テースト用データベースを作成
        conn, db_path = create_test_db()
        # メンバ変数を設定
        cls.conn = conn
        cls.db_path = db_path
        return result

    def setUp(self) -> None:  # noqa: D102
        result = super().setUp()
        self.conn.execute("BEGIN")
        return result

    def tearDown(self) -> None:  # noqa: D102
        self.conn.rollback()
        return super().tearDown()

    @classmethod
    def tearDownClass(cls) -> None:  # noqa: D102
        # テスト用データベースと切断
        cls.conn.close()
        # テスト用データベースを削除
        try:
            os.remove(cls.db_path)
        except Exception:
            print(f"can't remove {cls.db_path}", file=sys.stderr)
        return super().tearDownClass()


# class ExplicitIntegrationTestCaseTest(ExplicitIntegrationTestCase):
#     """統合テストクラスのテスト"""
#
#     def test_can_access_to_database(self) -> None:
#         """テスト用のデータベースにアクセスできるか確認"""
#         sql = "SELECT COUNT(*) FROM items"
#         cursor = self.conn.execute(sql)
#         number_of_rows = cursor.fetchone()[0]
#         self.assertEqual(0, number_of_rows)
#
#     def test_can_insert_row_to_database(self) -> None:
#         """テスト用のデータベースに行を挿入できるか確認"""
#         sql = "INSERT INTO items (id, name, unit_price) VALUES (?, ?, ?)"
#         self.conn.execute(sql, (str(uuid.uuid4()), "正露丸", "300"))
#         self.conn.commit()
#
#     def tearDown(self) -> None:  # noqa: D102
#         result = super().tearDown()
#         sql = "SELECT COUNT(*) FROM items"
#         cursor = self.conn.execute(sql)
#         number_of_rows = cursor.fetchone()[0]
#         if 0 < number_of_rows:
#             print(colored("[warn] database was not rollback", "red"), file=sys.stderr)
#         return result

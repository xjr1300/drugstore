import os
import sqlite3
import sys
import unittest
import uuid
from glob import glob
from typing import Tuple

DATABASE_DIR = os.path.join(os.getcwd(), "tests", "integration_tests", "dbs")

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


def create_test_db() -> Tuple[sqlite3.Connection, str]:
    """テスト用データベースを作成する。

    Returns:
        Tuple[sqlite3.Connection, str]: データベース接続とデータベースのファイルパスを
            格納したタプル
    """
    # テーブル作成SQL文を取得
    sql_path = os.path.join(SQL_DIR, "create_tables.sql")
    with open(sql_path, "rt") as sql_file:
        sql_statements = sql_file.read()
    # データベースを保存するディレクトリを作成
    if not os.path.isdir(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
    # データベースを作成
    db_name = f"test_{uuid.uuid4()}.db3"
    db_path = os.path.join(DATABASE_DIR, db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(sql_statements)
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
            print(f"can't remove {self.db_path}", file=sys.stderr)
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

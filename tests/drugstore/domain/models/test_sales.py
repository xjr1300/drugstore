import unittest


class SaleDetailTest(unittest.TestCase):
    """売上明細テストクラス

    - 妥当な属性で売上明細をインスタンス化できて、小計が単価と数量を乗じた額になっていることを確認
    - 売上明細の数量が0以下の場合に、売上明細をインスタンス化できないことを確認
    """  # noqa: E501

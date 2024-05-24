import unittest


class ConsumptionTaxesTest(unittest.TestCase):
    """消費税リストテスト

    # TODO: 次を確認する単体テストを実装すること

    - 消費税を複数格納したリストについて、消費税の期間が重複または途切れなく連続している場合にTrueを返す
    - 消費税を1つ格納したリストの場合にTrueを返す
    - 消費税を複数格納したリストについて、消費税の期間に重複がある場合にFalseを返す
    - 消費税を複数格納したリストについて、消費税の期間に途切れがある場合にFalseを返す
    """  # noqa: E501


class ConsumptionTaxManagerTest(unittest.TestCase):
    """消費税管理者クラステスト

    # TODO: 次の単体テストを実装すること

    - イニシャライザ
        - 消費税管理クラスを構築したとき、次の不変条件を満たしているか確認
            - 1つ以上の消費税を管理していること
            - 消費税の期間が連続していること
            - 起点日時が最も大きい消費税の終点日時が終点日時の最大値になっていること
        - 空の消費税のリストを受け取った場合、ValueError例外をスローすること
        - 消費税の期間が連続していない場合、ValueError例外をスローすること
    """

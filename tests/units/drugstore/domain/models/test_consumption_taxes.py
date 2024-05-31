import unittest
import uuid
from datetime import datetime
from decimal import Decimal

from drugstore.common import JST
from drugstore.domain.models.consumption_taxes import ConsumptionTax


class ConsumptionTaxTest(unittest.TestCase):
    """消費税テストクラス"""

    def test_instantiate_by_valid_attrs(self) -> None:
        """妥当な属性で消費税をインスタンス化できることを確認"""
        id = uuid.uuid4()
        begin = datetime(2024, 1, 1, 0, 0, 0, tzinfo=JST)
        end = datetime.max.replace(tzinfo=JST)
        rate = Decimal("0.10")

        sut = ConsumptionTax(id, begin, end, rate)

        self.assertEqual(begin, sut.begin)
        self.assertEqual(end, sut.end)
        self.assertEqual(rate, sut.rate)

    def test_can_not_instantiate_by_terms_are_not_jst(self) -> None:
        """起点日時または終点日時が日本標準時でない場合に、消費税をインスタンス化できないことを確認"""
        data = [
            (uuid.uuid4(), datetime(2024, 1, 1, 0, 0, 0), datetime.max),
            (uuid.uuid4(), datetime(2024, 1, 1, 0, 0, 0, tzinfo=JST), datetime.max),
            (
                uuid.uuid4(),
                datetime(2024, 1, 1, 0, 0, 0),
                datetime.max.replace(tzinfo=JST),
            ),
        ]
        rate = Decimal("0.10")

        for id, begin, end in data:
            with self.assertRaises(ValueError):
                _ = ConsumptionTax(id, begin, end, rate)

    def test_can_not_instantiate_by_begin_is_out_of_range(self) -> None:
        """最も過去の起点日時と最も将来の終点日時の消費税をインスタンス化できることを確認

        本来であれば、最も過去の起点日時よりも前の起点日時を持つ消費税をインスタンス化できないことを
        確認するべきだが、そのような起点日時をdatetime型が表現できないため、最も過去の起点日時を
        もつ消費税をインスタンス化できることを確認するテストにした。
        これは、最も将来の終点日時についても同様である。
        """
        id = uuid.uuid4()
        begin = datetime.min.replace(tzinfo=JST)
        end = datetime.max.replace(tzinfo=JST)
        rate = Decimal("0.10")

        sut = ConsumptionTax(id, begin, end, rate)

        self.assertEqual(begin, sut.begin)
        self.assertEqual(end, sut.end)

    def test_can_not_instantiate_by_begin_is_greater_than_or_equal_to_end(
        self,
    ) -> None:
        """起点日時が終点日時以降の場合に、消費税をインスタンス化できないことを確認"""
        data = [
            (
                uuid.uuid4(),
                datetime(2024, 1, 1, 0, 0, 0, tzinfo=JST),
                datetime(2024, 1, 1, 0, 0, 0, tzinfo=JST),
            ),
            (
                uuid.uuid4(),
                datetime(2024, 1, 1, 0, 0, 1, tzinfo=JST),
                datetime(2024, 1, 1, 0, 0, 0, tzinfo=JST),
            ),
        ]
        rate = Decimal("0.10")

        for id, begin, end in data:
            with self.assertRaises(ValueError):
                _ = ConsumptionTax(id, begin, end, rate)

    def test_can_not_instantiate_by_rate_is_less_than_zero(
        self,
    ) -> None:
        """消費税の税率が0.0より小さい場合に、消費税をインスタンス化できないことを確認"""
        id = uuid.uuid4()
        begin = datetime(2024, 1, 1, 0, 0, 0, tzinfo=JST)
        end = datetime.max.replace(tzinfo=JST)
        rate = Decimal("-0.01")

        with self.assertRaises(ValueError):
            _ = ConsumptionTax(id, begin, end, rate)

    def test_can_not_instantiate_by_rate_is_greater_equal_one(self) -> None:
        """消費税の税率が1.0以上の場合に、消費税をインスタンス化できないことを確認"""
        id = uuid.uuid4()
        begin = datetime(2024, 1, 1, 0, 0, 0, tzinfo=JST)
        end = datetime.max.replace(tzinfo=JST)
        rates = [Decimal("1.0"), Decimal("1.01")]

        with self.assertRaises(ValueError):
            for rate in rates:
                _ = ConsumptionTax(id, begin, end, rate)

    def test_contains(self) -> None:
        """containsメソッドが正しく判定するか確認"""
        target = ConsumptionTax(
            uuid.uuid4(),
            datetime(2024, 4, 1, tzinfo=JST),
            datetime(2024, 5, 1, tzinfo=JST),
            Decimal("0.1"),
        )
        data_list = [
            (
                True,
                ConsumptionTax(
                    uuid.uuid4(),
                    datetime(2024, 4, 1, tzinfo=JST),
                    datetime(2024, 5, 1, tzinfo=JST),
                    Decimal("0.1"),
                ),
            ),
            (
                True,
                ConsumptionTax(
                    uuid.uuid4(),
                    datetime(2024, 4, 2, tzinfo=JST),
                    datetime(2024, 5, 1, tzinfo=JST),
                    Decimal("0.1"),
                ),
            ),
            (
                True,
                ConsumptionTax(
                    uuid.uuid4(),
                    datetime(2024, 4, 1, tzinfo=JST),
                    datetime(2024, 4, 30, tzinfo=JST),
                    Decimal("0.1"),
                ),
            ),
            (
                True,
                ConsumptionTax(
                    uuid.uuid4(),
                    datetime(2024, 4, 2, tzinfo=JST),
                    datetime(2024, 4, 30, tzinfo=JST),
                    Decimal("0.1"),
                ),
            ),
            (
                False,
                ConsumptionTax(
                    uuid.uuid4(),
                    datetime(2024, 3, 31, tzinfo=JST),
                    datetime(2024, 5, 1, tzinfo=JST),
                    Decimal("0.1"),
                ),
            ),
            (
                False,
                ConsumptionTax(
                    uuid.uuid4(),
                    datetime(2024, 4, 1, tzinfo=JST),
                    datetime(2024, 5, 2, tzinfo=JST),
                    Decimal("0.1"),
                ),
            ),
            (
                False,
                ConsumptionTax(
                    uuid.uuid4(),
                    datetime(2024, 3, 31, tzinfo=JST),
                    datetime(2024, 5, 2, tzinfo=JST),
                    Decimal("0.1"),
                ),
            ),
        ]
        for data in data_list:
            result = target.contains(data[1])
            self.assertEqual(data[0], result, f"{data[1].begin}, {data[1].end}")


def is_same_consumption_tax_conditions(a: ConsumptionTax, b: ConsumptionTax) -> bool:
    """消費税の起点日時、終点日時、税率が等しいか確認する。

    Args:
        a (ConsumptionTax): 消費税
        b (ConsumptionTax): 消費税

    Returns:
        bool: 等しい場合はTrue、そうでない場合はFalse
    """
    if a.begin != b.begin:
        return False
    if a.end != b.end:
        return False
    return True if a.rate == b.rate else False

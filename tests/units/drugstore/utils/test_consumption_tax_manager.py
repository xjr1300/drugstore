import copy
import random
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from drugstore.common import jst_datetime
from drugstore.domain.models.consumption_taxes import (
    MAX_CONSUMPTION_TAX_END,
    MIN_CONSUMPTION_TAX_BEGIN,
    ConsumptionTax,
)
from drugstore.utils.consumption_tax_manager import (
    ConsumptionTaxManager,
)

# 消費税が1つ登録された消費税リスト
SIMPLE_CONSUMPTION_TAXES = [
    ConsumptionTax(
        uuid.uuid4(), MIN_CONSUMPTION_TAX_BEGIN, MAX_CONSUMPTION_TAX_END, Decimal("0.1")
    )
]

# 3つの消費税を登録した消費税リスト
THREE_CONSUMPTION_TAXES = [
    ConsumptionTax(
        uuid.uuid4(),
        MIN_CONSUMPTION_TAX_BEGIN,
        jst_datetime(2024, 4, 1),
        Decimal("0.05"),
    ),
    ConsumptionTax(
        uuid.uuid4(),
        jst_datetime(2024, 4, 1),
        jst_datetime(2024, 6, 1),
        Decimal("0.10"),
    ),
    ConsumptionTax(
        uuid.uuid4(),
        jst_datetime(2024, 6, 1),
        MAX_CONSUMPTION_TAX_END,
        Decimal("0.15"),
    ),
]

# 連続した消費税リスト
CONTINUOUS_CONSUMPTION_TAXES = [
    ConsumptionTax(
        uuid.uuid4(),
        jst_datetime(2024, 1, 1),
        jst_datetime(2024, 4, 1),
        Decimal("0.05"),
    ),
    ConsumptionTax(
        uuid.uuid4(),
        jst_datetime(2024, 4, 1),
        jst_datetime(2024, 7, 1),
        Decimal("0.10"),
    ),
    ConsumptionTax(
        uuid.uuid4(),
        jst_datetime(2024, 7, 1),
        jst_datetime(2024, 9, 1),
        Decimal("0.15"),
    ),
    ConsumptionTax(
        uuid.uuid4(),
        jst_datetime(2024, 9, 1),
        jst_datetime(2025, 1, 1),
        Decimal("0.20"),
    ),
]


class ConsumptionTaxManagerTest(unittest.TestCase):
    """消費税管理者クラステスト

    次の不変条件が成立することを確認する。

    - 消費税リストの要素数は1以上
    - 消費税リストの消費税の期間に重複または途切れがない
    - 消費税リストに含まれる消費税の全期間は、MIN_CONSUMPTION_TAX_BEGINからMAX_CONSUMPTION_TAX_ENDまで
    """  # noqa: E501

    def test_instantiate_by_list_contains_continuous_consumption_taxes(self) -> None:
        """期間が連続した消費税リストが渡されたとき、インスタンスを構築できることを確認"""
        # 連続した消費税リストをランダムに並び替え
        taxes = copy.deepcopy(CONTINUOUS_CONSUMPTION_TAXES)
        random.shuffle(taxes)

        sut = ConsumptionTaxManager(taxes)

        self.assertGreaterEqual(len(sut.consumption_taxes), 1)
        self.assertEqual(MIN_CONSUMPTION_TAX_BEGIN, sut.consumption_taxes[0].begin)
        self.assertEqual(MAX_CONSUMPTION_TAX_END, sut.consumption_taxes[-1].end)

    def test_instantiate_by_list_contains_one_consumption_tax(self) -> None:
        """1つの消費税を格納した消費税リストが渡されたとき、インスタンス化できることを確認"""
        taxes = [
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 1, 1),
                jst_datetime(2025, 1, 1),
                Decimal("0.10"),
            ),
        ]

        sut = ConsumptionTaxManager(taxes)

        self.assertGreaterEqual(len(sut.consumption_taxes), 1)
        self.assertEqual(MIN_CONSUMPTION_TAX_BEGIN, sut.consumption_taxes[0].begin)
        self.assertEqual(MAX_CONSUMPTION_TAX_END, sut.consumption_taxes[-1].end)

    def test_can_not_instantiate_by_consumption_tax_list_that_is_not_continuous(
        self,
    ) -> None:
        """期間が途切れている消費税リストが渡されたとき、インスタンス化できないことを確認"""
        taxes = copy.deepcopy(CONTINUOUS_CONSUMPTION_TAXES)
        # 2番目の消費税を削除して、期間を途切れさせる
        del taxes[1]

        with self.assertRaises(ValueError):
            _ = ConsumptionTaxManager(taxes)

    def test_can_not_instantiate_by_consumption_tax_list_that_period_is_overlapped(
        self,
    ) -> None:
        """期間が重複している消費税リストが渡されたとき、インスタンス化できないことを確認"""
        taxes = copy.deepcopy(CONTINUOUS_CONSUMPTION_TAXES)
        # 最初と次の消費税の期間を重複させる
        taxes[1].begin = taxes[1].begin - timedelta(seconds=1)

        with self.assertRaises(ValueError):
            _ = ConsumptionTaxManager(taxes)

    def test_ensure_return_consumption_tax_rate_if_assigning_middle_of_the_period(
        self,
    ) -> None:
        """消費税の起点日時と終点日時の間の日時を指定したとき、その消費税の税率を返すことを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        delta = taxes[1].end - taxes[1].begin
        dt = taxes[1].begin + delta / 2
        sut = ConsumptionTaxManager(taxes)

        result = sut.consumption_tax_rate(dt)

        self.assertEqual(taxes[1].rate, result)

    def test_ensure_return_consumption_tax_rate_if_assigning_beginning_of_the_period(
        self,
    ) -> None:
        """消費税の起点日時を指定したとき、その消費税の税率を返すことを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        sut = ConsumptionTaxManager(taxes)

        result = sut.consumption_tax_rate(taxes[1].begin)

        self.assertEqual(taxes[1].rate, result)

    def test_ensure_return_consumption_tax_rate_if_assigning_end_of_the_period(
        self,
    ) -> None:
        """消費税の終点日時を指定したとき、その消費税の次の消費税の税率を返すことを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        sut = ConsumptionTaxManager(taxes)

        result = sut.consumption_tax_rate(taxes[1].end)

        self.assertEqual(taxes[2].rate, result)

    def test_ensure_return_consumption_tax_rate_if_assigning_min_of_begin(self) -> None:
        """消費税の起点日時の最小値を指定したとき、その消費税の次の消費税の税率を返すことを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        sut = ConsumptionTaxManager(taxes)

        result = sut.consumption_tax_rate(MIN_CONSUMPTION_TAX_BEGIN)

        self.assertEqual(taxes[0].rate, result)

    def test_ensure_raise_exception_if_assigning_max_of_end(self) -> None:
        """消費税の終点日時の最大値を指定したとき、例外をスローすることを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        sut = ConsumptionTaxManager(taxes)

        with self.assertRaises(ValueError):
            _ = sut.consumption_tax_rate(MAX_CONSUMPTION_TAX_END)

    def test_ensure_raise_exception_if_assigning_non_jst(self) -> None:
        """日本標準時以外の日時を指定したとき、例外をスローすることを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        dts = [datetime(2024, 1, 1), datetime(2024, 1, 1, tzinfo=timezone.utc)]
        sut = ConsumptionTaxManager(taxes)

        with self.assertRaises(ValueError):
            for dt in dts:
                _ = sut.consumption_tax_rate(dt)

    def test_additional_included_consumption_tax(self) -> None:
        """既存の消費税の期間に完全に含まれる消費税を追加した後、不変条件を満たすことを確認

        追加する消費税(a)の期間を含む消費税(e)が消費税リストに存在して、追加する消費税の
        期間を含む消費税が消費税リストに存在する場合
        e.begin < a.begin, a.end < e.end
        """
        rate = Decimal("0.1")
        taxes = [
            ConsumptionTax(
                uuid.uuid4(), MIN_CONSUMPTION_TAX_BEGIN, MAX_CONSUMPTION_TAX_END, rate
            )
        ]
        sut = ConsumptionTaxManager(taxes)
        addition = ConsumptionTax(
            uuid.uuid4(),
            jst_datetime(2024, 1, 1),
            jst_datetime(2025, 1, 1),
            Decimal("0.05"),
        )

        sut.add_consumption_tax(addition)

        self.assertEqual(3, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[0],
                MIN_CONSUMPTION_TAX_BEGIN,
                addition.begin,
                rate,
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[1],
                addition.begin,
                addition.end,
                addition.rate,
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[2],
                addition.end,
                MAX_CONSUMPTION_TAX_END,
                rate,
            )
        )

    def test_additional_consumption_tax_has_same_period(self) -> None:
        """既存の消費税の期間と完全に一致する消費税を追加した後、不変条件を満たすことを確認

        追加する消費税(a)の期間を含む消費税(e)が消費税リストに存在して、追加する消費税の
        期間と完全に一致する消費税が消費税リストに存在する場合
        e.begin == a.begin, a.end == e.end
        """
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        addition = ConsumptionTax(
            uuid.uuid4(),
            jst_datetime(2024, 4, 1),
            jst_datetime(2024, 6, 1),
            Decimal("0.20"),
        )
        sut = ConsumptionTaxManager(taxes)

        sut.add_consumption_tax(addition)

        self.assertEqual(3, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[0],
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[1],
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 6, 1),
                Decimal("0.20"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[2],
                jst_datetime(2024, 6, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.15"),
            )
        )

    def test_additional_consumption_tax_has_same_begin(self) -> None:
        """既存の消費税の起点日時と起点日時が等しい消費税を追加した後、不変条件を満たすことを確認

        追加する消費税(a)の期間を含む消費税(e)が消費税リストに存在して、追加する消費税の
        起点日時が、消費税リストの消費税(e)と起点日時が一致する場合
        e.begin == a.begin, a.end < e.end
        消費税リストに追加する消費税(a)の期間を含む消費税(e)が存在する
        """
        existence_taxes = [
            ConsumptionTax(
                uuid.uuid4(),
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 6, 1),
                Decimal("0.10"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 6, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.15"),
            ),
        ]
        addition = ConsumptionTax(
            uuid.uuid4(),
            jst_datetime(2024, 4, 1),
            jst_datetime(2024, 5, 1),
            Decimal("0.20"),
        )
        sut = ConsumptionTaxManager(existence_taxes)

        sut.add_consumption_tax(addition)

        self.assertEqual(4, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[0],
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[1],
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 5, 1),
                Decimal("0.20"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[2],
                jst_datetime(2024, 5, 1),
                jst_datetime(2024, 6, 1),
                Decimal("0.10"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[3],
                jst_datetime(2024, 6, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.15"),
            )
        )

    def test_additional_consumption_tax_has_same_end(self) -> None:
        """既存の消費税の終点日時と終点日時が等しい消費税を追加した後、不変条件を満たすことを確認

        追加する消費税(a)の期間を含む消費税(e)が消費税リストに存在して、追加する消費税の
        終点日時が、消費税リストの消費税(e)と終点日時が一致する場合
        e.begin < a.begin, a.end == e.end
        消費税リストに追加する消費税(a)の期間を含む消費税(e)が存在する
        """
        existence_taxes = [
            ConsumptionTax(
                uuid.uuid4(),
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 6, 1),
                Decimal("0.10"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 6, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.15"),
            ),
        ]
        addition = ConsumptionTax(
            uuid.uuid4(),
            jst_datetime(2024, 5, 1),
            jst_datetime(2024, 6, 1),
            Decimal("0.20"),
        )
        sut = ConsumptionTaxManager(existence_taxes)

        sut.add_consumption_tax(addition)

        self.assertEqual(4, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[0],
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[1],
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 5, 1),
                Decimal("0.10"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[2],
                jst_datetime(2024, 5, 1),
                jst_datetime(2024, 6, 1),
                Decimal("0.20"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[3],
                jst_datetime(2024, 6, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.15"),
            )
        )

    def test_additional_consumption_tax_contains_taxes_in_list(self) -> None:
        """追加する消費税の期間に含まれる消費税が消費税リストに存在するとき、その消費税を追加しても不変条件を満たすことを確認"""
        existence_taxes = [
            ConsumptionTax(
                uuid.uuid4(),
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 5, 1),
                Decimal("0.10"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 5, 1),
                jst_datetime(2024, 6, 1),
                Decimal("0.15"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 6, 1),
                jst_datetime(2024, 7, 1),
                Decimal("0.20"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 7, 1),
                jst_datetime(2024, 8, 1),
                Decimal("0.25"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 8, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.30"),
            ),
        ]
        addition = ConsumptionTax(
            uuid.uuid4(),
            jst_datetime(2024, 5, 15),
            jst_datetime(2024, 7, 15),
            Decimal("0.35"),
        )
        sut = ConsumptionTaxManager(existence_taxes)

        sut.add_consumption_tax(addition)

        self.assertEqual(6, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[0],
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[1],
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 5, 1),
                Decimal("0.10"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[2],
                jst_datetime(2024, 5, 1),
                jst_datetime(2024, 5, 15),
                Decimal("0.15"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[3],
                jst_datetime(2024, 5, 15),
                jst_datetime(2024, 7, 15),
                Decimal("0.35"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[4],
                jst_datetime(2024, 7, 15),
                jst_datetime(2024, 8, 1),
                Decimal("0.25"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[5],
                jst_datetime(2024, 8, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.30"),
            )
        )

    def test_additional_consumption_tax_does_noe_contains_taxes_in_list(
        self,
    ) -> None:
        """追加する消費税の期間に含まれる消費税が消費税リストに存在しないとき、その消費税を追加しても不変条件を満たすことを確認"""
        existence_taxes = [
            ConsumptionTax(
                uuid.uuid4(),
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 6, 1),
                Decimal("0.10"),
            ),
            ConsumptionTax(
                uuid.uuid4(),
                jst_datetime(2024, 6, 1),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.15"),
            ),
        ]
        addition = ConsumptionTax(
            uuid.uuid4(),
            jst_datetime(2024, 5, 15),
            jst_datetime(2024, 6, 15),
            Decimal("0.20"),
        )
        sut = ConsumptionTaxManager(existence_taxes)

        sut.add_consumption_tax(addition)

        self.assertEqual(4, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[0],
                MIN_CONSUMPTION_TAX_BEGIN,
                jst_datetime(2024, 4, 1),
                Decimal("0.05"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[1],
                jst_datetime(2024, 4, 1),
                jst_datetime(2024, 5, 15),
                Decimal("0.10"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[2],
                jst_datetime(2024, 5, 15),
                jst_datetime(2024, 6, 15),
                Decimal("0.20"),
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[3],
                jst_datetime(2024, 6, 15),
                MAX_CONSUMPTION_TAX_END,
                Decimal("0.15"),
            )
        )

    def test_modify_consumption_tax_rate(self) -> None:
        """消費税リストに存在するidが一致する消費税の税率を変更できることを確認"""
        taxes = copy.deepcopy(SIMPLE_CONSUMPTION_TAXES)
        id = taxes[0].id
        begin = taxes[0].begin
        end = taxes[0].end
        rate = taxes[0].rate + Decimal("0.01")

        sut = ConsumptionTaxManager(taxes)

        sut.modify_consumption_tax_rate(id, rate)

        self.assertEqual(1, len(sut.consumption_taxes))
        self.assertEqual(rate, sut.consumption_taxes[0].rate)
        self.assertEqual(id, sut.consumption_taxes[0].id)
        self.assertEqual(begin, sut.consumption_taxes[0].begin)
        self.assertEqual(end, sut.consumption_taxes[0].end)

    def test_raise_exception_if_modifying_consumption_tax_rate_by_non_existence_id(
        self,
    ) -> None:
        """idが一致する消費税が消費税リストに存在しないときに、ValueErrorがスローされることを確認"""
        taxes = copy.deepcopy(SIMPLE_CONSUMPTION_TAXES)
        sut = ConsumptionTaxManager(taxes)

        with self.assertRaises(ValueError):
            sut.modify_consumption_tax_rate(uuid.uuid4(), Decimal("0.1"))

    def test_raise_exception_if_modifying_consumption_tax_rage_by_outrange_rate(
        self,
    ) -> None:
        """消費税の税率が範囲外のときに、ValueErrorがスローされることを確認"""
        taxes = copy.deepcopy(SIMPLE_CONSUMPTION_TAXES)
        sut = ConsumptionTaxManager(taxes)
        rates = [Decimal("-0.01"), Decimal("1.01")]

        with self.assertRaises(ValueError):
            for rate in rates:
                sut.modify_consumption_tax_rate(uuid.uuid4(), rate)

    """TODO: 次のテストケースを実装

    * ok: 消費税リストに格納されている消費税が3つのときに、2番目の消費税を削除した後、不変条件が守られているか確認
    * 消費税リストに格納されている消費税が2つのときに、最初の消費税を削除した後、不変条件が守られているか確認
    * 消費税リストに格納されている消費税が2つのときに、最後の消費税を削除した後、不変条件が守られているか確認
    * 消費税リストに格納されている消費税が1つの場合に、消費税の削除を試行したとき、例外がスローされることを確認
    * 消費税リストに格納されている消費税と一致しない消費税IDを指定して、消費税の削除を試行したとき、例外がスローされることを確認
    """  # noqa: E501

    def test_keep_invariant_conditions_after_removing_first_consumption_tax(
        self,
    ) -> None:
        """消費税リストに格納されている消費税が3つのときに、最初の消費税を削除した後、不変条件が守られているか確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        id = taxes[0].id
        sut = ConsumptionTaxManager(copy.deepcopy(taxes))

        sut.remove_consumption_tax(id)

        self.assertEqual(2, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[0],
                MIN_CONSUMPTION_TAX_BEGIN,
                taxes[1].end,
                taxes[1].rate,
            )
        )

    def test_keep_invariant_conditions_after_removing_second_consumption_tax(
        self,
    ) -> None:
        """消費税リストに格納されている消費税が3つのときに、2番目の消費税を削除した後、不変条件が守られているか確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        id = taxes[1].id
        sut = ConsumptionTaxManager(copy.deepcopy(taxes))

        sut.remove_consumption_tax(id)

        self.assertEqual(2, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[0], taxes[0].begin, taxes[0].end, taxes[0].rate
            )
        )
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[1], taxes[0].end, taxes[2].end, taxes[2].rate
            )
        )

    def test_keep_invariant_conditions_after_removing_last_consumption_tax(
        self,
    ) -> None:
        """消費税リストに格納されている消費税が3つのときに、最後の消費税を削除した後、不変条件が守られているか確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        id = taxes[2].id
        sut = ConsumptionTaxManager(copy.deepcopy(taxes))

        sut.remove_consumption_tax(id)

        self.assertEqual(2, len(sut.consumption_taxes))
        self.assertTrue(
            is_same_consumption_tax(
                sut.consumption_taxes[1],
                taxes[1].begin,
                MAX_CONSUMPTION_TAX_END,
                taxes[1].rate,
            )
        )

    def test_consumption_taxes_are_merged_because_addition_occurs_continuous_rate(
        self,
    ) -> None:
        """同じ税率の消費税が連続するように消費税を追加したとき、連続した消費税がマージされることを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        sut = ConsumptionTaxManager(taxes)
        addition = ConsumptionTax(
            uuid.uuid4(),
            jst_datetime(2024, 5, 1),
            jst_datetime(2024, 5, 15),
            Decimal("0.10"),
        )

        sut.add_consumption_tax(addition)

        self.assertEqual(3, len(sut.consumption_taxes))

    def test_consumption_taxes_are_merged_because_modifying_occurs_continuous_rate(
        self,
    ) -> None:
        """同じ税率の消費税が連続するように消費税の税率を変更したとき、連続した消費税がマージされることを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        sut = ConsumptionTaxManager(taxes)

        sut.modify_consumption_tax_rate(taxes[1].id, Decimal("0.05"))

        self.assertEqual(2, len(sut.consumption_taxes))

    def test_consumption_taxes_are_merged_because_removing_occurs_continuous_rate(
        self,
    ) -> None:
        """同じ税率の消費税が連続するように消費税を削除したとき、連続した消費税がマージされることを確認"""
        taxes = copy.deepcopy(THREE_CONSUMPTION_TAXES)
        taxes[2].rate = Decimal("0.05")
        sut = ConsumptionTaxManager(taxes)

        sut.remove_consumption_tax(taxes[1].id)

        self.assertEqual(1, len(sut.consumption_taxes))


def is_same_consumption_tax(
    tax: ConsumptionTax, begin: datetime, end: datetime, rate: Decimal
) -> bool:
    """消費税が等しいか確認する。

    消費税IDは比較の対象としない。

    Args:
        tax (ConsumptionTax): 消費税
        begin (datetime): 消費税の起点日時
        end (datetime): 消費税の終点日時
        rate (Decimal): 消費税率

    Returns:
        bool: 等しい場合はTrue、異なる場合はFalse
    """
    if tax.begin != begin:
        return False
    if tax.end != end:
        return False
    return tax.rate == rate

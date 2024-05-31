import bisect
import uuid
from datetime import datetime
from decimal import Decimal
from operator import attrgetter
from typing import Callable, List, Optional

from drugstore.common import is_jst_datetime
from drugstore.domain.models.consumption_taxes import (
    MAX_CONSUMPTION_TAX_END,
    MIN_CONSUMPTION_TAX_BEGIN,
    ConsumptionTax,
)


def ensure_consumption_tax_periods_are_continuous(taxes: List[ConsumptionTax]) -> bool:
    """消費税の期間が重複または途切れなく連続しているか確認する。

    Args:
        taxes (List[ConsumptionTax]): 消費税リスト

    Raises:
        ValueError: 消費税リストは1つ以上の消費税を格納していなければなりません。

    Returns:
        bool: 消費税の期間が重複または途切れなく連続している場合はTrue、
            連続していない場合はFalse
    """
    if len(taxes) == 0:
        raise ValueError(
            "消費税リストは1つ以上の消費税を格納していなければなりません。"
        )
    if len(taxes) == 1:
        return True
    end = taxes[0].end
    index = 1
    while index < len(taxes):
        if taxes[index].begin != end:
            return False
        end = taxes[index].end
        index += 1
    return True


class ConsumptionTaxManager:
    """消費税管理者クラス

    消費税管理者クラスが管理する消費税リストの不変条件を次に示す。

    - 消費税リストの要素数は1以上
    - 消費税リストの消費税の期間に重複または途切れがない
    - 消費税リストに含まれる消費税の全期間は、MIN_CONSUMPTION_TAX_BEGINからMAX_CONSUMPTION_TAX_ENDまで
    """  # noqa: E501

    def __init__(self, consumption_taxes: List[ConsumptionTax]) -> None:
        """イニシャライザ

        1. 消費税リストを起点日時でソート
        2. 消費税リストに消費税の期間が重複または途切れなく連続しているか確認
        3. 先頭の消費税の起点日時に起点日時の最小値を設定
        4. 最後の消費税の終点日時に終点日時の最大値を設定

        Args:
            consumption_taxes (List[ConsumptionTax]): 消費税リスト

        Raises:
            ValueError: 消費税管理者クラスは1つ以上の消費税を受け取ります。
            ValueError: 消費税の期間が途切れているか重複しています。
        """
        if len(consumption_taxes) == 0:
            raise ValueError("消費税管理者クラスは1つ以上の消費税を受け取ります。")
        consumption_taxes.sort(key=attrgetter("begin"))
        if not ensure_consumption_tax_periods_are_continuous(consumption_taxes):
            raise ValueError("消費税の期間が途切れているか重複しています。")
        consumption_taxes[0].begin = MIN_CONSUMPTION_TAX_BEGIN
        consumption_taxes[-1].end = MAX_CONSUMPTION_TAX_END
        self.consumption_taxes = consumption_taxes

    def consumption_tax_rate(self, dt: datetime) -> Decimal:
        """引数で指定された日時に適用される消費税の税率を返す。

        Args:
            dt (datetime): 日時

        Raises:
            ValueError: 日本標準時の日時を指定してください。
            ValueError: 消費税の税率が管理されていない日時です。
            RuntimeError: 消費税の税率を返すときに想定していないエラーが発生しました。

        Returns:
            Decimal: 消費税の税率
        """
        if not is_jst_datetime(dt):
            raise ValueError("日本標準時の日時を指定してください。")
        if dt == MAX_CONSUMPTION_TAX_END:
            raise ValueError("消費税の税率が管理されていない日時です。")
        for tax in self.consumption_taxes:
            if tax.begin <= dt and dt < tax.end:
                return tax.rate
        raise RuntimeError(
            "消費税の税率を返す関数内で想定していないエラーが発生しました。"
        )

    def add_consumption_tax(self, addition: ConsumptionTax) -> None:
        """消費税リストに消費税を追加する。

        消費税リストに追加する消費税を含む消費税が存在するか確認する。
        リスト内にそのような消費税が存在する場合は、次を実行する。
            -   既存の消費税の起点日時と追加する消費税の起点日時が異なる場合、既存の
                消費税の起点日時を起点日時、追加する消費税の起点日時を終点日時、既存
                の消費税の税率にした消費税を作成する。
            -   追加する消費税は何もしない。
            -   追加する消費税の終点日時と既存の消費税の終点日時が異なる場合、追加する
                消費税の終点日時を起点日時、既存の消費税の終点日時を終点日時、既存の
                消費税の税率にした消費税を作成する。
            -   その後、上記1から3つの消費税を、消費税リストの適切な位置に挿入する。
        リスト内にそのような消費税が存在しない場合は、次を実行する。
            -   追加する消費税の起点日時と終点日時に含まれる消費税をすべて削除する。
            -   追加する消費税より前後の消費税と、新しく追加する消費税の期間が途切れない
                ように、前後の消費税の終点日時または起点日時を、新しく追加する消費税の起
                点日時または終点日時にする。
            -   新しく追加する消費税より前の消費税がない場合は、新しく追加する消費税の
                起点日時を`MIN_CONSUMPTION_TAX_BEGIN`に変更する。
            -   新しく追加する消費税より後の消費税がない場合は、新しく追加する消費税の
                終点日時を`MAX_CONSUMPTION_TAX_END`に変更する。

        Args:
            addition (ConsumptionTax): 追加する消費税
        """
        # 追加する消費税の期間を含む消費税が消費税リストに存在するか確認
        index = retrieve_contained_consumption_tax_index(
            self.consumption_taxes, addition
        )
        if 0 <= index:
            # 追加する消費税の期間を含む消費税が消費税リストに存在する場合
            taxes = generate_consumption_taxes_for_included_addition(
                self.consumption_taxes, index, addition
            )
        else:
            # 追加する消費税の期間を含む消費税が消費税リストに存在しない場合
            taxes = generate_consumption_taxes_for_overlapped_addition(
                self.consumption_taxes, addition
            )
        # 同じ消費税の税率が連続している場合、消費税をマージ
        taxes = marge_consumption_tax_period(taxes)
        # 消費税リストメンバ変数を設定
        self.consumption_taxes = taxes

    def modify_consumption_tax_rate(self, id: uuid.UUID, renewal: Decimal) -> None:
        """消費税の税率を変更する。

        引数renewalのidと一致する消費税を消費税リストから検索して、その消費税の税率を変更する。
        消費税の起点日時や終点日時の変更は、add_consumption_taxメソッドで代用する。

        Args:
            id (uuid.UUID): 変更する消費税のID
            renewal (Decimal): 変更後の消費税の税率

        Raises:
            ValueError: 消費税の税率が0.0未満または1.0以上です。
            ValueError: 消費税IDが一致する消費税が消費税リストに存在しません。
        """
        # ダミーの消費税を構築して、消費税の税率が範囲内か確認
        try:
            _ = ConsumptionTax(
                uuid.uuid4(),
                MIN_CONSUMPTION_TAX_BEGIN,
                MAX_CONSUMPTION_TAX_END,
                renewal,
            )
        except ValueError:
            raise
        # 消費税リストから消費税IDが一致する消費税を検索
        func: Callable[[ConsumptionTax], bool] = lambda tax: tax.id == id
        target: Optional[ConsumptionTax] = next(
            filter(func, self.consumption_taxes), None
        )
        if target is None:
            raise ValueError("消費税IDが一致する消費税が消費税リストに存在しません。")
        # 消費税を変更
        target.rate = renewal
        # 同じ消費税の税率が連続している場合、消費税をマージ
        self.consumption_taxes = marge_consumption_tax_period(self.consumption_taxes)

    def remove_consumption_tax(self, id: uuid.UUID) -> None:
        """消費税IDで指定された消費税を消費税リストから削除する。

        Args:
            id (uuid.UUID): 削除する消費税のID

        Raises:
            ValueError: 消費税IDが一致する消費税が消費税リストに存在しません。
            RuntimeError: 消費税リストに登録された消費税の数を0にできません。
        """
        # 消費税が1つしか格納されていない場合は例外をスロー
        number_of_taxes = len(self.consumption_taxes)
        if number_of_taxes <= 1:
            raise RuntimeError("消費税リストに登録された消費税の数を0にできません。")
        # 消費税IDが一致する消費税を示す消費税リストのインデックスを取得
        index = 0
        while index < number_of_taxes:
            if self.consumption_taxes[index].id == id:
                break
            index += 1
        if number_of_taxes <= index:
            raise ValueError("消費税IDが一致する消費税が消費税リストに存在しません。")
        # 消費税リストの消費税の期間が連続するように、削除するインデックスの1つ後の
        # 消費税の起点日時を、削除するインデックスの1つ前の終点日時に変更
        # * index==0の場合は先頭の消費税を削除するため対象外
        # * 1==number_of_taxesの場合は末尾の消費税を削除するため
        #   対象外
        if 0 < index and 1 < number_of_taxes - index:
            self.consumption_taxes[index + 1].begin = self.consumption_taxes[
                index - 1
            ].end
        # 先頭の消費税を削除する場合は、次の消費税の起点日時を起点日時の最小値に変更
        if index == 0:
            self.consumption_taxes[1].begin = MIN_CONSUMPTION_TAX_BEGIN
        # 末尾の消費税を削除する場合は、前の消費税の終点日時を終点日時の最大値に変更
        if index == number_of_taxes - 1:
            self.consumption_taxes[index - 1].end = MAX_CONSUMPTION_TAX_END
        # 消費税を削除
        del self.consumption_taxes[index]
        # 同じ消費税の税率が連続している場合、消費税をマージ
        self.consumption_taxes = marge_consumption_tax_period(self.consumption_taxes)


def retrieve_contained_consumption_tax_index(
    taxes: List[ConsumptionTax], tax: ConsumptionTax
) -> int:
    """消費税リストに引数の消費税の期間を含む消費税のインデックスを取得する。

    Args:
        taxes (List[ConsumptionTax]): 消費税リスト
        tax (ConsumptionTax): 消費税

    Returns:
        int: 消費税リストのインデックス
            そのような消費税が消費税リストに存在しない場合は-1
    """
    for index, tax_in_list in enumerate(taxes):
        if tax_in_list.contains(tax):
            return index
    return -1


def generate_consumption_taxes_for_included_addition(
    taxes: List[ConsumptionTax], index: int, addition: ConsumptionTax
) -> List[ConsumptionTax]:
    """追加する消費税の期間を含む消費税が消費税リストに存在する場合に、消費税を消費税リストに追加する。

    Args:
        taxes (List[ConsumptionTax]): 消費税リスト
        index (int): 追加する消費税の期間を含む消費税リストの消費税のインデックス
        addition (ConsumptionTax): 追加する消費税

    Returns:
        List[ConsumptionTax]: 追加後の消費税リスト
    """
    new_taxes: List[ConsumptionTax] = []
    container = taxes[index]
    # 既存の消費税の起点日時と追加する消費税の起点日時が異なる場合、既存の消費税の
    # 起点日時を起点日時、追加する消費税の起点日時を終点日時、既存の消費税の税率に
    # した消費税を追加
    if container.begin < addition.begin:
        new_taxes.append(
            ConsumptionTax(
                uuid.uuid4(),
                container.begin,
                addition.begin,
                container.rate,
            )
        )
    # 追加する消費税を追加
    new_taxes.append(addition)
    # 追加する消費税の終点日時と既存の消費税の終点日時が異なる場合、追加する消費税の
    # 終点日時を起点日時、既存の消費税の終点日時を終点日時、既存の消費税の税率にした
    # 消費税を追加
    if addition.end < container.end:
        new_taxes.append(
            ConsumptionTax(
                uuid.uuid4(),
                addition.end,
                container.end,
                container.rate,
            )
        )
    # 追加する消費税を含む消費税リストの消費税を、新しく追加する最初の消費税で入れ替え
    taxes[index] = new_taxes[0]
    index += 1
    # 新しく追加する消費税を順に挿入
    for tax in new_taxes[1:]:
        taxes.insert(index, tax)
        index += 1
    return taxes


def generate_consumption_taxes_for_overlapped_addition(
    taxes: List[ConsumptionTax], addition: ConsumptionTax
) -> List[ConsumptionTax]:
    """追加する消費税の期間を含む消費税が消費税リストに存在しない場合に、消費税を消費税リストに追加する。

    Args:
        taxes (List[ConsumptionTax]): 消費税リスト
        addition (ConsumptionTax): 追加する消費税

    Returns:
        List[ConsumptionTax]: 追加後の消費税リスト
    """
    # 追加する消費税の期間に含まれる消費税を消費税リストから削除
    # filter関数で追加する消費税の期間に含まれない消費税を消費税リストから抽出した
    # リスト作成することで、実質的に、追加する消費税の期間に含まれる消費税を消費税
    # リストから削除
    func: Callable[[ConsumptionTax], bool] = lambda t: not addition.contains(t)
    taxes = list(filter(func, taxes))
    # 消費税リストに消費税を追加
    index = bisect.bisect_left(taxes, addition.begin, key=attrgetter("begin"))
    taxes.insert(index, addition)
    # 挿入した位置の前の消費税の終点日時を変更
    if 1 < index:
        taxes[index - 1].end = addition.begin
    # 挿入した位置の後ろの消費税の終点日時を変更
    if index < len(taxes) - 1:
        taxes[index + 1].begin = addition.end
    # 消費税リストの最初の消費税の起点日時を起点日時の最小値に設定
    taxes[0].begin = MIN_CONSUMPTION_TAX_BEGIN
    # 消費税リストの最後の消費税の終点日時を終点日時の最大値に設定
    taxes[-1].end = MAX_CONSUMPTION_TAX_END
    return taxes


def marge_consumption_tax_period(taxes: List[ConsumptionTax]) -> List[ConsumptionTax]:
    """同じ消費税の税率が連続している場合、後の消費税の終点日時を前の消費税の終点日時に変更して、後の消費税を削除する。

    Args:
        taxes (List[ConsumptionTax]): 消費税リスト

    Returns:
        List[ConsumptionTax]: マージ後の消費税のリスト
    """
    number_of_taxes = len(taxes)
    if number_of_taxes <= 1:
        return taxes
    index = 1
    while index < number_of_taxes:
        if taxes[index - 1].rate == taxes[index].rate:
            """同じ消費税の税率が連続している"""
            taxes[index - 1].end = taxes[index].end
            del taxes[index]
            number_of_taxes -= 1
        else:
            """同じ消費税の税率が連続していない"""
            index += 1
    return taxes


from datetime import datetime 
from lxml import etree
from typing import Any
import re


class Entry: 
    def __init__( self,
        namespaces: dict[str, str],
        stmt: etree._Element,
        entry: etree._Element,
        default_ns: str | None = None,
        default_timezone: Any | None = None
    ) -> None:
        self._namespaces = namespaces
        self._default_ns = default_ns
        self._regexp = re.compile(r"(\+(\d\d:)+\d\d(|\.\d+))$")

        self.stmt_id = self.get_direct_val(stmt, "ElctrncSeqNb")
        self.id_entry = self.get_direct_val(entry, "NtryRef")

        self.value = float(self.get_direct_val(entry, "Amt"))
        self.credito_debito = self.get_direct_val(entry, "CdtDbtInd")
        self.description = self.get_inner_val(entry, [ "NtryDtls", "TxDtls", "AddtlTxInf" ])

        self.data: datetime = datetime.strptime(
            self._cleanup_date(
                self.get_inner_val(entry, ['BookgDt', "Dt"])
            ),
            "%Y-%m-%d%z",
        ).astimezone(default_timezone)
        self.data_valuta: datetime = datetime.strptime(
            self._cleanup_date(
                self.get_inner_val(entry, ['ValDt', "Dt"])
            ),
            "%Y-%m-%d%z",
        ).astimezone(default_timezone)

    def _cleanup_date(self, s: str):
        dp = self._regexp.search(s)

        if dp is not None:
            start, end = dp.span()
            matched = s[start:end]
            return s[:start] + matched.replace(":", "")
        else:
            return s

    def get_inner_val(
        self,
        element: etree._Element,
        names: list[str],
        _ns: str | None = None,
    ):
        if self._default_ns is None:
            if _ns is None:
                raise ValueError()
            else:
                ns = _ns       
        else:
            ns = self._default_ns

        # NtryDtls
        current = element
        for n in names:
            current = current.find(f"{ns}:{n}", self._namespaces)

            if current is None:
                raise ValueError()

        if current.text is None:
            raise ValueError()
        else:
            return current.text


    def get_direct_val(
        self,
        element: etree._Element,
        name: str,
        _ns: str | None = None,
    ):
        if self._default_ns is None:
            if _ns is None:
                raise ValueError()
            else:
                ns = _ns       
        else:
            ns = self._default_ns
            
        tag_tofind = element.find(f"{ns}:{name}", self._namespaces)
        assert(tag_tofind is not None)
        assert(tag_tofind.text is not None)
        return tag_tofind.text

    @property
    def sign(self):
        if self.credito_debito == "CRDT":
            return "+"
        elif self.credito_debito == "DBIT":
            return "-"
        else:
            raise ValueError()

    @classmethod
    def to_print_headers(cls) -> list[str]:
        return ["data", "data_valuta", "sign", "value", "description"]

    def csv_exported(self) -> list[str]:
        ret: list[str] = []
        for el in self.to_print_headers():
            val = getattr(self, el)

            if isinstance(val, datetime):
                ret.append(val.strftime("%Y-%m-%d"))
            else:
                ret.append(val)

        return ret

    def __str__(self) -> str:
        return f"[E]:{self.stmt_id:2}:{self.id_entry:2} |{self.data}|{self.data_valuta}| {self.sign}{self.value:8.2f} -> {self.description}"

    def __repr__(self) -> str:
        return self.__str__()


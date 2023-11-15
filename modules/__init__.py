from dataclasses import dataclass, field
from enum import Enum
from re import compile, DOTALL, Pattern

from pathlib import Path
from pdfminer.high_level import extract_text


@dataclass
class Fee:
    excel_path: Path
    name_file:str = field(init=False)
    _text:str = field(init=False, repr=False)

    #Fields
    date = compile(r'(\d{2}-\d{2}-\d{4})')

    def __post_init__(self) -> None:
        self.name_file:str = self.excel_path.stem
        self._text: str = extract_text(self.excel_path, page_numbers=[0]).casefold() # First Page

    def get_data(self, *args: Pattern) -> tuple | None:
        result:list = []
        for pattern in args:
            pattern: Pattern
            data = pattern.search(self._text)
            if data != None: result.append(data.group(1).replace('\n', '').replace(' ', '').upper())
            else: result.append('')
        return tuple(result)

@dataclass
class AxactorFee(Fee):
    amount = compile(r'importe:\s+(.+)')
    nrc = compile(r'nrc:\s*(.+)\s*importe')

    
@dataclass
class CaixaBankFee(Fee):
    amount = compile(r'importe\s+:\n+(\d+)\s+euros')
    nrc = compile(r'nrc.+:\s*(.+)')

    
@dataclass
class SabadellFee(Fee):
    amount = compile(r'importe:\s+([0-9,]*)')
    nrc = compile(r'nrc:\s*([a-z0-9\n\s]*).+\nel', DOTALL)


class Client(Enum):
    AXACTOR = 1
    CAIXABANK = 2
    SABADELL = 3

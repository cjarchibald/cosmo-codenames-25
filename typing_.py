
from typing import AnyStr, Collection, TypeAlias

import numpy as np

from .enums import GameCondition


Word: TypeAlias = AnyStr
WordList: TypeAlias = Collection[Word]
EndStatus: TypeAlias = GameCondition
Clue = tuple[Word, int] | list[Word, int]

Sequence = list|tuple|np.ndarray
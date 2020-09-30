from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from .game import AbstractGame

class DummyPlayer:
    def getGameID(self) -> Optional[str]: return NotImplemented
    def setGameID(self, id: str): return NotImplemented

class DummyDB:
    def addPlayer(self) -> Tuple[str, DummyPlayer]: return NotImplemented
    def getPlayer(self, id: str) -> Optional[DummyPlayer]: return NotImplemented

class DummyDB2:
    def getGame(self, id: str) -> Optional[AbstractGame]: return NotImplemented

Player = DummyPlayer
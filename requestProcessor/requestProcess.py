from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from . import interactions

class DummyDB:
    def addPlayer(self) -> Tuple[str, object]: return NotImplemented
    def getPlayer(self, id: str) -> Optional[object]: return NotImplemented

playerDatabase = DummyDB()

def process(r: interactions.UnprocessedClientRequest):

    if r.playerID is None:
        # new player id
        playerID, playerData = playerDatabase.addPlayer()
        r.setPlayerID(playerID)
    else:
        playerData = playerDatabase.getPlayer(r.playerID)
        if playerData is None:
            return interactions.ResponseFailure('Player not found in database')
    
    # now we get r.playerID and playerData
        

from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Tuple
from . import interactions
from .game import AbstractGame    
from .dataTypes import DummyDB, DummyDB2, Player


playerDatabase = DummyDB()

gameDatabase = DummyDB2()

def process(r: interactions.UnprocessedClientRequest) -> interactions.Response:

    if r.playerID is None:
        # new player id
        playerID, playerData = playerDatabase.addPlayer()
        r.setPlayerID(playerID)
    else:
        playerData = playerDatabase.getPlayer(r.playerID)
        if playerData is None:
            return interactions.ResponseFailure('Player not found in database')
    
    # now we get r.playerID and playerData

    if isinstance(r, interactions.JoinGameClientRequest):
        game = gameDatabase.getGame(r.gameID)
        gameID = r.gameID
        # is game joinable? - not started & exists
        # if so, join
        if game is None:
            return interactions.ResponseFailure('Game not found in database')
        elif game.hasGameStarted:
            return interactions.ResponseFailure('Game has already started')
        
        game.joinPlayer(playerData)
        interactions.ResponseSuccess()
    else:
        gameID = playerData.getGameID()
        # todo
        

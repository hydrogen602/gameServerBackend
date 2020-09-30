from __future__ import annotations
from requestProcessor.errors import ActionError
from . import interactions
from .dataTypes import DummyDB, DummyDB2, Player, PlayerManager, GameManager


# playerDatabase: PlayerManager = DummyDB()

# gameDatabase: GameManager = DummyDB2()

class RequestProcessor:

    def __init__(self, playerDatabase: PlayerManager, gameDatabase: GameManager) -> None:
        self.playerDatabase = playerDatabase
        self.gameDatabase = gameDatabase
        super().__init__()
    
    def __joinRequestProcess(self, playerData: Player, r: interactions.JoinGameClientRequest) -> interactions.Response:        
        game = self.gameDatabase.getGame(r.gameID)
        # is game joinable? - not started & exists
        # if so, join
        if game is None:
            return interactions.ResponseFailure('Game not found in database')
        elif game.hasGameStarted:
            return interactions.ResponseFailure('Game has already started')
        
        response = game.joinPlayer(playerData)
        playerData.setGameID(r.gameID)
        if isinstance(response, interactions.Response):
                return response
        else:
            raise TypeError(f'Expected type "{type(interactions.Response)}" but got type "{type(response)}"')
            #interactions.ResponseFailure('Unknown Error')

    def __regularRequestProcess(self, playerData: Player, r: interactions.UnprocessedClientRequest) -> interactions.Response:
        # standard request
        if r.request is None:
            return interactions.ResponseFailure('Empty request')

        gameID = playerData.getGameID()
        game = self.gameDatabase.getGame(gameID)
        if game is None:
            return interactions.ResponseFailure('Game not found in database')
        
        try:
            response = game.handleRequest(playerData, r.request)
        except ActionError as e:
            return interactions.ResponseFailure('ActionError: ' + str(e))
        except Exception as e:
            return interactions.ResponseFailure('Unknown Error: ' + repr(e))
        else:
            if isinstance(response, interactions.Response):
                return response
            else:
                raise TypeError(f'Expected type "{type(interactions.Response)}" but got type "{type(response)}"')
                #interactions.ResponseFailure('Unknown Error')

    def process(self, r: interactions.UnprocessedClientRequest) -> interactions.Response:

        if r.playerID is None:
            # new player id
            playerID, playerData = self.playerDatabase.addPlayer()
            r.setPlayerID(playerID)
        else:
            playerData = self.playerDatabase.getPlayer(r.playerID)
            if playerData is None:
                return interactions.ResponseFailure('Player not found in database')
        
        # now we get r.playerID and playerData

        if isinstance(r, interactions.JoinGameClientRequest):
            return self.__joinRequestProcess(playerData, r)
        else:
            return self.__regularRequestProcess(playerData, r)
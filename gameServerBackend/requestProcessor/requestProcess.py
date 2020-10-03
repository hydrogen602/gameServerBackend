from __future__ import annotations
from .errors import ActionError
from . import interactions
from .dataTypes import Player, PlayerManager, GameManager


class RequestProcessor:
    '''
    RequestProcessor takes a request that is
    either of type `interactions.JoinGameClientRequest` or
    `interactions.UnprocessedClientRequest` and checks
    if the player has a valid id assigned already and otherwise
    assigns a new one. The idea is that it guarantees that every
    player has an id and that both the game exists and the player's
    request is send to the right game
    '''

    def __init__(self, playerDatabase: PlayerManager, gameDatabase: GameManager) -> None:
        self.playerDatabase = playerDatabase
        self.gameDatabase = gameDatabase
        super().__init__()
    
    def __joinRequestProcess(self, playerData: Player, r: interactions.JoinGameClientRequest) -> interactions.Response:        
        game = self.gameDatabase.getGame(r.gameID)
        # is game joinable? - not started & exists
        # if so, join
        if game is None:
            return interactions.ResponseFailure(playerData, 'Game not found in database')
        elif game.hasGameStarted:
            return interactions.ResponseFailure(playerData, 'Game has already started')
        
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
            return interactions.ResponseFailure(playerData, 'Empty request')

        gameID = playerData.getGameID()
        if gameID is None:
            return interactions.ResponseFailure(playerData, 'No joined game to send request to')

        game = self.gameDatabase.getGame(gameID)
        if game is None:
            return interactions.ResponseFailure(playerData, 'Game not found in database')
        
        try:
            response = game.handleRequest(playerData, r.request)
        except ActionError as e:
            return interactions.ResponseFailure(playerData, 'ActionError: ' + str(e))
        except Exception as e:
            return interactions.ResponseFailure(playerData, 'Unknown Error: ' + repr(e))
        else:
            if isinstance(response, interactions.Response):
                return response
            else:
                raise TypeError(f'Expected type "{type(interactions.Response)}" but got type "{type(response)}"')
                #interactions.ResponseFailure('Unknown Error')

    def process(self, r: interactions.UnprocessedClientRequest) -> interactions.Response:
        assert isinstance(r, interactions.UnprocessedClientRequest)
        
        playerData = self.playerDatabase.getPlayer(r.playerID)
        if playerData is None:
            playerData = self.playerDatabase.addPlayer(r.playerID)
        
        # now we get r.playerID and playerData

        if isinstance(r, interactions.JoinGameClientRequest):
            return self.__joinRequestProcess(playerData, r)
        else:
            return self.__regularRequestProcess(playerData, r)

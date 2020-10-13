from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Dict, Optional, TYPE_CHECKING, Union
from secrets import token_urlsafe
import sqlite3
import atexit

if TYPE_CHECKING:
    from ..requestProcessor.dataTypes import Player


class TokenStorage(ABC):
    '''
    An interface so that custom data structures can be used.
    It is used to match up tokens used for identifying players with their names, as if
    we used names for identification, it could easily be spoofed. 
    Note: This is not a secure system at all, it merely tries to dissuade
    basic shenanigens.
    Note: Player ID and Player name are used interchangeable 
    '''

    @abstractmethod
    def getPlayerIDbyToken(self, token: str) -> Optional[str]:
        '''
        Returns the token by player id. If the token isn't found,
        it returns None.
        '''
        return NotImplemented
    
    @abstractmethod
    def getTokenbyPlayerID(self, playerID: Union[str, Player]) -> Optional[str]:
        '''
        Returns the player id by name. If the player id isn't found,
        it returns None.
        '''
        return NotImplemented
    
    @abstractmethod
    def addPlayerID(self, playerID: Union[str, Player]) -> str:
        '''
        Add a player with a player id to the list and
        generate and return a unique token.
        Raise ValueError if the player id already exists.
        '''
        return NotImplemented


class PersistentTokenStorage(TokenStorage):
    '''
    An implementation for TokenStorage that allows
    for persistent data storage by using a sqlite database
    using python's module sqlite3. It can also be used
    for an in-memory database if ':memory:' is passed
    to `__init__` as the dbFileName.
    '''

    def __init__(self, dbFileName: str):
        self.__conn: sqlite3.Connection = sqlite3.connect(dbFileName)

        atexit.register(self.__cleanup)

        self.__cur: sqlite3.Cursor = self.__conn.cursor()

        self.__cur.execute('''
        CREATE TABLE IF NOT EXISTS token_storage (
            token TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL PRIMARY KEY
        )
        ''')
        self.__conn.commit()

    def __cleanup(self):
        self.__conn.close()

    def getPlayerIDbyToken(self, token: str) -> Optional[str]:
        result = self.__cur.execute('SELECT name FROM token_storage WHERE token=?', (token,)).fetchall()
        if len(result) == 0:
            return None
        elif len(result) == 1:
            return result[0][0]
        else:
            raise RuntimeError('Found token more than once. This should never happen!')

    def getTokenbyPlayerID(self, playerID: Union[str, Player]) -> Optional[str]:
        if not isinstance(playerID, str):
            playerID = playerID.getPlayerName()

        result = self.__cur.execute('SELECT token FROM token_storage WHERE name=?', (playerID,)).fetchall()
        if len(result) == 0:
            return None
        elif len(result) == 1:
            return result[0][0]
        else:
            raise RuntimeError('Found name more than once. This should never happen!')

    def addPlayerID(self, playerID: Union[str, Player]) -> str:
        if not isinstance(playerID, str):
            playerID = playerID.getPlayerName()

        if self.getTokenbyPlayerID(playerID) is not None:
            raise ValueError('Player ID taken')

        token = token_urlsafe(16)
        while self.getPlayerIDbyToken(token) is not None:
            token = token_urlsafe(16)

        self.__cur.execute('''
        INSERT INTO token_storage (name, token) VALUES (?, ?)
        ''', (playerID, token))
        self.__conn.commit()

        return token



class BasicTokenStorage(TokenStorage):
    '''
    A simple implementation for TokenStorage
    using two dictionaries. It is used as default
    if a custom implementation is not specified. 
    '''

    def __init__(self, maximum: int = 100):
        self.__tokenBased: Dict[str, str] = {}
        self.__playerIDBased: Dict[str, str] = {}
        self.__maximum: int = maximum

    def getPlayerIDbyToken(self, token: str) -> Optional[str]:
        return self.__tokenBased.get(token)

    def getTokenbyPlayerID(self, playerID: Union[str, Player]) -> Optional[str]:
        if not isinstance(playerID, str):
            playerID = playerID.getPlayerName()
        return self.__playerIDBased.get(playerID)

    def addPlayerID(self, playerID: Union[str, Player]):
        if len(self.__playerIDBased) >= self.__maximum:
            raise RuntimeError(f'Too many players:max is {self.__maximum}')
        if not isinstance(playerID, str):
            playerID = playerID.getPlayerName()
        if playerID in self.__playerIDBased:
            raise ValueError('Player ID taken')

        token = token_urlsafe(16)
        while token in self.__tokenBased:
            token = token_urlsafe(16)

        self.__playerIDBased[playerID] = token
        self.__tokenBased[token] = playerID

        return token
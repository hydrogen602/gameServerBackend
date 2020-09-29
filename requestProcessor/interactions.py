from __future__ import annotations
from typing import Optional

from requests.models import Response

class UnprocessedClientRequest:

    def __init__(self, playerID: Optional[str], request: Optional[str]):
        self.__playerID: Optional[str] = playerID
        self.__request: Optional[str] = request
    
    @property
    def playerID(self) -> Optional[str]:
        return self.__playerID
    
    @property
    def request(self) -> Optional[str]:
        return self.__request
    
    def setPlayerID(self, pID: str):
        self.__playerID = pID


class Response:

    def __init__(self):
        if type(self) is Response:
            raise TypeError('"Response" is only for subclassing and should not be instantiated')

        self.errorMsg: Optional[str] = None

    def __init_subclass__(cls):
        if cls.isValid is Response.isValid:
            raise TypeError(f'Response subclass "{cls.__name__}" did not implement "isValid"')
        super().__init_subclass__()
    
    @property
    def isValid(self) -> bool:
        return NotImplemented


class ResponseSuccess(Response):
    
    def __init__(self):
        super.__init__()
    
    @property
    def isValid(self) -> bool:
        return True


class ResponseFailure(Response):

    def __init__(self, errMsg: str):
        super.__init__()
        self.errorMsg = errMsg

    @property
    def isValid(self) -> bool:
        return False
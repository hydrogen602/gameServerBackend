
class ActionError(Exception):
    '''
    Called when a player tries to do something that
    is not allowed by the game rules. When thrown
    in `AbstractGame.handleRequest`, it will
    generate a ResponseFailure
    '''
    pass
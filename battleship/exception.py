class BattleshipException(Exception):
    pass


class InvalidShipPlacementException(BattleshipException):
    pass


class InvalidShotException(BattleshipException):
    pass


class QuitGameException(BattleshipException):
    pass

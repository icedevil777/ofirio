class NoPropertyError(Exception):
    pass


class OffMarketPropertyError(Exception):
    pass


class PropertyAlreadyExists(Exception):
    message = {'message': 'already exists'}

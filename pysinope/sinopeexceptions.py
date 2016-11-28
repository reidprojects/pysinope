# -*- coding: utf-8 -*-


class InvalidSinopeAuthenticationError(Exception):
    def __init__(self, email):
        super(InvalidSinopeAuthenticationError,
              self).__init__("Invalid authentication for '{}'.".format(email))


class UnknownSinopeError(Exception):
    def __init__(self, details):
        super(UnknownSinopeError,
              self).__init__("Unknown error from the Sinope interface. Details : '{}'.".format(details))

from abc import ABC, abstractmethod
from datetime import date, datetime
from functools import reduce


class ErrorSistemaSalud(Exception):
    pass


class DatosInvalidosError(ErrorSistemaSalud):
    pass


class CitaDuplicadaError(ErrorSistemaSalud):
    pass
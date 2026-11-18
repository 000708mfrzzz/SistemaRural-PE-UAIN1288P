from abc import ABC, abstractmethod
from datetime import date, datetime
from functools import reduce


class ErrorSistemaSalud(Exception):
    pass


class DatosInvalidosError(ErrorSistemaSalud):
    pass


class CitaDuplicadaError(ErrorSistemaSalud):
    pass

def validar_dni(dni: str) -> bool:
    return isinstance(dni, str) and len(dni) == 8 and dni.isdigit()


def filtrar_atenciones_por_rango(atenciones: list, inicio: date, fin: date) -> list:
    return list(filter(lambda a: inicio <= a.fecha <= fin, atenciones))


def resumir_atenciones(atenciones: list) -> list:
    return list(map(lambda a: (a.codigo, a.fecha.isoformat(), a.cita.paciente.dni_enmascarado), atenciones))


def contar_por_procedencia(atenciones: list) -> dict:
    return reduce(
        lambda acc, a: {**acc, a.cita.paciente.procedencia: acc.get(a.cita.paciente.procedencia, 0) + 1},
        atenciones,
        {},
    )

class GestorEventos:
    def __init__(self) -> None:
        self._suscriptores = {}
        self.auditoria = []

    def suscribir(self, evento: str, manejador) -> None:
        self._suscriptores.setdefault(evento, []).append(manejador)

    def emitir(self, evento: str, detalle: str) -> None:
        registro = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {evento}: {detalle}"
        self.auditoria.append(registro)
        for manejador in self._suscriptores.get(evento, []):
            manejador(registro)
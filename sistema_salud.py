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

            class Persona(ABC):
    def __init__(self, nombres: str, fecha_nacimiento: date, sexo: str) -> None:
        if not nombres.strip():
            raise DatosInvalidosError("El nombre no puede estar vacío.")
        self._nombres = nombres.strip()
        self._fecha_nacimiento = fecha_nacimiento
        self._sexo = sexo

    @property
    def nombres(self) -> str:
        return self._nombres

    @abstractmethod
    def obtener_datos(self) -> str:
        pass


class Paciente(Persona):
    def __init__(self, dni: str, nombres: str, fecha_nacimiento: date, sexo: str, procedencia: str) -> None:
        super().__init__(nombres, fecha_nacimiento, sexo)
        if not validar_dni(dni):
            raise DatosInvalidosError("El DNI debe contener 8 dígitos numéricos.")
        self.__dni = dni
        self._procedencia = procedencia.strip()

    @property
    def dni_enmascarado(self) -> str:
        return f"****{self.__dni[-4:]}"

    @property
    def procedencia(self) -> str:
        return self._procedencia

    def coincidir_dni(self, dni_consulta: str) -> bool:
        return self.__dni == dni_consulta

    def obtener_datos(self) -> str:
        return f"Paciente: {self._nombres} | DNI: {self.dni_enmascarado} | Procedencia: {self._procedencia}"


class Medico(Persona):
    def __init__(self, codigo_medico: str, nombres: str, fecha_nacimiento: date, sexo: str, especialidad: str) -> None:
        super().__init__(nombres, fecha_nacimiento, sexo)
        self._codigo_medico = codigo_medico
        self._especialidad = especialidad

    @property
    def codigo_medico(self) -> str:
        return self._codigo_medico

    def obtener_datos(self) -> str:
        return f"Médico [{self._codigo_medico}]: {self._nombres} ({self._especialidad})"
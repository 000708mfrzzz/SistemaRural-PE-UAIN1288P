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

    class CentroSalud:
    def __init__(self, nombre: str, ubicacion: str) -> None:
        self.nombre = nombre
        self.ubicacion = ubicacion
        self._medicos = []

    def agregar_medico(self, medico: Medico) -> None:
        self._medicos.append(medico)

    def consultar_personal(self) -> list:
        return list(self._medicos)


class Cita:
    def __init__(self, codigo: str, paciente: Paciente, medico: Medico, fecha_hora: datetime, motivo: str) -> None:
        self.codigo = codigo
        self.paciente = paciente
        self.medico = medico
        self.fecha_hora = fecha_hora
        self.motivo = motivo
        self.estado = "PROGRAMADA"

    def reprogramar(self, nueva_fecha: datetime) -> None:
        if self.estado == "CANCELADA":
            raise DatosInvalidosError("No se puede reprogramar una cita cancelada.")
        self.fecha_hora = nueva_fecha
        self.estado = "REPROGRAMADA"

    def cancelar(self) -> None:
        self.estado = "CANCELADA"


class Atencion:
    def __init__(self, codigo: str, cita: Cita, fecha: date, observacion: str) -> None:
        self.codigo = codigo
        self.cita = cita
        self.fecha = fecha
        self.__observacion_cifrada = "".join(chr(ord(c) + 3) for c in observacion)

    def consultar_observacion(self, rol_usuario: str) -> str:
        if rol_usuario not in ("MEDICO", "JEFA_ESTABLECIMIENTO"):
            raise PermissionError("Rol sin autorización para ver diagnósticos clínicos.")
        return "".join(chr(ord(c) - 3) for c in self.__observacion_cifrada)

    class RepositorioDatos:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._pacientes = []
            cls._instancia._citas = []
            cls._instancia._atenciones = []
            cls._instancia.eventos = GestorEventos()
        return cls._instancia

    @classmethod
    def obtener_instancia(cls):
        return cls()

    def registrar_paciente(self, paciente: Paciente) -> None:
        self._pacientes.append(paciente)
        self.eventos.emitir("PACIENTE_REGISTRADO", f"DNI {paciente.dni_enmascarado}")

    def programar_cita(self, nueva_cita: Cita) -> None:
        for c in self._citas:
            if c.estado != "CANCELADA" and c.fecha_hora == nueva_cita.fecha_hora and (
                c.paciente == nueva_cita.paciente or c.medico.codigo_medico == nueva_cita.medico.codigo_medico
            ):
                raise CitaDuplicadaError("Conflicto de horario: el paciente o médico ya tiene una cita activa.")
        self._citas.append(nueva_cita)
        self.eventos.emitir("CITA_PROGRAMADA", f"Cita {nueva_cita.codigo} ({nueva_cita.paciente.dni_enmascarado})")

    def registrar_atencion(self, atencion: Atencion) -> None:
        self._atenciones.append(atencion)
        self.eventos.emitir("ATENCION_REGISTRADA", f"Atención {atencion.codigo}")

    @property
    def citas(self) -> list:
        return list(self._citas)

    @property
    def atenciones(self) -> list:
        return list(self._atenciones)

    class DetalleReporte:
    def __init__(self, total_citas: int, total_atenciones: int, por_procedencia: dict) -> None:
        self.total_citas = total_citas
        self.total_atenciones = total_atenciones
        self.por_procedencia = por_procedencia


class ReporteAtencion(ABC):
    def __init__(self, fecha_inicio: date, fecha_fin: date) -> None:
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.detalle = None

    @abstractmethod
    def generar_reporte(self, repo: RepositorioDatos) -> dict:
        pass


class ReportePorPeriodo(ReporteAtencion):
    def generar_reporte(self, repo: RepositorioDatos) -> dict:
        filtradas = filtrar_atenciones_por_rango(repo.atenciones, self.fecha_inicio, self.fecha_fin)
        self.detalle = DetalleReporte(len(repo.citas), len(filtradas), contar_por_procedencia(filtradas))
        repo.eventos.emitir("REPORTE_GENERADO", f"Período {self.fecha_inicio} al {self.fecha_fin}")
        return {
            "tipo": "Reporte por Período",
            "total_atenciones": self.detalle.total_atenciones,
            "por_procedencia": self.detalle.por_procedencia,
            "registros": resumir_atenciones(filtradas),
        }


class ReporteMensual(ReporteAtencion):
    def generar_reporte(self, repo: RepositorioDatos) -> dict:
        datos = ReportePorPeriodo(self.fecha_inicio, self.fecha_fin).generar_reporte(repo)
        datos["tipo"] = "Reporte Mensual"
        return datos


class CreadorReporte(ABC):
    @abstractmethod
    def crear_reporte(self, fecha_inicio: date, fecha_fin: date) -> ReporteAtencion:
        pass


class ReportePorPeriodoFactory(CreadorReporte):
    def crear_reporte(self, fecha_inicio: date, fecha_fin: date) -> ReporteAtencion:
        return ReportePorPeriodo(fecha_inicio, fecha_fin)


class ReporteMensualFactory(CreadorReporte):
    def crear_reporte(self, fecha_inicio: date, fecha_fin: date) -> ReporteAtencion:
        return ReporteMensual(fecha_inicio, fecha_fin)
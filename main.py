from datetime import date, datetime
from sistema_salud import (
    Atencion,
    CentroSalud,
    Cita,
    CitaDuplicadaError,
    Medico,
    Paciente,
    ReportePorPeriodoFactory,
    RepositorioDatos,
)


def main() -> None:
    repo = RepositorioDatos.obtener_instancia()
    repo.eventos.suscribir("PACIENTE_REGISTRADO", lambda msg: print(f"[AUDITORÍA] {msg}"))
    repo.eventos.suscribir("ATENCION_REGISTRADA", lambda msg: print(f"[AUDITORÍA] {msg}"))

    centro = CentroSalud("Centro de Salud Santa Rosa", "Chugur, Cajamarca")
    medico = Medico("MED-01", "Dra. Marisol Quispe", date(1988, 5, 14), "F", "Medicina General")
    centro.agregar_medico(medico)

    p1 = Paciente("74859612", "Juan Pérez Rojas", date(1995, 3, 20), "M", "Caserío El Tambo")
    p2 = Paciente("41258963", "María Huamán Díaz", date(1982, 11, 2), "F", "Chugur Centro")
    repo.registrar_paciente(p1)
    repo.registrar_paciente(p2)

    print("\n--- Salida protegida (Ley N.° 29733) ---")
    print(p1.obtener_datos())

    cita1 = Cita("CIT-001", p1, medico, datetime(2026, 11, 18, 9, 0), "Control general")
    cita2 = Cita("CIT-002", p2, medico, datetime(2026, 11, 18, 10, 0), "Consulta respiratoria")
    repo.programar_cita(cita1)
    repo.programar_cita(cita2)

    try:
        repo.programar_cita(Cita("CIT-003", p1, medico, datetime(2026, 11, 18, 9, 0), "Duplicada"))
    except CitaDuplicadaError as e:
        print(f"\n[EXCEPCIÓN CONTROLADA] {e}")

    at1 = Atencion("ATE-001", cita1, date(2026, 11, 18), "Paciente estable, presión 110/70.")
    at2 = Atencion("ATE-002", cita2, date(2026, 11, 18), "Faringitis leve, se receta paracetamol.")
    repo.registrar_atencion(at1)
    repo.registrar_atencion(at2)

    reporte = ReportePorPeriodoFactory().crear_reporte(date(2026, 11, 1), date(2026, 11, 30))
    resultado = reporte.generar_reporte(repo)

    print("\n--- Reporte Generado (Factory + Filter/Map/Reduce) ---")
    for k, v in resultado.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
from modelos_base import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import Reserva, SistemaGestionFJ
from excepciones import ErrorSistemaFJ, registrar_error, registrar_evento


def ejecutar_simulacion():
    sistema = SistemaGestionFJ()
    registrar_evento("=== INICIO DE SIMULACIÓN DEL SISTEMA SOFTWARE FJ ===")
    print("Iniciando simulación de operaciones en Software FJ...\n")

    
    try:
        c1 = Cliente("CLI-001", "Laura Martínez", "1045678901", "laura.martinez@correo.com", "3001234567")
    except ErrorSistemaFJ as e:
        registrar_error("Operación 1 fallida", e)
        print(f"[OP 1 - ERROR] {e}")
    else:
        sistema.registrar_cliente(c1)
        print(f"[OP 1 - ÉXITO] {c1.obtener_resumen()}") 
    try:
        c2 = Cliente("CLI-002", "Carlos Gómez", "1082993412", "cgomez@empresa.co", "3109876543")
        sistema.registrar_cliente(c2)
        print(f"[OP 2 - ÉXITO] {c2.obtener_resumen()}")
    except ErrorSistemaFJ as e:
        registrar_error("Operación 2 fallida", e)
        print(f"[OP 2 - ERROR] {e}")

   
    try:
        c_invalido = Cliente("CLI-003", "Ana", "123", "correo_sin_arroba.com", "3001112233")
        sistema.registrar_cliente(c_invalido)
    except ErrorSistemaFJ as e:
        registrar_error("Operación 3 (Prueba de validación cliente)", e)
        print(f"[OP 3 - CONTROLADO] Intento de cliente inválido bloqueado: {e}")
    try:
        s_sala = ReservaSala("SRV-101", "Sala Innovación Norte", 80000, capacidad_maxima=15, tiene_proyector=True)
        s_equipo = AlquilerEquipo("SRV-102", "Workstation Dell Precision", 35000, stock_disponible=5, gama="Ultra")
        s_asesoria = AsesoriaEspecializada("SRV-103", "Arquitectura Cloud AWS", 150000, "Cloud Computing", "Arquitecto")

        sistema.registrar_servicio(s_sala)
        sistema.registrar_servicio(s_equipo)
        sistema.registrar_servicio(s_asesoria)
        print("[OP 4 - ÉXITO] 3 servicios especializados creados y registrados.")
    except ErrorSistemaFJ as e:
        registrar_error("Operación 4 fallida", e)
        print(f"[OP 4 - ERROR] {e}")

    
    try:
        s_malo = AlquilerEquipo("SRV-104", "Servidor Rack", "tarifa_invalida", stock_disponible=2)
        sistema.registrar_servicio(s_malo)
    except ErrorSistemaFJ as e:
        registrar_error("Operación 5 (Prueba encadenamiento de excepciones)", e)
        print(f"[OP 5 - CONTROLADO] Error de tarifa detectado y encadenado: {e} (Causa: {type(e.__cause__).__name__})")

    
    try:
        r1 = Reserva("RES-001", c1, s_sala, duracion_horas=4, asistentes=10, usar_proyector=True)
        r1.confirmar(impuesto=0.19, descuento=0.10)  # Uso de parámetros opcionales (sobrecarga)
        r1.procesar()
        sistema.registrar_reserva(r1)
        print(f"[OP 6 - ÉXITO] {r1.obtener_resumen()}")
    except ErrorSistemaFJ as e:
        registrar_error("Operación 6 fallida", e)
        print(f"[OP 6 - ERROR] {e}")

    
    try:
        r_fallida_cap = Reserva("RES-002", c2, s_sala, duracion_horas=2, asistentes=25)
        sistema.registrar_reserva(r_fallida_cap)
    except ErrorSistemaFJ as e:
        registrar_error("Operación 7 (Capacidad excedida)", e)
        print(f"[OP 7 - CONTROLADO] Reserva rechazada por capacidad: {e}")

   
    try:
        r2 = Reserva("RES-003", c2, s_equipo, duracion_horas=5, cantidad=3, seguro_danos=True)
        r2.confirmar()  # Usa valores por defecto de impuesto (19%) y descuento (0%)
        sistema.registrar_reserva(r2)
        print(f"[OP 8 - ÉXITO] {r2.obtener_resumen()} | Stock restante: {s_equipo.stock_disponible}")
    except ErrorSistemaFJ as e:
        registrar_error("Operación 8 fallida", e)
        print(f"[OP 8 - ERROR] {e}")
    finally:
        print("   -> [FINALLY OP 8] Verificación de inventario ejecutada correctamente.")

    
    try:
        # Solo quedan 2 unidades en stock, se intentan pedir 4
        r_sin_stock = Reserva("RES-004", c1, s_equipo, duracion_horas=3, cantidad=4)
        sistema.registrar_reserva(r_sin_stock)
    except ErrorSistemaFJ as e:
        registrar_error("Operación 9 (Stock insuficiente)", e)
        print(f"[OP 9 - CONTROLADO] Reserva rechazada por inventario: {e}")

    
    try:
        r3 = Reserva("RES-005", c1, s_asesoria, duracion_horas=3)
        r3.confirmar(impuesto=0.0)  # Exento de IVA
        r3.cancelar()
        sistema.registrar_reserva(r3)
        print(f"[OP 10 - ÉXITO] Reserva creada y cancelada correctamente: {r3.obtener_resumen()}")
    except ErrorSistemaFJ as e:
        registrar_error("Operación 10 fallida", e)
        print(f"[OP 10 - ERROR] {e}")

    
    try:
        r3.procesar()
    except ErrorSistemaFJ as e:
        registrar_error("Operación 11 (Transición de estado inválida)", e)
        print(f"[OP 11 - CONTROLADO] Bloqueo de operación ilegal: {e}")

    
    try:
        r4 = Reserva("RES-006", c2, s_asesoria, duracion_horas=2)
        r4.confirmar(descuento=1.5)  # 150% de descuento -> inconsistente
    except ErrorSistemaFJ as e:
        registrar_error("Operación 12 (Cálculo financiero inconsistente)", e)
        print(f"[OP 12 - CONTROLADO] Cálculo bloqueado: {e}")

    # Mostrar estado final en memoria
    sistema.mostrar_reporte_general()
    registrar_evento("=== FIN DE SIMULACIÓN EXITOSA ===")
    print("Simulación finalizada sin interrupciones. Revisa el archivo 'sistema_fj.log' generado.")


if __name__ == "__main__":
    ejecutar_simulacion()
from modelos_base import EntidadSistema, Cliente
from servicios import Servicio, AlquilerEquipo
from excepciones import (
    DatoInvalidoError,
    ReservaInvalidaError,
    ErrorSistemaFJ,
    registrar_evento,
    registrar_error
)


class Reserva(EntidadSistema):
    """Integra un Cliente, un Servicio, la duración y el ciclo de vida de la reserva."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion_horas: int, **parametros_extra):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Se requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Se requiere una instancia válida de Servicio.")
        if not isinstance(duracion_horas, int) or duracion_horas <= 0:
            raise DatoInvalidoError("La duración en horas debe ser un número entero positivo.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion_horas = duracion_horas
        self.parametros_extra = parametros_extra
        self._estado = "PENDIENTE"
        self._costo_total = 0.0

        # Validar desde la creación si el servicio soporta los parámetros solicitados
        self.servicio.validar_parametros(self.duracion_horas, **self.parametros_extra)
        registrar_evento(f"Reserva {self.id_entidad} creada en estado PENDIENTE para {self.cliente.nombre}.")

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def confirmar(self, impuesto: float = 0.19, descuento: float = 0.0):
        """Calcula el costo final y cambia el estado a CONFIRMADA."""
        if self._estado != "PENDIENTE":
            raise ReservaInvalidaError(f"No se puede confirmar la reserva {self.id_entidad} porque está en estado {self._estado}.")

        try:
            self._costo_total = self.servicio.calcular_costo(
                self.duracion_horas,
                impuesto=impuesto,
                descuento=descuento,
                **self.parametros_extra
            )
            # Descontar stock si se trata de alquiler de equipos
            if isinstance(self.servicio, AlquilerEquipo):
                cantidad = self.parametros_extra.get("cantidad", 1)
                self.servicio.stock_disponible -= cantidad

            self._estado = "CONFIRMADA"
            registrar_evento(f"Reserva {self.id_entidad} CONFIRMADA. Total a pagar: ${self._costo_total:,.2f}")
        except ErrorSistemaFJ as e:
            # Encadenamiento de excepciones
            raise ReservaInvalidaError(f"Fallo al confirmar la reserva {self.id_entidad}.") from e

    def procesar(self):
        """Marca la reserva como ejecutada/procesada."""
        if self._estado != "CONFIRMADA":
            raise ReservaInvalidaError(
                f"Operación no permitida: la reserva {self.id_entidad} debe estar CONFIRMADA para procesarse (actual: {self._estado})."
            )
        self._estado = "PROCESADA"
        registrar_evento(f"Reserva {self.id_entidad} PROCESADA exitosamente.")

    def cancelar(self):
        """Cancela la reserva y restaura inventario si aplica."""
        if self._estado == "PROCESADA":
            raise ReservaInvalidaError(f"No es posible cancelar la reserva {self.id_entidad} porque ya fue PROCESADA.")
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError(f"La reserva {self.id_entidad} ya se encuentra CANCELADA.")

        if self._estado == "CONFIRMADA" and isinstance(self.servicio, AlquilerEquipo):
            cantidad = self.parametros_extra.get("cantidad", 1)
            self.servicio.stock_disponible += cantidad

        self._estado = "CANCELADA"
        registrar_evento(f"Reserva {self.id_entidad} CANCELADA por solicitud.")

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self.id_entidad}] | Estado: {self.estado} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} ({self.duracion_horas}h) | Total: ${self.costo_total:,.2f}"
        )


class SistemaGestionFJ:
    """Controlador central que administra clientes, servicios y reservas en memoria (listas)."""

    def __init__(self):
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []

    def registrar_cliente(self, cliente: Cliente):
        if any(c.id_entidad == cliente.id_entidad or c.documento == cliente.documento for c in self._clientes):
            raise DatoInvalidoError(f"Ya existe un cliente registrado con ID {cliente.id_entidad} o documento {cliente.documento}.")
        self._clientes.append(cliente)

    def registrar_servicio(self, servicio: Servicio):
        if any(s.id_entidad == servicio.id_entidad for s in self._servicios):
            raise DatoInvalidoError(f"Ya existe un servicio con el ID {servicio.id_entidad}.")
        self._servicios.append(servicio)

    def registrar_reserva(self, reserva: Reserva):
        if any(r.id_entidad == reserva.id_entidad for r in self._reservas):
            raise ReservaInvalidaError(f"Ya existe una reserva con el ID {reserva.id_entidad}.")
        self._reservas.append(reserva)

    def mostrar_reporte_general(self):
        print("\n" + "=" * 75)
        print("REPORTE GENERAL EN MEMORIA - SOFTWARE FJ")
        print("=" * 75)
        print(f"\n--- CLIENTES REGISTRADOS ({len(self._clientes)}) ---")
        for c in self._clientes:
            print("  •", c.obtener_resumen())

        print(f"\n--- SERVICIOS DISPONIBLES ({len(self._servicios)}) ---")
        for s in self._servicios:
            print("  •", s.obtener_resumen())

        print(f"\n--- RESERVAS REGISTRADAS ({len(self._reservas)}) ---")
        for r in self._reservas:
            print("  •", r.obtener_resumen())
        print("=" * 75 + "\n")
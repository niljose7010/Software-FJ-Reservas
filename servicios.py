from abc import abstractmethod
from modelos_base import EntidadSistema
from excepciones import (
    DatoInvalidoError,
    ServicioNoDisponibleError,
    CalculoInconsistenteError,
    registrar_evento
)


class Servicio(EntidadSistema):
    """Clase abstracta que modela un servicio ofrecido por Software FJ."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_servicio)
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self._disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 4:
            raise DatoInvalidoError("El nombre del servicio debe tener al menos 4 caracteres.")
        self._nombre = valor.strip()

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float):
        try:
            valor_float = float(valor)
        except (TypeError, ValueError) as e:
            # Encadenamiento de excepciones (raise ... from e)
            raise DatoInvalidoError("La tarifa base debe ser un valor numérico.") from e

        if valor_float <= 0:
            raise DatoInvalidoError("La tarifa base debe ser mayor a cero.")
        self._tarifa_base = valor_float

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool):
        if not isinstance(estado, bool):
            raise DatoInvalidoError("El estado de disponibilidad debe ser booleano (True/False).")
        self._disponible = estado

    @abstractmethod
    def validar_parametros(self, duracion_horas: int, **kwargs) -> bool:
        """Valida condiciones específicas de cada tipo de servicio."""
        pass

    @abstractmethod
    def calcular_costo(self, duracion_horas: int, impuesto: float = 0.19, descuento: float = 0.0, **kwargs) -> float:
        """
        Método polimórfico y sobrecargado mediante parámetros opcionales:
        - Puede llamarse solo con duracion_horas
        - Con impuesto personalizado
        - Con descuento aplicado
        - Con parámetros extra específicos de cada servicio (**kwargs)
        """
        pass

    def _aplicar_ajustes_financieros(self, subtotal: float, impuesto: float, descuento: float) -> float:
        """Aplica descuentos e impuestos validando consistencia financiera."""
        if not (0 <= descuento < 1):
            raise CalculoInconsistenteError("El descuento debe estar entre 0 (0%) y 0.99 (99%).")
        if impuesto < 0:
            raise CalculoInconsistenteError("El impuesto no puede ser negativo.")

        total = (subtotal * (1 - descuento)) * (1 + impuesto)
        if total <= 0:
            raise CalculoInconsistenteError("El costo total calculado resultó menor o igual a cero.")
        return round(total, 2)


class ReservaSala(Servicio):
    """Servicio especializado para alquiler de salas de reuniones o capacitación."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, capacidad_maxima: int, tiene_proyector: bool = True):
        super().__init__(id_servicio, nombre, tarifa_base)
        if capacidad_maxima <= 0:
            raise DatoInvalidoError("La capacidad máxima de la sala debe ser mayor a 0.")
        self.capacidad_maxima = capacidad_maxima
        self.tiene_proyector = tiene_proyector
        registrar_evento(f"Servicio ReservaSala creado: {self.nombre} (Capacidad: {self.capacidad_maxima})")

    def validar_parametros(self, duracion_horas: int, **kwargs) -> bool:
        asistentes = kwargs.get("asistentes", 1)
        if not self.disponible:
            raise ServicioNoDisponibleError(f"La sala '{self.nombre}' no se encuentra disponible.")
        if duracion_horas < 1 or duracion_horas > 12:
            raise DatoInvalidoError("La reserva de sala debe ser entre 1 y 12 horas.")
        if asistentes > self.capacidad_maxima:
            raise ServicioNoDisponibleError(
                f"Los {asistentes} asistentes superan la capacidad máxima ({self.capacidad_maxima}) de la sala."
            )
        return True

    def calcular_costo(self, duracion_horas: int, impuesto: float = 0.19, descuento: float = 0.0, **kwargs) -> float:
        self.validar_parametros(duracion_horas, **kwargs)
        subtotal = self.tarifa_base * duracion_horas
        # Recargo fijo por uso de proyector si se solicita y está disponible
        if kwargs.get("usar_proyector", False) and self.tiene_proyector:
            subtotal += 25000.0
        return self._aplicar_ajustes_financieros(subtotal, impuesto, descuento)

    def obtener_resumen(self) -> str:
        estado = "Disponible" if self.disponible else "Ocupada"
        return f"Sala [{self.id_entidad}]: {self.nombre} | Cap: {self.capacidad_maxima} pers. | ${self.tarifa_base:,.0f}/h | {estado}"


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de computadores, servidores o hardware."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, stock_disponible: int, gama: str = "Alta"):
        super().__init__(id_servicio, nombre, tarifa_base)
        if stock_disponible < 0:
            raise DatoInvalidoError("El stock inicial no puede ser negativo.")
        self.stock_disponible = stock_disponible
        self.gama = gama
        registrar_evento(f"Servicio AlquilerEquipo creado: {self.nombre} (Stock: {self.stock_disponible})")

    def validar_parametros(self, duracion_horas: int, **kwargs) -> bool:
        cantidad = kwargs.get("cantidad", 1)
        if not self.disponible or self.stock_disponible <= 0:
            raise ServicioNoDisponibleError(f"El equipo '{self.nombre}' no tiene unidades disponibles.")
        if cantidad <= 0 or cantidad > self.stock_disponible:
            raise ServicioNoDisponibleError(
                f"Cantidad solicitada ({cantidad}) inválida o superior al stock disponible ({self.stock_disponible})."
            )
        if duracion_horas < 2:
            raise DatoInvalidoError("El alquiler de equipos requiere un mínimo de 2 horas.")
        return True

    def calcular_costo(self, duracion_horas: int, impuesto: float = 0.19, descuento: float = 0.0, **kwargs) -> float:
        self.validar_parametros(duracion_horas, **kwargs)
        cantidad = kwargs.get("cantidad", 1)
        subtotal = self.tarifa_base * duracion_horas * cantidad
        # Seguro obligatorio por equipo si se solicita cobertura extendida
        if kwargs.get("seguro_danos", False):
            subtotal += 15000.0 * cantidad
        return self._aplicar_ajustes_financieros(subtotal, impuesto, descuento)

    def obtener_resumen(self) -> str:
        return f"Equipo [{self.id_entidad}]: {self.nombre} (Gama {self.gama}) | Stock: {self.stock_disponible} | ${self.tarifa_base:,.0f}/h"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado de consultoría en arquitectura de software, nube o datos."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, especialidad: str, nivel_consultor: str = "Senior"):
        super().__init__(id_servicio, nombre, tarifa_base)
        if not especialidad or len(especialidad.strip()) < 3:
            raise DatoInvalidoError("Debe especificar un área de especialidad válida.")
        self.especialidad = especialidad.strip()
        self.nivel_consultor = nivel_consultor
        registrar_evento(f"Servicio AsesoriaEspecializada creado: {self.nombre} ({self.especialidad})")

    def validar_parametros(self, duracion_horas: int, **kwargs) -> bool:
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El consultor de '{self.nombre}' no está disponible actualmente.")
        if duracion_horas < 1 or duracion_horas > 8:
            raise DatoInvalidoError("Las sesiones de asesoría deben durar entre 1 y 8 horas por día.")
        return True

    def calcular_costo(self, duracion_horas: int, impuesto: float = 0.19, descuento: float = 0.0, **kwargs) -> float:
        self.validar_parametros(duracion_horas, **kwargs)
        multiplicador = 1.3 if self.nivel_consultor.lower() == "arquitecto" else 1.0
        subtotal = (self.tarifa_base * multiplicador) * duracion_horas
        return self._aplicar_ajustes_financieros(subtotal, impuesto, descuento)

    def obtener_resumen(self) -> str:
        return f"Asesoría [{self.id_entidad}]: {self.nombre} ({self.especialidad} - {self.nivel_consultor}) | ${self.tarifa_base:,.0f}/h"
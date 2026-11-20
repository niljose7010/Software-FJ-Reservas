from abc import ABC, abstractmethod
from datetime import datetime
import re
from excepciones import DatoInvalidoError, registrar_evento


class EntidadSistema(ABC):
    """Clase abstracta base para todas las entidades del sistema Software FJ."""

    def __init__(self, id_entidad: str):
        self.id_entidad = id_entidad
        self._fecha_creacion = datetime.now()

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @id_entidad.setter
    def id_entidad(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El ID de la entidad debe ser un texto de al menos 3 caracteres.")
        self._id_entidad = valor.strip().upper()

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Método abstracto que obliga a las subclases a describirse."""
        pass


class Cliente(EntidadSistema):
    """Representa un cliente de Software FJ con encapsulación y validaciones."""

    def __init__(self, id_cliente: str, nombre: str, documento: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        registrar_evento(f"Cliente creado exitosamente: {self.nombre} (ID: {self.id_entidad})")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str):
        if not valor or not str(valor).isdigit() or not (6 <= len(str(valor)) <= 12):
            raise DatoInvalidoError("El documento debe contener únicamente entre 6 y 12 dígitos.")
        self._documento = str(valor)

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not valor or not re.match(patron, valor.strip()):
            raise DatoInvalidoError(f"El correo electrónico '{valor}' no tiene un formato válido.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not str(valor).isdigit() or len(str(valor)) < 7:
            raise DatoInvalidoError("El teléfono debe contener al menos 7 dígitos numéricos.")
        self._telefono = str(valor)

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id_entidad}]: {self.nombre} | Doc: {self.documento} | Correo: {self.correo}"
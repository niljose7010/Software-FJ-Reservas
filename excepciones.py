import logging
from datetime import datetime

# Configuración del archivo de logs para registrar eventos y errores
logging.basicConfig(
    filename="sistema_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

def registrar_evento(mensaje: str):
    """Registra una operación exitosa o evento informativo en el log."""
    logging.info(mensaje)

def registrar_error(mensaje: str, excepcion: Exception = None):
    """Registra un error y su causa original (si existe) en el log."""
    detalle = f"{mensaje}"
    if excepcion:
        detalle += f" | Causa: {type(excepcion).__name__}: {excepcion}"
        if excepcion.__cause__:
            detalle += f" -> Encadenada de: {type(excepcion.__cause__).__name__}: {excepcion.__cause__}"
    logging.error(detalle)


# --- EXCEPCIONES PERSONALIZADAS ---

class ErrorSistemaFJ(Exception):
    """Excepción base para todos los errores del sistema Software FJ."""
    pass

class DatoInvalidoError(ErrorSistemaFJ):
    """Se lanza cuando los datos ingresados no cumplen con el formato o reglas."""
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando un servicio no está activo o no cumple capacidad/requisitos."""
    pass

class ReservaInvalidaError(ErrorSistemaFJ):
    """Se lanza ante operaciones no permitidas o inconsistencias en una reserva."""
    pass

class CalculoInconsistenteError(ErrorSistemaFJ):
    """Se lanza cuando un cálculo financiero arroja valores negativos o ilógicos."""
    pass
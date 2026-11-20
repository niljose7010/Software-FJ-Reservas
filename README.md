# Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ

Proyecto desarrollado en Python aplicando Programación Orientada a Objetos (POO) y manejo avanzado de excepciones sin uso de bases de datos.

## Estructura del Proyecto
- `excepciones.py`: Jerarquía de excepciones personalizadas y registro de logs en `sistema_fj.log`.
- `modelos_base.py`: Clase abstracta `EntidadSistema` y clase `Cliente` con encapsulación.
- `servicios.py`: Clase abstracta `Servicio` y clases derivadas (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`).
- `reservas.py`: Clase `Reserva` y controlador en memoria `SistemaGestionFJ`.
- `main.py`: Simulación secuencial de 12 operaciones (válidas e inválidas).

## Ejecución
```bash
python main.py
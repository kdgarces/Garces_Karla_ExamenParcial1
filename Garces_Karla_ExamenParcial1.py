from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


# --------------------------------------------------
# MODELOS PARA VALIDAR LAS ENTRADAS
# --------------------------------------------------

class CantidadOperacion(BaseModel):
    """Valida que una cantidad monetaria sea mayor que cero."""

    cantidad: float = Field(gt=0)


class SolicitudRetiro(CantidadOperacion):
    """Valida la cantidad y los fondos disponibles para un retiro."""

    saldo_disponible: float = Field(ge=0)

    @model_validator(mode="after")
    def validar_fondos(self):
        if self.cantidad > self.saldo_disponible:
            raise ValueError("Fondos insuficientes.")

        return self


class SolicitudRetiroCorriente(SolicitudRetiro):
    """Añade la validación del límite de una cuenta corriente."""

    limite_retiro: float = Field(gt=0)

    @model_validator(mode="after")
    def validar_limite(self):
        if self.cantidad > self.limite_retiro:
            raise ValueError(
                "La cantidad supera el límite permitido por retiro."
            )

        return self


class SeleccionTipoCuenta(BaseModel):
    opcion: Literal["1", "2"]


class SeleccionMenu(BaseModel):
    opcion: Literal["1", "2", "3", "4", "5", "6"]


class RespuestaContinuar(BaseModel):
    respuesta: Literal["si", "sí", "no"]

    @field_validator("respuesta", mode="before")
    @classmethod
    def preparar_respuesta(cls, respuesta):
        if isinstance(respuesta, str):
            return respuesta.strip().lower()

        return respuesta


# --------------------------------------------------
# CLASE ABSTRACTA CUENTA BANCARIA
# --------------------------------------------------

class CuentaBancaria(BaseModel, ABC):
    """Clase base que comparte el estado y las operaciones de las cuentas.

    No puede instanciarse directamente. Cada subclase debe definir sus
    propias reglas de retiro y su procesamiento mensual.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    numero_cuenta: str = Field(min_length=4)
    tipo_cuenta: str
    saldo: float = Field(default=0.0, ge=0)
    transacciones: list[Transaccion] = Field(default_factory=list)

    @field_validator("numero_cuenta")
    @classmethod
    def validar_numero_cuenta(cls, numero):
        if not numero.isdigit():
            raise ValueError(
                "El número de cuenta solamente debe contener números."
            )

        return numero

    def model_post_init(self, contexto: Any):
        if self.saldo > 0 and not self.transacciones:
            self.registrar_transaccion("Depósito inicial", self.saldo)

    def depositar(self, cantidad) -> bool:
        operacion = CantidadOperacion(cantidad=cantidad)
        self.saldo += operacion.cantidad
        self.registrar_transaccion("Depósito", operacion.cantidad)

        print(f"Depósito realizado: ${operacion.cantidad:.2f}")
        return True

    @abstractmethod
    def retirar(self, cantidad) -> bool:
        """Retira dinero aplicando las reglas de la subclase."""
        pass

    @abstractmethod
    def procesar_fin_de_mes(self) -> bool:
        """Ejecuta el comportamiento mensual propio de cada cuenta."""
        pass

    def completar_retiro(self, cantidad: float):
        self.saldo -= cantidad
        self.registrar_transaccion("Retiro", cantidad)
        print(f"Retiro realizado: ${cantidad:.2f}")

    def consultar_saldo(self):
        print(f"Saldo disponible: ${self.saldo:.2f}")

    def registrar_transaccion(self, tipo: str, cantidad: float):
        nueva_transaccion = Transaccion(tipo=tipo, cantidad=cantidad)
        self.transacciones.append(nueva_transaccion)

    def mostrar_historial(self):
        print(f"\nHistorial de la cuenta {self.numero_cuenta}:")

        if not self.transacciones:
            print("No hay transacciones registradas.")
            return

        for transaccion in self.transacciones:
            transaccion.mostrar_detalle()


# --------------------------------------------------
# CLASE CUENTA DE AHORROS
# --------------------------------------------------

class CuentaAhorros(CuentaBancaria):
    tipo_cuenta: Literal["Ahorros"] = "Ahorros"
    tasa_interes: float = Field(default=0.02, gt=0, le=1)

    def retirar(self, cantidad) -> bool:
        solicitud = SolicitudRetiro(
            cantidad=cantidad,
            saldo_disponible=self.saldo,
        )

        self.completar_retiro(solicitud.cantidad)
        return True

    def procesar_fin_de_mes(self) -> bool:
        if self.saldo == 0:
            print("No se puede aplicar interés a un saldo de cero.")
            return False

        interes = self.saldo * self.tasa_interes
        self.saldo += interes
        self.registrar_transaccion("Interés aplicado", interes)

        print(f"Interés agregado: ${interes:.2f}")
        return True


# --------------------------------------------------
# CLASE CUENTA CORRIENTE
# --------------------------------------------------

class CuentaCorriente(CuentaBancaria):
    tipo_cuenta: Literal["Corriente"] = "Corriente"
    limite_retiro: float = Field(default=1000.0, gt=0)
    comision_mensual: float = Field(default=5.0, gt=0)

    def retirar(self, cantidad) -> bool:
        solicitud = SolicitudRetiroCorriente(
            cantidad=cantidad,
            saldo_disponible=self.saldo,
            limite_retiro=self.limite_retiro,
        )

        self.completar_retiro(solicitud.cantidad)
        return True

    def procesar_fin_de_mes(self) -> bool:
        if self.saldo < self.comision_mensual:
            print("Saldo insuficiente para cobrar la comisión mensual.")
            return False

        self.saldo -= self.comision_mensual
        self.registrar_transaccion(
            "Comisión mensual",
            self.comision_mensual,
        )

        print(f"Comisión cobrada: ${self.comision_mensual:.2f}")
        return True


# --------------------------------------------------
# CLASE CLIENTE
# --------------------------------------------------

class Cliente(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=2)
    identificacion: str = Field(min_length=4)
    cuentas: list[CuentaBancaria] = Field(default_factory=list)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, nombre):
        nombre_sin_espacios = nombre.replace(" ", "")

        if not nombre_sin_espacios.isalpha():
            raise ValueError("El nombre solamente debe contener letras.")

        return nombre.title()

    @field_validator("identificacion")
    @classmethod
    def validar_identificacion(cls, identificacion):
        if not identificacion.isdigit():
            raise ValueError(
                "La identificación solamente debe contener números."
            )

        return identificacion

    def agregar_cuenta(self, cuenta: CuentaBancaria):
        self.cuentas.append(cuenta)

        print(
            f"La cuenta {cuenta.numero_cuenta} fue agregada "
            f"al cliente {self.nombre}."
        )

    def mostrar_cuentas(self):
        print(f"\nCuentas de {self.nombre}:")

        if not self.cuentas:
            print("El cliente no tiene cuentas registradas.")
            return

        for cuenta in self.cuentas:
            print(
                f"Número: {cuenta.numero_cuenta} | "
                f"Tipo: {cuenta.tipo_cuenta} | "
                f"Saldo: ${cuenta.saldo:.2f}"
            )


# --------------------------------------------------
# CLASE TRANSACCIÓN
# --------------------------------------------------

class Transaccion(BaseModel):
    tipo: str = Field(min_length=2)
    cantidad: float = Field(gt=0)
    fecha: datetime = Field(default_factory=datetime.now)

    def mostrar_detalle(self):
        print(
            f"{self.fecha.strftime('%d/%m/%Y %H:%M:%S')} | "
            f"{self.tipo} | ${self.cantidad:.2f}"
        )

# --------------------------------------------------
# FUNCIÓN PARA MOSTRAR ERRORES DE PYDANTIC
# --------------------------------------------------

def mostrar_error_validacion(error: ValidationError):
    primer_error = error.errors()[0]
    mensaje = primer_error["msg"]
    print(f"Error de validación: {mensaje}")


# --------------------------------------------------
# PROGRAMA PRINCIPAL
# --------------------------------------------------

def main():
    print("=== SISTEMA BANCARIO ===")

    print("\n--- REGISTRO DEL CLIENTE ---")

    try:
        cliente = Cliente(
            nombre=input("Ingrese el nombre del cliente: "),
            identificacion=input("Ingrese la identificación: "),
        )
    except ValidationError as error:
        mostrar_error_validacion(error)
        print("No se pudo registrar el cliente.")
        return

    print("\n--- CREACIÓN DE LA CUENTA ---")
    print("1. Cuenta de ahorros")
    print("2. Cuenta corriente")

    try:
        seleccion = SeleccionTipoCuenta(
            opcion=input("Seleccione el tipo de cuenta: ")
        )

        numero_cuenta = input("Ingrese el número de cuenta: ")
        saldo_inicial = input("Ingrese el saldo inicial: $")

        if seleccion.opcion == "1":
            cuenta: CuentaBancaria = CuentaAhorros(
                numero_cuenta=numero_cuenta,
                saldo=saldo_inicial,
            )
        else:
            cuenta = CuentaCorriente(
                numero_cuenta=numero_cuenta,
                saldo=saldo_inicial,
            )
    except ValidationError as error:
        mostrar_error_validacion(error)
        print("No se pudo crear la cuenta.")
        return

    cliente.agregar_cuenta(cuenta)
    continuar = True

    while continuar:
        print("\n=== MENÚ DE OPERACIONES ===")
        print("1. Depositar")
        print("2. Retirar")
        print("3. Consultar saldo")
        print("4. Mostrar historial")
        print("5. Procesar fin de mes")
        print("6. Mostrar información del cliente")

        try:
            seleccion_menu = SeleccionMenu(
                opcion=input("Seleccione una opción: ")
            )

            opcion = seleccion_menu.opcion

            if opcion == "1":
                cuenta.depositar(
                    input("Cantidad que desea depositar: $")
                )
            elif opcion == "2":
                # Llamada polimórfica: Python ejecuta el método de la
                # subclase real sin preguntar qué tipo de cuenta es.
                cuenta.retirar(
                    input("Cantidad que desea retirar: $")
                )
            elif opcion == "3":
                cuenta.consultar_saldo()
            elif opcion == "4":
                cuenta.mostrar_historial()
            elif opcion == "5":
                # La misma llamada aplica interés en ahorros o cobra una
                # comisión en corriente, según el objeto real.
                cuenta.procesar_fin_de_mes()
            elif opcion == "6":
                print(f"\nNombre: {cliente.nombre}")
                print(f"Identificación: {cliente.identificacion}")
                cliente.mostrar_cuentas()

        except ValidationError as error:
            mostrar_error_validacion(error)

        try:
            respuesta = RespuestaContinuar(
                respuesta=input(
                    "\n¿Desea realizar otra transacción? (sí/no): "
                )
            )
            continuar = respuesta.respuesta in ("si", "sí")
        except ValidationError as error:
            mostrar_error_validacion(error)
            continuar = False

    print("\nGracias por utilizar el sistema bancario.")


if __name__ == "__main__":
    main()

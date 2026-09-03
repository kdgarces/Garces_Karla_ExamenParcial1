## Descripción
Este proyecto consiste en la creación de un sistema bancario que permite registrar clientes, con sus respectivas cuentas de ahorros o corrientes y realizar operaciones bancarias básicas mediante un menú interactivo. El sistema aplica conceptos de programación orientada a objetos, como encapsulación, herencia, composición, clases abstractas, sobrescritura de métodos y polimorfismo. También utiliza Pydantic para validar los datos ingresados por el usuario.

## Objetivo del proyecto
Desarrollar una aplicación bancaria funcional que permita administrar clientes, cuentas y transacciones mediante el uso de clases abstractas para establecer una estructura común, herencia para crear cuentas especializadas y polimorfismo para ejecutar comportamientos diferentes según el tipo real de cuenta, incorporando validaciones que garanticen el manejo adecuado de los datos y las operaciones bancarias.

## Principales funcionalidades
- Registrar y validar los datos del cliente.
- Crear una cuenta de ahorros o una cuenta corriente.
- Registrar automáticamente el saldo inicial.
- Realizar depósitos y retiros.
- Validar cantidades positivas y fondos disponibles.
- Controlar el límite máximo por retiro de las cuentas corrientes.
- Consultar el saldo disponible.
- Mostrar el historial de transacciones con fecha y hora.
- Aplicar un interés mensual del 2 % a las cuentas de ahorros.
- Cobrar una comisión mensual de $5 a las cuentas corrientes.
- Mostrar la información del cliente y de su cuenta.
- Permitir la realización de varias operaciones mediante un menú interactivo.
- Informar al usuario cuando ingresa datos inválidos o intenta realizar una operación no permitida.

## Estructura del sistema
* CuentaBancaria: Clase abstracta que contiene los atributos y comportamientos compartidos por todas las cuentas. Define como métodos abstractos retirar() y procesar_fin_de_mes().
* CuentaAhorros: Hereda de CuentaBancaria. Permite retirar dinero cuando existen fondos suficientes y aplica un interés mensual del 2 %.
* CuentaCorriente: Hereda de CuentaBancaria. Valida los fondos y el límite máximo permitido por retiro. Durante el procesamiento mensual cobra una comisión de $5.
* Cliente: Almacena el nombre, la identificación y las cuentas asociadas al cliente.
* Transaccion: Representa cada movimiento realizado en una cuenta y registra el tipo, la cantidad, la fecha y la hora.
* Modelos de validación: Las clases CantidadOperacion, SolicitudRetiro y SolicitudRetiroCorriente validan las cantidades, los fondos disponibles y el límite de retiro. Otros modelos comprueban las opciones seleccionadas en el menú.
* Polimorfismo: Se demuestra mediante los métodos retirar() y procesar_fin_de_mes(). El programa utiliza las mismas llamadas:
  cuenta.retirar(cantidad)
  cuenta.procesar_fin_de_mes()
  Se ejecuta automáticamente la implementación correspondiente al tipo real del objeto. En una cuenta de ahorros, el procesamiento mensual agrega     intereses; en una cuenta corriente, cobra una comisión.

## Instrucciones para ejecutar el programa 
1. Descargar los archivos del repositorio o clonar el proyecto.
2. Verificar que Python 3.10 o una versión posterior esté instalado.
3. Abrir una terminal en la carpeta donde se encuentra el proyecto.
4. Instalar Pydantic versión 2 con el siguiente comando:
`python -m pip install "pydantic>=2,<3` 
5. Ejecutar el programa con el siguiente comando:
`python SistemaBancarioSemana3.py`
6. Seguir las instrucciones del menú para registrar un cliente, crear una cuenta y realizar operaciones bancarias.

## Ejemplos de funcionamiento

- Cuenta de ahorros

Saldo inicial: $1,000.

Retiro: $100.

Saldo después del retiro: $900.

Interés mensual del 2 %: $18.

Saldo final: $918.

- Cuenta corriente

Saldo inicial: $1,000.

Comisión mensual: $5.

Saldo después de la comisión: $995.

Un retiro superior a $1,000 es rechazado por superar el límite permitido.

## Lenguaje

Python.


## Estudiante: Karla D. Garcés

Proyecto académico desarrollado para la asignatura Programación Estructurada.


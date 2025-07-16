# Robotica 2025 I  Laboratorio No. 4
***Cinemática Directa - Phantom X - ROS***

Andrés Felipe Quenan Pozo - `aquenan@unal.edu.co`
***
# Introducción
El presente laboratorio tiene como propósito aplicar los conceptos de cinemática directa al brazo robótico Phantom X Pincher mediante ROS 2, integrando teoría y práctica en el modelado y control de manipuladores. A través de la identificación de parámetros Denavit-Hartenberg, el desarrollo de scripts en Python y la implementación de una interfaz gráfica, se busca controlar el movimiento secuencial de las articulaciones, visualizar sus posiciones en tiempo real y familiarizar al estudiante con la arquitectura y operación de un sistema robótico basado en ROS.

# Objetivos

* Identificar las longitudes de eslabón y establecer los parámetros DH del robot.
* Configurar los controladores articulares del Phantom X Pincher en ROS 2.
* Desarrollar un script en Python que permita mover el robot desde la posición “home” hasta una posición objetivo de forma secuencial.
* Leer y mostrar las posiciones actuales de las articulaciones en grados.
* Crear una interfaz gráfica para el control y visualización del estado del robot

# Desarrollo

## Mediciones
Se establecieron los eslabones, las articulaciones y posteriormente se establecieron las longitudes de eslabón para cada articulación del robot Phantom X Pincher utilizando un calibrador.

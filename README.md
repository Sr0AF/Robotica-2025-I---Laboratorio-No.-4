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

<img width="1080" height="1500" alt="Agregar algo de texto" src="https://github.com/user-attachments/assets/908c1782-be73-4999-83a2-8d9f61bfa204" />

## Análisis
A partir del anterior diagrama se obtuvieron los parámetros DH del robot Phantom X Pincher.
   | i | θi | di | ai | α |
   | :---         |     :---:      |          :---: |          :---: |          :---: |
   | 1 | q1 | 113 | 0 | π/2 |
   | 2 | q2 | 0 | 100.7 | 0 |
   | 3 | q3 | 0 | 100.7 | 0 |
   | 4 | q4 | 0 | 85 | π/2 |
   
Cada uno de los servomotores que componen el robot, tienen un rango de -150° a 150° que se obtienen a partir de la posición en bits definida previamente ya que el rango consta de 0 a 1023 bits.

## ROS 2
La función `move_sequential` que se muestra a continuación está diseñada para ejecutar un movimiento ordenado, donde cada articulación del robot Phantom X Pincher se desplaza una tras otra hacia su posición objetivo. El proceso comienza convirtiendo los valores de entrada, expresados en grados, a valores en bits utilizando la fórmula de conversión específica para los servos Dynamixel. Luego, mediante un bucle, se envía el comando de posición a cada motor individualmente usando su identificador (`dxl_id`) y el valor objetivo convertido. Después de mover cada articulación, se genera una pausa controlada con `time.sleep()`, permitiendo que el movimiento sea claramente visible antes de que inicie el siguiente.

```
def move_sequential(self, degrees):
    bits = [deg_to_bits(d) for d in degrees]  # Convertir grados a bits
    for dxl_id, goal, deg in zip(self.dxl_ids, bits, degrees):
        self.packet.write2ByteTxRx(self.port, dxl_id, ADDR_GOAL_POSITION, goal)  # Enviar comando
        self.get_logger().info(f"ID {dxl_id} → {deg}° ({goal} bits)")           # Mostrar en consola
        time.sleep(self.delay)  # Espera para que se vea el movimiento secuencial
```

El diagrama de flujo se muestra a continuación:

```mermaid
flowchart TD
    A(["Inicio"]) --> C["Recibir ángulos (°)"]
    C --> n1["Convertir ángulo a bits"]
    n1 --> n3["dxl_id = 1"]
    n3 --> n2["Enviar posición deseada"]
    n2 --> n5["Imprimir en consola:<br>ID X -&gt; N° Grados (Bits)"]
    n5 --> n4["Esperar delay de 2 seg"]
    n4 --> n6["dxl_id = 5"]
    n6 -- NO --> n8["dxl_id + 1"]
    n8 --> n2
    n6 -- SI --> n9(["FIN"])
    n1@{ shape: rect}
    n2@{ shape: rect}
    n4@{ shape: rect}
    n6@{ shape: diam}

```
## Conexión con Python

### Publicar en cada tópico de controlador validando límites articulares

El código encargado de publicar en cada tópico de controlador de articulación tiene como objetivo enviar comandos de movimiento a cada uno de los motores del robot, asegurando que dichos movimientos estén dentro de los límites articulares permitidos. Antes de publicar los valores convertidos en bits (a partir de grados ingresados), se realiza una validación para garantizar que los ángulos deseados no excedan el rango físico de operación de cada articulación.

La función `move_to_position` actua como publisher ya que publica los movimientos que deben realizar los servomotores, esto mediante el comando `write2ByteTxRx` que toma como parámetros el puerto, el ID del servomotor y la posición en bits.

```
def move_to_position(self, degrees):
    bits = [deg_to_bits(d) for d in degrees]
    for dxl_id, goal in zip(self.dxl_ids, bits):
        self.packet.write2ByteTxRx(self.port, dxl_id, ADDR_GOAL_POSITION, goal)
        time.sleep(self.delay)
```

EL diagrama de flujo se muestra a continuación:
```mermaid
flowchart TD
    A(["Inicio"]) --> C["Recibir ángulos (°)"]
    C --> D["Convertir ° a bits"]
    D --> n1["-150° &lt;= Grados &lt;= 150°"]
    n1 -- SI --> n2["Publicar en tópico<br>de servomotor"]
    n1 -- NO --> n3["Mostrar error"]
    n2 --> n4["Esperar delay de 2 seg"]
    n4 --> n5(["FIN"])
    n1@{ shape: diam}
    n2@{ shape: rect}
    n3@{ shape: rect}
``` 

### Suscribirse y retornar la configuración de 5 ángulos en grados
El código se encarga de suscribirse a los tópicos de estado de cada articulación y extraer la posición actual de los servos. Esta información, obtenida en bits, se convierte a grados utilizando una función específica y luego se presenta de forma comprensible. Esta funcionalidad es útil para conocer en tiempo real la configuración articular del robot.

La función `read_positions` funciona como suscriptor ya que crea un arreglo de posiciones mediante el comando `read2ByteTxRx` que recibe como parámetros el puerto, el ID del servomotor y la posición actual de los servomotores.

```
def read_positions(self):
    positions = []
    for dxl_id in self.dxl_ids:
        pos, _, _ = self.packet.read2ByteTxRx(self.port, dxl_id, ADDR_PRESENT_POSITION)
        deg = bits_to_deg(pos)
        positions.append(deg)
    return positions
```

Luego mediante la función `show_positions` imprime en consola las posiciones obtenidas mediante el anterior código

```
def show_positions(self):
    posiciones = self.read_positions()
    texto = " | ".join([f"Servo {i+1}: {p}°" for i, p in enumerate(posiciones)])
    self.label_posiciones.config(text=texto)
```
El diagrama de flujo se observa a continuación:

```mermaid
flowchart TD
    A(["INICIO"]) --> C["Leer posición en bits<br>de cada servomotor"]
    C --> D["Convertir bits a °"]
    D --> n1["Almacenar los<br>5 ángulos"]
    n1 --> n2["Retornar ángulos en °"]
    n2 --> n3(["FIN"])
```
### Control de posiciones por interfaz de usuario

El código implementa una interfaz gráfica en Tkinter que permite controlar el manipulador Phantom X Pincher de dos maneras: mediante botones de posiciones predefinidas y por entrada manual de ángulos. Las posiciones predefinidas (como "Home", "Pos A", etc.) están asociadas a valores específicos de ángulos en grados para cada una de las cinco articulaciones del brazo.

```
self.positions = {
    'Home': [0, 30, -30, 45, 0],
    'Pos A': [20, -10, 45, 10, 15],
    'Pos B': [-45, 20, 10, -20, 30],
    'Pos C': [10, 10, 10, 10, 10],
    'Pos D': [-20, -30, 30, -10, -10]
```
Los movimientos a una posición se realizan mediante la función `move_to_position` y se controlan con botones vinculados a cada arreglo de posiciones mediante el siguiente código.

```
for name, pos in self.positions.items():
    if name == 'Home':
        Button(self.window, text=name, width=30, bg="#d1e7dd",
               command=lambda p=pos: self.move_sequential(p)).pack(pady=4)
    else:
        Button(self.window, text=name, width=30, bg="#e2e3e5",
               command=lambda p=pos: self.move_to_position(p)).pack(pady=4)

```

Al hacer clic en uno de estos botones, el robot se mueve a esa configuración, y si es la posición "Home", el movimiento se realiza de manera secuencial desde la base hasta la muñeca. 

Además, la interfaz presenta cinco campos donde el usuario puede ingresar manualmente ángulos específicos para cada articulación, y al presionar el botón correspondiente, esos valores son convertidos a bits y enviados a los motores para ejecutar el movimiento mediante el siguiente código.

```
self.entries = []
entry_frame = Frame(self.window, bg="#f0f0f0")
entry_frame.pack()
for i in range(5):
    Label(entry_frame, text=f"Servo {i+1}", bg="#f0f0f0").grid(row=i, column=0, padx=5, pady=2)
    e = Entry(entry_frame)
    e.grid(row=i, column=1, padx=5, pady=2)
    self.entries.append(e)
```

EL diagrama de flujo se muestra a continuación.

```mermaid
flowchart TD
    A(["INICIO"]) --> C["Iniciar interfaz"]
    C --> n4["Botón presionado<br>es HOME"]
    n4 -- SI --> n6["Movimiento secuencial"]
    n4 -- NO --> n8["Movimiento inmediato"]
    n6 --> n9@{ label: "Botón presionado es<br style=\"--tw-scale-x:\">Leer posiciones" }
    n8 --> n9
    n9 -- SI --> n5["Actualizar e imprimir<br>las posiciones"]
    n5 --> n11["Ingresar posiciones<br>manualmente"]
    n9 -- NO --> n11
    n11 --> n12["Botón presionado<br>es Mover manualmente"]
    n12 -- SI --> n13["Movimiento inmediato"]
    n13 --> n3(["FIN"])
    n12 -- NO --> n4
    n4@{ shape: diam}
    n6@{ shape: subproc}
    n8@{ shape: subproc}
    n9@{ shape: decision}
    n12@{ shape: decision}
    n13@{ shape: subproc}
```

## Pruebas de Funcionamiento





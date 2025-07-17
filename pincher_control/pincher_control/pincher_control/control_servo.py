# ===== Script Unificado: control_robot.py =====
# Este script combina el movimiento secuencial, la publicación de límites,
# la lectura de posiciones y una interfaz gráfica para controlar el robot Phantom X Pincher.

import rclpy
from rclpy.node import Node
from tkinter import Tk, Button, Label, Entry, PhotoImage
import time
from dynamixel_sdk import PortHandler, PacketHandler
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "logo.png")

# Direcciones del AX-12A
ADDR_TORQUE_ENABLE = 24
ADDR_GOAL_POSITION = 30
ADDR_MOVING_SPEED = 32
ADDR_TORQUE_LIMIT = 34
ADDR_PRESENT_POSITION = 36

# Funciones de conversión
def bits_to_deg(bits):
    return round(((bits - 512) / 511)*150 , 1)

def deg_to_bits(deg):
    return int((deg/150) * 511 + 512)

class ControlRobot(Node):
    def __init__(self):
        super().__init__('control_robot')
        self.dxl_ids = [1, 2, 3, 4, 5]
        self.port_name = '/dev/ttyUSB0'
        self.baudrate = 1000000
        self.torque_limit = 1000
        self.speed = 100
        self.delay = 2.0

        # Inicializar puerto y paquete
        self.port = PortHandler(self.port_name)
        self.packet = PacketHandler(1.0)

        if not self.port.openPort() or not self.port.setBaudRate(self.baudrate):
            self.get_logger().error("Error al abrir o configurar el puerto.")
            rclpy.shutdown()
            return

        for dxl_id in self.dxl_ids:
            self.packet.write2ByteTxRx(self.port, dxl_id, ADDR_TORQUE_LIMIT, self.torque_limit)
            self.packet.write2ByteTxRx(self.port, dxl_id, ADDR_MOVING_SPEED, self.speed)
            self.packet.write1ByteTxRx(self.port, dxl_id, ADDR_TORQUE_ENABLE, 1)

        self.positions = {
            'Home': [0, 0, 0, 0, 0],
            'Pos A': [25, 25, 20, -20, 0],
            'Pos B': [-35, 35, -30, 30, 0],
            'Pos C': [85, -20, 55, 25, 0],
            'Pos D': [80, -35, 55, -45, 0]
        }

        self.create_gui()

    def move_to_position(self, degrees):
        bits = [deg_to_bits(d) for d in degrees]
        for dxl_id, goal in zip(self.dxl_ids, bits):
            self.packet.write2ByteTxRx(self.port, dxl_id, ADDR_GOAL_POSITION, goal)
            time.sleep(self.delay)
        self.get_logger().info(f"Movido a: {degrees} grados")

    def move_sequential(self, degrees):
        bits = [deg_to_bits(d) for d in degrees]
        for dxl_id, goal, deg in zip(self.dxl_ids, bits, degrees):
            self.packet.write2ByteTxRx(self.port, dxl_id, ADDR_GOAL_POSITION, goal)
            self.get_logger().info(f"ID {dxl_id} → {deg}° ({goal} bits)")
            time.sleep(self.delay)

    def read_positions(self):
        positions = []
        for dxl_id in self.dxl_ids:
            pos, _, _ = self.packet.read2ByteTxRx(self.port, dxl_id, ADDR_PRESENT_POSITION)
            deg = bits_to_deg(pos)
            positions.append(deg)
        return positions

    def create_gui(self):
        self.window = Tk()
        self.window.title("Control Phantom X Pincher")
        self.window.geometry("1920x1080")

        Label(self.window, text="Selecciona una posición:", font=("Arial", 12)).pack(pady=10)
        for name, pos in self.positions.items():
            if name == 'Home':
                Button(self.window, text=name, width=25,
                       command=lambda p=pos: self.move_sequential(p)).pack(pady=5)
            else:
                Button(self.window, text=name, width=25,
                       command=lambda p=pos: self.move_to_position(p)).pack(pady=5)

        Label(self.window, text="\nControl manual (grados):", font=("Arial", 12, "bold")).pack(pady=10)
        self.entries = []
        for i in range(5):
            Label(self.window, text=f"Servo {i+1}").pack()
            e = Entry(self.window)
            e.pack()
            self.entries.append(e)

        Button(self.window, text="Mover manualmente", command=self.move_manual).pack(pady=10)
        Button(self.window, text="Leer posiciones", command=self.show_positions).pack(pady=10)

        self.window.mainloop()

    def move_manual(self):
        try:
            grados = [float(e.get()) for e in self.entries]
            self.move_to_position(grados)
        except ValueError:
            self.get_logger().error("¡Entrada inválida en campos manuales!")

    def show_positions(self):
        posiciones = self.read_positions()
        for i, p in enumerate(posiciones):
            Label(self.window, text=f"Servo {i+1} = {p}°").pack()


def main(args=None):
    rclpy.init(args=args)
    app = ControlRobot()
    rclpy.shutdown()

if __name__ == '__main__':
    main()



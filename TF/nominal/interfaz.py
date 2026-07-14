import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import os

# -----------------------------
# Rutas
# -----------------------------
#sustituir rutas correctas
NS3_DIR = "/home/*/ns-3-dev"

ANIMATION_SCRIPT = "/home/*/animacion.py"

# -----------------------------
# Ejecutar simulación
# -----------------------------

def run_simulation():

    button.config(state="disabled")
    status["text"] = "Ejecutando simulación..."

    numDrones = num_drones.get()
    simTime = sim_time.get()
    speed = drone_speed.get()
    height = drone_height.get()

    freq = frequency.get()
    bw = bandwidth.get()
    mu = numerology.get()
    power = tx_power.get()

    command = f'''
    ./ns3 run "drone-video-demo \
    --droneNumPergNb={numDrones} \
    --simTime={simTime} \
    --speed={speed} \
    --height={height} \
    --frequency={freq} \
    --bandwidth={bw} \
    --numerology={mu} \
    --txPower={power}"
    '''

    subprocess.run(
        command,
        shell=True,
        cwd=NS3_DIR
    )

    status["text"] = "Mostrando animación..."

    subprocess.run(
        ["python3", ANIMATION_SCRIPT]
    )

    button.config(state="normal")
    status["text"] = "Finalizado"

# -----------------------------
# hilo
# -----------------------------

def start():

    threading.Thread(
        target=run_simulation,
        daemon=True
    ).start()

# -----------------------------
# GUI
# -----------------------------

root = tk.Tk()

root.title("5G Drone Simulator")

frame = ttk.Frame(root,padding=15)
frame.pack()

# -----------------------------
# Variables
# -----------------------------

num_drones = tk.IntVar(value=2)

sim_time = tk.DoubleVar(value=10)

drone_speed = tk.DoubleVar(value=8)

drone_height = tk.DoubleVar(value=50)

frequency = tk.DoubleVar(value=3.5e9)

bandwidth = tk.DoubleVar(value=100e6)

numerology = tk.IntVar(value=1)

tx_power = tk.DoubleVar(value=35)

# -----------------------------
# Widgets
# -----------------------------

row=0

ttk.Label(frame,text="Número de drones").grid(row=row,column=0,sticky="w")
ttk.Entry(frame,textvariable=num_drones,width=12).grid(row=row,column=1)

row+=1

ttk.Label(frame,text="Tiempo simulación (s)").grid(row=row,column=0,sticky="w")
ttk.Entry(frame,textvariable=sim_time,width=12).grid(row=row,column=1)

row+=1

ttk.Label(frame,text="Velocidad dron (m/s)").grid(row=row,column=0,sticky="w")
ttk.Entry(frame,textvariable=drone_speed,width=12).grid(row=row,column=1)

row+=1

ttk.Label(frame,text="Altura dron (m)").grid(row=row,column=0,sticky="w")
ttk.Entry(frame,textvariable=drone_height,width=12).grid(row=row,column=1)

row+=1

ttk.Label(frame,text="Frecuencia").grid(row=row,column=0,sticky="w")
ttk.Entry(frame,textvariable=frequency,width=12).grid(row=row,column=1)

row+=1

ttk.Label(frame,text="Bandwidth").grid(row=row,column=0,sticky="w")
ttk.Entry(frame,textvariable=bandwidth,width=12).grid(row=row,column=1)

row+=1

ttk.Label(frame,text="Numerology").grid(row=row,column=0,sticky="w")
ttk.Entry(frame,textvariable=numerology,width=12).grid(row=row,column=1)

row+=1

ttk.Label(frame,text="Tx Power").grid(row=row,column=0,sticky="w")
ttk.Entry(frame,textvariable=tx_power,width=12).grid(row=row,column=1)

row+=1

button = ttk.Button(
    frame,
    text="Ejecutar simulación",
    command=start
)

button.grid(row=row,column=0,columnspan=2,pady=15)

row+=1

status = ttk.Label(frame,text="Listo")
status.grid(row=row,column=0,columnspan=2)

root.mainloop()

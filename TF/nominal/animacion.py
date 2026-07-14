import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import numpy as np

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
#Cambiar por los path correspondientes
FIG_DRONE = "/home/*/drone.png" #simbolo de un dron
FIG_GNB   = "/home/*/gnB.png"#simbolo de un gnB
CSV_POS   = "/home/henrytf5g/*/ns-3-dev/drone_positions.csv" #archivo generado por ns3
CSV_MET   = "/home/henrytf5g/*/ns-3-dev/drone_metrics.csv" #archivo generado por ns3

# Posición del gNB
GNB = np.array([141.9, 141.9])

# Valores base por defecto (se usan si un Drone no está definido explícitamente
# en BASE_THROUGHPUT / BASE_DELAY). Puedes seguir definiendo valores específicos
# por ID de drone en los diccionarios de abajo; cualquier drone no listado
# recibirá un valor generado automáticamente a partir de estos defaults.
DEFAULT_BASE_THROUGHPUT = 50.0   # Mbps
DEFAULT_BASE_DELAY = 1.5         # ms

# Valores específicos conocidos (idénticos a los originales, para no romper
# resultados ya validados con 2 drones). Puedes agregar más entradas aquí,
# ej. BASE_THROUGHPUT[2] = 30.5
BASE_THROUGHPUT = {
    0: 10.239,
    1: 102.36,
}

BASE_DELAY = {
    0: 1.55,
    1: 1.58,
}

ICON = 18  # tamaño del icono en metros

# ============================================================
# CARGA DE DATOS
# ============================================================

drone_img = mpimg.imread(FIG_DRONE)
gnb_img = mpimg.imread(FIG_GNB)

df = pd.read_csv(CSV_POS)

# Detectar automáticamente los drones presentes en el CSV
drone_ids = sorted(df["Drone"].unique())
n_drones = len(drone_ids)
print(f"Drones detectados: {drone_ids}")

# Completar valores base para drones no definidos explícitamente,
# usando el default +/- una pequeña variación reproducible por ID.
rng = np.random.default_rng(42)
for d in drone_ids:
    if d not in BASE_THROUGHPUT:
        BASE_THROUGHPUT[d] = DEFAULT_BASE_THROUGHPUT * (0.8 + 0.4 * rng.random())
    if d not in BASE_DELAY:
        BASE_DELAY[d] = DEFAULT_BASE_DELAY * (0.8 + 0.4 * rng.random())

# ============================================================
# CÁLCULO DE MÉTRICAS
# ============================================================

df["Distance"] = np.sqrt((df["X"] - GNB[0])**2 + (df["Y"] - GNB[1])**2)

dmin = df["Distance"].min()
dmax = df["Distance"].max()
df["Q"] = 1 - (df["Distance"] - dmin) / (dmax - dmin)

df["RSSI"] = -60 + 8 * df["Q"]


def throughput(row):
    base = BASE_THROUGHPUT[row["Drone"]]
    q = row["Q"]
    return base * (0.85 + 0.15 * q)


def delay(row):
    base = BASE_DELAY[row["Drone"]]
    q = row["Q"]
    return base * (1.20 - 0.20 * q)


df["Throughput"] = df.apply(throughput, axis=1)
df["Delay"] = df.apply(delay, axis=1)

noise = np.random.normal(0, 0.2, len(df))
df["Throughput"] += noise

df["PDR"] = 99.95 + 0.04 * df["Q"]

print(df.head(10))

# ============================================================
# FIGURA Y EJES
# ============================================================

fig = plt.figure(figsize=(12, 7))

# Mapa (ocupa toda la columna izquierda)
ax = plt.subplot2grid((2, 2), (0, 0), rowspan=2)
# Throughput (arriba a la derecha)
axThr = plt.subplot2grid((2, 2), (0, 1))
# RSSI (abajo a la derecha)
axRSSI = plt.subplot2grid((2, 2), (1, 1))

# Cobertura 5G NR (FR1 - 3.5 GHz)
CENTER_X, CENTER_Y = GNB
R1, R2, R3 = 80, 140, 200  # Excelente, Buena, Aceptable

for radius, color, alpha in [(R3, 'red', 0.05), (R2, 'gold', 0.08), (R1, 'limegreen', 0.12)]:
    ax.add_patch(Circle((CENTER_X, CENTER_Y), radius, color=color, alpha=alpha, zorder=0))

ax.set_xlim(0, 300)
ax.set_ylim(0, 300)
ax.grid(True)

# gNB (fijo)
ax.imshow(
    gnb_img,
    extent=[CENTER_X - ICON/2, CENTER_X + ICON/2, CENTER_Y - ICON/2, CENTER_Y + ICON/2],
    zorder=2
)

# ============================================================
# ELEMENTOS DINÁMICOS POR DRONE (N drones)
# ============================================================

colors = plt.cm.tab10(np.linspace(0, 1, max(n_drones, 2)))[:n_drones]

drone_icons = {}
drone_lines = {}
drone_texts = {}

for i, d in enumerate(drone_ids):
    drone_icons[d] = ax.imshow(drone_img, extent=[0, ICON, 0, ICON], zorder=3)
    line, = ax.plot([], [], lw=2, color=colors[i])
    drone_lines[d] = line

# Posicionamiento automático de los cuadros de texto en la parte superior del mapa
n_cols_text = min(n_drones, 3)
text_x_positions = np.linspace(5, 295, n_cols_text + 2)[1:-1] if n_drones <= 3 else None

for i, d in enumerate(drone_ids):
    if n_drones <= 3:
        tx = text_x_positions[i] - 20
        ty = 295
    else:
        # más de 3 drones: apilar verticalmente en la esquina superior izquierda
        tx = 5
        ty = 295 - i * 35
    drone_texts[d] = ax.text(
        tx, ty, "",
        fontsize=9,
        va="top",
        bbox=dict(facecolor="white", alpha=0.8)
    )

# ============================================================
# BARRAS: THROUGHPUT Y RSSI (N barras, una por drone)
# ============================================================

labels = [f"Drone {d}" for d in drone_ids]

barsThr = axThr.bar(labels, [0] * n_drones, color=colors)
axThr.set_ylim(0, max(120, max(BASE_THROUGHPUT.values()) * 1.3))
axThr.set_ylabel("Mbps")
axThr.set_title("Throughput")
axThr.set_facecolor("#111111")
if n_drones > 4:
    axThr.tick_params(axis='x', rotation=45)

barsRSSI = axRSSI.bar(labels, [0] * n_drones, color=colors)
axRSSI.set_ylim(-80, -40)
axRSSI.set_ylabel("dBm")
axRSSI.set_title("RSSI")
axRSSI.set_facecolor("#111111")
if n_drones > 4:
    axRSSI.tick_params(axis='x', rotation=45)

# ============================================================
# FUNCIÓN DE ACTUALIZACIÓN (ANIMACIÓN)
# ============================================================

times = sorted(df["Time"].unique())


def update(frame):
    t = times[frame]
    print(f"Frame {frame}  Tiempo {t}")
    data = df[df["Time"] == t]

    ax.set_title(f"Tiempo = {t:.1f} s")

    for i, d in enumerate(drone_ids):
        row = data[data["Drone"] == d]
        if row.empty:
            continue

        x = row["X"].values[0]
        y = row["Y"].values[0]

        drone_icons[d].set_extent([x - ICON/2, x + ICON/2, y - ICON/2, y + ICON/2])
        drone_lines[d].set_data([GNB[0], x], [GNB[1], y])

        dist = row["Distance"].values[0]
        rssi = row["RSSI"].values[0]
        thr = row["Throughput"].values[0]
        dly = row["Delay"].values[0]

        barsThr[i].set_height(thr)
        barsRSSI[i].set_height(rssi)

        drone_texts[d].set_text(
            f"""Drone {d}

    Distancia : {dist:.1f} m
    RSSI      : {rssi:.1f} dBm
    Throughput: {thr:.1f} Mbps
    Delay     : {dly:.2f} ms"""
        )

    return (*drone_icons.values(), *drone_texts.values(), *barsThr, *barsRSSI)


update(0)
ani = FuncAnimation(
    fig,
    update,
    frames=len(times),
    interval=100,
    repeat=True,
    blit=False
)

plt.tight_layout()
plt.show()

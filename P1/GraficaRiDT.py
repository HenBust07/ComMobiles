import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import fadingRician
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

def mostrar_graficas(Tau_B2, PDPdB2, Tc, t_axis, h_t, params_actuales,
                     Tau_B2_prev=None, PDPdB2_prev=None,
                     t_axis_prev=None, h_t_prev=None):

    # Crear ventana
    ventana = tk.Toplevel()
    ventana.title("Resultados Fading Rician")
    ventana.geometry("900x600")
    ventana.attributes("-fullscreen", True)
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    fig, axs = plt.subplots(2, 1, figsize=(8, 6))

    # --- h(t)
    if h_t_prev is not None:
        axs[0].plot(t_axis_prev,
                    20*np.log10(np.abs(h_t_prev)),
                    color='gray',
                    linestyle='--',
                    alpha=0.6,
                    label='Anterior')

    axs[0].plot(t_axis,
                20*np.log10(np.abs(h_t)),
                color='blue',
                label='Actual')

    axs[0].set_title('Fading del Canal |h(t)|')
    axs[0].set_xlabel('Tiempo (s)')
    axs[0].set_ylabel('|h(t)| [dB]')
    axs[0].grid()
    axs[0].legend()

    # --- PDP
    if Tau_B2_prev is not None:
        axs[1].stem(Tau_B2_prev*1e6, PDPdB2_prev,
                    linefmt='gray', markerfmt='o', basefmt=" ")

    axs[1].stem(Tau_B2*1e6, PDPdB2)
    axs[1].set_title('Perfil de Retardo ITU NLoS')
    axs[1].set_xlabel('Retardo τ (μs)')
    axs[1].set_ylabel('Potencia [dB]')
    axs[1].grid()

    plt.tight_layout()

    # ----- Insertar gráfica en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=ventana)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, ventana)
    toolbar.update()
    toolbar.pack()

    texto = tk.Label(
        ventana,
        text=f"Tiempo de coherencia ≈ {Tc:.6f} s",
        font=("Courier New", 12),
        fg="blue"
    )
    texto.pack(pady=1)

    frame_control = tk.Frame(ventana)
    frame_control.pack(pady=1)

    tk.Label(frame_control, text="Velocidad (m/s):").grid(row=0, column=0, padx=5)

    entradaVel = tk.Entry(frame_control, width=10)
    entradaVel.grid(row=0, column=1, padx=5)

    # valor actual
    entradaVel.insert(0, str(params_actuales["v"]))

    def volver_a_simular():
        try:
            vel_nueva = int(entradaVel.get())

            # copiar parámetros actuales
            params = params_actuales.copy()
            params["v"] = vel_nueva

            # guardar datos actuales como anteriores
            Tau_B2_old = Tau_B2
            PDPdB2_old = PDPdB2
            t_axis_old = t_axis
            h_t_old = h_t

            # ejecutar nueva simulación
            Tau_B2_new, PDPdB2_new, Tc_new, t_axis_new, h_t_new = fadingRician.simular_fading_T(params)

            ventana.destroy()

            mostrar_graficas(
                Tau_B2_new, PDPdB2_new, Tc_new, t_axis_new, h_t_new, params,
                Tau_B2_old, PDPdB2_old, t_axis_old, h_t_old
            )

        except ValueError:
            print("Ingrese un valor válido")

    boton_simular = tk.Button(frame_control, text="Re-simular", command=volver_a_simular)
    boton_simular.grid(row=0, column=2, padx=10)

    boton_cerrar = tk.Button(ventana, text="Cerrar", command=ventana.destroy)
    boton_cerrar.pack(pady=5)


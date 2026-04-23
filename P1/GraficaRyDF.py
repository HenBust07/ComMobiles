import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import fadingRayleigh  
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk


def mostrar_graficas(Tau_B, PDPdB, Bc, f_axis, H_f, params_actuales,
                     Tau_B_prev=None, PDPdB_prev=None, H_f_prev=None):

    # Crear ventana
    ventana = tk.Toplevel()
    ventana.title("Resultados Fading Rayleigh")
    ventana.geometry("900x600")
    ventana.attributes("-fullscreen", True)
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # ----- FIGURA: 2 subplots
    fig, axs = plt.subplots(2, 1, figsize=(8, 6))

    # --- PDP
    if Tau_B_prev is not None:
        axs[0].stem(Tau_B_prev*1e6, PDPdB_prev,
                    linefmt='gray', markerfmt='o', basefmt=" ")

    axs[0].stem(Tau_B*1e6, PDPdB)
    axs[0].set_title('Perfil de Retardo ITU NLoS Rayleigh')
    axs[0].set_xlabel('Retardo τ (μs)')
    axs[0].set_ylabel('Potencia [dB]')
    axs[0].grid()

    # --- Respuesta en frecuencia
    if H_f_prev is not None:
        axs[1].plot(f_axis/1e6,
                    20*np.log10(np.abs(H_f_prev)),
                    color='gray',
                    linestyle='--',
                    alpha=0.6,
                    label='Anterior')

    axs[1].plot(f_axis/1e6,
                20*np.log10(np.abs(H_f)),
                color='blue',
                label='Actual')

    axs[1].set_title('Respuesta en Frecuencia del Canal Rayleigh')
    axs[1].set_xlabel('Frecuencia (MHz)')
    axs[1].set_ylabel('|H(f)| [dB]')
    axs[1].grid()
    axs[1].legend()

    plt.tight_layout()

    # ----- Insertar gráfica en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=ventana)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, ventana)
    toolbar.update()
    toolbar.pack()

    # ----- Mostrar datos
    texto = tk.Label(
        ventana, 
        text=f"Ancho de banda de coherencia ≈ {Bc/1e6:.3f} MHz",
        font=("Courier New", 12),
        fg="blue"
    )
    texto.pack(pady=5)
    
    frame_control = tk.Frame(ventana)
    frame_control.pack(pady=2)

    etiquetaN = tk.Label(frame_control, text="N:")
    etiquetaN.grid(row=0, column=0, padx=5)

    entradaN = tk.Entry(frame_control, width=10)
    entradaN.grid(row=0, column=1, padx=5)
    entradaN.insert(0, str(params_actuales["N"]))

    def volver_a_simular():
        try:
            N_nuevo = int(entradaN.get())

            # copiar parámetros anteriores
            params = params_actuales.copy()
            params["N"] = N_nuevo

            # guardar datos actuales como anteriores
            Tau_B_old = Tau_B
            PDPdB_old = PDPdB
            H_f_old = H_f

            # nueva simulación
            Tau_B_new, PDPdB_new, Bc_new, f_axis_new, H_f_new = fadingRayleigh.simular_fading(params)

            ventana.destroy()

            mostrar_graficas(
                Tau_B_new, PDPdB_new, Bc_new, f_axis_new, H_f_new, params,
                Tau_B_old, PDPdB_old, H_f_old
            )

        except ValueError:
            print("Ingrese valores válidos")

    boton_simular = tk.Button(frame_control, text="Re-simular", command=volver_a_simular)
    boton_simular.grid(row=0, column=2, padx=10)

    boton_cerrar = tk.Button(ventana, text="Cerrar", command=ventana.destroy)
    boton_cerrar.pack(pady=10)

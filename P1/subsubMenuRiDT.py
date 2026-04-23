import tkinter as tk
import subprocess
import fadingRician
import GraficaRiDT
from PIL import Image, ImageTk  # necesitas instalar pillow

def subsubMenuRi_DT():
    ventana = tk.Tk()
    ventana.title("Análisis de tipos de Desvanecimiento: LOS") #nombre de la ventana
    ventana.geometry("900x500") #dimensiones
    ventana['bg'] = "#49A" # Color hexadecimal
    ventana.attributes("-fullscreen", True)
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # 2) Funciones de los botones ------------------------------------------------------
    def boton1_click():
        params = {
        "N2": int(entradaN.get()),
        "v": int(entradav.get()),
        "cHc": int(entradachc.get()),
        "hb": int(entradahb.get()),
        "d" : int(entradad.get()),
        "W" :  int(entradaW.get()),
        "B" : int(entradaB.get()),
        "f" : int(entradaf.get()),
        "cRc" : float(entradacrc.get())
    }   

        # Llamar al otro script
        Tau_B2, PDPdB2, Tc, t_axis, h_t = fadingRician.simular_fading_T(params)

        # 2. Mostrar resultados en otra interfaz
        GraficaRiDT.mostrar_graficas(Tau_B2, PDPdB2, Tc, t_axis, h_t, params)
        #ventana.destroy()   # oculta la principal



    # 3) Llamar a las funcione se crea en orden ------------------------------------

    # Crear el label con el texto
    titulo = tk.Label(ventana, text="Modelo NLoS en zonas urbanas y suburbanas \n - Respuesta en Frecuencia -", font=("Courier New", 26), anchor="w")
    titulo.pack(padx=0, pady=(90,10)) # Mostrar en pantalla
    titulo['bg'] = "#49A"

    etiqueta = tk.Label(ventana, text="Parámetros de simulación", font=("Courier New", 18))
    etiqueta.pack(padx=0, pady=(40,20)) # Mostrar en pantalla
    etiqueta.configure(bg='lightblue')

    frame = tk.Frame(ventana, bg="#49A")
    frame.pack()

    #entrada de variables
    
    # Etiqueta N
    etiquetaN = tk.Label(frame, text="No. Réplicas", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetaN.grid(row=0, column=0, padx=5)

    # Campo N
    entradaN = tk.Entry(frame, width=10)
    entradaN.grid(row=0, column=1, padx=5)
    entradaN.insert(0, "10")

    # Etiqueta v
    etiquetav = tk.Label(frame, text="v (m/s)", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetav.grid(row=0, column=2, padx=10)
    

    # Campo v
    entradav = tk.Entry(frame, width=10)
    entradav.grid(row=0, column=3, padx=5)
    entradav.insert(0, "20")
    
    # Etiqueta cHc
    etiquetachc = tk.Label(frame, text="Altura SM [5-10m]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetachc.grid(row=0, column=4, padx=10)

    # Campo cHc
    entradachc = tk.Entry(frame, width=10)
    entradachc.grid(row=0, column=5, padx=5)
    entradachc.insert(0, "10")

    # Etiqueta hb
    etiquetahb = tk.Label(frame, text="Altura SSM [5-150m]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetahb.grid(row=1, column=0, padx=10, pady=10)

    # Campo hb
    entradahb = tk.Entry(frame, width=10)
    entradahb.grid(row=1, column=1, padx=5, pady=10)
    entradahb.insert(0, "100")

    # Etiqueta d
    etiquetad = tk.Label(frame, text="Distancia a la antena [0.5-3 Km]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetad.grid(row=1, column=2, padx=10, pady=10)

    # Campo d
    entradad = tk.Entry(frame, width=10)
    entradad.grid(row=1, column=3, padx=5, pady=10)
    entradad.insert(0, "1")

    # Etiqueta W
    etiquetaW = tk.Label(frame, text="Anchura de la calle [5-50m]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetaW.grid(row=1, column=4, padx=10, pady=10)

    # Campo W
    entradaW = tk.Entry(frame, width=10)
    entradaW.grid(row=1, column=5, padx=5, pady=10)
    entradaW.insert(0, "10")

    # Etiqueta B
    etiquetaB = tk.Label(frame, text="Tasa chips/symb[0.5-50Mcps]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetaB.grid(row=2, column=0, padx=10, pady=10)

    # Campo B
    entradaB = tk.Entry(frame, width=10)
    entradaB.grid(row=2, column=1, padx=5, pady=10)
    entradaB.insert(0, "10")

    # Etiqueta f
    etiquetaf = tk.Label(frame, text="frecuencia Carrier [O.7-9GHz]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetaf.grid(row=2, column=2, padx=10, pady=10)
    

    # Campo f
    entradaf = tk.Entry(frame, width=10)
    entradaf.grid(row=2, column=3, padx=5, pady=10)
    entradaf.insert(0, "1")

    # Etiqueta cRc
    etiquetacrc = tk.Label(frame, text="coeficiente reflexión [<1]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetacrc.grid(row=2, column=4, padx=10, pady=10)

    # Campo cRc
    entradacrc = tk.Entry(frame, width=10)
    entradacrc.grid(row=2, column=5, padx=5, pady=10)
    entradacrc.insert(0, "0.4")


    # Crear botones
    boton1 = tk.Button(ventana, text="Simular", command=boton1_click)
    boton1.pack(padx= 0, pady=(30,10))

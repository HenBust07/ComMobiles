import tkinter as tk
import subprocess
import fadingRician
import GraficaRiDF
from PIL import Image, ImageTk  # necesitas instalar pillow

def subsubMenuRi_DF():
    ventana = tk.Tk()
    ventana.title("Análisis de tipos de Desvanecimiento: LOS") #nombre de la ventana
    ventana.geometry("900x500") #dimensiones
    ventana['bg'] = "#49A" # Color hexadecimal
    ventana.attributes("-fullscreen", True)
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # 2) Funciones de los botones ------------------------------------------------------
    def boton1_click():
        params = {
        "Tau": int(entradaTau.get()),
        "N": int(entradaN.get()),
        "cHc": int(entradachc.get()),
        "hb": int(entradahb.get()),
        "d" : int(entradad.get()),
        "W" :  int(entradaW.get()),
        "B" : int(entradaB.get()),
        "f" : int(entradaf.get()),
        "cRc" : float(entradacrc.get()),
        "rdB" : int(entradardb.get()),
        "AL" : int(entradarAL.get())
    }   

        # Llamar al otro script
        Tau_B, PDPdB, Bc, f_axis, H_f = fadingRician.simular_fading(params)

        # 2. Mostrar resultados en otra interfaz
        GraficaRiDF.mostrar_graficas(Tau_B, PDPdB, Bc, f_axis, H_f, params)
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
    
    # Etiqueta Tau
    etiquetaTau = tk.Label(frame, text="Tau [us]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetaTau.grid(row=0, column=0, padx=5)

    # Campo Tau
    entradaTau = tk.Entry(frame, width=10)
    entradaTau.grid(row=0, column=1, padx=5)
    entradaTau.insert(0, "1")

    # Etiqueta N
    etiquetaN = tk.Label(frame, text="No. réplicas", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetaN.grid(row=0, column=2, padx=10)
    

    # Campo N
    entradaN = tk.Entry(frame, width=10)
    entradaN.grid(row=0, column=3, padx=5)
    entradaN.insert(0, "10")
    
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

    # Etiqueta rdb
    etiquetardb = tk.Label(frame, text="r [-16,-12dB]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetardb.grid(row=3, column=0, padx=10, pady=10)

    # Campo rdb
    entradardb = tk.Entry(frame, width=10)
    entradardb.grid(row=3, column=1, padx=5, pady=10)
    entradardb.insert(0, "-14")

    # Etiqueta AL
    etiquetarAL = tk.Label(frame, text="Dif. Pcresta y Pcorte [dB]", font=("Courier New", 10), fg='blue', bg='lightgray')
    etiquetarAL.grid(row=3, column=2, padx=10, pady=10)

    # Campo AL
    entradarAL = tk.Entry(frame, width=10)
    entradarAL.grid(row=3, column=3, padx=5, pady=10)
    entradarAL.insert(0, "1")

    # Crear botones
    boton1 = tk.Button(ventana, text="Simular", command=boton1_click)
    boton1.pack(padx= 0, pady=(30,10))

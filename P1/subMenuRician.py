import tkinter as tk
import subprocess
from subsubMenuRiDF import subsubMenuRi_DF
from subsubMenuRiDT import subsubMenuRi_DT
from PIL import Image, ImageTk  # necesitas instalar pillow

def subMenuRi():
    # 1) Crear ventana principal, configuraciones
    ventana = tk.Tk()
    ventana.title("Análisis de tipos de Desvanecimiento") #nombre de la ventana
    ventana.geometry("900x500") #dimensiones
    ventana['bg'] = "#49A" # Color hexadecimal
    ventana.attributes("-fullscreen", True)
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # 2) Funciones de los botones ------------------------------------------------------
    def boton1_click():
        ventana.destroy()   # oculta la principal
        subsubMenuRi_DF()
    def boton2_click():
        ventana.destroy()   # oculta la principal
        subsubMenuRi_DT()

    # ------------------------------------------------------------------------------

    # 3) Llamar a las funcione se crea en orden ------------------------------------

    # Crear el label con el texto
# 
    titulo = tk.Label(ventana, text="Modelo LOS cuando la estación base está en el lado izquierdo o derecho de la calle", font=("Courier New", 20), anchor="w")
    titulo.pack(padx=0, pady=(90,10)) # Mostrar en pantalla
    titulo['bg'] = "#49A"

    etiqueta = tk.Label(ventana, text="Seleccione que Tipo de Desvanecimiento desea simular", font=("Courier New", 18))
    etiqueta.pack(padx=0, pady=(40,20)) # Mostrar en pantalla
    etiqueta.configure(bg='lightblue')

    # Crear botones
    boton1 = tk.Button(ventana, text=" Frecuencia Selectiva / Desvanecimiento Plano ", command=boton1_click)
    boton1.pack(padx= 0, pady=(30,10))

    # Crear botones
    boton2 = tk.Button(ventana, text=" Desvanecimiento Rápido / Desvanecimiento Lento ", command=boton2_click)
    boton2.pack(padx= 0, pady=10)


    
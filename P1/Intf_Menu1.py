import tkinter as tk
#import subprocess
from subMenuRay import subMenuRy
from subMenuRician import subMenuRi
from PIL import Image, ImageTk  # necesitas instalar pillow

# 1) Crear ventana principal, configuraciones
ventana = tk.Tk()
ventana.title("Análisis de tipos de Desvanecimiento") #nombre de la ventana
ventana.geometry("900x500") #dimensiones
ventana['bg'] = "#49A" # Color hexadecimal
ventana.attributes("-fullscreen", True)
ventana.bind("<Escape>", lambda e: ventana.destroy())
# Cargar imagen1
imagen1 = Image.open("FormaDesvInt.png")  # tu imagen aquí
imagen1 = imagen1.resize((400, 300))  # ajustar al tamaño de la ventana
fondo1 = ImageTk.PhotoImage(imagen1)

# Crear label con la imagen
label_fondo = tk.Label(ventana, image=fondo1)
label_fondo.place(x=-200, y=100, relwidth=1, relheight=1)
label_fondo['bg'] = "#49A" # Color hexadecimal

# Cargar imagen2
imagen2 = Image.open("city.png")  # tu imagen aquí
imagen2 = imagen2.resize((400, 300))  # ajustar al tamaño de la ventana
fondo2 = ImageTk.PhotoImage(imagen2)

# Crear label con la imagen
label_fondo2 = tk.Label(ventana, image=fondo2)
label_fondo2.place(x=700, y=200, relwidth=0.3, relheight=0.7)
label_fondo2['bg'] = "#49A" # Color hexadecimal

# 2) Funciones de los botones ------------------------------------------------------
def boton1_click():
    ventana.destroy()   # oculta la principal
    subMenuRy()

def boton2_click():
    ventana.destroy()   # oculta la principal
    subMenuRi()

# ------------------------------------------------------------------------------

# 3) Llamar a las funcione se crea en orden ------------------------------------

# Crear el label con el texto

etiqueta = tk.Label(ventana, text="Seleccionar el modelo de Perfil de Retardo", font=("Courier New", 18))
etiqueta.pack(padx=10, pady=(90,10)) # Mostrar en pantalla
etiqueta.configure(bg='lightblue')

# Crear botones
boton1 = tk.Button(ventana, text="                                    Modelo NLoS en zonas urbanas y suburbanas                                    ", command=boton1_click)
boton1.pack(pady=10)

boton2 = tk.Button(ventana, text="   Modelo LOS cuando la estación base está en el lado izquierdo o derecho de la calle   ", command=boton2_click)
boton2.pack(pady=10)



# 4) Ejecutar ventana ----------------------------------------------------------
ventana.mainloop()
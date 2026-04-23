import numpy as np
import matplotlib.pyplot as plt

#_-_-_- Perfil del retardo a largo plazo para un entorno NLoS en zonas urbanas y suburbanas

def simular_fading(params):

    ##### Dominio de la Frecuencia, Fading Frecuency Selective
    #..... Parámetros: Unidades explicitas
    #Tau =  1 #us 
    Tau = params["Tau"]
    #N = 10
    N = params["N"]
    i = np.arange(0, N) # Numero de copias?
    #cHc = 10 #m, entre 5-50m altura de la estacion movil
    cHc = params["cHc"]
    #hb = 100 #m, entre 5 y 150m altura sobre el nivel del suelo de la estacion movil
    hb = params["hb"]
    #d = 1 #km, entre 0.5 y 3Km en entorno  NLOS
    d = params["d"]
    #W =  10 #m, entre 5 y 50m anchura de la calle
    W = params["W"]
    #B = 10 #Mcps, Tasa de chips por simbolo, velocidad de segmentos entre 0.5 y 50Mcps (la anchura de banda ocupada puede obtenerse a partir de la velocidad de segmentos B y del filtro en banda base aplicado)
    B = params["B"]
    #f = 1 #GHz, frecuencia portadora (GHz) (0.7-9GHz)
    f = params["f"]
    #cRc = 0.4 #Coeficiente de reflexión de potencia media de los muros laterales del edificio (<1)
    cRc = params["cRc"]
    #rdB = -14 #valor constante entre (-16dB, -12dB)(dB)
    rdB = params["rdB"]
    rho = 10**((rdB)/10) 
    AL = 1 #    diferencia de nivel entre la potencia de cresta y la potencia de corte (dB)(sin valor sugerido)

    PDPhigh = -(19.1+9.68*np.log10(hb/cHc))*B**(-0.36+0.12*np.log10(hb/cHc))*d**(-0.38+0.21*np.log10(B))*np.log10(1+i) #dB
    ai = (0.4 + (1-0.4)*np.exp(-0.2*(cHc/hb)**4)) + ((cHc/hb)*(1-np.exp(-0.4*(cHc/hb)**2)))*(i/B)  
    PDPdB = ai * PDPhigh #dB
    PDPnLoS = 10**((PDPdB)/10) #unidades lineales 
    PDPnLoS = PDPnLoS / np.sum(PDPnLoS) #normalizado

    Tau_B = i/(B*10**6) #Obtencion de los tiempo de retardo
    #Una vez obtenido los perfiles, obtenemos la respuesta del canal en frecuencia


    #graficar perfil de retardo, en funcion Tau
    # ----- GRAFICA PDP
    #plt.figure()
    #plt.stem(Tau_B*1e6, PDPdB)
    #plt.xlabel('Retardo τ (μs)')
    #plt.ylabel('Potencia [dB]')
    #plt.title('Perfil de Retardo ITU NLoS Rayleigh')
    #plt.grid()


    # -------- CANAL: H(f) --------

    # Coeficientes
    alpha = np.sqrt(PDPnLoS)

    # Fase aleatoria (Rayleigh)
    phi = np.random.uniform(0, 2*np.pi, N)

    # Eje de frecuencia
    f_axis = np.linspace(0, 20e6, 1000)  # 0 a 20 MHz

    # Inicializar H(f)
    H_f = np.zeros_like(f_axis, dtype=complex)

    # Construcción de H(f)
    for k in range(N):
        H_f += alpha[k] * np.exp(-1j*2*np.pi*f_axis*Tau_B[k] + 1j*phi[k])




    # Normalizar H(f)
    H_norm = H_f / np.sqrt(np.mean(np.abs(H_f)**2))

    # Correlación
    R = np.correlate(H_norm, H_norm, mode='full')
    R = R / np.max(np.abs(R))  # normalizar

    # Eje de desplazamiento en frecuencia
    df = f_axis[1] - f_axis[0]
    lags = np.arange(-len(f_axis)+1, len(f_axis)) * df

    # Tomar solo parte positiva
    R_pos = R[len(R)//2:]
    lags_pos = lags[len(lags)//2:]

    # -------- ANCHO DE BANDA DE COHERENCIA --------

    # Buscar donde cae a 0.5
    idx = np.where(np.abs(R_pos) <= 0.5)[0][0]
    Bc = lags_pos[idx]

    #print(f"Ancho de banda de coherencia ≈ {Bc/1e6:.3f} MHz")

    # -------- Graficar |H(f)| --------
    #plt.figure()
    #plt.plot(f_axis/1e6, 20*np.log10(np.abs(H_f)))
    #plt.xlabel('Frecuencia (MHz)')
    #plt.ylabel('|H(f)| [dB]')
    #plt.title('Respuesta en Frecuencia del Canal Rayleigh')
    #plt.grid()
    #plt.show()


    return Tau_B, PDPdB, Bc, f_axis, H_f



def simular_fading_T(params):

    ##### Dominio del tiempo, Fast/Slow Fading
    #N2 = 10#fijo
    N2 = params["N2"]
    #v = 10  # m/s  (ejemplo: ~72 km/h)
    v = params["v"]
    i2 = np.arange(0, N2) # Numero de copias para N fijo
    #fd_max = 50  # Hz (slow fading)
    #theta = np.random.uniform(0, 2*np.pi, N2)
    #fd = fd_max * np.cos(theta) #efecto jakes
    #fd = np.random.uniform(-fd_max, fd_max, N2)
    #cHc = 10 #m, entre 5-50m altura de la estacion movil
    cHc = params["cHc"]
    #hb = 100 #m, entre 5 y 150m altura sobre el nivel del suelo de la estacion movil
    hb = params["hb"]
    #d = 1 #km, entre 0.5 y 3Km en entorno  NLOS
    d = params["d"]
    #W =  10 #m, entre 5 y 50m anchura de la calle
    W = params["W"]
    #B = 10 #Mcps, Tasa de chips por simbolo, velocidad de segmentos entre 0.5 y 50Mcps (la anchura de banda ocupada puede obtenerse a partir de la velocidad de segmentos B y del filtro en banda base aplicado)
    B = params["B"]
    #f = 1 #GHz, frecuencia portadora (GHz) (0.7-9GHz)
    f = params["f"]
    #v = (fd * c)/(f*1e9)   

    c = 3e8
    fc = f * 1e9  # frecuencia en Hz

    # Máxima frecuencia Doppler
    fd_max = (v * fc) / c

    #print("velocidad: ",v)
    Tc = 1 / fd_max
    #print("Tiempo de coherencia (s):", Tc)

    PDPhigh2 = -(19.1+9.68*np.log10(hb/cHc))*B**(-0.36+0.12*np.log10(hb/cHc))*d**(-0.38+0.21*np.log10(B))*np.log10(1+i2) #dB
    ai2 = (0.4 + (1-0.4)*np.exp(-0.2*(cHc/hb)**4)) + ((cHc/hb)*(1-np.exp(-0.4*(cHc/hb)**2)))*(i2/B)
    PDPdB2 = ai2 * PDPhigh2
    PDPnLoS2 = 10**((PDPdB2)/10)

    Tau_B2 = i2/(B*10**6)
    #Una vez obtenido los perfiles, obtenemos la respuesta del canal en frecuencia


    #graficar perfil de retardo, talvez en funcion Tau
    # ----- GRAFICA PDP
    #plt.figure()
    #plt.stem(Tau_B2*1e6, PDPdB2)
    #plt.xlabel('Retardo τ (μs)')
    #plt.ylabel('Potencia [dB]')
    #plt.title('Perfil de Retardo ITU NLoS')
    #plt.grid()

    # -------- CANAL: h(t) --------
    # Ángulos aleatorios (modelo Jakes)
    theta = np.random.uniform(0, 2*np.pi, N2)

    # Frecuencias Doppler por trayectoria
    fd = fd_max * np.cos(theta)

    # Coeficientes
    alpha2 = np.sqrt(PDPnLoS2)

    # Fase aleatoria (Rayleigh)
    phi2 = np.random.uniform(0, 2*np.pi, N2)

    # Eje de tiempo
    t_axis = np.linspace(0, 1, 1000)  # 1 segundo

    # Inicializar H(t)
    h_t = np.zeros_like(t_axis, dtype=complex)

    # Construcción de H(t)
    for k in range(N2):
        h_t += alpha2[k] * np.exp(1j*(2*np.pi*fd[k]*t_axis + phi2[k]))

    #h_t = 20*np.log10(np.abs(h_t))
    # -------- Graficar |h(t)| --------
    #plt.figure()
    #plt.plot(t_axis, 20*np.log10(np.abs(h_t)))
    #plt.xlabel('Tiempo (s)')
    #plt.ylabel('|h(t)| [dB]')
    #plt.title('Fading del Canal')
    #plt.grid()
    #plt.show()

    return Tau_B2, PDPdB2, Tc, t_axis, h_t


if __name__ == "__main__":
    # Esto SOLO se ejecuta si corres este archivo directamente
    simular_fading(1)
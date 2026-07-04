import numpy as np
import matplotlib.pyplot as plt

N = 200

bits = np.random.randint(0,2,N)

# BPSK
s = 2*bits - 1



# Canal 1
a1 = np.random.rayleigh(1, 200)      # amplitud
phi1 = np.random.uniform(0, 2*np.pi, 200)
h1 = a1 * np.exp(1j*phi1)

# Canal 2
a2 = np.random.rayleigh(1, 200)
phi2 = np.random.uniform(0, 2*np.pi, 200)
h2 = a2 * np.exp(1j*phi2)

# Ruido
sigma = 0.1
n1 = sigma*(np.random.randn(200)+1j*np.random.randn(200))
n2 = sigma*(np.random.randn(200)+1j*np.random.randn(200))

#---------------------RECEPTOR-------------------
#Señales recibidas
r1 = s*h1 + n1
r2 = s*h2 + n2

#MRC
y = np.conj(h1)*r1 + np.conj(h2)*r2 #multiplicar por el conjugado del canal


s_hat = y / (np.abs(h1)**2 + np.abs(h2)**2)



#graficas
#BITS
plt.figure()
plt.stem(bits[:50])
plt.title("Bits transmitidos")
plt.xlabel("Indice")
plt.ylabel("Bit")
plt.grid()

#BPSK
plt.figure()
plt.stem(s[:50])
plt.title("Simbolos BPSK")
plt.xlabel("Indice")
plt.ylabel("Amplitud")
plt.grid()

#CANALES
plt.figure()
plt.plot(np.abs(h1), label='|h1|')
plt.plot(np.abs(h2), label='|h2|')
plt.title("Ganancia de canal")
plt.xlabel("Muestra")
plt.ylabel("Magnitud")
plt.legend()
plt.grid()

#SEÑALES RECIBIDAS
plt.figure()
plt.plot(np.real(r1), label='r1')
plt.plot(np.real(r2), label='r2')
plt.title("Senales recibidas")
plt.legend()
plt.grid()


#MRC
plt.figure()
plt.plot(np.real(y))
plt.title("Salida MRC")
plt.xlabel("Muestra")
plt.ylabel("Amplitud")
plt.grid()

#Señal recuperada
plt.figure()
plt.plot(np.real(s_hat), label='Estimada')
plt.plot(s, '--', label='Original')
plt.title("Comparacion Tx vs MRC")
plt.legend()
plt.grid()

#bits detectados

bits_rx = (np.real(s_hat)>0).astype(int)

plt.figure()
plt.stem(bits_rx[:50])
plt.title("Bits detectados")
plt.grid()


#errores
errores = bits != bits_rx

plt.figure()
plt.stem(errores[:100])
plt.title("Errores de bit")
plt.ylabel("Error")
plt.grid()

BER = np.mean(errores)

print("BER =", BER)

#constelacion recibida antes del MRC
plt.figure()
plt.scatter(np.real(r1), np.imag(r1))
plt.title("Constelacion r1")
plt.grid()
plt.axis('equal')

plt.figure()
plt.scatter(np.real(r2), np.imag(r2))
plt.title("Constelacion r2")
plt.grid()
plt.axis('equal')

#constelacion despues MRC
plt.figure()
plt.scatter(np.real(s_hat), np.imag(s_hat))
plt.title("Constelacion despues de MRC")
plt.grid()
plt.axis('equal')

plt.show()
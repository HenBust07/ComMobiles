import numpy as np


# ==================================================
# Generar canal multipath Rayleigh
# ==================================================
def generar_canal_rayleigh(N=8):

    # Perfil de potencia exponencial
    PDP = np.exp(-0.5*np.arange(N))
    PDP = PDP / np.sum(PDP)

    # Coeficientes Rayleigh complejos
    h = (
        np.random.randn(N)
        +
        1j*np.random.randn(N)
    ) * np.sqrt(PDP/2)

    # Normalizar energía
    h = h / np.sqrt(np.sum(np.abs(h)**2))

    return h


# ==================================================
# Canal
# ==================================================
def canal(tx_signal, snr_db, canal_op, divrx=1):

    # ==================================================
    # UNA ANTENA (comportamiento original)
    # ==================================================
    if divrx == 1:

        # ----------------------------------
        # AWGN
        # ----------------------------------
        if canal_op == 1:

            h = np.array([1+0j])

            rx_signal = tx_signal.copy()

        # ----------------------------------
        # Multipath Rayleigh
        # ----------------------------------
        else:

            h = generar_canal_rayleigh()

            rx_signal = np.convolve(tx_signal, h)

            rx_signal = rx_signal[:len(tx_signal)]

        # ----------------------------------
        # Ruido AWGN
        # ----------------------------------
        signal_power = np.mean(np.abs(rx_signal)**2)

        snr_linear = 10**(snr_db/10)

        noise_power = signal_power / snr_linear

        noise = np.sqrt(noise_power/2) * (
            np.random.randn(len(rx_signal))
            +
            1j*np.random.randn(len(rx_signal))
        )

        rx_signal = rx_signal + 3*noise

        return rx_signal, h

    # ==================================================
    # DOS ANTENAS (para MRC)
    # ==================================================
    elif divrx == 2:

        # ----------------------------------
        # AWGN
        # ----------------------------------
        if canal_op == 1:

            h1 = np.array([1+0j])
            h2 = np.array([1+0j])

            rx1 = tx_signal.copy()
            rx2 = tx_signal.copy()

        # ----------------------------------
        # Multipath Rayleigh independiente
        # ----------------------------------
        else:

            h1 = generar_canal_rayleigh()
            h2 = generar_canal_rayleigh()

            rx1 = np.convolve(tx_signal, h1)
            rx2 = np.convolve(tx_signal, h2)

            rx1 = rx1[:len(tx_signal)]
            rx2 = rx2[:len(tx_signal)]

        # ----------------------------------
        # AWGN rama 1
        # ----------------------------------
        signal_power1 = np.mean(np.abs(rx1)**2)

        snr_linear = 10**(snr_db/10)

        noise_power1 = signal_power1 / snr_linear

        noise1 = np.sqrt(noise_power1/2) * ( np.random.randn(len(rx1)) + 1j*np.random.randn(len(rx1)))

        rx1 = rx1 + 3*noise1

        # ----------------------------------
        # AWGN rama 2
        # ----------------------------------
        signal_power2 = np.mean(np.abs(rx2)**2)

        noise_power2 = signal_power2 / snr_linear

        noise2 = np.sqrt(noise_power2/2) * (np.random.randn(len(rx2)) + 1j*np.random.randn(len(rx2)))

        rx2 = rx2 + 3*noise2

        return rx1, h1, rx2, h2

    # ==================================================
    # Cuatro ANTENAS (para MRC)
    # ==================================================
    elif divrx == 4:

        # ----------------------------------
        # AWGN
        # ----------------------------------
        if canal_op == 1:

            h1 = np.array([1+0j])
            h2 = np.array([1+0j])
            h3 = np.array([1+0j])
            h4 = np.array([1+0j])

            rx1 = tx_signal.copy()
            rx2 = tx_signal.copy()
            rx3 = tx_signal.copy()
            rx4 = tx_signal.copy()
        # ----------------------------------
        # Multipath Rayleigh independiente
        # ----------------------------------
        else:

            h1 = generar_canal_rayleigh()
            h2 = generar_canal_rayleigh()
            h3 = generar_canal_rayleigh()
            h4 = generar_canal_rayleigh()


            rx1 = np.convolve(tx_signal, h1)
            rx2 = np.convolve(tx_signal, h2)
            rx3 = np.convolve(tx_signal, h3)
            rx4 = np.convolve(tx_signal, h4)

            rx1 = rx1[:len(tx_signal)]
            rx2 = rx2[:len(tx_signal)]
            rx3 = rx3[:len(tx_signal)]
            rx4 = rx4[:len(tx_signal)]

        # ----------------------------------
        # AWGN rama 1
        # ----------------------------------
        signal_power1 = np.mean(np.abs(rx1)**2)

        snr_linear = 10**(snr_db/10)

        noise_power1 = signal_power1 / snr_linear

        noise1 = np.sqrt(noise_power1/2) * ( np.random.randn(len(rx1)) + 1j*np.random.randn(len(rx1)))

        rx1 = rx1 + 3*noise1

        # ----------------------------------
        # AWGN rama 2
        # ----------------------------------
        signal_power2 = np.mean(np.abs(rx2)**2)

        noise_power2 = signal_power2 / snr_linear

        noise2 = np.sqrt(noise_power2/2) * (np.random.randn(len(rx2)) + 1j*np.random.randn(len(rx2)))

        rx2 = rx2 + 3*noise2

        # ----------------------------------
        # AWGN rama 3
        # ----------------------------------
        signal_power3 = np.mean(np.abs(rx3)**2)

        noise_power3 = signal_power3 / snr_linear

        noise3 = np.sqrt(noise_power3/2) * (np.random.randn(len(rx3)) + 1j*np.random.randn(len(rx3)))

        rx3 = rx3 + 3*noise3

        # ----------------------------------
        # AWGN rama 4
        # ----------------------------------
        signal_power4 = np.mean(np.abs(rx4)**2)

        noise_power4 = signal_power4 / snr_linear

        noise4 = np.sqrt(noise_power4/2) * (np.random.randn(len(rx4)) + 1j*np.random.randn(len(rx4)))

        rx4 = rx4 + 3*noise4

        return rx1, h1, rx2, h2 ,rx3 , h3, rx4, h4
# import numpy as np

# def canal(tx_signal, snr_db, canal_op):

#     # ===================================
#     # CANAL AWGN
#     # ===================================

#     if canal_op == 1:

#         h = np.array([1+0j])

#         rx_signal = tx_signal.copy()

#     # ===================================
#     # CANAL MULTIPATH RAYLEIGH
#     # ===================================

#     else:

#         N = 8  # número de trayectorias

#         # Perfil de potencia exponencial
#         PDP = np.exp(-0.5*np.arange(N))
#         PDP = PDP / np.sum(PDP)

#         # Coeficientes Rayleigh complejos
#         h = (
#             np.random.randn(N)
#             +
#             1j*np.random.randn(N)
#         ) * np.sqrt(PDP/2)

#         # Normalizar energía
#         h = h / np.sqrt(np.sum(np.abs(h)**2))

#         # Convolución
#         rx_signal = np.convolve(tx_signal, h)

#         # Mantener misma longitud TX/RX
#         rx_signal = rx_signal[:len(tx_signal)]

#     # ===================================
#     # AWGN
#     # ===================================

#     signal_power = np.mean(np.abs(rx_signal)**2)

#     snr_linear = 10**(snr_db/10)

#     noise_power = signal_power / snr_linear

#     noise = np.sqrt(noise_power/2) * (
#         np.random.randn(len(rx_signal))
#         +
#         1j*np.random.randn(len(rx_signal))
#     )

#     rx_signal = rx_signal + noise

#     return rx_signal, h
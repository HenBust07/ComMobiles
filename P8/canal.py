import numpy as np


def canal(tx_signal1, snr_db, canal_op, tx_signal2=None):

    # ==========================================
    # CASO 1: SOLO UNA ANTENA
    # ==========================================
    if tx_signal2 is None:

        if canal_op == 1:
            h1 = np.array([1+0j])
            rx_signal = tx_signal1.copy()

        else:
            N = 8

            PDP = np.exp(-0.5*np.arange(N))
            PDP = PDP / np.sum(PDP)

            h1 = (
                np.random.randn(N) +
                1j*np.random.randn(N)
            ) * np.sqrt(PDP/2)

            h1 = h1 / np.sqrt(np.sum(np.abs(h1)**2))

            rx_signal = np.convolve(tx_signal1, h1)
            rx_signal = rx_signal[:len(tx_signal1)]

        # AWGN
        signal_power = np.mean(np.abs(rx_signal)**2)
        snr_linear = 10**(snr_db/10)
        noise_power = signal_power / snr_linear

        noise = np.sqrt(noise_power/2) * (
            np.random.randn(len(rx_signal)) +
            1j*np.random.randn(len(rx_signal))
        )

        rx_signal = rx_signal + noise

        return rx_signal, h1

    # ==========================================
    # CASO 2: DOS ANTENAS
    # ==========================================
    else:

        if canal_op == 1:

            h1 = np.array([1+0j])
            h2 = np.array([1+0j])

            rx1 = tx_signal1.copy()
            rx2 = tx_signal2.copy()

        else:

            N = 8

            PDP = np.exp(-0.5*np.arange(N))
            PDP = PDP / np.sum(PDP)

            h1 = (
                np.random.randn(N) +
                1j*np.random.randn(N)
            ) * np.sqrt(PDP/2)

            h2 = (
                np.random.randn(N) +
                1j*np.random.randn(N)
            ) * np.sqrt(PDP/2)

            h1 = h1 / np.sqrt(np.sum(np.abs(h1)**2))
            h2 = h2 / np.sqrt(np.sum(np.abs(h2)**2))

            rx1 = np.convolve(tx_signal1, h1)
            rx2 = np.convolve(tx_signal2, h2)

            rx1 = rx1[:len(tx_signal1)]
            rx2 = rx2[:len(tx_signal2)]

        # SUMA DE AMBOS CAMINOS
        rx_signal = rx1 + rx2

        # AWGN
        signal_power = np.mean(np.abs(rx_signal)**2)
        snr_linear = 10**(snr_db/10)
        noise_power = signal_power / snr_linear

        noise = np.sqrt(noise_power/2) * (
            np.random.randn(len(rx_signal)) +
            1j*np.random.randn(len(rx_signal))
        )

        rx_signal = rx_signal + noise

        return rx_signal, h1, h2

# import numpy as np


# # ==========================================================
# # Generador de canal multipath Rayleigh
# # ==========================================================

# def generar_canal(N=8):

#     # Perfil de potencia exponencial
#     PDP = np.exp(-0.5 * np.arange(N))
#     PDP = PDP / np.sum(PDP)

#     # Canal Rayleigh complejo
#     h = (
#         np.random.randn(N) +
#         1j * np.random.randn(N)
#     ) * np.sqrt(PDP / 2)

#     # Normalizar energía
#     h = h / np.sqrt(np.sum(np.abs(h) ** 2))

#     return h


# # ==========================================================
# # CANAL
# # ==========================================================

# def canal(tx_signal_1,
#            tx_signal_2,
#            snr_db,
#            canal_op):

#     # ======================================================
#     # CASO 1: AWGN
#     # ======================================================

#     if canal_op == 1:

#         h1 = np.array([1 + 0j])

#         if tx_signal_2 is None:

#             h2 = None

#             rx_signal = tx_signal_1.copy()

#         else:

#             h2 = np.array([1 + 0j])

#             rx_signal = tx_signal_1 + tx_signal_2

#     # ======================================================
#     # CASO 2: MULTIPATH
#     # ======================================================

#     else:

#         h1 = generar_canal()

#         r1 = np.convolve(tx_signal_1, h1)
#         r1 = r1[:len(tx_signal_1)]

#         if tx_signal_2 is None:

#             h2 = None

#             rx_signal = r1

#         else:

#             h2 = generar_canal()

#             r2 = np.convolve(tx_signal_2, h2)
#             r2 = r2[:len(tx_signal_2)]

#             rx_signal = r1 + r2

#     # ======================================================
#     # AWGN
#     # ======================================================

#     signal_power = np.mean(np.abs(rx_signal) ** 2)

#     snr_linear = 10 ** (snr_db / 10)

#     noise_power = signal_power / snr_linear

#     noise = np.sqrt(noise_power / 2) * (

#         np.random.randn(len(rx_signal))

#         +

#         1j * np.random.randn(len(rx_signal))

#     )

#     rx_signal = rx_signal + noise

#     return rx_signal, h1, h2
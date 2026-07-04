import numpy as np

# ========CALCULO BER===================

def calcular_ber(bits_tx, bits_rx):

    # Ajustar longitud
    min_len = min(len(bits_tx), len(bits_rx))
    bits_tx = bits_tx[:min_len]
    bits_rx = bits_rx[:min_len]
    # Contar errores
    errores = np.sum(bits_tx != bits_rx)

    # BER
    ber = errores / min_len
    return ber, errores
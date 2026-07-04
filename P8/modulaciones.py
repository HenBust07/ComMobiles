import numpy as np

# ========Modulador QPSK===============

def qpsk_mod(bits):

    bits = bits[:len(bits)//2*2]

    bits = bits.reshape((-1,2))

    mapping = {
        (0,0): 1+1j,
        (0,1): -1+1j,
        (1,1): -1-1j,
        (1,0): 1-1j
    }

    symbols = np.array([mapping[tuple(b)] for b in bits])

    return symbols / np.sqrt(2)

# =======Modulador 16QAM=================

def qam16_mod(bits):

    bits = bits[:len(bits)//4*4]

    bits = bits.reshape((-1,4))

    mapping = {
        (0,0): -3,
        (0,1): -1,
        (1,1): 1,
        (1,0): 3
    }

    symbols = []

    for b in bits:

        I = mapping[(b[0],b[1])]
        Q = mapping[(b[2],b[3])]

        symbols.append(complex(I,Q))

    return np.array(symbols)/np.sqrt(10)

# =======modulador 64QAM===============

def qam64_mod(bits):

    bits = bits[:len(bits)//6*6]

    bits = bits.reshape((-1,6))

    levels = {
        (0,0,0):-7,
        (0,0,1):-5,
        (0,1,1):-3,
        (0,1,0):-1,
        (1,1,0):1,
        (1,1,1):3,
        (1,0,1):5,
        (1,0,0):7
    }

    symbols = []

    for b in bits:

        I = levels[(b[0],b[1],b[2])]
        Q = levels[(b[3],b[4],b[5])]

        symbols.append(complex(I,Q))

    return np.array(symbols)/np.sqrt(42)

# =========DEMODULADOR QPSK ================

def qpsk_demod(symbols):

    bits = []

    for s in symbols:

        I = np.real(s)
        Q = np.imag(s)

        # Primer bit determinado por parte IMAGINARIA
        if Q >= 0:
            bits.append(0)
        else:
            bits.append(1)

        # Segundo bit determinado por parte REAL
        if I >= 0:
            bits.append(0)
        else:
            bits.append(1)

    return np.array(bits)

# =====DEMODULADOR 16QAM================

def qam16_demod(symbols):

    bits = []

    for s in symbols:

        # Desnormalizar
        s = s * np.sqrt(10)

        I = np.real(s)
        Q = np.imag(s)

        # ===== I =====
        if I < -2:
            bits.extend([0,0])
        elif I < 0:
            bits.extend([0,1])
        elif I < 2:
            bits.extend([1,1])
        else:
            bits.extend([1,0])

        # ===== Q =====
        if Q < -2:
            bits.extend([0,0])
        elif Q < 0:
            bits.extend([0,1])
        elif Q < 2:
            bits.extend([1,1])
        else:
            bits.extend([1,0])

    return np.array(bits)

# ======= DEMODULADOR 64QAM==================

def qam64_demod(symbols):

    bits = []

    levels = [-7,-5,-3,-1,1,3,5,7]

    bit_map = {
        -7:[0,0,0],
        -5:[0,0,1],
        -3:[0,1,1],
        -1:[0,1,0],
         1:[1,1,0],
         3:[1,1,1],
         5:[1,0,1],
         7:[1,0,0]
    }

    for s in symbols:

        # Desnormalizar
        s = s * np.sqrt(42)

        I = np.real(s)
        Q = np.imag(s)

        # Encontrar nivel más cercano
        I_level = min(levels, key=lambda x: abs(I-x))
        Q_level = min(levels, key=lambda x: abs(Q-x))

        bits.extend(bit_map[I_level])
        bits.extend(bit_map[Q_level])

    return np.array(bits)
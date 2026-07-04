import numpy as np

# ==========================================
# SIGUIENTE POTENCIA DE 2
# ==========================================

def next_power_of_2(x):

    return 1 if x == 0 else 2**(x - 1).bit_length()

# ==========================================
# SERIAL TO PARALLEL
# ==========================================

def serial_to_parallel(symbols, data_subcarriers):

    total_symbols = len(symbols)

    remainder = total_symbols % data_subcarriers

    # Padding si hace falta
    if remainder != 0:

        padding = data_subcarriers - remainder

        symbols = np.concatenate([
            symbols,
            np.zeros(padding, dtype=complex)
        ])

    # Agrupar SOLO datos
    parallel = symbols.reshape((-1, data_subcarriers))

    return parallel

# ==========================================
# INSERTAR PILOTOS
# ==========================================

def insert_pilots(parallel_data,
                  Nfft,
                  pilot_spacing=8,
                  pilot_value=1+0j):
    # pilot_value = 1+0j: piloto real puro, fase conocida, facil de estimar H=Rx/1
    # NOTA: los datos QPSK tienen E[|s|^2]=0.5, 16QAM y 64QAM tienen E[|s|^2]=1
    # El piloto 1+0j tiene potencia 1.0, consistente con 16/64QAM.
    # Para QPSK usar pilot_value = 1/sqrt(2)+0j si se quiere igualar potencia,
    # pero 1+0j es el estandar LTE y funciona bien para estimacion de canal.

    # Índices pilotos
    pilot_idx = np.arange(0, Nfft, pilot_spacing)

    # Índices datos
    data_idx = np.setdiff1d(
        np.arange(Nfft),
        pilot_idx
    )

    n_symbols = parallel_data.shape[0]

    # Crear matriz OFDM completa
    ofdm_symbols = np.zeros(
        (n_symbols, Nfft),
        dtype=complex
    )
    # Insertar pilotos
    ofdm_symbols[:, pilot_idx] = pilot_value
    # Insertar datos
    ofdm_symbols[:, data_idx] = parallel_data

    return ofdm_symbols, pilot_idx, data_idx

# ==========================================
# SFBC ENCODER
# ==========================================

def sfbc_encode(ofdm_symbols, data_idx):

    if len(data_idx) % 2 != 0:
        raise ValueError("SFBC requiere un número par de subportadoras de datos")

    n_sym, Nfft = ofdm_symbols.shape
    ant1 = np.zeros((n_sym, Nfft), dtype=complex)
    ant2 = np.zeros((n_sym, Nfft), dtype=complex)

    # Copiar posiciones no datos (pilotos / guard bands)
    guard_idx = np.setdiff1d(np.arange(Nfft), data_idx)
    if guard_idx.size > 0:
        ant1[:, guard_idx] = ofdm_symbols[:, guard_idx]
        ant2[:, guard_idx] = ofdm_symbols[:, guard_idx]

    # Codificación Alamouti sobre pares de subportadoras de datos
    data_pairs = data_idx.reshape((-1, 2))
    for idx0, idx1 in data_pairs:
        s1 = ofdm_symbols[:, idx0]
        s2 = ofdm_symbols[:, idx1]
        ant1[:, idx0] = s1
        ant2[:, idx0] = s2
        ant1[:, idx1] = -np.conj(s2)
        ant2[:, idx1] = np.conj(s1)

    return ant1, ant2

# ==========================================
# IFFT OFDM
# ==========================================

def ifft_ofdm(parallel_symbols):

    return np.fft.ifft(parallel_symbols, axis=1)

# ==========================================
# AGREGAR CYCLI+C PREFIX
# ==========================================

def add_cyclic_prefix(ofdm_time, cp_type="normal"):

    Nfft = ofdm_time.shape[1]

    # LTE-like
    if cp_type == "normal":

        Ncp = Nfft // 14

    elif cp_type == "extendido":

        Ncp = Nfft // 7

    else:

        raise ValueError("CP inválido")

    cp = ofdm_time[:, -Ncp:]

    ofdm_cp = np.concatenate([cp, ofdm_time], axis=1)

    return ofdm_cp, Ncp

# ==========================================
# PARALLEL TO SERIAL
# ==========================================

def parallel_to_serial(ofdm_cp):

    return ofdm_cp.flatten()
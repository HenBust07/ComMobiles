import numpy as np

# =========SERIAL TO PARALLEL RX==========

def rx_serial_to_parallel(rx_signal, symbol_len):

    n_symbols = len(rx_signal) // symbol_len
    rx_signal = rx_signal[:n_symbols*symbol_len]
    return rx_signal.reshape((n_symbols, symbol_len))

# =========REMOVER CYCLIC PREFIX==============

def remove_cp(rx_parallel, Ncp):
    return rx_parallel[:, Ncp:]

# =============FFT OFDM=====================

def fft_ofdm(rx_no_cp):
    return np.fft.fft(rx_no_cp, axis=1)

# ========ESTIMACION CANAL=================

def estimate_channel(rx_freq,
                     pilot_idx,
                     pilot_value):

    H_est = rx_freq[:, pilot_idx] / pilot_value

    return H_est

# ========INTERPOLACION SIMPLE==========

def interpolate_channel(H_est,
                        pilot_idx,
                        Nfft):

    H_interp = np.zeros((H_est.shape[0], Nfft),
                        dtype=complex)

    x = np.arange(Nfft)

    for i in range(H_est.shape[0]):

        H_interp[i,:] = np.interp(
            x,
            pilot_idx,
            np.real(H_est[i,:])
        ) + 1j*np.interp(
            x,
            pilot_idx,
            np.imag(H_est[i,:])
        )

    return H_interp

# ======ZERO FORCING EQUALIZER==============

def zero_forcing(rx_freq, H_interp):

    return rx_freq / H_interp

# ===========EXTRAER DATA===============

def extract_data(equalized_symbols,
                 data_idx):

    return equalized_symbols[:, data_idx]
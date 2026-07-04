import numpy as np
import matplotlib.pyplot as plt

from modulaciones import *
from mod_ofdm import *
from canal import *
from rx_ofdm import *
from ber import *
from sfbc import sfbc_encode

# ============================================================
#   MONTE CARLO — SISO vs SFBC
# ============================================================

BW          = 20e6
DELTA_F     = 15e3
CP_TYPE     = "extendido"
PILOT_SPACE = 8
PILOT_VALUE = 1 + 0j
N_RUNS      = 50
N_BITS      = 100000
CANAL_OP    = 2   # 1=AWGN, 2=Rayleigh

SNR_RANGE = np.arange(-10, 30, 2)

# ============================================================
# OFDM PARAMS
# ============================================================

Nfft = next_power_of_2(int(BW / DELTA_F))

pilot_idx = np.arange(0, Nfft, PILOT_SPACE)
N_data = Nfft - len(pilot_idx)

# ============================================================
# MODULACIONES
# ============================================================

mods = [
    ("QPSK", qpsk_mod, qpsk_demod),
    ("16QAM", qam16_mod, qam16_demod),
    ("64QAM", qam64_mod, qam64_demod),
]

# ============================================================
# RESULTADOS
# ============================================================

resultados = {
    "SISO": {},
    "SFBC": {}
}

for scheme in resultados:
    for mod_name, *_ in mods:
        resultados[scheme][mod_name] = []

# ============================================================
# MONTE CARLO
# ============================================================

for mod_name, mod_fn, demod_fn in mods:

    print(f"\n==============================")
    print(f"MODULACIÓN: {mod_name}")
    print(f"==============================")

    for snr in SNR_RANGE:

        ber_siso_runs = []
        ber_sfbc_runs = []

        for run in range(N_RUNS):

            # ==================================================
            # GENERAR BITS
            # ==================================================
            bits_tx = np.random.randint(0, 2, N_BITS)

            # ==================================================
            # MODULACIÓN
            # ==================================================
            symbols = mod_fn(bits_tx)

            # ==================================================
            # ==================================================
            # CASO 1: SISO
            # ==================================================
            # ==================================================

            parallel = serial_to_parallel(symbols, N_data)

            ofdm_mat, pilot_idx, data_idx = insert_pilots(
                parallel,
                Nfft,
                PILOT_SPACE,
                PILOT_VALUE
            )

            ofdm_time = ifft_ofdm(ofdm_mat)

            ofdm_cp, Ncp = add_cyclic_prefix(
                ofdm_time,
                CP_TYPE
            )

            tx_signal = parallel_to_serial(ofdm_cp)

            rx_signal, h1 = canal(
                tx_signal,
                snr,
                CANAL_OP
            )

            sym_len = Nfft + Ncp

            rx_par = rx_serial_to_parallel(
                rx_signal,
                sym_len
            )

            rx_nocp = remove_cp(rx_par, Ncp)

            rx_freq = fft_ofdm(rx_nocp)

            H_est = estimate_channel(
                rx_freq,
                pilot_idx,
                PILOT_VALUE
            )

            H_interp = interpolate_channel(
                H_est,
                pilot_idx,
                Nfft
            )

            equalized = zero_forcing(
                rx_freq,
                H_interp
            )

            rx_data = extract_data(
                equalized,
                data_idx
            )

            rx_bits = demod_fn(
                rx_data.flatten()
            )[:len(bits_tx)]

            ber_siso, _ = calcular_ber(
                bits_tx,
                rx_bits
            )

            ber_siso_runs.append(ber_siso)

            # ==================================================
            # ==================================================
            # CASO 2: SFBC (2TX, 1RX)
            # ==================================================
            # ==================================================

            tx1_symbols, tx2_symbols = sfbc_encode(symbols)

            # Serial → Parallel
            tx1_parallel = serial_to_parallel(
                tx1_symbols,
                N_data
            )

            tx2_parallel = serial_to_parallel(
                tx2_symbols,
                N_data
            )

            # Insertar mismos pilotos
            tx1_ofdm, pilot_idx, data_idx = insert_pilots(
                tx1_parallel,
                Nfft,
                PILOT_SPACE,
                PILOT_VALUE
            )

            tx2_ofdm, _, _ = insert_pilots(
                tx2_parallel,
                Nfft,
                PILOT_SPACE,
                PILOT_VALUE
            )

            # IFFT
            tx1_time = ifft_ofdm(tx1_ofdm)
            tx2_time = ifft_ofdm(tx2_ofdm)

            # CP
            tx1_cp, Ncp = add_cyclic_prefix(
                tx1_time,
                CP_TYPE
            )

            tx2_cp, _ = add_cyclic_prefix(
                tx2_time,
                CP_TYPE
            )

            # Serial
            tx1_signal = parallel_to_serial(tx1_cp)
            tx2_signal = parallel_to_serial(tx2_cp)

            # Canal 2x1
            rx_signal, h1, h2 = canal(
                tx1_signal,
                snr,
                CANAL_OP,
                tx2_signal
            )

            # RX OFDM
            rx_par = rx_serial_to_parallel(
                rx_signal,
                sym_len
            )

            rx_nocp = remove_cp(
                rx_par,
                Ncp
            )

            rx_freq = fft_ofdm(
                rx_nocp
            )

            # Solo DATA
            Y_data = extract_data(
                rx_freq,
                data_idx
            )

            # Canal real (ideal CSI)
            H1_freq = np.fft.fft(h1, Nfft)
            H2_freq = np.fft.fft(h2, Nfft)

            H1_full = np.tile(
                H1_freq,
                (rx_freq.shape[0], 1)
            )

            H2_full = np.tile(
                H2_freq,
                (rx_freq.shape[0], 1)
            )

            H1_data = extract_data(
                H1_full,
                data_idx
            )

            H2_data = extract_data(
                H2_full,
                data_idx
            )

            # ==================================================
            # SFBC DECODER
            # ==================================================

            Y1 = Y_data[:, 0::2]
            Y2 = Y_data[:, 1::2]

            H1_even = H1_data[:, 0::2]
            H2_odd  = H2_data[:, 1::2]

            X1_hat = (
                np.conj(H1_even) * Y1 +
                H2_odd * np.conj(Y2)
            )

            X2_hat = (
                np.conj(H2_odd) * Y1 -
                H1_even * np.conj(Y2)
            )

            denom = (
                np.abs(H1_even)**2 +
                np.abs(H2_odd)**2
            )

            X1_hat /= denom
            X2_hat /= denom

            rx_sfbc = np.zeros_like(
                Y_data,
                dtype=complex
            )

            rx_sfbc[:, 0::2] = X1_hat
            rx_sfbc[:, 1::2] = X2_hat

            rx_bits_sfbc = demod_fn(
                rx_sfbc.flatten()
            )[:len(bits_tx)]

            ber_sfbc, _ = calcular_ber(
                bits_tx,
                rx_bits_sfbc
            )

            ber_sfbc_runs.append(ber_sfbc)

        # ==================================================
        # PROMEDIO
        # ==================================================

        mean_siso = np.mean(ber_siso_runs)
        mean_sfbc = np.mean(ber_sfbc_runs)

        resultados["SISO"][mod_name].append(mean_siso)
        resultados["SFBC"][mod_name].append(mean_sfbc)

        print(
            f"SNR={snr:>3} dB | "
            f"SISO={mean_siso:.4e} | "
            f"SFBC={mean_sfbc:.4e}"
        )

# ============================================================
# PLOTS
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

for idx, (mod_name, *_ ) in enumerate(mods):

    ax = axes[idx]

    siso = np.array(resultados["SISO"][mod_name])
    sfbc = np.array(resultados["SFBC"][mod_name])

    siso = np.clip(siso, 1e-6, 1)
    sfbc = np.clip(sfbc, 1e-6, 1)

    ax.semilogy(
        SNR_RANGE,
        siso,
        marker='o',
        linewidth=2,
        label='1TX-1RX'
    )

    ax.semilogy(
        SNR_RANGE,
        sfbc,
        marker='s',
        linewidth=2,
        label='2TX-1RX SFBC'
    )

    ax.set_title(mod_name)
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("BER")
    ax.grid(True, which='both')
    ax.legend()

plt.tight_layout()
plt.show()
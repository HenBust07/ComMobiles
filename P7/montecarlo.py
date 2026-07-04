import numpy as np
import matplotlib.pyplot as plt

from modulaciones import *
from mod_ofdm import *
from canal import *
from rx_ofdm import *
from ber import *

# ============================================================
# MONTE CARLO BER vs SNR
# Comparación 1RX vs 2RX vs 4RX
# Canal real (ground truth)
# ============================================================

# ---------------- Parámetros ----------------
BW = 20e6
DELTA_F = 15e3
CP_TYPE = "normal"
PILOT_SPACE = 8
PILOT_VALUE = 1 + 0j
CANAL_OP = 2

N_RUNS = 50
N_BITS = 100000

SNR_RANGE = np.arange(-5, 31, 2)

# ---------------- OFDM ----------------
Nsub = int(BW / DELTA_F)
Nfft = next_power_of_2(Nsub)

pilot_idx_arr = np.arange(0, Nfft, PILOT_SPACE)
N_data = Nfft - len(pilot_idx_arr)

# Resultados
ber_1rx = []
ber_2rx = []
ber_4rx = []

print("=" * 80)
print("Monte Carlo BER vs SNR")
print("Comparación 1RX vs 2RX vs 4RX")
print("QPSK | OFDM | Multipath Rayleigh")
print("=" * 80)

# ============================================================
# Simulación Monte Carlo
# ============================================================

for snr in SNR_RANGE:

    ber_runs_1rx = []
    ber_runs_2rx = []
    ber_runs_4rx = []

    print(f"\nSNR = {snr} dB")

    for _ in range(N_RUNS):

        # ====================================================
        # TX
        # ====================================================
        bits_tx = np.random.randint(0, 2, N_BITS)

        symbols = qpsk_mod(bits_tx)

        parallel_symbols = serial_to_parallel(symbols, N_data)

        ofdm_mat, pilot_idx, data_idx = insert_pilots(
            parallel_symbols,
            Nfft,
            PILOT_SPACE,
            PILOT_VALUE
        )

        ofdm_time = ifft_ofdm(ofdm_mat)

        ofdm_cp, Ncp = add_cyclic_prefix(ofdm_time, CP_TYPE)

        tx_signal = parallel_to_serial(ofdm_cp)

        sym_len = Nfft + Ncp

        # ====================================================
        # CASO 1RX
        # ====================================================
        rx_signal, h = canal(tx_signal, snr, CANAL_OP, divrx=1)

        rx_par = rx_serial_to_parallel(rx_signal, sym_len)
        rx_nocp = remove_cp(rx_par, Ncp)
        rx_freq = fft_ofdm(rx_nocp)

        H = np.fft.fft(h, Nfft)
        H_full = np.tile(H, (rx_freq.shape[0], 1))

        equalized = rx_freq / (H_full + 1e-12)

        rx_data = extract_data(equalized, data_idx)

        rx_bits = qpsk_demod(rx_data.flatten())[:len(bits_tx)]

        ber1, _ = calcular_ber(bits_tx, rx_bits)

        ber_runs_1rx.append(ber1)

        # ====================================================
        # CASO 2RX
        # ====================================================
        rx1, h1, rx2, h2 = canal(tx_signal, snr, CANAL_OP, divrx=2)

        rx_freqs = []
        channels = []

        for rx, h in [(rx1, h1), (rx2, h2)]:
            rx_par = rx_serial_to_parallel(rx, sym_len)
            rx_nocp = remove_cp(rx_par, Ncp)
            rx_freq = fft_ofdm(rx_nocp)

            H = np.fft.fft(h, Nfft)
            H_full = np.tile(H, (rx_freq.shape[0], 1))

            rx_freqs.append(rx_freq)
            channels.append(H_full)

        numerator = (
            np.conj(channels[0]) * rx_freqs[0]
            +
            np.conj(channels[1]) * rx_freqs[1]
        )

        denominator = (
            np.abs(channels[0])**2
            +
            np.abs(channels[1])**2
            +
            1e-12
        )

        equalized_mrc = numerator / denominator

        rx_data_mrc = extract_data(equalized_mrc, data_idx)

        rx_bits_mrc = qpsk_demod(rx_data_mrc.flatten())[:len(bits_tx)]

        ber2, _ = calcular_ber(bits_tx, rx_bits_mrc)

        ber_runs_2rx.append(ber2)

        # ====================================================
        # CASO 4RX
        # ====================================================
        rx1, h1, rx2, h2, rx3, h3, rx4, h4 = canal(
            tx_signal,
            snr,
            CANAL_OP,
            divrx=4
        )

        rx_list = [rx1, rx2, rx3, rx4]
        h_list = [h1, h2, h3, h4]

        rx_freqs = []
        channels = []

        for rx, h in zip(rx_list, h_list):

            rx_par = rx_serial_to_parallel(rx, sym_len)
            rx_nocp = remove_cp(rx_par, Ncp)
            rx_freq = fft_ofdm(rx_nocp)

            H = np.fft.fft(h, Nfft)
            H_full = np.tile(H, (rx_freq.shape[0], 1))

            rx_freqs.append(rx_freq)
            channels.append(H_full)

        numerator = (
            np.conj(channels[0]) * rx_freqs[0]
            +
            np.conj(channels[1]) * rx_freqs[1]
            +
            np.conj(channels[2]) * rx_freqs[2]
            +
            np.conj(channels[3]) * rx_freqs[3]
        )

        denominator = (
            np.abs(channels[0])**2
            +
            np.abs(channels[1])**2
            +
            np.abs(channels[2])**2
            +
            np.abs(channels[3])**2
            +
            1e-12
        )

        equalized_mrc_4 = numerator / denominator

        rx_data_mrc_4 = extract_data(equalized_mrc_4, data_idx)

        rx_bits_mrc_4 = qpsk_demod(
            rx_data_mrc_4.flatten()
        )[:len(bits_tx)]

        ber4, _ = calcular_ber(bits_tx, rx_bits_mrc_4)

        ber_runs_4rx.append(ber4)

    mean_1rx = np.mean(ber_runs_1rx)
    mean_2rx = np.mean(ber_runs_2rx)
    mean_4rx = np.mean(ber_runs_4rx)

    ber_1rx.append(mean_1rx)
    ber_2rx.append(mean_2rx)
    ber_4rx.append(mean_4rx)

    print(f"1RX BER: {mean_1rx:.4e}")
    print(f"2RX BER: {mean_2rx:.4e}")
    print(f"4RX BER: {mean_4rx:.4e}")

# ============================================================
# Gráfica
# ============================================================

plt.figure(figsize=(10, 6))

plt.semilogy(SNR_RANGE, np.clip(ber_1rx, 1e-6, 1),
             marker='o', linewidth=2, label='1 RX')

plt.semilogy(SNR_RANGE, np.clip(ber_2rx, 1e-6, 1),
             marker='s', linewidth=2, label='2 RX (MRC)')

plt.semilogy(SNR_RANGE, np.clip(ber_4rx, 1e-6, 1),
             marker='^', linewidth=2, label='4 RX (MRC)')

plt.grid(True, which='both', alpha=0.4)
plt.xlabel("SNR (dB)")
plt.ylabel("BER")
plt.title(
    "BER vs SNR — Comparación 1RX vs 2RX vs 4RX\n"
    "QPSK | OFDM | Multipath Rayleigh"
)

plt.legend()
plt.tight_layout()
plt.savefig("comparacion_1rx_2rx_4rx.png", dpi=150)
plt.show()

# ============================================================
# Tabla
# ============================================================

print("\n" + "=" * 80)
print("TABLA RESUMEN")
print("=" * 80)

for snr, b1, b2, b4 in zip(SNR_RANGE, ber_1rx, ber_2rx, ber_4rx):
    print(
        f"SNR={snr:>3} dB | "
        f"1RX={b1:.6e} | "
        f"2RX={b2:.6e} | "
        f"4RX={b4:.6e}"
    )

print("=" * 80)

# import numpy as np
# import matplotlib.pyplot as plt

# from modulaciones import *
# from mod_ofdm import *
# from canal import *
# from rx_ofdm import *
# from ber import *

# # ============================================================
# # MONTE CARLO BER vs SNR
# # Comparación 1RX vs 2RX (MRC)
# # Canal real (ground truth)
# # ============================================================

# # ---------------- Parámetros ----------------
# BW = 20e6
# DELTA_F = 15e3
# CP_TYPE = "normal"
# PILOT_SPACE = 8
# PILOT_VALUE = 1 + 0j
# CANAL_OP = 2  # Multipath Rayleigh

# N_RUNS = 50
# N_BITS = 100000

# SNR_RANGE = np.arange(-5, 31, 2)

# # ---------------- OFDM ----------------
# Nsub = int(BW / DELTA_F)
# Nfft = next_power_of_2(Nsub)

# pilot_idx_arr = np.arange(0, Nfft, PILOT_SPACE)
# N_data = Nfft - len(pilot_idx_arr)

# # Resultados
# ber_1rx = []
# ber_2rx = []

# print("=" * 70)
# print("Monte Carlo BER vs SNR")
# print("Comparación 1RX vs 2RX (MRC)")
# print("QPSK | OFDM | Multipath Rayleigh")
# print("=" * 70)

# # ============================================================
# # Simulación Monte Carlo
# # ============================================================

# for snr in SNR_RANGE:

#     ber_runs_1rx = []
#     ber_runs_2rx = []

#     print(f"\nSNR = {snr} dB")

#     for _ in range(N_RUNS):

#         # ====================================================
#         # TX
#         # ====================================================
#         bits_tx = np.random.randint(0, 2, N_BITS)

#         symbols = qpsk_mod(bits_tx)

#         parallel_symbols = serial_to_parallel(symbols, N_data)

#         ofdm_mat, pilot_idx, data_idx = insert_pilots(
#             parallel_symbols,
#             Nfft,
#             PILOT_SPACE,
#             PILOT_VALUE
#         )

#         ofdm_time = ifft_ofdm(ofdm_mat)

#         ofdm_cp, Ncp = add_cyclic_prefix(ofdm_time, CP_TYPE)

#         tx_signal = parallel_to_serial(ofdm_cp)

#         sym_len = Nfft + Ncp

#         # ====================================================
#         # CASO 1RX
#         # ====================================================
#         rx_signal, h = canal(
#             tx_signal,
#             snr,
#             CANAL_OP,
#             divrx=1
#         )

#         rx_par = rx_serial_to_parallel(rx_signal, sym_len)
#         rx_nocp = remove_cp(rx_par, Ncp)
#         rx_freq = fft_ofdm(rx_nocp)

#         # Canal real
#         H = np.fft.fft(h, Nfft)

#         # Expandir para todos los símbolos OFDM
#         H_full = np.tile(H, (rx_freq.shape[0], 1))

#         # Zero Forcing ideal
#         equalized = rx_freq / (H_full + 1e-12)

#         rx_data = extract_data(equalized, data_idx)

#         rx_bits = qpsk_demod(
#             rx_data.flatten()
#         )[:len(bits_tx)]

#         ber1, _ = calcular_ber(bits_tx, rx_bits)

#         ber_runs_1rx.append(ber1)

#         # ====================================================
#         # CASO 2RX (MRC)
#         # ====================================================
#         rx1, h1, rx2, h2 = canal(
#             tx_signal,
#             snr,
#             CANAL_OP,
#             divrx=2
#         )

#         # Rama 1
#         rx_par1 = rx_serial_to_parallel(rx1, sym_len)
#         rx_nocp1 = remove_cp(rx_par1, Ncp)
#         rx_freq1 = fft_ofdm(rx_nocp1)

#         # Rama 2
#         rx_par2 = rx_serial_to_parallel(rx2, sym_len)
#         rx_nocp2 = remove_cp(rx_par2, Ncp)
#         rx_freq2 = fft_ofdm(rx_nocp2)

#         # Canales reales
#         H1 = np.fft.fft(h1, Nfft)
#         H2 = np.fft.fft(h2, Nfft)

#         H1_full = np.tile(H1, (rx_freq1.shape[0], 1))
#         H2_full = np.tile(H2, (rx_freq2.shape[0], 1))

#         # MRC ideal
#         numerator = (
#             np.conj(H1_full) * rx_freq1
#             +
#             np.conj(H2_full) * rx_freq2
#         )

#         denominator = (
#             np.abs(H1_full) ** 2
#             +
#             np.abs(H2_full) ** 2
#             +
#             1e-12
#         )

#         equalized_mrc = numerator / denominator

#         rx_data_mrc = extract_data(equalized_mrc, data_idx)

#         rx_bits_mrc = qpsk_demod(
#             rx_data_mrc.flatten()
#         )[:len(bits_tx)]

#         ber2, _ = calcular_ber(bits_tx, rx_bits_mrc)

#         ber_runs_2rx.append(ber2)

#     mean_1rx = np.mean(ber_runs_1rx)
#     mean_2rx = np.mean(ber_runs_2rx)

#     ber_1rx.append(mean_1rx)
#     ber_2rx.append(mean_2rx)

#     print(f"1RX BER: {mean_1rx:.4e}")
#     print(f"2RX BER: {mean_2rx:.4e}")

# # ============================================================
# # Gráfica
# # ============================================================

# ber_1rx = np.array(ber_1rx)
# ber_2rx = np.array(ber_2rx)

# plt.figure(figsize=(10, 6))

# plt.semilogy(
#     SNR_RANGE,
#     np.clip(ber_1rx, 1e-6, 1),
#     marker='o',
#     linewidth=2,
#     label='1 RX (ZF ideal)'
# )

# plt.semilogy(
#     SNR_RANGE,
#     np.clip(ber_2rx, 1e-6, 1),
#     marker='s',
#     linewidth=2,
#     label='2 RX (MRC ideal)'
# )

# plt.grid(True, which='both', alpha=0.4)
# plt.xlabel("SNR (dB)")
# plt.ylabel("BER")
# plt.title(
#     "BER vs SNR — Comparación 1RX vs 2RX\n"
#     "QPSK | OFDM | Multipath Rayleigh"
# )

# plt.legend()
# plt.tight_layout()
# plt.savefig("comparacion_1rx_vs_2rx_ideal.png", dpi=150)
# plt.show()

# # ============================================================
# # Tabla
# # ============================================================

# print("\n" + "=" * 70)
# print("TABLA RESUMEN")
# print("=" * 70)

# for snr, b1, b2 in zip(SNR_RANGE, ber_1rx, ber_2rx):
#     print(
#         f"SNR={snr:>3} dB | "
#         f"1RX={b1:.6e} | "
#         f"2RX={b2:.6e}"
#     )

# print("=" * 70)

# import numpy as np
# import matplotlib.pyplot as plt
# from modulaciones import *
# from mod_ofdm import *
# from canal import *
# from rx_ofdm import *
# from ber import *

# # ============================================================
# #   MONTE CARLO — BER vs SNR
# #   Escenario: BW=20MHz, df=15KHz, CP extendido, Pilotos
# #   Canal: 1=AWGN  2=Rayleigh Multipath
# # ============================================================

# # ---- Parámetros fijos ----
# BW          = 5e6
# DELTA_F     = 15e3
# CP_TYPE     = "extendido"
# PILOT_SPACE = 8
# PILOT_VALUE = 1 + 0j
# N_RUNS      = 50          # realizaciones Monte Carlo por punto SNR
# N_BITS      = 100000       # bits por corrida
# CANAL_OP    = 1           # 2 = Rayleigh Multipath

# # Barrido de SNR
# SNR_RANGE = np.arange(-10, 30, 2)   # -10 a 15 dB paso 1

# # ---- Parámetros OFDM derivados ----
# Nfft   = next_power_of_2(int(BW / DELTA_F))
# p_idx  = np.arange(0, Nfft, PILOT_SPACE)
# N_data = Nfft - len(p_idx)

# print("=" * 60)
# print("  MONTE CARLO BER vs SNR — OFDM")
# print("=" * 60)
# print(f"  Nfft={Nfft}  Datos/sym={N_data}  Pilotos={len(p_idx)}")
# print(f"  CP={CP_TYPE}  Canal={'Rayleigh' if CANAL_OP==2 else 'AWGN'}")
# print(f"  Ejecuciones={N_RUNS}  Bits/corrida={N_BITS}")
# print(f"  SNR: {SNR_RANGE[0]} a {SNR_RANGE[-1]} dB")
# print("=" * 60)

# # ---- Modulaciones ----
# mods = [
#     ("QPSK",  qpsk_mod,  qpsk_demod,  2),
#     ("16QAM", qam16_mod, qam16_demod, 4),
#     ("64QAM", qam64_mod, qam64_demod, 6),
# ]

# # Almacenar resultados
# resultados = {m[0]: {"mean": [], "std": [], "ic95": []} for m in mods}

# # ============================================================
# #   BUCLE PRINCIPAL
# # ============================================================

# for mod_name, mod_fn, demod_fn, bps in mods:

#     print(f"\n  [{mod_name}] simulando {len(SNR_RANGE)} puntos SNR × {N_RUNS} corridas...")

#     for snr in SNR_RANGE:

#         ber_corridas = []

#         for _ in range(N_RUNS):

#             # 1) Bits aleatorios
#             bits_tx = np.random.randint(0, 2, N_BITS)

#             # 2) Modular
#             symbols = mod_fn(bits_tx)

#             # 3) Serial → Paralelo
#             parallel = serial_to_parallel(symbols, N_data)

#             # 4) Pilotos
#             ofdm_mat, pilot_idx, data_idx = insert_pilots(
#                 parallel, Nfft, PILOT_SPACE, PILOT_VALUE
#             )

#             # 5) IFFT
#             ofdm_time = ifft_ofdm(ofdm_mat)

#             # 6) Cyclic Prefix
#             ofdm_cp, Ncp = add_cyclic_prefix(ofdm_time, CP_TYPE)

#             # 7) P → S
#             tx_signal = parallel_to_serial(ofdm_cp)

#             # 8) Canal
#             rx_signal, _ = canal(tx_signal, snr, CANAL_OP)

#             # 9) RX
#             sym_len  = Nfft + Ncp
#             rx_par   = rx_serial_to_parallel(rx_signal, sym_len)
#             rx_nocp  = remove_cp(rx_par, Ncp)
#             rx_freq  = fft_ofdm(rx_nocp)

#             # 10) Ecualización ZF
#             H_est    = estimate_channel(rx_freq, pilot_idx, PILOT_VALUE)
#             H_interp = interpolate_channel(H_est, pilot_idx, Nfft)
#             equalized = zero_forcing(rx_freq, H_interp)
#             rx_data  = extract_data(equalized, data_idx)

#             # 11) Demodular
#             rx_bits = demod_fn(rx_data.flatten())[:len(bits_tx)]

#             # 12) BER
#             ber_v, _ = calcular_ber(bits_tx, rx_bits)
#             ber_corridas.append(ber_v)

#         arr  = np.array(ber_corridas)
#         mean = np.mean(arr)
#         std  = np.std(arr)
#         ic95 = 1.96 * std / np.sqrt(N_RUNS)

#         resultados[mod_name]["mean"].append(mean)
#         resultados[mod_name]["std"].append(std)
#         resultados[mod_name]["ic95"].append(ic95)

#         print(f"    SNR={snr:>4}dB  BER={mean:.4e}  ±{ic95:.2e}")

#     # Convertir a numpy
#     for k in resultados[mod_name]:
#         resultados[mod_name][k] = np.array(resultados[mod_name][k])

# # ============================================================
# #   GRAFICAS
# # ============================================================

# colores = {"QPSK": "steelblue", "16QAM": "darkorange", "64QAM": "green"}
# markers = {"QPSK": "o", "16QAM": "s", "64QAM": "^"}

# # ---- Figura 1: Escala logarítmica (estándar académico) ----
# fig, axes = plt.subplots(1, 2, figsize=(14, 6))
# fig.suptitle(
#     f"BER vs SNR — Monte Carlo (N={N_RUNS} corridas)\n"
#     f"OFDM | BW=20MHz | Δf=15kHz | CP {CP_TYPE} | Pilotos | "
#     f"Canal={'Rayleigh' if CANAL_OP==2 else 'AWGN'}",
#     fontsize=12
# )

# # Subplot izquierdo: escala LOG (académico)
# ax = axes[0]
# for mod_name, *_ in mods:
#     r   = resultados[mod_name]
#     col = colores[mod_name]
#     mk  = markers[mod_name]

#     # Evitar log(0)
#     mean_safe = np.clip(r["mean"], 1e-6, 1)

#     ax.semilogy(SNR_RANGE, mean_safe,
#                 color=col, marker=mk, linewidth=2,
#                 markersize=5, label=mod_name)

#     # Banda de confianza 95%
#     lo = np.clip(r["mean"] - r["ic95"], 1e-6, 1)
#     hi = np.clip(r["mean"] + r["ic95"], 1e-6, 1)
#     ax.fill_between(SNR_RANGE, lo, hi, color=col, alpha=0.15)

# ax.set_title("Escala Logarítmica (estándar)")
# ax.set_xlabel("SNR (dB)")
# ax.set_ylabel("BER")
# ax.legend()
# ax.grid(which='both', alpha=0.4)
# ax.set_xlim([SNR_RANGE[0], SNR_RANGE[-1]])
# ax.set_ylim([1e-3, 1])

# # Subplot derecho: escala lineal (como tu gráfica original)
# ax2 = axes[1]
# for mod_name, *_ in mods:
#     r   = resultados[mod_name]
#     col = colores[mod_name]
#     mk  = markers[mod_name]

#     ax2.plot(SNR_RANGE, r["mean"],
#              color=col, marker=mk, linewidth=2,
#              markersize=5, label=mod_name)

#     ax2.fill_between(
#         SNR_RANGE,
#         np.clip(r["mean"] - r["ic95"], 0, 1),
#         np.clip(r["mean"] + r["ic95"], 0, 1),
#         color=col, alpha=0.15
#     )

# ax2.set_title("Escala Lineal")
# ax2.set_xlabel("SNR (dB)")
# ax2.set_ylabel("BER")
# ax2.legend()
# ax2.grid(alpha=0.4)
# ax2.set_xlim([SNR_RANGE[0], SNR_RANGE[-1]])
# ax2.set_ylim([0, 0.8])

# plt.tight_layout()
# plt.savefig("ber_vs_snr_montecarlo.png", dpi=150, bbox_inches='tight')
# plt.show()

# # ---- Figura 2: Solo log, más limpia para el informe ----
# fig2, ax3 = plt.subplots(figsize=(8, 6))

# for mod_name, *_ in mods:
#     r   = resultados[mod_name]
#     col = colores[mod_name]
#     mk  = markers[mod_name]

#     mean_safe = np.clip(r["mean"], 1e-6, 1)
#     lo = np.clip(r["mean"] - r["ic95"], 1e-6, 1)
#     hi = np.clip(r["mean"] + r["ic95"], 1e-6, 1)

#     ax3.semilogy(SNR_RANGE, mean_safe,
#                  color=col, marker=mk, linewidth=2,
#                  markersize=6, label=mod_name)
#     ax3.fill_between(SNR_RANGE, lo, hi, color=col, alpha=0.2,
#                      label=f'{mod_name} IC 95%')

# ax3.set_title(
#     f"BER vs SNR — Monte Carlo N={N_RUNS}\n"
#     f"OFDM BW=20MHz | Canal {'Rayleigh' if CANAL_OP==2 else 'AWGN'} | CP {CP_TYPE}",
#     fontsize=11
# )
# ax3.set_xlabel("SNR (dB)", fontsize=12)
# ax3.set_ylabel("BER", fontsize=12)
# ax3.legend(fontsize=10)
# ax3.grid(which='both', alpha=0.4)
# ax3.set_xlim([SNR_RANGE[0], SNR_RANGE[-1]])
# ax3.set_ylim([1e-4, 1])

# plt.tight_layout()
# plt.savefig("ber_vs_snr_informe.png", dpi=150, bbox_inches='tight')
# plt.show()

# # ============================================================
# #   TABLA RESUMEN — SNR clave
# # ============================================================

# snr_clave = [-10, -5, 0, 5, 10, 15]
# print("\n" + "=" * 70)
# print("  TABLA BER PROMEDIO POR SNR (Monte Carlo)")
# print("=" * 70)
# print(f"  {'SNR':>6}  {'QPSK':>12}  {'16QAM':>12}  {'64QAM':>12}")
# print(f"  {'-'*6}  {'-'*12}  {'-'*12}  {'-'*12}")

# for snr in snr_clave:
#     idx = np.where(SNR_RANGE == snr)[0]
#     if len(idx) == 0:
#         continue
#     i = idx[0]
#     row = f"  {snr:>5}dB"
#     for mod_name, *_ in mods:
#         row += f"  {resultados[mod_name]['mean'][i]:>12.4e}"
#     print(row)

# print("=" * 70)
# print(f"\n  Sombra = Intervalo de Confianza 95% (IC = 1.96 * std / sqrt(N))")
# print(f"  Archivos guardados: ber_vs_snr_montecarlo.png, ber_vs_snr_informe.png")
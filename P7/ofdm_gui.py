"""
OFDM System — Interfaz Gráfica
Requiere: matplotlib, numpy, pillow, tkinter (incluido en Python estándar)
Coloca este archivo en la misma carpeta que:
  modulaciones.py, mod_ofdm.py, canal.py, rx_ofdm.py, ber.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import threading
import os
import sys
import math

# ── Colores y fuentes ────────────────────────────────────────────────────────
BG        = "#F5F5F2"          # blanco roto cálido
PANEL     = "#FFFFFF"
ACCENT    = "#1A1A2E"          # azul noche
ACCENT2   = "#16213E"
BTN_TX    = "#1B4F72"          # azul acero
BTN_RX    = "#1E8449"          # verde profundo
BTN_EXIT  = "#922B21"
BTN_BACK  = "#5D6D7E"
BTN_NEXT  = "#1B4F72"
TEXT_MAIN = "#1A1A2E"
TEXT_SUB  = "#5D6D7E"
BORDER    = "#D5D8DC"
ENTRY_BG  = "#FAFAFA"

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_SUB    = ("Georgia", 11)
FONT_LABEL  = ("Helvetica", 10)
FONT_BOLD   = ("Helvetica", 10, "bold")
FONT_BTN    = ("Helvetica", 11, "bold")
FONT_SMALL  = ("Helvetica", 9)


# ── Helpers ──────────────────────────────────────────────────────────────────
def styled_button(parent, text, command, bg, fg="#FFFFFF", width=18, padx=10, pady=6):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, font=FONT_BTN,
        relief="flat", cursor="hand2",
        activebackground=bg, activeforeground=fg,
        padx=padx, pady=pady, width=width,
        bd=0
    )
    def on_enter(e): btn.config(bg=_darken(bg))
    def on_leave(e): btn.config(bg=bg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def _darken(hex_color, factor=0.85):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return "#{:02x}{:02x}{:02x}".format(int(r*factor), int(g*factor), int(b*factor))

def separator(parent, pady=8):
    f = tk.Frame(parent, height=1, bg=BORDER)
    f.pack(fill="x", padx=24, pady=pady)

def section_label(parent, text):
    tk.Label(parent, text=text, font=FONT_BOLD, bg=PANEL,
             fg=TEXT_SUB).pack(anchor="w", padx=24, pady=(10,2))


# ── App principal ────────────────────────────────────────────────────────────
class OFDMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema OFDM")
        self.configure(bg=BG)
        self.state("zoomed")          # maximizado al inicio
        self.minsize(900, 600)
        self.resizable(True, True)

        # Variables de configuración
        self.img_path   = tk.StringVar(value="")
        self.mod_var    = tk.StringVar(value="QPSK")
        self.bw_var     = tk.StringVar(value="20")
        self.df_var     = tk.StringVar(value="15")
        self.cp_var     = tk.StringVar(value="Normal")
        self.eq_var     = tk.StringVar(value="Sin ecualización")
        self.canal_var  = tk.StringVar(value="AWGN")
        self.snr_var    = tk.StringVar(value="20")
        self.divrx_var    = tk.StringVar(value="Una antena")

        # Resultados compartidos TX→RX
        self._tx_results = {}
        self._rx_results = {}

        self._show_menu()

    # ── Utilidades de frame ───────────────────────────────────────────────────
    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # =========================================================================
    # MENÚ PRINCIPAL
    # =========================================================================
    def _show_menu(self):
        self._clear()

        # Layout: columna izquierda (logo+título) | columna derecha (parámetros)
        root_frame = tk.Frame(self, bg=BG)
        root_frame.pack(fill="both", expand=True)
        root_frame.columnconfigure(0, weight=1)
        root_frame.columnconfigure(1, weight=2)
        root_frame.rowconfigure(0, weight=1)

        # ── Panel izquierdo ──────────────────────────────────────────────────
        left = tk.Frame(root_frame, bg=ACCENT, width=320)
        left.grid(row=0, column=0, sticky="nsew")
        left.pack_propagate(False)
        left.columnconfigure(0, weight=1)

        # Título
        tk.Label(left, text="OFDM", font=("Georgia", 44, "bold"),
                 bg=ACCENT, fg="#FFFFFF").pack(pady=(50, 0))
        tk.Label(left, text="Sistema de Comunicaciones\nDigitales", font=("Georgia", 12),
                 bg=ACCENT, fg="#A9B7C6", justify="center").pack(pady=(6, 30))

        # Diagrama decorativo SVG-like con Canvas
        canvas = tk.Canvas(left, width=240, height=120, bg=ACCENT,
                           highlightthickness=0)
        canvas.pack(pady=10)
        self._draw_ofdm_diagram(canvas)

        tk.Label(left, text="Configuración del sistema\nOFDM multiportadora", font=FONT_SMALL,
                 bg=ACCENT, fg="#6C8097", justify="center").pack(pady=(20, 0))

        # Versión
        tk.Label(left, text="v2.0", font=FONT_SMALL, bg=ACCENT,
                 fg="#3D5A80").pack(side="bottom", pady=16)

        # ── Panel derecho (scroll) ───────────────────────────────────────────
        right_outer = tk.Frame(root_frame, bg=BG)
        right_outer.grid(row=0, column=1, sticky="nsew")
        right_outer.rowconfigure(0, weight=1)
        right_outer.columnconfigure(0, weight=1)

        canvas_r = tk.Canvas(right_outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_outer, orient="vertical", command=canvas_r.yview)
        canvas_r.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas_r.pack(side="left", fill="both", expand=True)

        right = tk.Frame(canvas_r, bg=BG)
        win_id = canvas_r.create_window((0, 0), window=right, anchor="nw")

        def _on_configure(e):
            canvas_r.configure(scrollregion=canvas_r.bbox("all"))
            canvas_r.itemconfig(win_id, width=canvas_r.winfo_width())
        right.bind("<Configure>", _on_configure)
        canvas_r.bind("<Configure>", lambda e: canvas_r.itemconfig(win_id, width=e.width))
        canvas_r.bind_all("<MouseWheel>", lambda e: canvas_r.yview_scroll(-1*(e.delta//120), "units"))

        # Título panel derecho
        tk.Label(right, text="Parámetros de Entrada", font=FONT_TITLE,
                 bg=BG, fg=TEXT_MAIN).pack(anchor="w", padx=40, pady=(40, 4))
        tk.Label(right, text="Configure el sistema antes de transmitir", font=FONT_SUB,
                 bg=BG, fg=TEXT_SUB).pack(anchor="w", padx=40, pady=(0, 20))

        # ── Card de parámetros ───────────────────────────────────────────────
        card = tk.Frame(right, bg=PANEL, bd=0, relief="flat",
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=40, pady=(0, 16))

        # Imagen
        section_label(card, "📁  IMAGEN DE ENTRADA")
        img_frame = tk.Frame(card, bg=PANEL)
        img_frame.pack(fill="x", padx=24, pady=(0, 8))
        self._img_label = tk.Label(img_frame, textvariable=self.img_path,
                                   font=FONT_SMALL, bg=PANEL, fg=TEXT_SUB,
                                   wraplength=300, anchor="w")
        self._img_label.pack(side="left", fill="x", expand=True)
        styled_button(img_frame, "Cargar imagen", self._load_image,
                      bg="#3D5A80", width=14).pack(side="right", padx=(8,0))

        separator(card)

        # Modulación
        section_label(card, "📡  MODULACIÓN")
        self._radio_group(card, self.mod_var, ["QPSK", "16QAM", "64QAM"])

        separator(card)

        # BW y Δf
        section_label(card, "📶  ANCHO DE BANDA Y SEPARACIÓN")
        row1 = tk.Frame(card, bg=PANEL)
        row1.pack(fill="x", padx=24, pady=(0, 8))
        self._entry_field(row1, "BW (MHz):", self.bw_var, width=8)
        tk.Frame(row1, width=20, bg=PANEL).pack(side="left")
        self._radio_inline(row1, "Δf:", self.df_var, [("15 kHz", "15"), ("7.5 kHz", "7.5")])

        separator(card)

        # CP
        section_label(card, "🔄  PREFIJO CÍCLICO")
        self._radio_group(card, self.cp_var, ["Normal", "Extendido"], horizontal=True)

        separator(card)

        # Ecualización
        section_label(card, "⚖️  ECUALIZACIÓN")
        self._radio_group(card, self.eq_var,
                          ["Sin ecualización", "Con pilotos"], horizontal=True)

        separator(card)

        # Canal
        section_label(card, "🌐  CANAL")
        self._radio_group(card, self.canal_var,
                          ["AWGN", "Multipath"], horizontal=True)

        separator(card)

        # SNR
        section_label(card, "📊  SNR (dB)")
        snr_frame = tk.Frame(card, bg=PANEL)
        snr_frame.pack(fill="x", padx=24, pady=(0, 16))
        self._entry_field(snr_frame, "SNR [dB]:", self.snr_var, width=8)
        
        separator(card)

        #Div Rx
        section_label(card, ">= >=  Diversidad en Rx")
        self._radio_group(card, self.divrx_var,
                          ["Una antena", "Dos antenas"], horizontal=True)
        print("Div Rx: ", self.divrx_var.get())

        separator(card)

        # ── Botones TX / RX ──────────────────────────────────────────────────
        btn_frame = tk.Frame(right, bg=BG)
        btn_frame.pack(pady=(10, 6), padx=40, anchor="e")

        styled_button(btn_frame, "▶  TRANSMITIR (TX)",
                      self._run_tx, BTN_TX, width=22).pack(side="left", padx=(0, 12))
        styled_button(btn_frame, "◀  RECIBIR (RX)",
                      self._run_rx, BTN_RX, width=22).pack(side="left")
        styled_button(btn_frame, "📋 RESUMEN", self._run_summary, "#3D5A80", width=18).pack(side="left", padx=6)

        # Salir
        exit_frame = tk.Frame(right, bg=BG)
        exit_frame.pack(fill="x", padx=40, pady=(0, 30))
        styled_button(exit_frame, "Salir", self.destroy,
                      BTN_EXIT, width=10).pack(side="right")

    # ── Widgets reutilizables ─────────────────────────────────────────────────
    def _radio_group(self, parent, var, options, horizontal=False):
        f = tk.Frame(parent, bg=PANEL)
        f.pack(fill="x", padx=24, pady=(0, 8))
        for opt in options:
            rb = tk.Radiobutton(f, text=opt, variable=var, value=opt,
                                font=FONT_LABEL, bg=PANEL, fg=TEXT_MAIN,
                                activebackground=PANEL, selectcolor="#D6EAF8",
                                cursor="hand2")
            if horizontal:
                rb.pack(side="left", padx=(0, 16))
            else:
                rb.pack(anchor="w")

    def _radio_inline(self, parent, label, var, options):
        tk.Label(parent, text=label, font=FONT_BOLD, bg=PANEL,
                 fg=TEXT_MAIN).pack(side="left")
        for text, val in options:
            tk.Radiobutton(parent, text=text, variable=var, value=val,
                           font=FONT_LABEL, bg=PANEL, fg=TEXT_MAIN,
                           activebackground=PANEL, selectcolor="#D6EAF8",
                           cursor="hand2").pack(side="left", padx=(4, 8))

    def _entry_field(self, parent, label, var, width=10):
        tk.Label(parent, text=label, font=FONT_BOLD, bg=PANEL,
                 fg=TEXT_MAIN).pack(side="left")
        e = tk.Entry(parent, textvariable=var, font=FONT_LABEL,
                     width=width, bg=ENTRY_BG, fg=TEXT_MAIN,
                     relief="solid", bd=1)
        e.pack(side="left", padx=(6, 0))

    def _draw_ofdm_diagram(self, canvas):
        """Pequeño diagrama decorativo de bloques OFDM."""
        blocks = ["DATOS", "MOD", "IFFT", "CP", "CANAL", "FFT", "MRC", "DEM"]
        colors = ["#2E4057", "#3D7EAA", "#1B6CA8", "#0D4F8B",
                  "#2E4057", "#1B6CA8", "#C0392B" , "#3D7EAA"]
        W = 240
        bw, bh, gap = 26, 20, 4
        total = len(blocks) * bw + (len(blocks)-1) * gap
        x0 = (W - total) // 2
        y = 50
        for i, (blk, col) in enumerate(zip(blocks, colors)):
            x = x0 + i*(bw+gap)
            canvas.create_rectangle(x, y, x+bw, y+bh, fill=col, outline="")
            canvas.create_text(x+bw//2, y+bh//2, text=blk,
                               font=("Helvetica", 6, "bold"), fill="white")
            if i < len(blocks)-1:
                canvas.create_line(x+bw, y+bh//2, x+bw+gap, y+bh//2,
                                   fill="#6C8097", width=1,
                                   arrow=tk.LAST, arrowshape=(4,5,2))
        canvas.create_text(W//2, 90, text="Sistema OFDM", fill="#6C8097",
                           font=("Helvetica", 8))

    # ── Carga de imagen ───────────────────────────────────────────────────────
    def _load_image(self):
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                       ("Todos", "*.*")]
        )
        if path:
            self.img_path.set(path)

    # ── Lectura y validación de parámetros ────────────────────────────────────
    def _get_params(self):
        errors = []
        if not self.img_path.get() or not os.path.exists(self.img_path.get()):
            errors.append("Seleccione una imagen válida.")
        try:
            bw = float(self.bw_var.get())
            if bw <= 0: raise ValueError
        except ValueError:
            errors.append("BW debe ser un número positivo.")
            bw = 20.0
        try:
            snr = float(self.snr_var.get())
        except ValueError:
            errors.append("SNR debe ser un número.")
            snr = 20.0
        if errors:
            messagebox.showerror("Error de configuración", "\n".join(errors))
            return None

        mod_map   = {"QPSK": 1, "16QAM": 2, "64QAM": 3}
        df_map    = {"15": 15e3, "7.5": 7.5e3}
        cp_map    = {"Normal": "normal", "Extendido": "extendido"}
        eq_map    = {"Sin ecualización": False, "Con pilotos": True}
        canal_map = {"AWGN": 1, "Multipath": 2}

        return {
            "img_path":   self.img_path.get(),
            "mod_op":     mod_map[self.mod_var.get()],
            "mod_name":   self.mod_var.get(),
            "bw":         bw * 1e6,
            "delta_f":    df_map[self.df_var.get()],
            "cp_type":    cp_map[self.cp_var.get()],
            "use_pilots": eq_map[self.eq_var.get()],
            "canal_op":   canal_map[self.canal_var.get()],
            "snr_db":     snr,
        }
    
    # =========================================================================
    # Proceso Resumen
    # =========================================================================
    def _run_summary(self):
        #Tx----------------
        p = self._get_params()
        if p is None:
            return

        # Importar módulos OFDM (del mismo directorio)
        try:
            from modulaciones import qpsk_mod, qam16_mod, qam64_mod
            from mod_ofdm import (next_power_of_2, serial_to_parallel,
                                  insert_pilots, ifft_ofdm,
                                  add_cyclic_prefix, parallel_to_serial)
        except ImportError as e:
            messagebox.showerror("Error de importación",
                                 f"No se encontraron los módulos OFDM:\n{e}\n\n"
                                 "Asegúrese de que ofdm_gui.py esté en la misma\n"
                                 "carpeta que modulaciones.py, mod_ofdm.py, etc.")
            return

        from PIL import Image

        # Leer imagen
        img      = Image.open(p["img_path"])
        img_gray = img.convert('L')
        img_arr  = np.array(img_gray)
        bits     = np.unpackbits(img_arr)

        alto, ancho = img_arr.shape[:2]
        total_bits = len(bits)

        # Modulación
        if p["mod_op"] == 1:
            symbols = qpsk_mod(bits)
            bits_por_sub = 2
        elif p["mod_op"] == 2:
            symbols = qam16_mod(bits)
            bits_por_sub = 4      # 16QAM
        else:
            symbols = qam64_mod(bits)
            bits_por_sub = 6      # 64QAM

        # Parámetros OFDM
        Nsub   = int(p["bw"] / p["delta_f"])
        Nfft   = next_power_of_2(Nsub)
        pilot_spacing  = 8
        pilot_idx_arr  = np.arange(0, Nfft, pilot_spacing)
        data_subcarriers = Nfft - len(pilot_idx_arr)

        n_data = data_subcarriers if p["use_pilots"] else Nfft

        n_pilots = len(pilot_idx_arr) if p["use_pilots"] else 0

        parallel_symbols = serial_to_parallel(symbols, n_data)

        if p["use_pilots"]:
            parallel_symbols, pilot_idx, data_idx = insert_pilots(
                parallel_symbols, Nfft, pilot_spacing)
        else:
            pilot_idx, data_idx = None, None

        bits_por_simbolo = len(data_idx) * bits_por_sub
        n_ofdm = math.ceil(
            total_bits / bits_por_simbolo
        )
        ofdm_time = ifft_ofdm(parallel_symbols)
        ofdm_cp, Ncp = add_cyclic_prefix(ofdm_time, p["cp_type"])
        tx_signal = parallel_to_serial(ofdm_cp)

        # PAPR
        papr_data = self._calc_papr(ofdm_cp)

        # Guardar todo para RX
        self._tx_results = {
            "n_data":           n_data,  #se muestra esto
            "n_pilots":         n_pilots,#se muestra esto
            "Nfft":             Nfft,    #se muestra esto
            "img_width":        ancho,   #se muestra esto
            "img_height":       alto,    #se muestra esto
            "total_bits": total_bits,    #se muestra esto
            "bits_por_simbolo": bits_por_simbolo, #se muestra esto
            "n_ofdm":           n_ofdm,
            "img_arr":          img_arr,
            "bits":             bits,
            "symbols":          symbols,
            "tx_signal":        tx_signal,
            "ofdm_cp":          ofdm_cp,
            "Nfft":             Nfft,
            "Ncp":              Ncp,
            "pilot_idx":        pilot_idx,
            "data_idx":         data_idx,
            "papr_data":        papr_data,
            "bw":               p["bw"],
            "use_pilots":       p["use_pilots"],
            "mod_name":         p["mod_name"],
            "mod_op":           p["mod_op"],
            "canal_op":         p["canal_op"],
            "snr_db":           p["snr_db"],
            "cp_type":          p["cp_type"],
        }

        #Rx-------------    
        if not self._tx_results:
            messagebox.showinfo("Información",
                                "Primero ejecute el TX para generar la señal.")
            return
        try:
            from canal   import canal
            from rx_ofdm import (rx_serial_to_parallel, remove_cp, fft_ofdm,
                                 estimate_channel, interpolate_channel,
                                 zero_forcing, extract_data)
            from ber     import calcular_ber
            from modulaciones import qpsk_demod, qam16_demod, qam64_demod
        except ImportError as e:
            messagebox.showerror("Error", f"No se encontraron módulos:\n{e}")
            return

        t = self._tx_results

        #Segun el tipo de recepción seleccionada, se procederá dependiendo una o dos antenas
        divrx = self.divrx_var.get()
        # Longitud símbolo OFDM
        symbol_len = t["Nfft"] + t["Ncp"]

        if divrx == "Una antena":
            rx_signal, h = canal(t["tx_signal"], t["snr_db"], t["canal_op"], divrx=1)
            rx_parallel = rx_serial_to_parallel(rx_signal, symbol_len)
            rx_no_cp    = remove_cp(rx_parallel, t["Ncp"])
            rx_freq     = fft_ofdm(rx_no_cp)

            if not t["use_pilots"]:
                rx_data = rx_freq
            else:
                H_est    = estimate_channel(rx_freq, t["pilot_idx"], 1+0j)
                H_interp = interpolate_channel(H_est, t["pilot_idx"], t["Nfft"])
                equalized= zero_forcing(rx_freq, H_interp)
                rx_data  = extract_data(equalized, t["data_idx"])

            rx_symbols = rx_data.flatten()

            if t["mod_op"] == 1:
                rx_bits = qpsk_demod(rx_symbols)
            elif t["mod_op"] == 2:
                rx_bits = qam16_demod(rx_symbols)
            else:
                rx_bits = qam64_demod(rx_symbols)

            rx_bits  = rx_bits[:len(t["bits"])]
            rx_bytes = np.packbits(rx_bits)
            rx_image = rx_bytes.reshape(t["img_arr"].shape)

            ber, errores = calcular_ber(t["bits"], rx_bits)

            print("una antena, BER =", ber)

            self._rx_results = {
                #"rx_symbols": rx_symbols,
                #"rx_image":   rx_image,
                #"rx_signal":  rx_signal,
                #"h":          h,
                "ber":        ber, #se muestra esto 
                "errores":    errores,
                "divrx":      "Una antena" #se muestra esto
            }

        elif divrx == "Dos antenas":
            rx_signal1, h1, rx_signal2, h2 = canal(t["tx_signal"], t["snr_db"], t["canal_op"], divrx=2)

            rx_parallel1 = rx_serial_to_parallel(rx_signal1, symbol_len)
            rx_no_cp1    = remove_cp(rx_parallel1, t["Ncp"])
            rx_freq1     = fft_ofdm(rx_no_cp1)

            rx_parallel2 = rx_serial_to_parallel(rx_signal2, symbol_len)
            rx_no_cp2    = remove_cp(rx_parallel2, t["Ncp"])
            rx_freq2     = fft_ofdm(rx_no_cp2)

            if not t["use_pilots"]:
                rx_data1 = rx_freq1
                rx_data2 = rx_freq2
            else:
                #Estimación de los canales de cada antena
                H_est1 = estimate_channel(rx_freq1,t["pilot_idx"],1+0j)
                H_est2 = estimate_channel(rx_freq2,t["pilot_idx"],1+0j)

                #print("pilot_idx shape =", np.shape(t["pilot_idx"]))
                #print("pilot_idx dtype =", type(t["pilot_idx"]))
                #print("H_est1 shape =", H_est1.shape)
                #print("H_est2 shape =", H_est2.shape)
                #print("pilot_idx", t["pilot_idx"])
                #Interpolar los canales
                H_interp1 = interpolate_channel(H_est1,t["pilot_idx"],t["Nfft"])
                H_interp2 = interpolate_channel(H_est2,t["pilot_idx"],t["Nfft"])

                mrc_freq = (np.conj(H_interp1) * rx_freq1 + np.conj(H_interp2) * rx_freq2)
                #aqui simplemente se combinó ambas antenas dando más peso a la rama que tiene mejor canal.
                #luego se normaliza
                equalized = mrc_freq / (np.abs(H_interp1)**2 + np.abs(H_interp2)**2 + 1e-12)

                rx_data = extract_data(equalized,t["data_idx"])

                rx_symbols = rx_data.flatten()

                if t["mod_op"] == 1:
                    rx_bits = qpsk_demod(rx_symbols)

                elif t["mod_op"] == 2:
                    rx_bits = qam16_demod(rx_symbols)

                else:
                    rx_bits = qam64_demod(rx_symbols)

                rx_bits  = rx_bits[:len(t["bits"])]
                #rx_bytes = np.packbits(rx_bits)
                #rx_image = rx_bytes.reshape(t["img_arr"].shape)
                print("Antes del BER del receptor")
                ber, errores = calcular_ber(t["bits"], rx_bits)

                print("dos antenas, BER =", ber)

                self._rx_results = {
                    #"rx_symbols": rx_symbols,
                    #"rx_image":   rx_image,
                    #"rx_signal1":  rx_signal1,
                    #"rx_signal2":  rx_signal2,
                    #"h1":          h1,
                    #"h2":          h2,
                    "ber":        ber, #se muestra esto
                    #"errores":    errores,
                    "divrx":      "Dos antenas" #se muestra esto
                }

        self._show_summary_view()

    # =========================================================================
    # Vista Resumen
    # =========================================================================
    def _show_summary_view(self):
        self._clear()
        t = self._tx_results
        r = self._rx_results

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True)
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(main, bg=ACCENT, height=56)
        header.pack(fill="x")
        tk.Label(header, text="  TRANSMISOR (TX) — " + t["mod_name"],
                 font=("Georgia", 14, "bold"), bg=ACCENT,
                 fg="#FFFFFF").pack(side="left", padx=20, pady=12)

        # ── Área de scroll ────────────────────────────────────────────────────
        scroll_area = tk.Frame(main, bg=BG)
        scroll_area.pack(fill="both", expand=True)
        scroll_area.rowconfigure(0, weight=1)
        scroll_area.columnconfigure(0, weight=1)

        canvas = tk.Canvas(scroll_area, bg=BG, highlightthickness=0)
        vbar   = ttk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")

        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())
        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
       
        info = (
            f"Resolución: {t['img_width']} x {t['img_height']} px\n"
            f"Total bits: {t['total_bits']:,}\n"
            f"Nfft: {t['Nfft']}\n"
            f"Subportadoras piloto: {t['n_pilots']}\n"
            f"Subportadoras de datos: {t['n_data']}\n"
            f"Bits por símbolo OFDM: {t['bits_por_simbolo']:,}\n"
            f"Símbolos OFDM requeridos: {t['n_ofdm']:,}"
        )

        info_card = tk.Frame(
            inner,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        info_card.pack(fill="x", padx=12, pady=12)
        
        # TÍTULO
        tk.Label(
            info_card,
            text="Información de la Transmisión",
            font=("Georgia", 12, "bold"),
            bg=PANEL,
            fg=ACCENT
        ).pack(anchor="w", padx=15, pady=(10,5))


        tk.Label(
            info_card,
            text=info,
            justify="left",
            font=("Segoe UI", 11),
            bg=PANEL,
            fg=TEXT_MAIN
        ).pack(anchor="w", padx=15, pady=15)

        infoRx = (
            f"BER: {r['ber']}\n"
        )

        infoRx_card = tk.Frame(
            inner,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        infoRx_card.pack(fill="x", padx=12, pady=12)
        
        # TÍTULO
        tk.Label(
            infoRx_card,
            text="Información en el Receptor",
            font=("Georgia", 12, "bold"),
            bg=PANEL,
            fg=ACCENT
        ).pack(anchor="w", padx=15, pady=(10,5))


        tk.Label(
            infoRx_card,
            text=infoRx,
            justify="left",
            font=("Segoe UI", 11),
            bg=PANEL,
            fg=TEXT_MAIN
        ).pack(anchor="w", padx=15, pady=15)

        # ── Footer ───────────────────────────────────────────────────────────
        footer = tk.Frame(main, bg=PANEL, height=56,
                          highlightbackground=BORDER, highlightthickness=1)
        footer.pack(fill="x", side="bottom")
        styled_button(footer, "← Regresar al Menú", self._show_menu,
                      BTN_BACK, width=20).pack(side="left",  padx=20, pady=10)
    

    # =========================================================================
    # PROCESO TX
    # =========================================================================
    def _run_tx(self):
        p = self._get_params()
        if p is None:
            return

        # Importar módulos OFDM (del mismo directorio)
        try:
            from modulaciones import qpsk_mod, qam16_mod, qam64_mod
            from mod_ofdm import (next_power_of_2, serial_to_parallel,
                                  insert_pilots, ifft_ofdm,
                                  add_cyclic_prefix, parallel_to_serial)
        except ImportError as e:
            messagebox.showerror("Error de importación",
                                 f"No se encontraron los módulos OFDM:\n{e}\n\n"
                                 "Asegúrese de que ofdm_gui.py esté en la misma\n"
                                 "carpeta que modulaciones.py, mod_ofdm.py, etc.")
            return

        from PIL import Image

        # Leer imagen
        img      = Image.open(p["img_path"])
        img_gray = img.convert('L')
        img_arr  = np.array(img_gray)
        bits     = np.unpackbits(img_arr)

        alto, ancho = img_arr.shape[:2]
        total_bits = len(bits)

        # Modulación
        if p["mod_op"] == 1:
            symbols = qpsk_mod(bits)
            bits_por_sub = 2
        elif p["mod_op"] == 2:
            symbols = qam16_mod(bits)
            bits_por_sub = 4      # 16QAM
        else:
            symbols = qam64_mod(bits)
            bits_por_sub = 6      # 64QAM

        # Parámetros OFDM
        Nsub   = int(p["bw"] / p["delta_f"])
        Nfft   = next_power_of_2(Nsub)
        pilot_spacing  = 8
        pilot_idx_arr  = np.arange(0, Nfft, pilot_spacing)
        data_subcarriers = Nfft - len(pilot_idx_arr)

        n_data = data_subcarriers if p["use_pilots"] else Nfft

        n_pilots = len(pilot_idx_arr) if p["use_pilots"] else 0

        parallel_symbols = serial_to_parallel(symbols, n_data)

        if p["use_pilots"]:
            parallel_symbols, pilot_idx, data_idx = insert_pilots(
                parallel_symbols, Nfft, pilot_spacing)
        else:
            pilot_idx, data_idx = None, None

        bits_por_simbolo = len(data_idx) * bits_por_sub
        n_ofdm = math.ceil(
            total_bits / bits_por_simbolo
        )
        ofdm_time = ifft_ofdm(parallel_symbols)
        ofdm_cp, Ncp = add_cyclic_prefix(ofdm_time, p["cp_type"])
        tx_signal = parallel_to_serial(ofdm_cp)

        # PAPR
        papr_data = self._calc_papr(ofdm_cp)

        # Guardar todo para RX
        self._tx_results = {
            "n_data":           n_data,
            "n_pilots":         n_pilots,
            "Nfft":             Nfft,
            "img_width":        ancho,
            "img_height":       alto,
            "total_bits": total_bits,
            "bits_por_simbolo": bits_por_simbolo,
            "n_ofdm":           n_ofdm,
            "img_arr":          img_arr,
            "bits":             bits,
            "symbols":          symbols,
            "tx_signal":        tx_signal,
            "ofdm_cp":          ofdm_cp,
            "Nfft":             Nfft,
            "Ncp":              Ncp,
            "pilot_idx":        pilot_idx,
            "data_idx":         data_idx,
            "papr_data":        papr_data,
            "bw":               p["bw"],
            "use_pilots":       p["use_pilots"],
            "mod_name":         p["mod_name"],
            "mod_op":           p["mod_op"],
            "canal_op":         p["canal_op"],
            "snr_db":           p["snr_db"],
            "cp_type":          p["cp_type"],
        }

        self._show_tx_view()

    def _calc_papr(self, ofdm_cp):
        signal   = ofdm_cp.flatten()
        pot_inst = np.abs(signal)**2
        papr_por_simbolo = []
        for i in range(ofdm_cp.shape[0]):
            s  = ofdm_cp[i]
            pi = np.abs(s)**2
            pm = np.mean(pi)
            pp = np.max(pi)
            if pm > 0:
                papr_por_simbolo.append(pp / pm)
        papr_por_simbolo = np.array(papr_por_simbolo)
        p_media  = np.mean(pot_inst)
        p_pico   = np.max(pot_inst)
        return {
            "pot_inst":         pot_inst,
            "p_media":          p_media,
            "p_pico":           p_pico,
            "papr_db":          10*np.log10(np.mean(papr_por_simbolo)),
            "papr_db_peor":     10*np.log10(np.max(papr_por_simbolo)),
            "n_muestras":       np.arange(len(pot_inst)),
            "papr_por_simbolo": papr_por_simbolo,
        }

    # =========================================================================
    # VISTA TX
    # =========================================================================
    def _show_tx_view(self):
        self._clear()
        t = self._tx_results

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True)
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(main, bg=ACCENT, height=56)
        header.pack(fill="x")
        tk.Label(header, text="  TRANSMISOR (TX) — " + t["mod_name"],
                 font=("Georgia", 14, "bold"), bg=ACCENT,
                 fg="#FFFFFF").pack(side="left", padx=20, pady=12)

        # ── Área de scroll ────────────────────────────────────────────────────
        scroll_area = tk.Frame(main, bg=BG)
        scroll_area.pack(fill="both", expand=True)
        scroll_area.rowconfigure(0, weight=1)
        scroll_area.columnconfigure(0, weight=1)

        canvas = tk.Canvas(scroll_area, bg=BG, highlightthickness=0)
        vbar   = ttk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")

        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())
        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # ── Gráficas ──────────────────────────────────────────────────────────
        plots = [
            ("Imagen Original",          self._fig_img_orig),
            ("Constelación TX — " + t["mod_name"], self._fig_constTX),
            ("Asignación de Pilotos OFDM", self._fig_pilots),
            ("Señal OFDM en Tiempo",     self._fig_ofdm_time),
            ("Espectro OFDM",            self._fig_spectrum),
            ("Potencia Instantánea OFDM",self._fig_papr),
        ]

        info = (
            f"Resolución: {t['img_width']} x {t['img_height']} px\n"
            f"Total bits: {t['total_bits']:,}\n"
            f"Nfft: {t['Nfft']}\n"
            f"Subportadoras piloto: {t['n_pilots']}\n"
            f"Subportadoras de datos: {t['n_data']}\n"
            f"Bits por símbolo OFDM: {t['bits_por_simbolo']:,}\n"
            f"Símbolos OFDM requeridos: {t['n_ofdm']:,}"
        )

        info_card = tk.Frame(
            inner,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        info_card.pack(fill="x", padx=12, pady=12)
        
        # TÍTULO
        tk.Label(
            info_card,
            text="Información de la Transmisión",
            font=("Georgia", 12, "bold"),
            bg=PANEL,
            fg=ACCENT
        ).pack(anchor="w", padx=15, pady=(10,5))


        tk.Label(
            info_card,
            text=info,
            justify="left",
            font=("Segoe UI", 11),
            bg=PANEL,
            fg=TEXT_MAIN
        ).pack(anchor="w", padx=15, pady=15)

        for title, fn in plots:
            self._add_plot_card(inner, title, fn, t)

        # ── Footer ───────────────────────────────────────────────────────────
        footer = tk.Frame(main, bg=PANEL, height=56,
                          highlightbackground=BORDER, highlightthickness=1)
        footer.pack(fill="x", side="bottom")
        styled_button(footer, "← Regresar al Menú", self._show_menu,
                      BTN_BACK, width=20).pack(side="left",  padx=20, pady=10)
        styled_button(footer, "Pasar a RX →", self._run_rx,
                      BTN_NEXT, width=16).pack(side="right", padx=20, pady=10)

    # =========================================================================
    # PROCESO RX
    # =========================================================================
    def _run_rx(self):
        if not self._tx_results:
            messagebox.showinfo("Información",
                                "Primero ejecute el TX para generar la señal.")
            return
        try:
            from canal   import canal
            from rx_ofdm import (rx_serial_to_parallel, remove_cp, fft_ofdm,
                                 estimate_channel, interpolate_channel,
                                 zero_forcing, extract_data)
            from ber     import calcular_ber
            from modulaciones import qpsk_demod, qam16_demod, qam64_demod
        except ImportError as e:
            messagebox.showerror("Error", f"No se encontraron módulos:\n{e}")
            return

        t = self._tx_results

        #Segun el tipo de recepción seleccionada, se procederá dependiendo una o dos antenas
        divrx = self.divrx_var.get()
        # Longitud símbolo OFDM
        symbol_len = t["Nfft"] + t["Ncp"]

        if divrx == "Una antena":
            rx_signal, h = canal(t["tx_signal"], t["snr_db"], t["canal_op"], divrx=1)
            rx_parallel = rx_serial_to_parallel(rx_signal, symbol_len)
            rx_no_cp    = remove_cp(rx_parallel, t["Ncp"])
            rx_freq     = fft_ofdm(rx_no_cp)

            if not t["use_pilots"]:
                rx_data = rx_freq
            else:
                H_est    = estimate_channel(rx_freq, t["pilot_idx"], 1+0j)
                H_interp = interpolate_channel(H_est, t["pilot_idx"], t["Nfft"])
                equalized= zero_forcing(rx_freq, H_interp)
                rx_data  = extract_data(equalized, t["data_idx"])

            rx_symbols = rx_data.flatten()

            if t["mod_op"] == 1:
                rx_bits = qpsk_demod(rx_symbols)
            elif t["mod_op"] == 2:
                rx_bits = qam16_demod(rx_symbols)
            else:
                rx_bits = qam64_demod(rx_symbols)

            rx_bits  = rx_bits[:len(t["bits"])]
            rx_bytes = np.packbits(rx_bits)
            rx_image = rx_bytes.reshape(t["img_arr"].shape)

            ber, errores = calcular_ber(t["bits"], rx_bits)

            print("una antena, BER =", ber)

            self._rx_results = {
                "rx_symbols": rx_symbols,
                "rx_image":   rx_image,
                "rx_signal":  rx_signal,
                "h":          h,
                "ber":        ber,
                "errores":    errores,
                "divrx": "Una antena"
            }
            self._show_rx_view()

        elif divrx == "Dos antenas":
            rx_signal1, h1, rx_signal2, h2 = canal(t["tx_signal"], t["snr_db"], t["canal_op"], divrx=2)

            rx_parallel1 = rx_serial_to_parallel(rx_signal1, symbol_len)
            rx_no_cp1    = remove_cp(rx_parallel1, t["Ncp"])
            rx_freq1     = fft_ofdm(rx_no_cp1)

            rx_parallel2 = rx_serial_to_parallel(rx_signal2, symbol_len)
            rx_no_cp2    = remove_cp(rx_parallel2, t["Ncp"])
            rx_freq2     = fft_ofdm(rx_no_cp2)

            if not t["use_pilots"]:
                rx_data1 = rx_freq1
                rx_data2 = rx_freq2
            else:
                #Estimación de los canales de cada antena
                H_est1 = estimate_channel(rx_freq1,t["pilot_idx"],1+0j)
                H_est2 = estimate_channel(rx_freq2,t["pilot_idx"],1+0j)

                print("pilot_idx shape =", np.shape(t["pilot_idx"]))
                print("pilot_idx dtype =", type(t["pilot_idx"]))
                print("H_est1 shape =", H_est1.shape)
                print("H_est2 shape =", H_est2.shape)
                print("pilot_idx", t["pilot_idx"])
                #Interpolar los canales
                H_interp1 = interpolate_channel(H_est1,t["pilot_idx"],t["Nfft"])
                H_interp2 = interpolate_channel(H_est2,t["pilot_idx"],t["Nfft"])

                mrc_freq = (np.conj(H_interp1) * rx_freq1 + np.conj(H_interp2) * rx_freq2)
                #aqui simplemente se combinó ambas antenas dando más peso a la rama que tiene mejor canal.
                #luego se normaliza
                equalized = mrc_freq / (np.abs(H_interp1)**2 + np.abs(H_interp2)**2 + 1e-12)

                rx_data = extract_data(equalized,t["data_idx"])

                rx_symbols = rx_data.flatten()

                if t["mod_op"] == 1:
                    rx_bits = qpsk_demod(rx_symbols)

                elif t["mod_op"] == 2:
                    rx_bits = qam16_demod(rx_symbols)

                else:
                    rx_bits = qam64_demod(rx_symbols)

                rx_bits  = rx_bits[:len(t["bits"])]
                rx_bytes = np.packbits(rx_bits)
                rx_image = rx_bytes.reshape(t["img_arr"].shape)

                ber2, errores = calcular_ber(t["bits"], rx_bits)

                print("dos antenas, BER =", ber2)

                self._rx_results = {
                    "rx_symbols": rx_symbols,
                    "rx_image":   rx_image,
                    "rx_signal1":  rx_signal1,
                    "rx_signal2":  rx_signal2,
                    "h1":          h1,
                    "h2":          h2,
                    "ber":        ber2,
                    "errores":    errores,
                    "divrx": "Dos antenas"
                }
        

            self._show_rx_view()
        # Canal
        #rx_signal, h = canal(t["tx_signal"], t["snr_db"], t["canal_op"])


        # MRC
        

        # RX OFDM
        

    # =========================================================================
    # VISTA RX
    # =========================================================================
    def _show_rx_view(self):
        self._clear()
        t = self._tx_results
        r = self._rx_results

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True)

        header = tk.Frame(main, bg=BTN_RX, height=56)
        header.pack(fill="x")
        tk.Label(header,
                 text=f"  RECEPTOR (RX) — {t['mod_name']} | BER = {r['ber']:.2e} | Errores = {r['errores']}",
                 font=("Georgia", 13, "bold"), bg=BTN_RX, fg="#FFFFFF"
                 ).pack(side="left", padx=20, pady=12)

        scroll_area = tk.Frame(main, bg=BG)
        scroll_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_area, bg=BG, highlightthickness=0)
        vbar   = ttk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")
        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())
        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        plots = [
            (f"Constelación RX {'Ecualizada' if t['use_pilots'] else 'Sin EQ'} — {t['mod_name']}",
             self._fig_constRX),
            (f"Imagen RX — {t['mod_name']} | BER={r['ber']:.2e}", self._fig_img_rx),
            ("TX vs RX OFDM",            self._fig_tx_vs_rx),
            ("Respuesta Impulso del Canal", self._fig_canal),
        ]

        combined = {"t": t, "r": r}
        for title, fn in plots:
            self._add_plot_card(inner, title, fn, combined)

        footer = tk.Frame(main, bg=PANEL, height=56,
                          highlightbackground=BORDER, highlightthickness=1)
        footer.pack(fill="x", side="bottom")
        styled_button(footer, "← Regresar al Menú", self._show_menu,
                      BTN_BACK, width=20).pack(side="left",  padx=20, pady=10)
        styled_button(footer, "← Volver al TX", self._show_tx_view,
                      BTN_TX, width=16).pack(side="right", padx=20, pady=10)

    # =========================================================================
    # TARJETA DE GRÁFICA con toolbar (zoom, pan, etc.)
    # =========================================================================
    def _add_plot_card(self, parent, title, fig_fn, data):
        card = tk.Frame(parent, bg=PANEL, bd=0,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=30, pady=10)

        tk.Label(card, text=title, font=("Georgia", 12, "bold"),
                 bg=PANEL, fg=TEXT_MAIN).pack(anchor="w", padx=16, pady=(12, 4))

        fig = fig_fn(data)
        fig.patch.set_facecolor(PANEL)

        fc = tk.Frame(card, bg=PANEL)
        fc.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        embed = FigureCanvasTkAgg(fig, master=fc)
        embed.draw()
        embed.get_tk_widget().pack(fill="both", expand=True)

        # Toolbar navegación (zoom, pan, guardar)
        tb_frame = tk.Frame(card, bg="#F0F0F0")
        tb_frame.pack(fill="x", padx=8)
        toolbar = NavigationToolbar2Tk(embed, tb_frame)
        toolbar.update()

    # =========================================================================
    # FUNCIONES DE FIGURAS
    # =========================================================================
    PLOT_H = 4.0  # altura figura en pulgadas

    def _make_fig(self, rows=1, cols=1, h=None):
        h = h or self.PLOT_H
        fig, axes = plt.subplots(rows, cols, figsize=(11, h))
        fig.patch.set_facecolor(PANEL)
        return fig, axes

    # -- TX -------------------------------------------------------------------
    def _fig_img_orig(self, t):
        fig, ax = self._make_fig(h=4)
        ax.imshow(t["img_arr"], cmap="gray")
        ax.set_title("Imagen Original", fontsize=11)
        ax.axis("off")
        fig.tight_layout()
        return fig

    def _fig_constTX(self, t):
        fig, ax = self._make_fig(h=4.5)
        s = t["symbols"][:5000]
        ax.scatter(np.real(s), np.imag(s), s=4, alpha=0.6, color=BTN_TX)
        ax.set_xlabel("I"); ax.set_ylabel("Q")
        ax.set_title(f"Constelación TX — {t['mod_name']}", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_aspect("equal")
        fig.tight_layout()
        return fig

    def _fig_pilots(self, t):
        fig, ax = self._make_fig(h=3)
        if t["use_pilots"] and t["pilot_idx"] is not None:
            carriers = np.zeros(t["Nfft"])
            carriers[t["pilot_idx"]] = 1
            ax.stem(carriers, markerfmt="C1o", linefmt="C1-", basefmt="k-")
            ax.set_title("Asignación de Pilotos OFDM", fontsize=11)
        else:
            ax.text(0.5, 0.5, "Sin pilotos (ecualización desactivada)",
                    ha="center", va="center", transform=ax.transAxes,
                    fontsize=11, color=TEXT_SUB)
            ax.set_title("Asignación de Pilotos OFDM", fontsize=11)
        ax.set_xlabel("Índice Subportadora"); ax.set_ylabel("Piloto")
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()
        return fig

    def _fig_ofdm_time(self, t):
        fig, ax = self._make_fig(h=3.5)
        sig = np.real(t["tx_signal"][:2000])
        ax.plot(sig, linewidth=0.8, color=BTN_TX)
        ax.set_title("Señal OFDM en Tiempo", fontsize=11)
        ax.set_xlabel("Muestras"); ax.set_ylabel("Amplitud")
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()
        return fig

    def _fig_spectrum(self, t):
        fig, ax = self._make_fig(h=3.5)
        spectrum = np.fft.fftshift(np.fft.fft(t["tx_signal"]))
        freq = np.linspace(-t["bw"]/2, t["bw"]/2, len(spectrum))
        ax.plot(freq/1e6, 20*np.log10(np.abs(spectrum)+1e-12),
                linewidth=0.8, color="#8E44AD")
        ax.set_title("Espectro OFDM", fontsize=11)
        ax.set_xlabel("Frecuencia [MHz]"); ax.set_ylabel("Magnitud [dB]")
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()
        return fig

    def _fig_papr(self, t):
        fig, ax = self._make_fig(h=3.5)
        pd = t["papr_data"]
        ax.plot(pd["n_muestras"], pd["pot_inst"],
                linewidth=0.6, color="#2E86C1", label="Potencia instantánea")
        ax.axhline(pd["p_media"], color="orange", linestyle="--", linewidth=1.4,
                   label=f'Promedio = {pd["p_media"]:.4f}')
        ax.axhline(pd["p_pico"],  color="red",    linestyle="--", linewidth=1.4,
                   label=f'Pico = {pd["p_pico"]:.4f}')
        pk = np.argmax(pd["pot_inst"])
        ax.plot(pk, pd["p_pico"], 'ro', markersize=5)
        ax.set_title(f'Potencia Instantánea OFDM — PAPR {pd["papr_db"]:.2f} dB', fontsize=11)
        ax.set_xlabel("Muestras"); ax.set_ylabel("Potencia")
        ax.legend(fontsize=8); ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()
        return fig

    # -- RX -------------------------------------------------------------------
    def _fig_constRX(self, data):
        t, r = data["t"], data["r"]
        fig, ax = self._make_fig(h=4.5)
        s = r["rx_symbols"][:5000]
        ax.scatter(np.real(s), np.imag(s), s=4, alpha=0.6, color=BTN_RX)
        ax.set_xlabel("Real"); ax.set_ylabel("Imag")
        label = "Ecualizada" if t["use_pilots"] else "Sin EQ"
        ax.set_title(f"Constelación RX {label} — {t['mod_name']}", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_aspect("equal")
        fig.tight_layout()
        return fig

    def _fig_img_rx(self, data):
        t, r = data["t"], data["r"]
        fig, ax = self._make_fig(h=4)
        ax.imshow(r["rx_image"], cmap="gray")
        ax.set_title(f"Imagen RX — {t['mod_name']} | BER={r['ber']:.2e}", fontsize=11)
        ax.axis("off")
        fig.tight_layout()
        return fig

    def _fig_tx_vs_rx(self, data):
        t, r = data["t"], data["r"]
        fig, ax = self._make_fig(h=3.5)
        ax.plot(np.real(t["tx_signal"][:1000]), linewidth=0.8,
                label="TX OFDM", color=BTN_TX)
        

        #ax.plot(np.real(r["rx_signal"][:1000]), linewidth=0.8,
        #        label="RX OFDM", color=BTN_RX, alpha=0.75)
        if r.get("divrx") == "Dos antenas":
            ax.plot(np.real(r["rx_signal1"][:1000]), linewidth=0.8, label="RX Ant 1", alpha=0.8)
            ax.plot(np.real(r["rx_signal2"][:1000]), linewidth=0.8, label="RX Ant 2", alpha=0.8)
        else:
            ax.plot(np.real(r["rx_signal"][:1000]), linewidth=0.8, label="RX OFDM", alpha=0.8)


        ax.set_title("TX vs RX OFDM", fontsize=11)
        ax.set_xlabel("Muestras"); ax.set_ylabel("Amplitud")
        ax.legend(fontsize=9); ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()
        return fig

    def _fig_canal(self, data):
        r = data["r"]
        fig, ax = self._make_fig(h=3.5)
        #h = r["h"]
        #ax.stem(np.abs(h), markerfmt="C3o", linefmt="C3-", basefmt="k-")
        if r.get("divrx") == "Dos antenas":
            ax.stem(np.arange(len(r["h1"])), np.abs(r["h1"]), markerfmt="C0o", linefmt="C0-", basefmt=" ")

            ax.stem(np.arange(len(r["h2"])), np.abs(r["h2"]), markerfmt="C1s", linefmt="C1-", basefmt=" ")

            ax.plot([], [], 'C0o-', label='Canal Antena 1')
            ax.plot([], [], 'C1s-', label='Canal Antena 2')

            ax.legend()

        else:

            h = r["h"]

            ax.stem(np.abs(h), markerfmt="C3o", linefmt="C3-", basefmt="k-")



        ax.set_title("Respuesta Impulso del Canal", fontsize=11)
        ax.set_xlabel("Tap"); ax.set_ylabel("|h[n]|")
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()
        return fig


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Añadir directorio del script al path para importar módulos OFDM
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    app = OFDMApp()
    app.mainloop()

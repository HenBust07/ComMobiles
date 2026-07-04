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
import os
import sys

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
        self.sfbc_var   = tk.StringVar(value="Desactivar")

        # Resultados compartidos TX→RX
        self._tx_results = {}
        self._rx_results = {}

        self._show_menu()

    # ── Utilidades de frame ───────────────────────────────────────────────────
    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # =========================================================================
    # EJECUTAR TX SEGÚN SFBC
    # =========================================================================
    def _run_all_tx(self):

        p = self._get_params()
        if p is None:
            return

        print("\n========== CONTROL TX ==========")
        print("[CTRL] SFBC:", p["use_sfbc"])

        # Siempre TX1
        print("\n========== INICIO TX1 ==========")
        self._run_tx1()

        # Solo si SFBC activo
        if p["use_sfbc"]:

            print("\n========== INICIO TX2 ==========")
            self._run_tx2()

        else:
            self._tx2_results = None
            print("[CTRL] TX2 desactivado")

        print("\n========== MOSTRANDO TX ==========")

        self._show_tx_view()

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
                          ["Sin ecualización", "Estimación de Canal"], horizontal=True)

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

        # SFCB
        section_label(card, "⚖️  SFCB")
        self._radio_group(card, self.sfbc_var,
                          ["Desactivar", "Activar"], horizontal=True)

        separator(card)



        # ── Botones TX / RX ──────────────────────────────────────────────────
        btn_frame = tk.Frame(right, bg=BG)
        btn_frame.pack(pady=(10, 6), padx=40, anchor="e")

        styled_button(
            btn_frame,
            "▶  TRANSMITIR (TX1+TX2)",
            self._run_all_tx,
            BTN_TX,
            width=22
        ).pack(side="left", padx=(0, 12))
        

        styled_button(btn_frame, "◀  RECIBIR (RX)",
                      self._run_rx, BTN_RX, width=22).pack(side="left")

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
        blocks = ["DATOS", "MOD", "SFBC","IFFT", "CP", "CANAL", "FFT", "DEM"]
        colors = ["#2E4057", "#3D7EAA", "#C0392B", "#1B6CA8", "#0D4F8B",
                  "#3D7EAA", "#1B6CA8", "#2E4057"]
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
        eq_map    = {"Sin ecualización": False, "Estimación de Canal": True}
        canal_map = {"AWGN": 1, "Multipath": 2}
        sfbc_map  = {"Desactivar": False, "Activar": True}

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
            "use_sfbc":   sfbc_map[self.sfbc_var.get()],
        }

    


    # =========================================================================
    # BLOQUE COMÚN TX
    # =========================================================================
    def _tx_common(self, p):

        try:
            from modulaciones import qpsk_mod, qam16_mod, qam64_mod
            from mod_ofdm import next_power_of_2

        except ImportError as e:
            messagebox.showerror(
                "Error de importación",
                f"No se encontraron módulos OFDM:\n{e}"
            )
            return None

        from PIL import Image

        print("\n========== TX COMMON ==========")

        # Leer imagen
        img = Image.open(p["img_path"])
        img_gray = img.convert('L')
        img_arr = np.array(img_gray)

        print("[COMMON] Shape imagen:", img_arr.shape)

        # Bits
        bits = np.unpackbits(img_arr)

        print("[COMMON] Total bits:", len(bits))
        print("[COMMON] Primeros 20 bits:", bits[:20])

        # Modulación
        if p["mod_op"] == 1:
            symbols = qpsk_mod(bits)
        elif p["mod_op"] == 2:
            symbols = qam16_mod(bits)
        else:
            symbols = qam64_mod(bits)

        print("[COMMON] Símbolos generados:", len(symbols))
        print("[COMMON] Primeros 10 símbolos:", symbols[:10])

        # ================================
        # SFBC (solo si está activado)
        # ================================
        use_sfbc = p["use_sfbc"]

        if use_sfbc:
            print("[TX COMMON] SFBC ACTIVADO")

            from sfbc import sfbc_encode
            symbols_tx1, symbols_tx2 = sfbc_encode(symbols)

            print("[TX COMMON] SFBC shape TX1:", len(symbols_tx1))
            print("[TX COMMON] SFBC shape TX2:", len(symbols_tx2))

        else:
            print("[TX COMMON] SFBC DESACTIVADO")

            symbols_tx1 = symbols
            symbols_tx2 = None

        # Parámetros base
        Nsub = int(p["bw"] / p["delta_f"])
        Nfft = next_power_of_2(Nsub)

        print("[COMMON] Nsub:", Nsub)
        print("[COMMON] Nfft:", Nfft)

        return {
            "img_arr": img_arr,
            "bits": bits,

            "symbols": symbols,          # opcional
            "symbols_tx1": symbols_tx1,  # importante
            "symbols_tx2": symbols_tx2 if p["use_sfbc"] else None,

            "Nfft": Nfft,
            "mod_op": p["mod_op"],
            "mod_name": p["mod_name"],
            "bw": p["bw"],
            "snr_db": p["snr_db"],
            "canal_op": p["canal_op"],
            "use_pilots": p["use_pilots"],
            "use_sfbc": p["use_sfbc"]
        }

    # =========================================================================
    # PROCESO TX1
    # =========================================================================
    def _run_tx1(self):
        p = self._get_params()
        if p is None:
            return

        common = self._tx_common(p)
        if common is None:
            return

        from mod_ofdm import (
            serial_to_parallel,
            insert_pilots,
            ifft_ofdm,
            add_cyclic_prefix,
            parallel_to_serial
        )

        import numpy as np

        print("\n========== TX1 ==========")

        # =========================
        # CONFIG OFDM
        # =========================
        pilot_spacing = 8
        pilot_idx_arr = np.arange(0, common["Nfft"], pilot_spacing)
        data_subcarriers = common["Nfft"] - len(pilot_idx_arr) #Calculo de cuantas portadoras quedan para datos

        n_data = data_subcarriers if p["use_pilots"] else common["Nfft"]

        print("[TX1] n_data:", n_data)

        # =========================
        # SFBC / NO SFBC
        # =========================
        symbols_tx1 = common.get("symbols_tx1", common["symbols"])

        print("[TX1] Symbols TX1:", len(symbols_tx1))

        # =========================
        # SERIAL → PARALLEL
        # =========================
        parallel_symbols = serial_to_parallel( #aqui se expande las portadoras de datos y se completa a 2048 portadoras añadiendo pilotos. 
            symbols_tx1,
            n_data
        )

        print("[TX1] Parallel shape:", parallel_symbols.shape)

        # =========================
        # PILOTOS (solo TX1 decide estructura OFDM)
        # =========================
        if p["use_pilots"]:
            parallel_symbols, pilot_idx, data_idx = insert_pilots(
                parallel_symbols,
                common["Nfft"],
                pilot_spacing
            )

            print("[TX1] Pilotos insertados")
            print("[TX1] pilot_idx:", pilot_idx)

        else:
            pilot_idx, data_idx = None, None
            print("[TX1] Sin pilotos")

        # =========================
        # OFDM
        # =========================
        ofdm_time = ifft_ofdm(parallel_symbols)
        print("[TX1] OFDM time shape:", ofdm_time.shape)

        ofdm_cp, Ncp = add_cyclic_prefix(
            ofdm_time,
            p["cp_type"]
        )

        print("[TX1] Ncp:", Ncp)

        tx_signal = parallel_to_serial(ofdm_cp)
        print("[TX1] TX len:", len(tx_signal))

        # =========================
        # PAPR
        # =========================
        papr_data = self._calc_papr(ofdm_cp)

        # =========================
        # STORE RESULTS
        # =========================
        self._tx1_results = {
            **common,
            "tx_signal": tx_signal,
            "ofdm_cp": ofdm_cp,
            "Ncp": Ncp,
            "pilot_idx": pilot_idx,
            "data_idx": data_idx,
            "papr_data": papr_data
        }

        print("========== FIN TX1 ==========\n")

    # =========================================================================
    # PROCESO TX2
    # =========================================================================
    def _run_tx2(self):
        p = self._get_params()
        if p is None:
            return

        common = self._tx_common(p)
        if common is None:
            return

        from mod_ofdm import (
            serial_to_parallel,
            insert_pilots,
            ifft_ofdm,
            add_cyclic_prefix,
            parallel_to_serial
        )

        import numpy as np

        print("\n========== TX2 ==========")

        # =========================
        # CONFIG OFDM
        # =========================
        pilot_spacing = 8
        pilot_idx_arr = np.arange(0, common["Nfft"], pilot_spacing)
        data_subcarriers = common["Nfft"] - len(pilot_idx_arr) #Calculo de cuantas portadoras quedan para datos

        n_data = data_subcarriers if p["use_pilots"] else common["Nfft"]

        print("[TX2] n_data:", n_data)

        # =========================
        # SFBC / NO SFBC
        # =========================
        if p["use_sfbc"]:
            symbols_tx2 = common["symbols_tx2"]
        else:
            symbols_tx2 = common["symbols"]

        print("[TX2] Symbols TX2:", len(symbols_tx2))

        # =========================
        # SERIAL → PARALLEL
        # =========================
        parallel_symbols = serial_to_parallel(
            symbols_tx2,
            n_data
        )

        print("[TX2] Parallel shape:", parallel_symbols.shape)

        # =========================
        # PILOTOS (igual lógica que TX1)
        # =========================
        if p["use_pilots"]:
            parallel_symbols, pilot_idx, data_idx = insert_pilots(
                parallel_symbols,
                common["Nfft"],
                pilot_spacing
            )

            print("[TX2] Pilotos insertados")
            print("[TX2] pilot_idx:", pilot_idx)

        else:
            pilot_idx, data_idx = None, None
            print("[TX2] Sin pilotos")

        # =========================
        # OFDM
        # =========================
        ofdm_time = ifft_ofdm(parallel_symbols)
        print("[TX2] OFDM time shape:", ofdm_time.shape)

        ofdm_cp, Ncp = add_cyclic_prefix(
            ofdm_time,
            p["cp_type"]
        )

        print("[TX2] Ncp:", Ncp)

        tx_signal = parallel_to_serial(ofdm_cp)
        print("[TX2] TX len:", len(tx_signal))

        # =========================
        # PAPR
        # =========================
        papr_data = self._calc_papr(ofdm_cp)

        # =========================
        # STORE RESULTS
        # =========================
        self._tx2_results = {
            **common,
            "tx_signal": tx_signal,
            "ofdm_cp": ofdm_cp,
            "Ncp": Ncp,
            "pilot_idx": pilot_idx,
            "data_idx": data_idx,
            "papr_data": papr_data
        }

        print("========== FIN TX2 ==========\n")


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
    # PROCESO RX (TX1 + TX2)
    # =========================================================================
    def _run_rx(self):

        if not hasattr(self, "_tx1_results") or not hasattr(self, "_tx2_results"):
            messagebox.showinfo(
                "Información",
                "Primero ejecute TX1 y TX2."
            )
            return

        try:
            from canal import canal
            from rx_ofdm import (
                rx_serial_to_parallel,
                remove_cp,
                fft_ofdm,
                estimate_channel,
                interpolate_channel,
                zero_forcing,
                extract_data
            )
            from ber import calcular_ber
            from modulaciones import (
                qpsk_demod,
                qam16_demod,
                qam64_demod
            )

        except ImportError as e:
            messagebox.showerror(
                "Error",
                f"No se encontraron módulos:\n{e}"
            )
            return

        t1 = self._tx1_results
        t2 = self._tx2_results

        print("\n========== RX ==========")

        # ==================================================
        # CANAL SEGÚN MODO
        # ==================================================
        if not t1["use_sfbc"]:

            print("[RX] Modo 1 antena (SFBC OFF)")
            print("[RX] Longitud TX1:", len(t1["tx_signal"]))
            rx_signal, h1 = canal(t1["tx_signal"],t1["snr_db"],t1["canal_op"])
            h2 = None
        else:
            print("[RX] Modo 2 antenas (SFBC ON)")
            print("[RX] Longitud TX1:", len(t1["tx_signal"]))
            print("[RX] Longitud TX2:", len(t2["tx_signal"]))
            rx_signal, h1, h2 = canal(t1["tx_signal"],t1["snr_db"],t1["canal_op"],t2["tx_signal"])
        print("[RX] Canal h1:", h1)

        if h2 is not None:
            print("[RX] Canal h2:", h2)

        print("[RX] RX signal len:", len(rx_signal))

        # ==================================================
        # RX OFDM (DECODIFICAR TX1)
        # ==================================================
        symbol_len = t1["Nfft"] + t1["Ncp"]
        rx_parallel = rx_serial_to_parallel(rx_signal,symbol_len)
        print("[RX] Parallel shape:", rx_parallel.shape)
        rx_no_cp = remove_cp(rx_parallel,t1["Ncp"])
        print("[RX] No CP shape:", rx_no_cp.shape)
        rx_freq = fft_ofdm(rx_no_cp)
        print("[RX] FFT shape:", rx_freq.shape)

        # ==================================================
        # ECUALIZACIÓN / ESTIMACIÓN
        # ==================================================
        if not t1["use_sfbc"]:

            # =============================================
            # CASO NORMAL (SISO)
            # =============================================
            if t1["pilot_idx"] is None:

                print("[RX] Sin pilotos")
                rx_data = rx_freq

            else:

                print("[RX] Con pilotos")
                H_est = estimate_channel(rx_freq,t1["pilot_idx"],1 + 0j)
                H_interp = interpolate_channel(H_est,t1["pilot_idx"],t1["Nfft"])
                equalized = zero_forcing(rx_freq,H_interp)
                rx_data = extract_data(equalized,t1["data_idx"])

        else:

            # =============================================
            # CASO SFBC
            # =============================================
            print("[RX] SFBC ACTIVADO")

            #Aqui no se puede hacer Y/H
            #porque en este punto se tiene: Y = H1*X1 + H2*X2

            # ------------------------------------------------
            # IMPORTANTE:
            # Para validar Alamouti usamos canal REAL
            # (no estimate_channel sobre la suma RX)
            # ------------------------------------------------

            #Se aprovecha que el canal se conoce y se simula la estimación de canal perfecta
            # Los convertimos a dominio frecuencia porque OFDM trabaja subportadora por subportadora
            H1_freq = np.fft.fft(h1,t1["Nfft"])
            H2_freq = np.fft.fft(h2,t1["Nfft"])

           
            # H1_freq y H2_freq tienen tamaño (Nfft,)
            # pero rx_freq tiene tamaño (num_ofdm_symbols, Nfft)

            # Para poder operar símbolo por símbolo,
            # repetimos el canal para cada símbolo OFDM recibido
            H1_interp_full = np.tile(H1_freq,(rx_freq.shape[0], 1))
            H2_interp_full = np.tile(H2_freq,(rx_freq.shape[0], 1))

            if t1["pilot_idx"] is None:

                print("[RX] Sin pilotos")
                # Si no hay pilotos:
                # usamos todo el bloque OFDM completo
                # (todas las subportadoras son datos)
                Y_data = rx_freq
                # El canal también se usa completo
                H1_interp = H1_interp_full
                H2_interp = H2_interp_full

            else:
                print("[RX] Con pilotos")
                # Si sí hay pilotos:
                # eliminamos esas posiciones para quedarnos solo con datos
                Y_data = extract_data(rx_freq,t1["data_idx"]) # Señal recibida solo en subportadoras de datos
                H1_interp = extract_data(H1_interp_full,t1["data_idx"]) # Canal TX1 solo en subportadoras de datos
                H2_interp = extract_data(H2_interp_full,t1["data_idx"]) # Canal TX2 solo en subportadoras de datos

        # ==================================================
        # SFBC DECODING
        # ==================================================
        if t1["use_sfbc"]:

            print("[RX] SFBC ACTIVADO")

            # TX1:
            # k   -> s1
            # k+1 -> -conj(s2)

            # TX2:
            # k   -> s2
            # k+1 -> conj(s1)

            # En recepción agrupamos por pares
            # para reconstruir s1 y s2
            Y1 = Y_data[:, 0::2]# Subportadoras pares (k)
            Y2 = Y_data[:, 1::2]# Subportadoras impares (k+1)

            # Canal correspondiente a TX1 en subportadoras pares
            # (h1[k])
            H1_even = H1_interp[:, 0::2]
            # Canal correspondiente a TX2 en subportadoras impares
            # (h2[k+1])
            H2_odd  = H2_interp[:, 1::2]

            # Decoder Alamouti correcto

            # ==================================================
            # COMBINADOR ALAMOUTI
            # ==================================================
            #
            # Y1 = h1*s1 + h2*s2
            # Y2 = -h1*conj(s2) + h2*conj(s1)
            #
            # Aprovechando ortogonalidad:
            #
            # s1_hat = conj(h1)*Y1 + h2*conj(Y2)
            # s2_hat = conj(h2)*Y1 - h1*conj(Y2)
            #
            # Esto separa los símbolos originales
            X1_hat = (np.conj(H1_even) * Y1 + H2_odd * np.conj(Y2))
            X2_hat = (np.conj(H2_odd) * Y1 - H1_even * np.conj(Y2))

            # ==================================================
            # NORMALIZACIÓN
            # ==================================================
            #
            # Alamouti introduce ganancia:
            # |h1|² + |h2|²
            #
            # La dividimos para recuperar amplitud original
            denom = (np.abs(H1_even)**2 + np.abs(H2_odd)**2)

            X1_hat /= denom
            X2_hat /= denom

            rx_data = np.zeros_like(Y_data,dtype=complex)

            rx_data[:, 0::2] = X1_hat
            rx_data[:, 1::2] = X2_hat

        else:

            print("[RX] SFBC OFF")


        rx_symbols = rx_data.flatten()

        print("[RX] Símbolos recibidos:", len(rx_symbols))
        print("[RX] Primeros símbolos:", rx_symbols[:10])

        # ==================================================
        # DEMODULACIÓN
        # ==================================================
        if t1["mod_op"] == 1:
            rx_bits = qpsk_demod(rx_symbols)

        elif t1["mod_op"] == 2:
            rx_bits = qam16_demod(rx_symbols)

        else:
            rx_bits = qam64_demod(rx_symbols)

        rx_bits = rx_bits[:len(t1["bits"])]

        print("[RX] Bits recuperados:", len(rx_bits))
        print("[RX] Primeros bits:", rx_bits[:20])

        # ==================================================
        # RECONSTRUCCIÓN IMAGEN
        # ==================================================
        rx_bytes = np.packbits(rx_bits)
        rx_image = rx_bytes.reshape(t1["img_arr"].shape)

        # ==================================================
        # BER
        # ==================================================

        print("TX symbols:", t1["symbols"][:10])
        print("RX symbols:", rx_symbols[:10])
        ber, errores = calcular_ber(
            t1["bits"],
            rx_bits
        )

        print("[RX] BER:", ber)
        print("[RX] Errores:", errores)

        self._rx_results = {
            "rx_symbols": rx_symbols,
            "rx_image": rx_image,
            "rx_signal": rx_signal,
            "h1": h1,
            "h2": h2,
            "ber": ber,
            "errores": errores
        }

        print("========== FIN RX ==========\n")

        self._show_rx_view()









    


    # =========================================================================
    # VISTA TX (TX1 + TX2)
    # =========================================================================
    def _show_tx_view(self):

        self._clear()

        t1 = self._tx1_results
        t2 = self._tx2_results
        sfbc_active = (t2 is not None)

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True)

        # HEADER
        header = tk.Frame(main, bg=ACCENT, height=56)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"  {'TX1 + TX2' if sfbc_active else 'TX1'} — {t1['mod_name']}",
            font=("Georgia", 14, "bold"),
            bg=ACCENT,
            fg="#FFFFFF"
        ).pack(side="left", padx=20, pady=12)

        # SCROLL
        scroll_area = tk.Frame(main, bg=BG)
        scroll_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_area, bg=BG, highlightthickness=0)
        vbar = ttk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)

        canvas.configure(yscrollcommand=vbar.set)

        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())

        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

        # ==================================================
        # SECCIÓN TX1
        # ==================================================
        tk.Label(
            inner,
            text="TRANSMISOR 1",
            font=("Georgia", 14, "bold"),
            bg=BG
        ).pack(pady=10)

        plots_tx1 = [
            ("TX1 - Imagen Original", self._fig_img_orig),
            ("TX1 - Constelación", self._fig_constTX),
            ("TX1 - Pilotos OFDM", self._fig_pilots),
            ("TX1 - Señal OFDM", self._fig_ofdm_time),
            ("TX1 - Espectro", self._fig_spectrum),
            ("TX1 - PAPR", self._fig_papr),
        ]

        for title, fn in plots_tx1:
            self._add_plot_card(inner, title, fn, t1)

        # ==================================================
        # SECCIÓN TX2 (solo si SFBC activo)
        # ==================================================
        if sfbc_active:

            tk.Label(
                inner,
                text="TRANSMISOR 2",
                font=("Georgia", 14, "bold"),
                bg=BG
            ).pack(pady=10)

            plots_tx2 = [
                ("TX2 - Constelación", self._fig_constTX),
                ("TX2 - Pilotos OFDM", self._fig_pilots),
                ("TX2 - Señal OFDM", self._fig_ofdm_time),
                ("TX2 - Espectro", self._fig_spectrum),
                ("TX2 - PAPR", self._fig_papr),
            ]

            for title, fn in plots_tx2:
                self._add_plot_card(inner, title, fn, t2)


        # ==================================================
        # FOOTER
        # ==================================================
        footer = tk.Frame(
            main,
            bg=PANEL,
            height=56,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        footer.pack(fill="x", side="bottom")

        styled_button(
            footer,
            "← Regresar al Menú",
            self._show_menu,
            BTN_BACK,
            width=20
        ).pack(side="left", padx=20, pady=10)

        styled_button(
            footer,
            "Pasar a RX →",
            self._run_rx,
            BTN_NEXT,
            width=16
        ).pack(side="right", padx=20, pady=10)

    # =========================================================================
    # VISTA RX (TX1 + TX2)
    # =========================================================================
    def _show_rx_view(self):

        self._clear()

        t1 = self._tx1_results
        t2 = self._tx2_results
        r = self._rx_results

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True)

        # HEADER
        header = tk.Frame(main, bg=BTN_RX, height=56)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"  RECEPTOR OFDM (TX1 + TX2) | BER={r['ber']:.2e} | Errores={r['errores']}",
            font=("Georgia", 13, "bold"),
            bg=BTN_RX,
            fg="#FFFFFF"
        ).pack(side="left", padx=20, pady=12)

        # SCROLL
        scroll_area = tk.Frame(main, bg=BG)
        scroll_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_area, bg=BG, highlightthickness=0)
        vbar = ttk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)

        canvas.configure(yscrollcommand=vbar.set)

        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())

        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

        # ==================================================
        # RESULTADO RX
        # ==================================================
        combined = {
            "t": t1,   # TX1 como referencia principal
            "t1": t1,
            "t2": t2,
            "r": r
        }

        plots = [
            ("Constelación RX", self._fig_constRX),
            ("Imagen Recuperada", self._fig_img_rx),
            ("TX1 vs RX", self._fig_tx_vs_rx),
            ("Señal Combinada RX", self._fig_rx_signal),
            ("Canal h1", self._fig_canal_h1)
        ]

        # Solo agregar h2 si existe
        if r["h2"] is not None:
            plots.append(
                ("Canal h2", self._fig_canal_h2)
            )
        for title, fn in plots:
            self._add_plot_card(inner, title, fn, combined)

        # FOOTER
        footer = tk.Frame(
            main,
            bg=PANEL,
            height=56,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        footer.pack(fill="x", side="bottom")

        styled_button(
            footer,
            "← Regresar al Menú",
            self._show_menu,
            BTN_BACK,
            width=20
        ).pack(side="left", padx=20, pady=10)

        styled_button(
            footer,
            "← Volver al TX",
            self._show_tx_view,
            BTN_TX,
            width=16
        ).pack(side="right", padx=20, pady=10)


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
    # =========================================================================
    # FIGURA CANAL H1
    # =========================================================================
    def _fig_canal_h1(self, data):

        r = data["r"]

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        h1 = r["h1"]

        ax.stem(np.abs(h1))
        ax.set_title("Respuesta impulso h1")
        ax.set_xlabel("Tap")
        ax.set_ylabel("|h1[n]|")
        ax.grid(True)

        return fig
    
    # =========================================================================
    # FIGURA CANAL H2
    # =========================================================================
    def _fig_canal_h2(self, data):

        r = data["r"]

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        h2 = r["h2"]

        ax.stem(np.abs(h2))
        ax.set_title("Respuesta impulso h2")
        ax.set_xlabel("Tap")
        ax.set_ylabel("|h2[n]|")
        ax.grid(True)

        return fig
    # =========================================================================
    # FIGURA SEÑAL RX
    # =========================================================================
    def _fig_rx_signal(self, data):

        r = data["r"]

        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)

        rx_signal = r["rx_signal"]

        N = min(2000, len(rx_signal))

        ax.plot(np.real(rx_signal[:N]))

        ax.set_title("Señal RX combinada (parte real)")
        ax.set_xlabel("Muestras")
        ax.set_ylabel("Amplitud")
        ax.grid(True)
        ax.set_xlim(0, 2000)
        ax.set_ylim(-0.05, 0.45)

        return fig
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
        ax.plot(np.real(r["rx_signal"][:1000]), linewidth=0.8,
                label="RX OFDM", color=BTN_RX, alpha=0.75)
        ax.set_title("TX vs RX OFDM", fontsize=11)
        ax.set_xlabel("Muestras"); ax.set_ylabel("Amplitud")
        ax.legend(fontsize=9); ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()
        return fig
    def _fig_canal(self, data):
        r = data["r"]
        fig, ax = self._make_fig(h=3.5)
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
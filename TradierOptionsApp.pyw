import tkinter as tk
from tkinter import ttk, messagebox, Listbox
import json
import requests
from datetime import datetime, timedelta
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import yfinance as yf
import math

class TradierOptionsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Option Selling Jaume")
        self.root.state('zoomed')  # Ventana maximizada en Windows
        
        # Configurar icono
        try:
            self.root.iconbitmap("wheel_icon.ico")
        except:
            pass  # Si no encuentra el icono, continuar sin él
        
        "Poner la Api propia de tu broker"

        self.api_token = None  # Se cargará desde config
        self.base_url = "https://api.tradier.com/v1"
        self.config_file = "app_config.json"
        
        # Cargar configuración guardada primero (inicializa variables)
        self.load_config()
        
        # Si no hay API token en config, usar el por defecto
        if not self.api_token:
            self.api_token = "s1pVW9EshLbwL6kGyJswWbATmXZF"
        
        # Aplicar tema Dark Professional después
        self.apply_dark_theme()
        
        # Cache para datos de volatilidad histórica
        self.iv_history_cache = {}
    
    def apply_dark_theme(self):
        """Aplica tema Dark Professional a toda la aplicación"""
        # Colores del tema oscuro profesional
        self.colors = {
            'bg_dark': '#1E1E1E',           # Fondo principal
            'bg_medium': '#252526',         # Fondo secundario
            'bg_light': '#2D2D30',          # Fondo elementos
            'bg_hover': '#3E3E42',          # Hover
            'fg_primary': '#E0E0E0',        # Texto principal
            'fg_secondary': '#CCCCCC',      # Texto secundario
            'fg_muted': '#858585',          # Texto apagado
            'accent_blue': '#0078D4',       # Azul corporativo
            'accent_blue_light': '#4A90E2', # Azul claro
            'success': '#00C853',           # Verde éxito
            'danger': '#F44336',            # Rojo peligro
            'warning': '#FF9800',           # Naranja advertencia
            'info': '#26A69A',              # Turquesa info
            'border': '#3E3E42',            # Bordes
        }
        
        # Configurar ventana principal
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Crear estilo TTK
        style = ttk.Style()
        style.theme_use('clam')
        
        # ========== CONFIGURACIÓN GENERAL ==========
        style.configure('.',
            background=self.colors['bg_dark'],
            foreground=self.colors['fg_primary'],
            bordercolor=self.colors['border'],
            darkcolor=self.colors['bg_medium'],
            lightcolor=self.colors['bg_light'],
            troughcolor=self.colors['bg_medium'],
            focuscolor=self.colors['accent_blue'],
            selectbackground=self.colors['accent_blue'],
            selectforeground=self.colors['fg_primary'],
            fieldbackground=self.colors['bg_light'],
            font=('Segoe UI', 10)
        )
        
        # ========== FRAMES ==========
        style.configure('TFrame',
            background=self.colors['bg_dark'],
            borderwidth=0
        )
        
        style.configure('TLabelframe',
            background=self.colors['bg_dark'],
            foreground=self.colors['fg_primary'],
            bordercolor=self.colors['border'],
            borderwidth=1,
            relief='solid'
        )
        
        style.configure('TLabelframe.Label',
            background=self.colors['bg_dark'],
            foreground=self.colors['accent_blue_light'],
            font=('Segoe UI', 10, 'bold')
        )
        
        # ========== LABELS ==========
        style.configure('TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['fg_primary'],
            font=('Segoe UI', 10)
        )
        
        # ========== BUTTONS ==========
        style.configure('TButton',
            background=self.colors['accent_blue'],
            foreground=self.colors['fg_primary'],
            borderwidth=0,
            focuscolor='none',
            padding=(15, 8),
            font=('Segoe UI', 10, 'bold')
        )
        
        style.map('TButton',
            background=[('active', self.colors['accent_blue_light']),
                       ('pressed', self.colors['bg_hover'])],
            foreground=[('disabled', self.colors['fg_muted'])]
        )
        
        # ========== NOTEBOOK (PESTAÑAS) ==========
        style.configure('TNotebook',
            background=self.colors['bg_dark'],
            borderwidth=0,
            tabmargins=[2, 5, 2, 0]
        )
        
        style.configure('TNotebook.Tab',
            background=self.colors['bg_medium'],
            foreground=self.colors['fg_secondary'],
            padding=[15, 8],
            borderwidth=0,
            font=('Segoe UI', 10, 'bold')
        )
        
        style.map('TNotebook.Tab',
            background=[('selected', self.colors['bg_light'])],
            foreground=[('selected', self.colors['accent_blue_light'])],
            padding=[('selected', [20, 12])],
            expand=[('selected', [1, 1, 1, 0])]
        )
        
        # ========== TREEVIEW (TABLAS) ==========
        style.configure('Treeview',
            background=self.colors['bg_light'],
            foreground=self.colors['fg_primary'],
            fieldbackground=self.colors['bg_light'],
            borderwidth=0,
            font=('Segoe UI', 9),
            rowheight=28
        )
        
        style.configure('Treeview.Heading',
            background=self.colors['bg_medium'],
            foreground=self.colors['accent_blue_light'],
            borderwidth=0,
            relief='flat',
            font=('Segoe UI', 10, 'bold')
        )
        
        style.map('Treeview',
            background=[('selected', self.colors['accent_blue'])],
            foreground=[('selected', self.colors['fg_primary'])]
        )
        
        style.map('Treeview.Heading',
            background=[('active', self.colors['bg_hover'])]
        )
        
        # ========== ENTRY ==========
        style.configure('TEntry',
            fieldbackground=self.colors['bg_light'],
            foreground=self.colors['fg_primary'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['bg_hover'],
            darkcolor=self.colors['bg_hover'],
            insertcolor=self.colors['fg_primary'],
            font=('Segoe UI', 10)
        )
        
        # ========== COMBOBOX ==========
        style.configure('TCombobox',
            fieldbackground=self.colors['bg_light'],
            background=self.colors['bg_light'],
            foreground=self.colors['fg_primary'],
            arrowcolor=self.colors['fg_primary'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['bg_hover'],
            darkcolor=self.colors['bg_hover'],
            font=('Segoe UI', 10)
        )
        
        style.map('TCombobox',
            fieldbackground=[('readonly', self.colors['bg_light'])],
            selectbackground=[('readonly', self.colors['bg_light'])],
            selectforeground=[('readonly', self.colors['fg_primary'])]
        )
        
        # ========== SCROLLBAR ==========
        style.configure('Vertical.TScrollbar',
            background=self.colors['bg_medium'],
            troughcolor=self.colors['bg_dark'],
            bordercolor=self.colors['bg_dark'],
            arrowcolor=self.colors['fg_secondary']
        )
        
        style.configure('Horizontal.TScrollbar',
            background=self.colors['bg_medium'],
            troughcolor=self.colors['bg_dark'],
            bordercolor=self.colors['bg_dark'],
            arrowcolor=self.colors['fg_secondary']
        )
        
        # ========== PROGRESSBAR ==========
        style.configure('TProgressbar',
            background=self.colors['accent_blue'],
            troughcolor=self.colors['bg_medium'],
            bordercolor=self.colors['bg_dark'],
            lightcolor=self.colors['accent_blue'],
            darkcolor=self.colors['accent_blue']
        )
        
        # Crear sistema de pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 0: Dashboard Principal
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="🏠 Dashboard")
        
        # Pestaña 1: Análisis & Scanner (fusionado)
        self.tab_analysis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analysis, text="🔬 Análisis & Scanner")
        
        # Pestaña 2: Seguimiento de Cuenta
        self.tab_account = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_account, text="📈 Mi Cuenta")
        
        # Frame principal para análisis
        main_frame = ttk.Frame(self.tab_analysis, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título con estilo profesional
        title_label = ttk.Label(main_frame, text="� ANÁLISIS DETALLADO DE OPCIONES", 
                               font=('Segoe UI', 18, 'bold'),
                               foreground='#4A90E2')
        title_label.grid(row=0, column=0, columnspan=4, pady=15)
        
        # Frame de controles
        control_frame = ttk.LabelFrame(main_frame, text="Configuracion", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=(0, 10))
        
        # Frame para búsqueda de tickers
        ticker_search_frame = ttk.LabelFrame(control_frame, text=" Buscar y Agregar Tickers", padding="10")
        ticker_search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(ticker_search_frame, text="Buscar Ticker:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(ticker_search_frame, width=20)
        self.search_entry.grid(row=0, column=1, padx=5)
        # self.search_entry.bind('<KeyRelease>', self.search_ticker)  # Deshabilitado
        self.search_entry.bind('<Return>', self.add_ticker_from_search)
        
        self.search_btn = ttk.Button(ticker_search_frame, text=" Agregar", 
                                     command=self.add_ticker_from_search)
        self.search_btn.grid(row=0, column=2, padx=5)
        
        # Label para sugerencias (oculto)
        # self.suggestion_label = ttk.Label(ticker_search_frame, text="", foreground="blue")
        # self.suggestion_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # Frame de tickers seleccionados
        selected_frame = ttk.LabelFrame(control_frame, text=" Tickers Seleccionados", padding="10")
        selected_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        selected_frame.grid_rowconfigure(0, weight=1)
        selected_frame.grid_rowconfigure(1, weight=0)
        selected_frame.grid_columnconfigure(0, weight=1)
        
        # Listbox para tickers seleccionados con scrollbar
        listbox_frame = ttk.Frame(selected_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        self.tickers_listbox = Listbox(listbox_frame, height=8, selectmode=tk.MULTIPLE,
                                       bg='#2D2D30', fg='#E0E0E0',
                                       selectbackground='#0078D4', selectforeground='#E0E0E0',
                                       font=('Segoe UI', 10), borderwidth=0,
                                       highlightthickness=1, highlightbackground='#3E3E42',
                                       highlightcolor='#4A90E2', width=25)
        scrollbar_tickers = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.tickers_listbox.yview)
        self.tickers_listbox.configure(yscrollcommand=scrollbar_tickers.set)
        
        self.tickers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tickers.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones para gestionar tickers
        btn_frame = ttk.Frame(selected_frame)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(btn_frame, text="🗑️ Eliminar Seleccionados", 
                  command=self.remove_selected_tickers).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🧹 Limpiar Todos", 
                  command=self.clear_all_tickers).pack(side=tk.LEFT, padx=5)
        
        # Actualizar listbox inicial
        self.update_tickers_listbox()
        
        # Frame de parámetros de análisis
        params_frame = ttk.LabelFrame(control_frame, text=" Parámetros de Análisis", padding="10")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Fecha de expiración
        ttk.Label(params_frame, text="Expiración:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.exp_var = tk.StringVar(value=self.saved_expirations[0] if self.saved_expirations else "")
        self.exp_combo = ttk.Combobox(params_frame, textvariable=self.exp_var, width=15)
        self.exp_combo['values'] = tuple(self.saved_expirations)
        self.exp_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Botón para actualizar expiraciones
        ttk.Button(params_frame, text="🔄 Actualizar", 
                  command=self.update_expirations).grid(row=0, column=2, padx=5, sticky=tk.W)
        
        # Delta mínimo y máximo
        ttk.Label(params_frame, text="Delta Min (%):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.delta_min = ttk.Entry(params_frame, width=10)
        self.delta_min.insert(0, "45")
        self.delta_min.grid(row=1, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(params_frame, text="Delta Max (%):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.delta_max = ttk.Entry(params_frame, width=10)
        self.delta_max.insert(0, "70")
        self.delta_max.grid(row=2, column=1, padx=5, sticky=tk.W)
        
        # Botón de análisis
        self.analyze_btn = ttk.Button(params_frame, text=" ANALIZAR OPCIONES", 
                                      command=self.analyze_options)
        self.analyze_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(params_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        

        # Frame del Simulador de Primas
        simulator_frame = ttk.LabelFrame(control_frame, text=" Simulador de Primas", padding="10")
        simulator_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Strike
        ttk.Label(simulator_frame, text="Strike ($):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.sim_strike = ttk.Entry(simulator_frame, width=15)
        self.sim_strike.grid(row=0, column=1, padx=5, sticky=tk.W)
        self.sim_strike.bind('<KeyRelease>', self.calculate_premium)

        # Prima
        ttk.Label(simulator_frame, text="Prima ($):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.sim_premium = ttk.Entry(simulator_frame, width=15)
        self.sim_premium.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.sim_premium.bind('<KeyRelease>', self.calculate_premium)

        # Contratos
        ttk.Label(simulator_frame, text="Contratos:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.sim_contracts = ttk.Entry(simulator_frame, width=15)
        self.sim_contracts.grid(row=2, column=1, padx=5, sticky=tk.W)
        self.sim_contracts.bind('<KeyRelease>', self.calculate_premium)

        # Resultados
        ttk.Separator(simulator_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(simulator_frame, text="Prima Total:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, padx=5)
        self.sim_total_premium = ttk.Label(simulator_frame, text="$0.00", foreground="green", font=('Arial', 10, 'bold'))
        self.sim_total_premium.grid(row=4, column=1, sticky=tk.W, padx=5)

        ttk.Label(simulator_frame, text="Capital Necesario:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, padx=5)
        self.sim_capital = ttk.Label(simulator_frame, text="$0.00", foreground="green", font=('Arial', 10, 'bold'))
        self.sim_capital.grid(row=5, column=1, sticky=tk.W, padx=5)

        ttk.Label(simulator_frame, text="Rentabilidad:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, padx=5)
        self.sim_profitability = ttk.Label(simulator_frame, text="0.00%", foreground="green", font=('Arial', 10, 'bold'))
        self.sim_profitability.grid(row=6, column=1, sticky=tk.W, padx=5)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(main_frame, text=" Resultados", padding="10")
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=(0, 10))
        
        # Botón para eliminar de resultados
        btn_results_frame = ttk.Frame(results_frame)
        btn_results_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(btn_results_frame, text=" Eliminar Fila Seleccionada", 
                  command=self.delete_selected_row).pack(side=tk.LEFT, padx=5)
        
        # Tabla de resultados con más información
        columns = ('Rank', 'Ticker', 'Precio', 'Strike', 'Prima', 'Delta', 'Theta',
                   'OI', 'Rent%', 'Rent.Anual%', 'Breakeven')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        column_widths = {'Rank': 40, 'Ticker': 70, 'Precio': 80, 'Strike': 80, 'Prima': 80,
                        'Delta': 70, 'Theta': 70, 'OI': 80,
                        'Rent%': 70, 'Rent.Anual%': 100, 'Breakeven': 90}
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        

        # Frame de Gráficas
        chart_frame = ttk.LabelFrame(results_frame, text=" Gráfica de Velas", padding="5")
        chart_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

        # Selector de ticker para gráfica
        ticker_chart_frame = ttk.Frame(chart_frame)
        ticker_chart_frame.pack(fill=tk.X, pady=5)

        ttk.Label(ticker_chart_frame, text="Ticker:").pack(side=tk.LEFT, padx=5)
        self.chart_ticker = ttk.Entry(ticker_chart_frame, width=10)
        self.chart_ticker.pack(side=tk.LEFT, padx=5)

        ttk.Label(ticker_chart_frame, text="Intervalo:").pack(side=tk.LEFT, padx=(15, 5))
        self.chart_interval = ttk.Combobox(ticker_chart_frame, width=10, state='readonly')
        self.chart_interval['values'] = ('30min', '1h', '4h')
        self.chart_interval.set('1h')
        self.chart_interval.pack(side=tk.LEFT, padx=5)

        ttk.Button(ticker_chart_frame, text=" Ver Gráfica", command=self.show_chart).pack(side=tk.LEFT, padx=5)

        # Canvas para la gráfica
        self.chart_canvas_frame = ttk.Frame(chart_frame)
        self.chart_canvas_frame.pack(fill=tk.BOTH, expand=True)
        # Etiqueta de estado
        self.status_label = ttk.Label(main_frame, text="Listo", relief=tk.SUNKEN)
        self.status_label.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Configurar expansión de pestaña de análisis
        self.tab_analysis.columnconfigure(0, weight=1)
        self.tab_analysis.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1, minsize=300)  # Control frame
        main_frame.columnconfigure(1, weight=2, minsize=500)  # Results frame
        main_frame.columnconfigure(2, weight=2, minsize=500)  # Scanner frame (aumentado)
        main_frame.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        control_frame.rowconfigure(1, weight=1)
        
        # ========== INTEGRACIÓN DEL SCANNER EN ANÁLISIS ==========
        self.create_scanner_in_analysis(main_frame)
        
        # ========== PESTAÑA 0: DASHBOARD PRINCIPAL ==========
        self.create_dashboard()
        
        # ========== PESTAÑA 2: SEGUIMIENTO DE CUENTA ==========
        self.create_account_tracker()
        
        # Actualizar precios de mercado inicial (deshabilitado)
        # self.update_market_prices()

    def update_market_prices(self):
        """Actualiza los precios de SPY y QQQ"""
        try:
            # Obtener precio de SPY
            spy_data = self.get_quote('SPY')
            if spy_data and 'quotes' in spy_data:
                spy_quote = spy_data['quotes']['quote']
                if isinstance(spy_quote, dict):
                    spy_price = spy_quote.get('last', 0) or spy_quote.get('bid', 0)
                    self.spy_price.config(text=f"${spy_price:.2f}")
            
            # Obtener precio de QQQ
            qqq_data = self.get_quote('QQQ')
            if qqq_data and 'quotes' in qqq_data:
                qqq_quote = qqq_data['quotes']['quote']
                if isinstance(qqq_quote, dict):
                    qqq_price = qqq_quote.get('last', 0) or qqq_quote.get('bid', 0)
                    self.qqq_price.config(text=f"${qqq_price:.2f}")
        except:
            pass

    def load_config(self):
        """Carga la configuración guardada desde el archivo JSON"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.selected_tickers = set(config.get('tickers', ['TSLL', 'AMDL', 'NVDX', 'TSLA', 'AMD', 'NVDA']))
                self.saved_expirations = config.get('expirations', [])
                self.account_id = config.get('account_id', None)
                self.api_token = config.get('api_token', None)
        except FileNotFoundError:
            # Si no existe el archivo, usar valores por defecto
            self.selected_tickers = set(['TSLL', 'AMDL', 'NVDX', 'TSLA', 'AMD', 'NVDA'])
            self.saved_expirations = []
            self.account_id = None
            self.api_token = None
        except:
            # En caso de error al leer, usar valores por defecto
            self.selected_tickers = set(['TSLL', 'AMDL', 'NVDX', 'TSLA', 'AMD', 'NVDA'])
            self.saved_expirations = []
            self.account_id = None
            self.api_token = None
    
    def save_config(self):
        """Guarda la configuración actual en el archivo JSON"""
        try:
            config = {
                'tickers': list(self.selected_tickers),
                'expirations': self.saved_expirations,
                'account_id': self.account_id,
                'api_token': self.api_token
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def format_date(self, date_str):
        """Convierte fecha de formato YYYY-MM-DD a DD-MM-YYYY"""
        try:
            if not date_str or len(date_str) < 10:
                return date_str
            # Si viene en formato YYYY-MM-DD
            if '-' in date_str and date_str[4] == '-':
                parts = date_str[:10].split('-')
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
            return date_str[:10]
        except:
            return date_str

    def calculate_breakeven(self, strike, premium):
        """Punto de equilibrio para una put vendida"""
        breakeven = strike - premium
        return f"${breakeven:.2f}"

    def show_chart(self):
        """Muestra la gráfica de velas usando Yahoo Finance"""
        ticker = self.chart_ticker.get().strip().upper()
        interval = self.chart_interval.get()
        
        if not ticker:
            messagebox.showwarning("Advertencia", "Ingresa un ticker")
            return
        
        # Limpiar canvas anterior
        for widget in self.chart_canvas_frame.winfo_children():
            widget.destroy()
        
        # Obtener datos históricos con yfinance
        self.status_label.config(text=f"Cargando gráfica de {ticker}...")
        
        try:
            # Determinar período según intervalo
            if interval == '30min':
                period = '7d'
                yf_interval = '30m'
            elif interval == '1h':
                period = '1mo'
                yf_interval = '1h'
            else:  # 4h
                period = '60d'
                yf_interval = '1h'  # Descargar 1h y agrupar a 4h
            
            # Descargar datos
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=yf_interval)
            
            if df.empty:
                messagebox.showerror("Error", f"No se pudieron obtener datos para {ticker}")
                self.status_label.config(text="Error al cargar gráfica")
                return
            
            # Si es 4h, agrupar datos de 1h
            if interval == '4h':
                df = df.resample('4h').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
            
            # Crear figura con tema oscuro
            fig = Figure(figsize=(8, 4), dpi=80, facecolor='#1E1E1E')
            ax = fig.add_subplot(111, facecolor='#2D2D30')

            # Preparar datos con índices numéricos
            df_reset = df.reset_index()
            
            # Renombrar columna de fecha si es necesario
            if 'Datetime' in df_reset.columns:
                df_reset.rename(columns={'Datetime': 'Date'}, inplace=True)
            elif df_reset.columns[0] not in ['Date', 'Datetime']:
                df_reset.rename(columns={df_reset.columns[0]: 'Date'}, inplace=True)
            
            dates = df_reset.index.tolist()
            
            # Calcular ancho de barra según cantidad de datos
            bar_width = 0.8 if len(df) < 50 else 0.6

            # Dibujar velas con colores profesionales
            for i in range(len(df_reset)):
                row = df_reset.iloc[i]
                color = '#00C853' if row['Close'] >= row['Open'] else '#F44336'

                # Cuerpo de la vela
                body_height = abs(row['Close'] - row['Open'])
                body_bottom = min(row['Open'], row['Close'])
                
                # Evitar velas de altura 0
                if body_height < 0.01:
                    body_height = 0.01
                
                ax.bar(i, body_height, bottom=body_bottom, width=bar_width, color=color, alpha=0.8, edgecolor=color)

                # Mecha superior
                ax.plot([i, i], [max(row['Open'], row['Close']), row['High']], color=color, linewidth=1.5)

                # Mecha inferior
                ax.plot([i, i], [row['Low'], min(row['Open'], row['Close'])], color=color, linewidth=1.5)

            # Configurar etiquetas del eje X
            step = max(1, len(dates) // 8)  # Mostrar máximo 8 etiquetas para evitar solapamiento
            ax.set_xticks(range(0, len(dates), step))
            ax.set_xticklabels([df_reset['Date'].iloc[i].strftime('%m/%d\n%H:%M') if i < len(df_reset) else '' for i in range(0, len(dates), step)], rotation=0, ha='center', color='#E0E0E0', fontsize=8)
            
            interval_text = {'30min': '30 minutos', '1h': '1 hora', '4h': '4 horas'}
            ax.set_title(f'{ticker} - Intervalo: {interval_text[interval]}', fontsize=12, fontweight='bold', color='#4A90E2', pad=15)
            ax.set_ylabel('Precio ($)', fontsize=10, color='#E0E0E0')
            ax.set_xlabel('Fecha/Hora', fontsize=9, color='#E0E0E0', labelpad=10)
            ax.tick_params(colors='#E0E0E0', labelsize=8)
            ax.grid(True, alpha=0.2, linestyle='--', color='#3E3E42')
            ax.spines['bottom'].set_color('#3E3E42')
            ax.spines['top'].set_color('#3E3E42')
            ax.spines['left'].set_color('#3E3E42')
            ax.spines['right'].set_color('#3E3E42')
            fig.tight_layout(pad=2.0, h_pad=1.5, w_pad=1.5)
            
            # Integrar en tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.status_label.config(text=f"Gráfica de {ticker} cargada ({interval})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar gráfica: {str(e)}")
            self.status_label.config(text="Error al cargar gráfica")
    def calculate_premium(self, event=None):
        """Calcula la prima total y el capital necesario"""
        try:
            strike = float(self.sim_strike.get() or 0)
            premium = float(self.sim_premium.get() or 0)
            contracts = int(self.sim_contracts.get() or 0)

            # Cada contrato = 100 acciones
            total_premium = premium * contracts * 100
            capital_needed = strike * contracts * 100
            profitability = (total_premium / capital_needed * 100) if capital_needed > 0 else 0

            self.sim_total_premium.config(text=f"${total_premium:,.2f}")
            self.sim_capital.config(text=f"${capital_needed:,.2f}")
            self.sim_profitability.config(text=f"{profitability:.2f}%")
        except:
            pass
    def delete_selected_row(self):
        """Elimina la fila seleccionada de la tabla de resultados"""
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Advertencia", "Selecciona una fila para eliminar")
            return
        
        for item in selected_items:
            self.tree.delete(item)
        
        # Reordenar los números de ranking
        for idx, item in enumerate(self.tree.get_children(), 1):
            values = list(self.tree.item(item)['values'])
            values[0] = idx
            self.tree.item(item, values=values)
    
    def search_ticker(self, event=None):
        """Busca el ticker en tiempo real y muestra sugerencias"""
        search_text = self.search_entry.get().strip().upper()
        
        if len(search_text) < 1:
            self.suggestion_label.config(text="")
            return
        
        # Buscar ticker en la API
        thread = threading.Thread(target=self._search_ticker_thread, args=(search_text,))
        thread.daemon = True
        thread.start()
    
    def _search_ticker_thread(self, search_text):
        """Busca el ticker en la API"""
        url = f"{self.base_url}/markets/search"
        params = {'q': search_text, 'indexes': 'false'}
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=3)
            response.raise_for_status()
            data = response.json()
            
            if data and 'securities' in data and 'security' in data['securities']:
                securities = data['securities']['security']
                if not isinstance(securities, list):
                    securities = [securities]
                
                # Mostrar primeras 3 sugerencias
                suggestions = []
                for sec in securities[:3]:
                    symbol = sec.get('symbol', '')
                    description = sec.get('description', '')
                    exchange = sec.get('exchange', '')
                    suggestions.append(f"{symbol} - {description} ({exchange})")
                
                suggestion_text = " | ".join(suggestions)
                self.suggestion_label.config(text=suggestion_text[:100])
            else:
                self.suggestion_label.config(text="No se encontraron resultados")
        except:
            self.suggestion_label.config(text="")
    
    def add_ticker_from_search(self, event=None):
        """Agrega el ticker buscado a la lista si existe"""
        ticker = self.search_entry.get().strip().upper()

        if not ticker:
            messagebox.showwarning("Advertencia", "Por favor, ingresa un ticker")
            return

        if ticker in self.selected_tickers:
            messagebox.showinfo("Info", f"{ticker} ya está en la lista")
            return

        # Verificar si el ticker existe en la API
        quote_data = self.get_quote(ticker)
        
        if not quote_data or 'quotes' not in quote_data:
            messagebox.showerror("Error", f"Ticker '{ticker}' no encontrado")
            return
        
        quote = quote_data.get('quotes', {}).get('quote', {})
        if not quote or (isinstance(quote, dict) and quote.get('symbol') != ticker):
            messagebox.showerror("Error", f"Ticker '{ticker}' no encontrado")
            return

        # Ticker válido, agregar a la lista
        self.selected_tickers.add(ticker)
        self.save_config()
        self.update_tickers_listbox()
        self.search_entry.delete(0, tk.END)
        messagebox.showinfo("Éxito", f"{ticker} agregado correctamente")
    def update_tickers_listbox(self):
        """Actualiza el listbox con los tickers seleccionados"""
        self.tickers_listbox.delete(0, tk.END)
        for ticker in sorted(self.selected_tickers):
            self.tickers_listbox.insert(tk.END, ticker)
    
    def remove_selected_tickers(self):
        """Elimina los tickers seleccionados del listbox"""
        selected_indices = self.tickers_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Advertencia", "Selecciona al menos un ticker para eliminar")
            return
        
        tickers_to_remove = [self.tickers_listbox.get(i) for i in selected_indices]
        
        for ticker in tickers_to_remove:
            self.selected_tickers.discard(ticker)
        
        self.save_config()
        self.update_tickers_listbox()
    
    def clear_all_tickers(self):
        """Limpia todos los tickers"""
        if messagebox.askyesno("Confirmar", "¿Deseas eliminar todos los tickers?"):
            self.selected_tickers.clear()
            self.save_config()
            self.update_tickers_listbox()
    
    def get_option_chain(self, symbol, expiration):
        url = f"{self.base_url}/markets/options/chains"
        params = {
            'symbol': symbol,
            'expiration': expiration,
            'greeks': 'true'
        }
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_quote(self, symbol):
        url = f"{self.base_url}/markets/quotes"
        params = {'symbols': symbol}
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_expirations(self, symbol):
        """Obtiene las fechas de expiración disponibles para un símbolo"""
        url = f"{self.base_url}/markets/options/expirations"
        params = {'symbol': symbol}
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def update_expirations(self):
        """Actualiza las fechas de expiración disponibles"""
        if not self.selected_tickers:
            messagebox.showwarning("Advertencia", "Agrega al menos un ticker para obtener expiraciones")
            return
        
        thread = threading.Thread(target=self._update_expirations_thread)
        thread.daemon = True
        thread.start()
    
    def _update_expirations_thread(self):
        """Thread para actualizar expiraciones"""
        self.status_label.config(text="Obteniendo fechas de expiración...")
        
        # Usar el primer ticker disponible para obtener expiraciones
        ticker = list(self.selected_tickers)[0]
        expirations_data = self.get_expirations(ticker)
        
        if expirations_data and 'expirations' in expirations_data:
            expirations = expirations_data['expirations'].get('date', [])
            
            if not isinstance(expirations, list):
                expirations = [expirations]
            
            # Filtrar solo fechas futuras
            today = datetime.now().date()
            future_expirations = [exp for exp in expirations 
                                 if datetime.strptime(exp, '%Y-%m-%d').date() > today]
            
            # Tomar solo las primeras 3 fechas
            future_expirations = future_expirations[:3]
            
            if future_expirations:
                # Guardar las expiraciones
                self.saved_expirations = future_expirations
                self.save_config()
                
                # Actualizar el combobox
                self.exp_combo['values'] = tuple(future_expirations)
                self.exp_var.set(future_expirations[0])
                self.status_label.config(text=f"Expiraciones actualizadas: {len(future_expirations)} disponibles")
                messagebox.showinfo("Éxito", f"Se encontraron {len(future_expirations)} fechas de expiración")
            else:
                self.status_label.config(text="No se encontraron expiraciones futuras")
                messagebox.showwarning("Advertencia", "No se encontraron fechas de expiración futuras")
        else:
            self.status_label.config(text="Error al obtener expiraciones")
            messagebox.showerror("Error", "No se pudieron obtener las fechas de expiración")
    
    def analyze_options(self):
        # Iniciar análisis en thread separado
        thread = threading.Thread(target=self._analyze_thread)
        thread.daemon = True
        thread.start()
    
    def _analyze_thread(self):
        self.progress.start()
        self.analyze_btn.config(state='disabled')
        self.status_label.config(text="Analizando opciones...")
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Verificar que hay tickers seleccionados
        if not self.selected_tickers:
            self.progress.stop()
            self.analyze_btn.config(state='normal')
            self.status_label.config(text="Error: No hay tickers seleccionados")
            messagebox.showwarning("Advertencia", "Por favor, agrega al menos un ticker")
            return
        
        tickers = list(self.selected_tickers)
        expiration = self.exp_var.get()
        delta_min = float(self.delta_min.get())
        delta_max = float(self.delta_max.get())
        
        options_list = []
        
        for ticker in tickers:
            self.status_label.config(text=f"Analizando {ticker}...")
            
            # Obtener precio actual
            quote_data = self.get_quote(ticker)
            current_price = 0
            
            if quote_data and 'quotes' in quote_data:
                quote = quote_data['quotes']['quote']
                if isinstance(quote, dict):
                    current_price = quote.get('last', 0) or quote.get('bid', 0)
            
            # Obtener cadena de opciones
            chain = self.get_option_chain(ticker, expiration)
            
            if chain and 'options' in chain:
                options_data = chain['options']
                if options_data and 'option' in options_data:
                    puts = [opt for opt in options_data['option'] 
                           if opt.get('option_type') == 'put']
                    
                    valid_puts = []
                    for put in puts:
                        greeks = put.get('greeks')
                        if not greeks:
                            continue
                        
                        delta = greeks.get('delta', 0)
                        abs_delta = abs(delta) * 100
                        
                        if (delta_min <= abs_delta <= delta_max and 
                            put.get('open_interest', 0) > 0 and 
                            put.get('bid', 0) > 0):
                            
                            bid = put.get('bid', 0)
                            ask = put.get('ask', 0)
                            mid_price = (bid + ask) / 2
                            strike = put.get('strike', 0)
                            
                            rentabilidad = (mid_price / strike) * 100 if strike > 0 else 0
                            rentabilidad_anualizada = rentabilidad * 365
                            
                            # Obtener Greeks adicionales
                            theta = greeks.get('theta', 0)
                            gamma = greeks.get('gamma', 0)
                            delta_x_gamma = delta * gamma
                            
                            # Calcular breakeven
                            breakeven = self.calculate_breakeven(strike, mid_price)
                            
                            valid_puts.append({
                                'ticker': ticker,
                                'strike': strike,
                                'prima': mid_price,
                                'delta': delta,
                                'theta': theta,
                                'delta_x_gamma': delta_x_gamma,
                                'oi': put.get('open_interest', 0),
                                'rentabilidad': rentabilidad,
                                'rentabilidad_anualizada': rentabilidad_anualizada,
                                'current_price': current_price,
                                'breakeven': breakeven
                            })
                    
                    if valid_puts:
                        # Ordenar por rentabilidad (mayor a menor) y open interest
                        valid_puts_sorted = sorted(valid_puts, key=lambda x: (x['rentabilidad'], x['oi']), reverse=True)
                        # Tomar las 3 con mejor rentabilidad
                        top_3 = valid_puts_sorted[:3]
                        options_list.extend(top_3)
        
        # Ordenar por ticker y luego por rentabilidad (mayor a menor)
        options_list.sort(key=lambda x: (x['ticker'], -x['rentabilidad']))
        
        # Actualizar tabla
        for idx, opt in enumerate(options_list, 1):
            self.tree.insert('', tk.END, values=(
                idx,
                opt['ticker'],
                f"${opt['current_price']:.2f}",
                f"${opt['strike']:.2f}",
                f"${opt['prima']:.2f}",
                f"{opt['delta']:.4f}",
                f"{opt['theta']:.4f}",
                f"{opt['oi']:,}",
                f"{opt['rentabilidad']:.2f}%",
                f"{opt['rentabilidad_anualizada']:.1f}%",
                opt['breakeven']
            ))
        
        # Actualizar precios de mercado al finalizar análisis (deshabilitado)
        # self.update_market_prices()
        
        self.progress.stop()
        self.analyze_btn.config(state='normal')
        self.status_label.config(text=f"Análisis completado: {len(options_list)} opciones encontradas")

    # ==================== SCANNER INTEGRADO ====================
    
    def create_scanner_in_analysis(self, parent_frame):
        """Integra el scanner en la pestaña de análisis"""
        # Frame del scanner (columna derecha)
        scanner_frame = ttk.LabelFrame(parent_frame, text=" SCANNER DE OPORTUNIDADES ", padding="10")
        scanner_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Filtros del scanner
        filters_frame = ttk.Frame(scanner_frame)
        filters_frame.pack(fill=tk.X, pady=5)
        
        # Fila 1: Filtros básicos
        row1 = ttk.Frame(filters_frame)
        row1.pack(fill=tk.X, pady=2)
        
        
        ttk.Label(row1, text="Δ Min:").pack(side=tk.LEFT, padx=2)
        self.scan_min_delta = ttk.Entry(row1, width=8)
        self.scan_min_delta.insert(0, "0.10")
        self.scan_min_delta.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(row1, text="Δ Max:").pack(side=tk.LEFT, padx=2)
        self.scan_max_delta = ttk.Entry(row1, width=8)
        self.scan_max_delta.insert(0, "0.30")
        self.scan_max_delta.pack(side=tk.LEFT, padx=2)
        
        # Fila 2: DTE y opciones
        row2 = ttk.Frame(filters_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="DTE Min:").pack(side=tk.LEFT, padx=2)
        self.scan_min_dte = ttk.Entry(row2, width=8)
        self.scan_min_dte.insert(0, "1")
        self.scan_min_dte.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(row2, text="DTE Max:").pack(side=tk.LEFT, padx=2)
        self.scan_max_dte = ttk.Entry(row2, width=8)
        self.scan_max_dte.insert(0, "15")
        self.scan_max_dte.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(row2, text="Tipo:").pack(side=tk.LEFT, padx=2)
        self.scan_option_type = ttk.Combobox(row2, width=8, state='readonly')
        self.scan_option_type['values'] = ('Puts', 'Calls', 'Ambos')
        self.scan_option_type.set('Puts')
        self.scan_option_type.pack(side=tk.LEFT, padx=2)
        
        # Fila 3: Ordenar
        row3 = ttk.Frame(filters_frame)
        row3.pack(fill=tk.X, pady=2)
        
        ttk.Label(row3, text="Ordenar por:").pack(side=tk.LEFT, padx=2)
        self.scan_sort_by = ttk.Combobox(row3, width=12, state='readonly')
        self.scan_sort_by['values'] = ('Premium', 'ROI Anualizado', 'Probabilidad', 'Premium/Riesgo')
        self.scan_sort_by.set('ROI Anualizado')
        self.scan_sort_by.pack(side=tk.LEFT, padx=2)
        
        # Botones
        btn_row = ttk.Frame(filters_frame)
        btn_row.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_row, text="🔍 Escanear", 
                  command=self.scan_opportunities).pack(side=tk.LEFT, padx=5)
        
        self.scan_use_selected = tk.BooleanVar(value=True)
        ttk.Checkbutton(btn_row, text="Usar tickers seleccionados", 
                       variable=self.scan_use_selected).pack(side=tk.LEFT, padx=5)
        
        # Tabla de resultados del scanner
        results_scan = ttk.Frame(scanner_frame)
        results_scan.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scan_columns = ('Ticker', 'Strike', 'Prima', 'Delta', 'DTE', 'ROI%', 'Calif.')
        self.scan_tree = ttk.Treeview(results_scan, columns=scan_columns, 
                                     show='headings', height=10)
        
        column_widths = {'Ticker': 60, 'Strike': 70, 'Prima': 70, 'Delta': 60,
                        'DTE': 40, 'ROI%': 70, 'Calif.': 60}
        
        for col in scan_columns:
            self.scan_tree.heading(col, text=col)
            self.scan_tree.column(col, width=column_widths.get(col, 70), anchor=tk.CENTER)
        
        scrollbar_scan = ttk.Scrollbar(results_scan, orient=tk.VERTICAL, 
                                      command=self.scan_tree.yview)
        self.scan_tree.configure(yscroll=scrollbar_scan.set)
        
        self.scan_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_scan.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Label de estado
        self.scan_status = ttk.Label(scanner_frame, text="Listo para escanear", 
                                     font=('Segoe UI', 9), foreground='#858585')
        self.scan_status.pack(pady=2)

    # ==================== DASHBOARD PRINCIPAL ====================
    
    def create_dashboard(self):
        """Crea el dashboard principal con resumen y métricas"""
        # Frame principal
        dash_main = ttk.Frame(self.tab_dashboard, padding="15")
        dash_main.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(dash_main)
        title_frame.pack(pady=(0, 20), fill=tk.X)
        
        title = ttk.Label(title_frame, text="🏠 DASHBOARD PRINCIPAL", 
                         font=('Segoe UI', 18, 'bold'), foreground='#4A90E2')
        title.pack(side=tk.LEFT)
        
        # Botón para cambiar API Key
        ttk.Button(title_frame, text="🔑 Cambiar API Key", 
                  command=self.change_api_key).pack(side=tk.RIGHT, padx=10)
        
        # Botón de actualizar dashboard
        ttk.Button(title_frame, text="🔄 Actualizar Dashboard", 
                  command=self.refresh_dashboard).pack(side=tk.RIGHT)
        
        # Frame superior: Métricas principales (cards)
        metrics_frame = ttk.Frame(dash_main)
        metrics_frame.pack(fill=tk.X, pady=10)
        
        # Card 1: Balance Total
        card1 = ttk.LabelFrame(metrics_frame, text=" 💰 Balance Total ", padding="15")
        card1.grid(row=0, column=0, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dash_balance = ttk.Label(card1, text="$0.00", 
                                      font=('Segoe UI', 24, 'bold'), foreground='#4A90E2')
        self.dash_balance.pack()
        ttk.Label(card1, text="Capital disponible", 
                 font=('Segoe UI', 9), foreground='#858585').pack()
        
        # Card 2: P&L Mensual
        card2 = ttk.LabelFrame(metrics_frame, text=" 📊 P&L Este Mes ", padding="15")
        card2.grid(row=0, column=1, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dash_pl_month = ttk.Label(card2, text="$0.00", 
                                       font=('Segoe UI', 24, 'bold'), foreground='#00C853')
        self.dash_pl_month.pack()
        ttk.Label(card2, text="Beneficio del mes", 
                 font=('Segoe UI', 9), foreground='#858585').pack()
        
        # Card 3: Win Rate
        card3 = ttk.LabelFrame(metrics_frame, text=" 🎯 Win Rate ", padding="15")
        card3.grid(row=0, column=2, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dash_winrate = ttk.Label(card3, text="0%", 
                                      font=('Segoe UI', 24, 'bold'), foreground='#FF9800')
        self.dash_winrate.pack()
        ttk.Label(card3, text="Tasa de éxito", 
                 font=('Segoe UI', 9), foreground='#858585').pack()
        
        # Card 4: Retorno Anualizado
        card4 = ttk.LabelFrame(metrics_frame, text=" 📈 Retorno Anual ", padding="15")
        card4.grid(row=0, column=3, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dash_annual_return = ttk.Label(card4, text="0%", 
                                           font=('Segoe UI', 24, 'bold'), foreground='#26A69A')
        self.dash_annual_return.pack()
        ttk.Label(card4, text="ROI anualizado", 
                 font=('Segoe UI', 9), foreground='#858585').pack()
        
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)
        metrics_frame.columnconfigure(2, weight=1)
        metrics_frame.columnconfigure(3, weight=1)
        
        # Frame medio: Calendario de Próximas Expiraciones
        calendar_frame = ttk.LabelFrame(dash_main, text=" 📅 Próximas Expiraciones ", padding="15")
        calendar_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tabla de expiraciones
        exp_columns = ('Fecha', 'Días', 'Tickers', 'Contratos')
        self.dash_expirations_tree = ttk.Treeview(calendar_frame, columns=exp_columns, 
                                                  show='headings', height=5)
        
        for col in exp_columns:
            self.dash_expirations_tree.heading(col, text=col)
            self.dash_expirations_tree.column(col, width=150, anchor=tk.CENTER)
        
        scrollbar_exp = ttk.Scrollbar(calendar_frame, orient=tk.VERTICAL, 
                                     command=self.dash_expirations_tree.yview)
        self.dash_expirations_tree.configure(yscroll=scrollbar_exp.set)
        
        self.dash_expirations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_exp.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame inferior: Mejores y Peores Trades
        trades_frame = ttk.Frame(dash_main)
        trades_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Mejores trades
        best_frame = ttk.LabelFrame(trades_frame, text=" 🏆 Mejores Trades ", padding="10")
        best_frame.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        best_columns = ('Ticker', 'Fecha', 'P&L')
        self.dash_best_tree = ttk.Treeview(best_frame, columns=best_columns, 
                                          show='headings', height=5)
        for col in best_columns:
            self.dash_best_tree.heading(col, text=col)
            self.dash_best_tree.column(col, width=100, anchor=tk.CENTER)
        self.dash_best_tree.pack(fill=tk.BOTH, expand=True)
        
        # Peores trades
        worst_frame = ttk.LabelFrame(trades_frame, text=" ⚠️ Peores Trades ", padding="10")
        worst_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        worst_columns = ('Ticker', 'Fecha', 'P&L')
        self.dash_worst_tree = ttk.Treeview(worst_frame, columns=worst_columns, 
                                           show='headings', height=5)
        for col in worst_columns:
            self.dash_worst_tree.heading(col, text=col)
            self.dash_worst_tree.column(col, width=100, anchor=tk.CENTER)
        self.dash_worst_tree.pack(fill=tk.BOTH, expand=True)
        
        trades_frame.columnconfigure(0, weight=1)
        trades_frame.columnconfigure(1, weight=1)
        trades_frame.rowconfigure(0, weight=1)
    
    def refresh_dashboard(self):
        """Actualiza todos los datos del dashboard"""
        thread = threading.Thread(target=self._refresh_dashboard_thread)
        thread.daemon = True
        thread.start()
    
    def change_api_key(self):
        """Permite cambiar la API key de forma segura"""
        from tkinter import simpledialog
        
        # Mostrar mensaje informativo
        messagebox.showinfo(
            "Cambiar API Key", 
            "Ingresa tu nuevo API Key de Tradier.\n\nEl código será guardado de forma segura y no será visible en la aplicación."
        )
        
        # Solicitar nueva API key con entrada oculta
        new_api_key = simpledialog.askstring(
            "Nueva API Key",
            "Ingresa tu API Key de Tradier:",
            show='*'
        )
        
        # Validar entrada
        if new_api_key is None:  # Usuario canceló
            return
        
        if not new_api_key.strip():
            messagebox.showerror("Error", "La API Key no puede estar vacía")
            return
        
        # Actualizar API key
        self.api_token = new_api_key.strip()
        
        # Guardar en configuración
        self.save_config()
        
        # Mostrar confirmación (sin mostrar el código completo)
        masked_key = new_api_key[:4] + "..." + new_api_key[-4:] if len(new_api_key) > 8 else "****"
        messagebox.showinfo(
            "Éxito", 
            f"API Key actualizada correctamente.\n\nCódigo: {masked_key}\n\nLa configuración se ha guardado."
        )
        
        self.status_label.config(text="API Key actualizada correctamente")
    
    def _refresh_dashboard_thread(self):
        """Thread para actualizar dashboard"""
        self.status_label.config(text="Actualizando dashboard...")
        
        try:
            # Obtener datos de cuenta si no los tenemos
            if not self.account_id:
                accounts = self.get_user_profile()
                if accounts:
                    for acc in accounts:
                        if acc.get('account_number', '').endswith('52350'):
                            self.account_id = acc.get('account_number')
                            break
            
            if not self.account_id:
                messagebox.showerror("Error", "No se pudo obtener la cuenta")
                self.status_label.config(text="Error: no se encontró la cuenta")
                return
            
            # Obtener balance desde Mi Cuenta (que ya funciona correctamente)
            # En lugar de intentar obtenerlo aquí, lo tomaremos después de actualizar Mi Cuenta
            total_equity = 0
            
            # Obtener gainloss para calcular métricas
            gainloss_data = self.get_account_gainloss(self.account_id)
            
            # Debug: verificar si hay datos
            if not gainloss_data:
                self.status_label.config(text="No se pudieron obtener datos de gainloss")
            elif 'gainloss' not in gainloss_data:
                self.status_label.config(text="gainloss_data no contiene 'gainloss'")
            
            if gainloss_data and 'gainloss' in gainloss_data:
                gl = gainloss_data['gainloss']
                
                # Debug: verificar si hay posiciones cerradas
                if 'closed_position' not in gl:
                    self.status_label.config(text="No hay posiciones cerradas en gainloss")
                    # Establecer valores por defecto
                    self.dash_pl_month.config(text="$0.00", foreground='#858585')
                    self.dash_winrate.config(text="0.0%")
                    self.dash_annual_return.config(text="0.0%")
                else:
                    closed_positions = gl['closed_position']
                    if not isinstance(closed_positions, list):
                        closed_positions = [closed_positions]
                    
                    # Debug: mostrar cuántas posiciones hay
                    self.status_label.config(text=f"Procesando {len(closed_positions)} posiciones cerradas...")

                    
                    # Calcular P&L del mes actual
                    from datetime import datetime
                    current_month = datetime.now().strftime('%Y-%m')
                    current_year = datetime.now().year
                    monthly_pl = 0
                    winning_trades = 0
                    total_trades = 0
                    ytd_pl = 0
                    
                    best_trades = []
                    worst_trades = []
                    
                    for pos in closed_positions:
                        close_date = pos.get('close_date', '')
                        pl = float(pos.get('gain_loss', 0) or 0)
                        symbol = pos.get('symbol', 'N/A')
                        
                        # Para YTD P&L (todos los trades del año actual)
                        if str(current_year) in close_date:
                            ytd_pl += pl
                            best_trades.append((symbol, self.format_date(close_date), pl))
                            worst_trades.append((symbol, self.format_date(close_date), pl))
                        
                        # Para estadísticas del mes actual
                        if current_month in close_date:
                            monthly_pl += pl
                            total_trades += 1
                            if pl > 0:
                                winning_trades += 1
                    
                    # Actualizar P&L mensual
                    color = '#00C853' if monthly_pl >= 0 else '#F44336'
                    self.dash_pl_month.config(text=f"${monthly_pl:,.2f}", foreground=color)
                    
                    # Actualizar Win Rate
                    winrate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                    self.dash_winrate.config(text=f"{winrate:.1f}%")
                    
                    # Calcular retorno anualizado
                    days_passed = datetime.now().timetuple().tm_yday
                    annual_return = (ytd_pl / total_equity * 365 / days_passed * 100) if total_equity > 0 and days_passed > 0 else 0
                    self.dash_annual_return.config(text=f"{annual_return:.1f}%")
                    
                    # Debug: mostrar información en consola
                    print(f"DEBUG Dashboard - YTD P&L: ${ytd_pl:,.2f} | Mes: ${monthly_pl:,.2f} | Trades mes: {total_trades}")
                    print(f"DEBUG Dashboard - Total posiciones cerradas procesadas: {len(closed_positions)}")
                    print(f"DEBUG Dashboard - Winrate: {winrate:.1f}% | Annual return: {annual_return:.1f}%")
                    print(f"DEBUG Dashboard - Balance para cálculo: ${total_equity:,.2f}")


                    
                    # Actualizar mejores trades
                    best_trades.sort(key=lambda x: x[2], reverse=True)
                    for item in self.dash_best_tree.get_children():
                        self.dash_best_tree.delete(item)
                    for ticker, date, pl in best_trades[:5]:
                        self.dash_best_tree.insert('', tk.END, values=(ticker, date, f"${pl:,.2f}"))
                    
                    # Actualizar peores trades
                    worst_trades.sort(key=lambda x: x[2])
                    for item in self.dash_worst_tree.get_children():
                        self.dash_worst_tree.delete(item)
                    for ticker, date, pl in worst_trades[:5]:
                        self.dash_worst_tree.insert('', tk.END, values=(ticker, date, f"${pl:,.2f}"))
            
            # Actualizar primero la pestaña de Mi Cuenta (que ya funciona correctamente)
            self.status_label.config(text="Actualizando Mi Cuenta...")
            self._refresh_account_thread()
            
            # Copiar solo algunos valores de Mi Cuenta al Dashboard
            # Balance total
            balance_text = self.acc_balance.cget("text")
            self.dash_balance.config(text=balance_text)
            
            # Win Rate
            winrate_text = self.acc_win_rate.cget("text")
            self.dash_winrate.config(text=winrate_text)
            
            # Return % (Retorno anual)
            return_text = self.acc_return.cget("text")
            return_color = self.acc_return.cget("foreground")
            self.dash_annual_return.config(text=return_text, foreground=return_color)
            
            # NOTA: dash_pl_month ya se actualiza arriba con el cálculo mensual desde gainloss
            
            self.status_label.config(text="Dashboard y cuenta actualizados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar dashboard: {str(e)}")
            self.status_label.config(text="Error al actualizar dashboard")
    
    # ==================== SCANNER DE OPORTUNIDADES ====================
    
    def create_scanner(self):
        """Crea la interfaz del scanner de oportunidades"""
        # Frame principal
        scanner_main = ttk.Frame(self.tab_scanner, padding="15")
        scanner_main.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(scanner_main, text="🎯 SCANNER DE OPORTUNIDADES", 
                         font=('Segoe UI', 18, 'bold'), foreground='#4A90E2')
        title.pack(pady=(0, 15))
        
        # Frame contenedor para filtros y simulador (lado a lado)
        top_frame = ttk.Frame(scanner_main)
        top_frame.pack(fill=tk.X, pady=10)
        
        # Frame de filtros (izquierda)
        filters_frame = ttk.LabelFrame(top_frame, text=" ⚙️ Filtros de Búsqueda ", padding="15")
        filters_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Fila 1: Premium y Delta
        row1 = ttk.Frame(filters_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Premium Mínimo ($):").pack(side=tk.LEFT, padx=5)
        self.scan_min_premium = ttk.Entry(row1, width=10)
        self.scan_min_premium.insert(0, "0.50")
        self.scan_min_premium.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Delta Mínimo:").pack(side=tk.LEFT, padx=(20, 5))
        self.scan_min_delta = ttk.Entry(row1, width=10)
        self.scan_min_delta.insert(0, "0.10")
        self.scan_min_delta.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Delta Máximo:").pack(side=tk.LEFT, padx=(20, 5))
        self.scan_max_delta = ttk.Entry(row1, width=10)
        self.scan_max_delta.insert(0, "0.30")
        self.scan_max_delta.pack(side=tk.LEFT, padx=5)
        
        # Fila 1.5: DTE
        row1_5 = ttk.Frame(filters_frame)
        row1_5.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1_5, text="DTE Mínimo:").pack(side=tk.LEFT, padx=5)
        self.scan_min_dte = ttk.Entry(row1_5, width=10)
        self.scan_min_dte.insert(0, "1")
        self.scan_min_dte.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1_5, text="DTE Máximo:").pack(side=tk.LEFT, padx=(20, 5))
        self.scan_max_dte = ttk.Entry(row1_5, width=10)
        self.scan_max_dte.insert(0, "15")
        self.scan_max_dte.pack(side=tk.LEFT, padx=5)
        
        # Fila 2: Tipo de opción y lista de tickers
        row2 = ttk.Frame(filters_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Tipo:").pack(side=tk.LEFT, padx=5)
        self.scan_option_type = ttk.Combobox(row2, width=12, state='readonly')
        self.scan_option_type['values'] = ('Puts', 'Calls', 'Ambos')
        self.scan_option_type.set('Puts')
        self.scan_option_type.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Ordenar por:").pack(side=tk.LEFT, padx=(20, 5))
        self.scan_sort_by = ttk.Combobox(row2, width=15, state='readonly')
        self.scan_sort_by['values'] = ('Premium', 'ROI Anualizado', 'Probabilidad', 'Premium/Riesgo')
        self.scan_sort_by.set('ROI Anualizado')
        self.scan_sort_by.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Usar tickers seleccionados:").pack(side=tk.LEFT, padx=(20, 5))
        self.scan_use_selected = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, variable=self.scan_use_selected).pack(side=tk.LEFT, padx=5)
        
        # Botón de escaneo
        btn_frame = ttk.Frame(filters_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🔍 Escanear Oportunidades", 
                  command=self.scan_opportunities).pack()
        
        # Frame del Simulador de Primas (derecha)
        simulator_frame = ttk.LabelFrame(top_frame, text=" 💰 Simulador de Primas ", padding="15")
        simulator_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # Strike
        ttk.Label(simulator_frame, text="Strike ($):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.scan_sim_strike = ttk.Entry(simulator_frame, width=12)
        self.scan_sim_strike.grid(row=0, column=1, padx=5, pady=3)
        self.scan_sim_strike.bind('<KeyRelease>', self.calculate_scanner_premium)
        
        # Prima
        ttk.Label(simulator_frame, text="Prima ($):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.scan_sim_premium = ttk.Entry(simulator_frame, width=12)
        self.scan_sim_premium.grid(row=1, column=1, padx=5, pady=3)
        self.scan_sim_premium.bind('<KeyRelease>', self.calculate_scanner_premium)
        
        # Contratos
        ttk.Label(simulator_frame, text="Contratos:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.scan_sim_contracts = ttk.Entry(simulator_frame, width=12)
        self.scan_sim_contracts.grid(row=2, column=1, padx=5, pady=3)
        self.scan_sim_contracts.bind('<KeyRelease>', self.calculate_scanner_premium)
        
        # Separador
        ttk.Separator(simulator_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=8)
        
        # Resultados
        ttk.Label(simulator_frame, text="Prima Total:", font=('Segoe UI', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.scan_sim_total = ttk.Label(simulator_frame, text="$0.00", foreground="#00C853", font=('Segoe UI', 9, 'bold'))
        self.scan_sim_total.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(simulator_frame, text="Capital Nec.:", font=('Segoe UI', 9, 'bold')).grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.scan_sim_capital = ttk.Label(simulator_frame, text="$0.00", foreground="#4A90E2", font=('Segoe UI', 9, 'bold'))
        self.scan_sim_capital.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(simulator_frame, text="Rentabilidad:", font=('Segoe UI', 9, 'bold')).grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.scan_sim_profit = ttk.Label(simulator_frame, text="0.00%", foreground="#9C27B0", font=('Segoe UI', 9, 'bold'))
        self.scan_sim_profit.grid(row=6, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(scanner_main, text=" 📋 Resultados ", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tabla de resultados
        scan_columns = ('Ticker', 'Tipo', 'Strike', 'Expiración', 'DTE', 
                       'Premium', 'Delta', 'Prob.%', 'ROI Anual', 'Calificación')
        self.scan_tree = ttk.Treeview(results_frame, columns=scan_columns, 
                                     show='headings', height=15)
        
        column_widths = {'Ticker': 70, 'Tipo': 60, 'Strike': 80, 'Expiración': 100,
                        'DTE': 50, 'Premium': 80, 'Delta': 70, 'Prob.%': 70,
                        'ROI Anual': 90, 'Calificación': 90}
        
        for col in scan_columns:
            self.scan_tree.heading(col, text=col)
            self.scan_tree.column(col, width=column_widths.get(col, 80), anchor=tk.CENTER)
        
        scrollbar_scan = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                      command=self.scan_tree.yview)
        self.scan_tree.configure(yscroll=scrollbar_scan.set)
        
        self.scan_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_scan.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Label de estado
        self.scan_status = ttk.Label(scanner_main, text="Listo para escanear", 
                                     font=('Segoe UI', 9), foreground='#858585')
        self.scan_status.pack(pady=5)
    
    def calculate_scanner_premium(self, event=None):
        """Calcula la prima total para el simulador del scanner"""
        try:
            strike = float(self.scan_sim_strike.get() or 0)
            premium = float(self.scan_sim_premium.get() or 0)
            contracts = int(self.scan_sim_contracts.get() or 0)
            
            total_premium = premium * contracts * 100
            capital_needed = strike * contracts * 100
            profitability = (total_premium / capital_needed * 100) if capital_needed > 0 else 0
            
            self.scan_sim_total.config(text=f"${total_premium:,.2f}")
            self.scan_sim_capital.config(text=f"${capital_needed:,.2f}")
            self.scan_sim_profit.config(text=f"{profitability:.2f}%")
        except:
            pass
    
    def scan_opportunities(self):
        """Escanea oportunidades de venta de opciones"""
        thread = threading.Thread(target=self._scan_opportunities_thread)
        thread.daemon = True
        thread.start()
    
    def _scan_opportunities_thread(self):
        """Thread para escanear oportunidades"""
        try:
            # Obtener parámetros
            min_delta = float(self.scan_min_delta.get())
            max_delta = float(self.scan_max_delta.get())
            min_dte = int(self.scan_min_dte.get())
            max_dte = int(self.scan_max_dte.get())
            option_type = self.scan_option_type.get()
            use_selected = self.scan_use_selected.get()
            
            # Determinar lista de tickers
            if use_selected and self.selected_tickers:
                tickers = list(self.selected_tickers)
            else:
                # Lista por defecto de tickers populares
                tickers = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'META', 'GOOGL', 'AMZN']
            
            self.scan_status.config(text=f"Escaneando {len(tickers)} tickers...")
            
            # Limpiar resultados anteriores
            for item in self.scan_tree.get_children():
                self.scan_tree.delete(item)
            
            opportunities = []
            
            # Escanear cada ticker
            for i, ticker in enumerate(tickers, 1):
                self.scan_status.config(text=f"Escaneando {ticker} ({i}/{len(tickers)})...")
                
                # Obtener expiraciones
                exp_data = self.get_expirations(ticker)
                if not exp_data or 'expirations' not in exp_data:
                    continue
                
                expirations = exp_data['expirations']['date']
                if not isinstance(expirations, list):
                    expirations = [expirations]
                
                # Filtrar expiraciones por DTE
                from datetime import datetime
                today = datetime.now()
                valid_expirations = []
                
                for exp_date in expirations:
                    exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                    dte = (exp_datetime - today).days
                    if min_dte <= dte <= max_dte:
                        valid_expirations.append(exp_date)
                
                # Obtener cadena de opciones para cada expiración válida
                for exp_date in valid_expirations[:1]:  # Limitar a 1 expiración por ticker para velocidad
                    chain_data = self.get_option_chain(ticker, exp_date)
                    if not chain_data or 'options' not in chain_data:
                        continue
                    
                    options = chain_data['options']['option']
                    if not isinstance(options, list):
                        options = [options]
                    
                    # Filtrar opciones según criterios (procesar máximo 50 opciones por velocidad)
                    for option in options[:50]:
                        opt_type = option.get('option_type', '')
                        
                        # Filtrar por tipo
                        if option_type == 'Puts' and opt_type != 'put':
                            continue
                        elif option_type == 'Calls' and opt_type != 'call':
                            continue
                        
                        # Obtener datos
                        strike = float(option.get('strike', 0) or 0)
                        bid = float(option.get('bid', 0) or 0)
                        
                        # Obtener delta de forma segura
                        greeks = option.get('greeks')
                        if greeks and isinstance(greeks, dict):
                            delta = abs(float(greeks.get('delta', 0) or 0))
                        else:
                            delta = 0
                        
                        # Aplicar filtros
                        if delta == 0 or delta < min_delta or delta > max_delta:
                            continue
                        if bid <= 0:  # Solo filtrar bids inválidos
                            continue
                        
                        # Calcular métricas
                        dte = (datetime.strptime(exp_date, '%Y-%m-%d') - today).days
                        roi_annual = (bid / strike * 365 / dte * 100) if strike > 0 and dte > 0 else 0
                        probability = (1 - delta) * 100  # Aproximación de probabilidad OTM
                        
                        # Calificación (0-100)
                        rating = (roi_annual * 0.4 + probability * 0.4 + (bid / max_delta) * 20) / 2
                        rating = min(100, max(0, rating))
                        
                        opportunities.append({
                            'ticker': ticker,
                            'type': 'PUT' if opt_type == 'put' else 'CALL',
                            'strike': strike,
                            'expiration': exp_date,
                            'dte': dte,
                            'premium': bid,
                            'delta': delta,
                            'probability': probability,
                            'roi_annual': roi_annual,
                            'rating': rating
                        })
                        
                        # Si ya tenemos suficientes oportunidades buenas, saltar al siguiente ticker
                        if len(opportunities) >= 200:
                            break
                    
                    # Break del loop de expiraciones si ya tenemos suficientes
                    if len(opportunities) >= 200:
                        break
            
            # Ordenar resultados
            sort_key = self.scan_sort_by.get()
            if sort_key == 'Premium':
                opportunities.sort(key=lambda x: x['premium'], reverse=True)
            elif sort_key == 'ROI Anualizado':
                opportunities.sort(key=lambda x: x['roi_annual'], reverse=True)
            elif sort_key == 'Probabilidad':
                opportunities.sort(key=lambda x: x['probability'], reverse=True)
            else:  # Premium/Riesgo
                opportunities.sort(key=lambda x: x['rating'], reverse=True)
            
            # Mostrar top 50 resultados
            for opp in opportunities[:50]:
                # Color según calificación
                tag = 'excellent' if opp['rating'] > 70 else 'good' if opp['rating'] > 50 else 'normal'
                
                self.scan_tree.insert('', tk.END, values=(
                    opp['ticker'],
                    f"${opp['strike']:.2f}",
                    f"${opp['premium']:.2f}",
                    f"{opp['delta']:.3f}",
                    opp['dte'],
                    f"{opp['roi_annual']:.1f}%",
                    f"{opp['rating']:.0f}"
                ), tags=(tag,))
            
            # Configurar colores por tags
            self.scan_tree.tag_configure('excellent', background='#1B5E20', foreground='#00C853')
            self.scan_tree.tag_configure('good', background='#1A237E', foreground='#4A90E2')
            self.scan_tree.tag_configure('normal', background='#2D2D30', foreground='#E0E0E0')
            
            self.scan_status.config(text=f"✅ Encontradas {len(opportunities[:50])} oportunidades")
            
            # Mostrar automáticamente la gráfica de la mejor oportunidad
            if opportunities:
                best_ticker = opportunities[0]['ticker']
                self.chart_ticker.delete(0, tk.END)
                self.chart_ticker.insert(0, best_ticker)
                # Ejecutar la gráfica desde el hilo principal
                self.root.after(100, self.show_chart)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al escanear: {str(e)}")
            self.scan_status.config(text="❌ Error en el escaneo")

    # ==================== SEGUIMIENTO DE CUENTA ====================
    
    def create_account_tracker(self):
        """Crea la interfaz de seguimiento de cuenta"""
        # Frame principal
        account_main = ttk.Frame(self.tab_account, padding="10")
        account_main.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(account_main, text="📈 SEGUIMIENTO DE CUENTA", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Frame superior: Resumen de cuenta
        summary_frame = ttk.LabelFrame(account_main, text=" Resumen de Cuenta ", padding="15")
        summary_frame.pack(fill=tk.X, pady=10)
        
        # Grid para resumen
        # Fila 1
        ttk.Label(summary_frame, text="💰 Balance Total:", font=('Segoe UI', 11, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.acc_balance = ttk.Label(summary_frame, text="$0.00", 
                                     foreground="#4A90E2", font=('Segoe UI', 12, 'bold'))
        self.acc_balance.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="📊 P&L YTD:", font=('Arial', 11, 'bold')).grid(
            row=0, column=2, sticky=tk.W, padx=20, pady=5)
        self.acc_pl_ytd = ttk.Label(summary_frame, text="$0.00", 
                                    foreground="green", font=('Arial', 12, 'bold'))
        self.acc_pl_ytd.grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="📈 Return %:", font=('Arial', 11, 'bold')).grid(
            row=0, column=4, sticky=tk.W, padx=20, pady=5)
        self.acc_return = ttk.Label(summary_frame, text="0.00%", 
                                    foreground="green", font=('Arial', 12, 'bold'))
        self.acc_return.grid(row=0, column=5, sticky=tk.W, padx=10, pady=5)
        
        # Fila 2
        ttk.Label(summary_frame, text="💵 Cash:", font=('Arial', 11)).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.acc_cash = ttk.Label(summary_frame, text="$0.00", font=('Arial', 11))
        self.acc_cash.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="⚡ Buying Power:", font=('Arial', 11)).grid(
            row=1, column=2, sticky=tk.W, padx=20, pady=5)
        self.acc_buying_power = ttk.Label(summary_frame, text="$0.00", font=('Arial', 11))
        self.acc_buying_power.grid(row=1, column=3, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(summary_frame, text="🎯 Win Rate:", font=('Arial', 11)).grid(
            row=1, column=4, sticky=tk.W, padx=20, pady=5)
        self.acc_win_rate = ttk.Label(summary_frame, text="0.0%", font=('Arial', 11))
        self.acc_win_rate.grid(row=1, column=5, sticky=tk.W, padx=10, pady=5)
        
        # Mostrar número de cuenta
        ttk.Label(summary_frame, text="🏦 Cuenta:", font=('Arial', 9)).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.acc_number_label = ttk.Label(summary_frame, text="No seleccionada", 
                                         font=('Arial', 9), foreground="gray")
        self.acc_number_label.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # Frame central: Pestañas de contenido
        content_notebook = ttk.Notebook(account_main)
        content_notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Sub-pestaña 1: Historial de Operaciones
        tab_history = ttk.Frame(content_notebook)
        content_notebook.add(tab_history, text="📋 Historial")
        
        # Controles de filtro
        filter_frame = ttk.Frame(tab_history)
        filter_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(filter_frame, text="Desde:").pack(side=tk.LEFT, padx=5)
        self.date_from = ttk.Entry(filter_frame, width=12)
        self.date_from.insert(0, "2025-01-01")
        self.date_from.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Hasta:").pack(side=tk.LEFT, padx=5)
        self.date_to = ttk.Entry(filter_frame, width=12)
        self.date_to.insert(0, datetime.now().strftime('%d-%m-%Y'))
        self.date_to.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="🔍 Filtrar", command=self.filter_history).pack(side=tk.LEFT, padx=10)
        ttk.Button(filter_frame, text="💾 Exportar CSV", command=self.export_history).pack(side=tk.LEFT, padx=5)
        
        # Tabla de historial
        history_table_frame = ttk.Frame(tab_history)
        history_table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('Fecha', 'Tipo', 'Símbolo', 'Qty', 'Precio', 'Valor', 'P&L', 'Estado')
        self.history_tree = ttk.Treeview(history_table_frame, columns=columns, 
                                        show='headings', height=15)
        
        column_widths = {'Fecha': 100, 'Tipo': 80, 'Símbolo': 120, 'Qty': 60,
                        'Precio': 80, 'Valor': 100, 'P&L': 100, 'Estado': 100}
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=column_widths.get(col, 100), anchor=tk.CENTER)
        
        scrollbar_hist = ttk.Scrollbar(history_table_frame, orient=tk.VERTICAL, 
                                      command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar_hist.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_hist.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        history_table_frame.columnconfigure(0, weight=1)
        history_table_frame.rowconfigure(0, weight=1)
        
        # Sub-pestaña 2: Estadísticas
        tab_stats = ttk.Frame(content_notebook)
        content_notebook.add(tab_stats, text="📊 Estadísticas")
        
        stats_frame = ttk.Frame(tab_stats, padding="20")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Texto para estadísticas
        self.stats_text = tk.Text(stats_frame, height=20, wrap=tk.WORD, 
                                 font=('Consolas', 10),
                                 bg='#2D2D30', fg='#E0E0E0',
                                 insertbackground='#E0E0E0',
                                 selectbackground='#0078D4',
                                 selectforeground='#E0E0E0',
                                 borderwidth=0, relief='flat')
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, 
                                       command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sub-pestaña 3: Posiciones Actuales
        tab_positions = ttk.Frame(content_notebook)
        content_notebook.add(tab_positions, text="📦 Posiciones")
        
        positions_table_frame = ttk.Frame(tab_positions, padding="5")
        positions_table_frame.pack(fill=tk.BOTH, expand=True)
        
        pos_columns = ('Símbolo', 'Tipo', 'Cantidad', 'Costo Base', 'Precio', 'Valor', 'P&L', '%')
        self.positions_tree = ttk.Treeview(positions_table_frame, columns=pos_columns, 
                                          show='headings', height=15)
        
        pos_widths = {'Símbolo': 100, 'Tipo': 80, 'Cantidad': 80, 'Costo Base': 100,
                     'Precio': 80, 'Valor': 100, 'P&L': 100, '%': 80}
        
        for col in pos_columns:
            self.positions_tree.heading(col, text=col)
            self.positions_tree.column(col, width=pos_widths.get(col, 100), anchor=tk.CENTER)
        
        scrollbar_pos = ttk.Scrollbar(positions_table_frame, orient=tk.VERTICAL, 
                                     command=self.positions_tree.yview)
        self.positions_tree.configure(yscroll=scrollbar_pos.set)
        
        self.positions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_pos.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        positions_table_frame.columnconfigure(0, weight=1)
        positions_table_frame.rowconfigure(0, weight=1)
        
        # Sub-pestaña 4: Primas Mensuales
        tab_premiums = ttk.Frame(content_notebook)
        content_notebook.add(tab_premiums, text="📈 Beneficios y Proyección")
        
        premiums_frame = ttk.Frame(tab_premiums, padding="10")
        premiums_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para la gráfica
        self.premiums_chart_frame = ttk.Frame(premiums_frame)
        self.premiums_chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cargar datos iniciales
        self.account_id = None  # Se obtendrá del perfil
        self.history_data = []
        self.gainloss_data = None
        
    def get_user_profile(self):
        """Obtiene el perfil del usuario y todas las cuentas"""
        url = f"{self.base_url}/user/profile"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data and 'profile' in data:
                profile = data['profile']
                # El account puede estar en diferentes ubicaciones
                if 'account' in profile:
                    accounts = profile['account']
                    if isinstance(accounts, list):
                        return accounts  # Devolver todas las cuentas
                    else:
                        return [accounts]  # Devolver como lista
            return None
        except:
            return None
    
    def select_account(self):
        """Permite al usuario seleccionar qué cuenta usar"""
        accounts = self.get_user_profile()
        
        if not accounts:
            messagebox.showerror("Error", "No se pudieron obtener las cuentas")
            return
        
        if len(accounts) == 1:
            messagebox.showinfo("Info", "Solo tienes una cuenta vinculada")
            return
        
        # Crear diálogo de selección
        dialog = tk.Toplevel(self.root)
        dialog.title("Seleccionar Cuenta")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Selecciona la cuenta a usar:", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Frame para las cuentas
        accounts_frame = ttk.Frame(dialog)
        accounts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        selected_var = tk.StringVar()
        
        for acc in accounts:
            acc_number = acc.get('account_number', 'N/A')
            acc_type = acc.get('type', 'N/A')
            
            # Obtener balance de cada cuenta para mostrar
            balance_info = ""
            try:
                balance_data = self.get_account_balance(acc_number)
                if balance_data and 'balances' in balance_data:
                    balances = balance_data['balances']
                    if isinstance(balances, list):
                        balance = balances[0]
                    else:
                        balance = balances
                    equity = balance.get('total_equity', 0) or balance.get('account_value', 0)
                    balance_info = f" - Balance: ${equity:,.2f}"
            except:
                pass
            
            radio_text = f"{acc_number} ({acc_type}){balance_info}"
            ttk.Radiobutton(accounts_frame, text=radio_text, 
                           variable=selected_var, value=acc_number).pack(anchor=tk.W, pady=5)
        
        # Preseleccionar la cuenta actual si existe
        if self.account_id:
            selected_var.set(self.account_id)
        elif len(accounts) > 1:
            selected_var.set(accounts[1]['account_number'])  # Preseleccionar la segunda
        
        def save_selection():
            selected = selected_var.get()
            if not selected:
                messagebox.showwarning("Advertencia", "Selecciona una cuenta")
                return
            
            self.account_id = selected
            self.save_config()
            self.acc_number_label.config(text=f"***{selected[-4:]}", foreground="blue")
            dialog.destroy()
            messagebox.showinfo("Éxito", f"Cuenta {selected} seleccionada")
            # Actualizar datos automáticamente
            self.refresh_account_data()
        
        ttk.Button(dialog, text="Guardar", command=save_selection).pack(pady=10)
    
    def get_account_balance(self, account_id):
        """Obtiene el balance de la cuenta"""
        url = f"{self.base_url}/accounts/{account_id}/balances"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_account_history(self, account_id):
        """Obtiene el historial de operaciones desde inicio de año"""
        # Obtener fecha de inicio del año y fecha actual
        start_date = f"{datetime.now().year}-01-01"
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/accounts/{account_id}/history"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        params = {
            'start': start_date,
            'end': end_date,
            'limit': 1000  # Obtener hasta 1000 eventos
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_account_gainloss(self, account_id):
        """Obtiene el P&L realizado desde inicio de año"""
        # Obtener fecha de inicio del año y fecha actual
        start_date = f"{datetime.now().year}-01-01"
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/accounts/{account_id}/gainloss"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        params = {
            'start': start_date,
            'end': end_date
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_account_positions(self, account_id):
        """Obtiene las posiciones actuales"""
        url = f"{self.base_url}/accounts/{account_id}/positions"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def refresh_account_data(self):
        """Actualiza todos los datos de la cuenta"""
        thread = threading.Thread(target=self._refresh_account_thread)
        thread.daemon = True
        thread.start()
    
    def _refresh_account_thread(self):
        """Thread para actualizar datos de cuenta"""
        self.status_label.config(text="Actualizando datos de cuenta...")
        
        # Obtener account_id si no lo tenemos
        if not self.account_id:
            accounts = self.get_user_profile()
            if not accounts:
                messagebox.showerror("Error", "No se pudo obtener el ID de cuenta")
                self.status_label.config(text="Error al obtener ID de cuenta")
                return
            
            # Buscar la cuenta que termina en 52350
            target_account = None
            for acc in accounts:
                acc_number = acc.get('account_number', '')
                if acc_number.endswith('52350'):
                    target_account = acc_number
                    break
            
            if target_account:
                self.account_id = target_account
                self.save_config()
                self.acc_number_label.config(text=f"***{self.account_id[-4:]}", foreground="blue")
            else:
                messagebox.showerror("Error", "No se encontró la cuenta terminada en 52350")
                self.status_label.config(text="Cuenta no encontrada")
                return
        
        # Obtener balance
        balance_data = self.get_account_balance(self.account_id)
        if balance_data and 'balances' in balance_data:
            balances = balance_data['balances']
            
            # Puede ser un objeto directo o dentro de una lista
            if isinstance(balances, list):
                balance = balances[0]
            else:
                balance = balances
            
            total_equity = balance.get('total_equity', 0) or balance.get('account_value', 0)
            total_cash = balance.get('total_cash', 0) or balance.get('cash_available', 0)
            buying_power = balance.get('option_buying_power', 0) or balance.get('buying_power', 0)
            
            self.acc_balance.config(text=f"${total_equity:,.2f}")
            self.acc_cash.config(text=f"${total_cash:,.2f}")
            self.acc_buying_power.config(text=f"${buying_power:,.2f}")
        
        # Obtener historial
        history_data = self.get_account_history(self.account_id)
        self.update_history_table(history_data)
        
        # Obtener gainloss
        gainloss_data = self.get_account_gainloss(self.account_id)
        self.update_statistics(gainloss_data)
        
        # Actualizar gráfica de beneficios mensuales (debe ir después de obtener gainloss)
        self.gainloss_data = gainloss_data  # Guardar para la gráfica
        self.update_premiums_chart()
        
        # Obtener posiciones
        positions_data = self.get_account_positions(self.account_id)
        self.update_positions_table(positions_data)
        
        self.status_label.config(text="Datos de cuenta actualizados")
        messagebox.showinfo("Éxito", "Datos actualizados correctamente")
    
    def update_history_table(self, history_data):
        """Actualiza la tabla de historial"""
        # Limpiar tabla
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        if not history_data or 'history' not in history_data:
            return
        
        history = history_data['history']
        if 'event' not in history:
            return
        
        events = history['event']
        if not isinstance(events, list):
            events = [events]
        
        # Guardar para filtrado posterior y para la gráfica
        self.history_data_events = events
        self.history_data = history_data  # Guardar el objeto completo también
        
        # Mostrar eventos - más recientes primero
        # Ordenar por fecha descendente (más nuevo primero) y tomar los primeros 100
        sorted_events = sorted(events, key=lambda x: x.get('date', ''), reverse=True)
        for event in sorted_events[:100]:  # Primeros 100 (más recientes)
            date = self.format_date(event.get('date', ''))
            event_type = event.get('type', '')
            
            # Extraer información según tipo de evento
            amount = event.get('amount', 0)
            description = event.get('description', '')
            
            # Parsear símbolo del description
            symbol = ''
            if 'trade' in event:
                trade = event['trade']
                symbol = trade.get('symbol', '')
                qty = trade.get('quantity', 0)
                price = trade.get('price', 0)
            else:
                qty = ''
                price = ''
            
            self.history_tree.insert('', tk.END, values=(
                date,
                event_type,
                symbol,
                qty,
                f"${price}" if price else '',
                f"${amount:.2f}" if amount else '',
                '',  # P&L se calcula después
                'Completado'
            ))
    
    def update_premiums_chart(self):
        """Actualiza las gráficas de beneficios mensuales, acumulativo y proyección"""
        if not self.account_id or not self.gainloss_data:
            return
        
        try:
            # Limpiar frame anterior
            for widget in self.premiums_chart_frame.winfo_children():
                widget.destroy()
            
            # Diccionario para acumular P&L por mes
            monthly_pl = {}
            
            # Procesar datos de gainloss
            gainloss = self.gainloss_data.get('gainloss', {})
            if 'closed_position' not in gainloss:
                # Sin datos
                ttk.Label(self.premiums_chart_frame, 
                         text="No hay datos de beneficios disponibles",
                         font=('Arial', 12)).pack(pady=50)
                return
            
            closed_positions = gainloss['closed_position']
            if not isinstance(closed_positions, list):
                closed_positions = [closed_positions]
            
            # Filtrar solo posiciones de 2025 y acumular por mes
            for position in closed_positions:
                close_date = position.get('close_date', '')
                if not close_date or '2025' not in close_date:
                    continue
                
                gain_loss = position.get('gain_loss', 0)
                
                try:
                    # Extraer año-mes
                    year_month = close_date[:7]  # 'YYYY-MM'
                    if year_month not in monthly_pl:
                        monthly_pl[year_month] = 0
                    monthly_pl[year_month] += float(gain_loss)
                except:
                    pass
            
            if not monthly_pl:
                ttk.Label(self.premiums_chart_frame, 
                         text="No hay operaciones cerradas en 2025",
                         font=('Arial', 12)).pack(pady=50)
                return
            
            # Ordenar por mes
            sorted_months = sorted(monthly_pl.keys())
            months_labels = []
            pl_values = []
            
            for month in sorted_months:
                # Convertir 'YYYY-MM' a formato más legible 'MM/YY'
                try:
                    year = month[:4]
                    month_num = month[5:7]
                    months_labels.append(f"{month_num}/{year[2:]}")
                    pl_values.append(monthly_pl[month])
                except:
                    months_labels.append(month)
                    pl_values.append(monthly_pl[month])
            
            # Calcular acumulativo
            cumulative_pl = []
            cumulative_sum = 0
            for pl in pl_values:
                cumulative_sum += pl
                cumulative_pl.append(cumulative_sum)
            
            # Crear figura con 3 subgráficas - Tema Oscuro
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import numpy as np
            
            fig = Figure(figsize=(12, 10), dpi=100, facecolor='#1E1E1E')
            
            # ==================== GRÁFICA 1: P&L Mensual ====================
            ax1 = fig.add_subplot(311, facecolor='#2D2D30')
            
            # Colores: verde para positivo, rojo para negativo
            colors = ['#00C853' if pl >= 0 else '#F44336' for pl in pl_values]
            bars = ax1.bar(months_labels, pl_values, color=colors, alpha=0.9, edgecolor='#1E1E1E', linewidth=1.5)
            
            ax1.set_title('Beneficios/Pérdidas Mensuales', fontsize=14, fontweight='bold', pad=15, color='#4A90E2')
            ax1.set_ylabel('P&L ($)', fontsize=11, fontweight='bold', color='#E0E0E0')
            ax1.tick_params(colors='#E0E0E0', labelsize=9)
            ax1.grid(axis='y', alpha=0.15, linestyle='--', color='#3E3E42')
            ax1.set_axisbelow(True)
            ax1.axhline(y=0, color='#858585', linestyle='-', linewidth=1.2, alpha=0.7)
            
            # Configurar spines
            for spine in ax1.spines.values():
                spine.set_color('#3E3E42')
                spine.set_linewidth(1)
            
            # Rotar etiquetas del eje X para evitar solapamiento
            ax1.tick_params(axis='x', rotation=45, labelsize=8)
            for label in ax1.get_xticklabels():
                label.set_horizontalalignment('right')
            
            # Valores encima de cada barra
            for bar in bars:
                height = bar.get_height()
                label_y = height + (max(pl_values) * 0.02) if height >= 0 else height - (max(pl_values) * 0.02)
                va = 'bottom' if height >= 0 else 'top'
                ax1.text(bar.get_x() + bar.get_width()/2., label_y,
                       f'${height:,.0f}',
                       ha='center', va=va, fontsize=8, fontweight='bold', color='#E0E0E0')
            
            # Total y promedio
            total_pl = sum(pl_values)
            avg_pl = total_pl / len(pl_values) if pl_values else 0
            ax1.text(0.02, 0.98, f'Total: ${total_pl:,.2f}\nPromedio: ${avg_pl:,.2f}',
                   transform=ax1.transAxes, fontsize=10, verticalalignment='top', color='#E0E0E0',
                   bbox=dict(boxstyle='round', facecolor='#3E3E42', alpha=0.9, edgecolor='#4A90E2'))
            
            # ==================== GRÁFICA 2: P&L Acumulativo ====================
            ax2 = fig.add_subplot(312, facecolor='#2D2D30')
            
            line = ax2.plot(months_labels, cumulative_pl, marker='o', linewidth=2.5, 
                           markersize=8, color='#4A90E2', label='P&L Acumulativo')
            ax2.fill_between(range(len(months_labels)), cumulative_pl, alpha=0.3, color='#4A90E2')
            
            ax2.set_title('Beneficios Acumulativos', fontsize=14, fontweight='bold', pad=15, color='#4A90E2')
            ax2.set_ylabel('P&L Acumulado ($)', fontsize=11, fontweight='bold', color='#E0E0E0')
            ax2.tick_params(colors='#E0E0E0', labelsize=9)
            ax2.grid(axis='both', alpha=0.15, linestyle='--', color='#3E3E42')
            ax2.set_axisbelow(True)
            ax2.axhline(y=0, color='#858585', linestyle='-', linewidth=1.2, alpha=0.7)
            
            # Configurar spines
            for spine in ax2.spines.values():
                spine.set_color('#3E3E42')
                spine.set_linewidth(1)
            
            # Rotar etiquetas del eje X para evitar solapamiento
            ax2.tick_params(axis='x', rotation=45, labelsize=8)
            for label in ax2.get_xticklabels():
                label.set_horizontalalignment('right')
            
            # Valores en los puntos
            for i, (x, y) in enumerate(zip(range(len(months_labels)), cumulative_pl)):
                ax2.text(x, y, f'${y:,.0f}',
                       ha='center', va='bottom', fontsize=7, fontweight='bold', color='#E0E0E0')
            
            # Mostrar valor final
            final_pl = cumulative_pl[-1] if cumulative_pl else 0
            color_final = '#00C853' if final_pl >= 0 else '#F44336'
            ax2.text(0.02, 0.98, f'P&L Total: ${final_pl:,.2f}',
                   transform=ax2.transAxes, fontsize=11, verticalalignment='top',
                   fontweight='bold', color=color_final,
                   bbox=dict(boxstyle='round', facecolor='#3E3E42', alpha=0.9, edgecolor='#4A90E2'))
            
            # ==================== GRÁFICA 3: Proyección a 1 año ====================
            ax3 = fig.add_subplot(313, facecolor='#2D2D30')
            
            # Calcular proyección lineal
            if len(pl_values) >= 2:
                # Usar regresión lineal simple
                x_data = np.arange(len(pl_values))
                y_data = np.array(cumulative_pl)
                
                # Ajuste lineal
                z = np.polyfit(x_data, y_data, 1)
                p = np.poly1d(z)
                
                # Días transcurridos desde el primer mes
                from datetime import datetime
                first_month = sorted_months[0] + '-01'
                last_month = sorted_months[-1] + '-01'
                first_date = datetime.strptime(first_month, '%Y-%m-%d')
                last_date = datetime.strptime(last_month, '%Y-%m-%d')
                current_date = datetime.now()
                
                # Calcular meses hasta fin de año
                months_passed = len(pl_values)
                months_in_year = 12
                months_remaining = months_in_year - (datetime.now().month - 1)
                
                # Generar fechas futuras (hasta completar 12 meses o fin de 2025)
                future_months = []
                future_labels = []
                
                last_year = int(sorted_months[-1][:4])
                last_month_num = int(sorted_months[-1][5:7])
                
                for i in range(1, months_remaining + 1):
                    next_month = last_month_num + i
                    next_year = last_year
                    if next_month > 12:
                        next_month -= 12
                        next_year += 1
                    if next_year > 2025:
                        break
                    future_months.append(f"{next_year}-{next_month:02d}")
                    future_labels.append(f"{next_month:02d}/{str(next_year)[2:]}")
                
                # Proyectar valores
                future_x = np.arange(len(pl_values), len(pl_values) + len(future_months))
                future_y = p(future_x)
                
                # Graficar datos reales
                ax3.plot(range(len(months_labels)), cumulative_pl, marker='o', linewidth=2.5,
                        markersize=8, color='#4A90E2', label='Real')
                
                # Graficar proyección
                all_x = np.concatenate([x_data, future_x])
                all_y = p(all_x)
                ax3.plot(all_x, all_y, linestyle='--', linewidth=2, color='#FF9800',
                        marker='s', markersize=6, alpha=0.8, label='Proyección')
                
                # Línea vertical separando real de proyección
                ax3.axvline(x=len(pl_values)-0.5, color='#858585', linestyle=':', linewidth=2, alpha=0.5)
                
                # Configurar etiquetas del eje X
                all_labels = months_labels + future_labels
                ax3.set_xticks(range(len(all_labels)))
                ax3.set_xticklabels(all_labels, rotation=45, color='#E0E0E0')
                
                ax3.set_title('Proyección de Beneficios a Fin de Año', fontsize=14, fontweight='bold', pad=15, color='#4A90E2')
                ax3.set_ylabel('P&L Acumulado ($)', fontsize=11, fontweight='bold', color='#E0E0E0')
                ax3.tick_params(colors='#E0E0E0', labelsize=9)
                ax3.grid(axis='both', alpha=0.15, linestyle='--', color='#3E3E42')
                ax3.set_axisbelow(True)
                ax3.axhline(y=0, color='#858585', linestyle='-', linewidth=1.2, alpha=0.7)
                
                # Configurar spines
                for spine in ax3.spines.values():
                    spine.set_color('#3E3E42')
                    spine.set_linewidth(1)
                
                # Leyenda con estilo oscuro
                legend = ax3.legend(loc='upper left', fontsize=10, facecolor='#3E3E42', 
                                   edgecolor='#4A90E2', framealpha=0.9)
                legend.get_frame().set_linewidth(1.5)
                for text in legend.get_texts():
                    text.set_color('#E0E0E0')
                
                # Mostrar proyección final
                projected_final = future_y[-1] if len(future_y) > 0 else cumulative_pl[-1]
                ax3.text(0.98, 0.02, f'Proyección fin de año: ${projected_final:,.2f}',
                       transform=ax3.transAxes, fontsize=11, verticalalignment='bottom',
                       horizontalalignment='right', fontweight='bold', color='#FF9800',
                       bbox=dict(boxstyle='round', facecolor='#3E3E42', alpha=0.9, edgecolor='#FF9800'))
            else:
                ax3.text(0.5, 0.5, 'Se necesitan al menos 2 meses de datos para proyección',
                        transform=ax3.transAxes, fontsize=11, ha='center', va='center', color='#E0E0E0')
            
            # Ajustar layout con más espacio para evitar solapamientos
            fig.tight_layout(pad=2.5, h_pad=3.0, w_pad=1.5)
            fig.subplots_adjust(bottom=0.08, top=0.96)
            
            # Integrar gráfica en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.premiums_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            import traceback
            error_msg = f"Error al generar gráficas: {str(e)}\n{traceback.format_exc()}"
            ttk.Label(self.premiums_chart_frame, 
                     text=error_msg,
                     font=('Arial', 10), foreground='red').pack(pady=50)
    
    def update_statistics(self, gainloss_data):
        """Actualiza las estadísticas"""
        self.stats_text.delete(1.0, tk.END)
        
        current_year = datetime.now().year
        stats = "═══════════════════════════════════════════════════════════\n"
        stats += f"  ESTADÍSTICAS DE TRADING {current_year} (YTD)\n"
        stats += "═══════════════════════════════════════════════════════════\n\n"
        
        if gainloss_data and 'gainloss' in gainloss_data:
            gl = gainloss_data['gainloss']
            
            if 'closed_position' in gl:
                all_positions = gl['closed_position']
                if not isinstance(all_positions, list):
                    all_positions = [all_positions]
                
                # Filtrar solo posiciones del año actual
                positions = [p for p in all_positions if str(current_year) in p.get('close_date', '')]
                
                total_trades = len(positions)
                winners = sum(1 for p in positions if p.get('gain_loss', 0) > 0)
                losers = total_trades - winners
                win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
                
                total_pl = sum(p.get('gain_loss', 0) for p in positions)
                avg_win = sum(p.get('gain_loss', 0) for p in positions if p.get('gain_loss', 0) > 0) / winners if winners > 0 else 0
                avg_loss = sum(p.get('gain_loss', 0) for p in positions if p.get('gain_loss', 0) < 0) / losers if losers > 0 else 0
                
                best_trade = max(positions, key=lambda x: x.get('gain_loss', 0)) if positions else None
                worst_trade = min(positions, key=lambda x: x.get('gain_loss', 0)) if positions else None
                
                stats += f"📊 Total de operaciones cerradas: {total_trades}\n"
                stats += f"✅ Ganadas: {winners} ({win_rate:.1f}%)\n"
                stats += f"❌ Perdidas: {losers} ({100-win_rate:.1f}%)\n\n"
                
                color = "positivo" if total_pl >= 0 else "negativo"
                stats += f"💰 P&L Total Realizado: ${total_pl:,.2f} ({color})\n"
                stats += f"📈 Promedio por operación: ${total_pl/total_trades:.2f}\n\n" if total_trades > 0 else ""
                
                stats += f"🎯 Promedio de ganancias: ${avg_win:.2f}\n"
                stats += f"📉 Promedio de pérdidas: ${avg_loss:.2f}\n\n"
                
                if best_trade:
                    stats += f"🏆 Mejor operación: ${best_trade.get('gain_loss', 0):.2f}\n"
                    stats += f"   {best_trade.get('symbol', '')} - {best_trade.get('close_date', '')[:10]}\n\n"
                
                if worst_trade:
                    stats += f"💔 Peor operación: ${worst_trade.get('gain_loss', 0):.2f}\n"
                    stats += f"   {worst_trade.get('symbol', '')} - {worst_trade.get('close_date', '')[:10]}\n\n"
                
                # Actualizar labels superiores
                self.acc_pl_ytd.config(text=f"${total_pl:,.2f}", 
                                      foreground="green" if total_pl >= 0 else "red")
                self.acc_win_rate.config(text=f"{win_rate:.1f}%")
                
                # Calcular return si tenemos el balance
                balance_text = self.acc_balance.cget("text").replace('$', '').replace(',', '')
                if balance_text and balance_text != "0.00":
                    balance = float(balance_text)
                    initial_capital = balance - total_pl
                    if initial_capital > 0:
                        return_pct = (total_pl / initial_capital) * 100
                        self.acc_return.config(text=f"{return_pct:.2f}%",
                                             foreground="green" if return_pct >= 0 else "red")
                
                stats += "───────────────────────────────────────────────────────────\n"
                stats += "  DISTRIBUCIÓN POR SÍMBOLO\n"
                stats += "───────────────────────────────────────────────────────────\n\n"
                
                # Agrupar por símbolo
                symbol_stats = {}
                for pos in positions:
                    symbol = pos.get('symbol', 'N/A')
                    pl = pos.get('gain_loss', 0)
                    
                    if symbol not in symbol_stats:
                        symbol_stats[symbol] = {'count': 0, 'total_pl': 0}
                    
                    symbol_stats[symbol]['count'] += 1
                    symbol_stats[symbol]['total_pl'] += pl
                
                # Ordenar por P&L
                sorted_symbols = sorted(symbol_stats.items(), 
                                      key=lambda x: x[1]['total_pl'], reverse=True)
                
                for symbol, data in sorted_symbols[:10]:  # Top 10
                    stats += f"{symbol:10} | {data['count']:3} ops | ${data['total_pl']:>10,.2f}\n"
        else:
            stats += "No hay datos de P&L disponibles.\n"
            stats += "\nAsegúrate de que tu cuenta tenga operaciones cerradas.\n"
        
        self.stats_text.insert(1.0, stats)
    
    def update_positions_table(self, positions_data):
        """Actualiza la tabla de posiciones actuales"""
        # Limpiar tabla
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
        
        if not positions_data or 'positions' not in positions_data:
            return
        
        positions = positions_data['positions']
        if 'position' not in positions:
            return
        
        pos_list = positions['position']
        if not isinstance(pos_list, list):
            pos_list = [pos_list]
        
        for pos in pos_list:
            symbol = pos.get('symbol', '')
            quantity = pos.get('quantity', 0)
            cost_basis = pos.get('cost_basis', 0)
            
            # Obtener precio actual del quote
            quote_data = self.get_quote(symbol)
            current_price = 0
            if quote_data and 'quotes' in quote_data:
                quote = quote_data['quotes']['quote']
                if isinstance(quote, dict):
                    current_price = quote.get('last', 0) or quote.get('bid', 0)
            
            # Determinar tipo (stock/option)
            pos_type = 'Stock' if len(symbol) <= 5 else 'Option'
            
            # Usar directamente los datos del broker (Total Gain/Loss)
            # El broker ya calcula el P&L correctamente
            pl = float(pos.get('gain_loss', 0) or 0)
            pl_pct = float(pos.get('gain_loss_percent', 0) or 0)
            
            # Valor actual de mercado
            if pos_type == 'Option':
                current_value = current_price * abs(quantity) * 100
            else:
                current_value = current_price * abs(quantity)
            
            pl_color = 'green' if pl >= 0 else 'red'
            
            self.positions_tree.insert('', tk.END, values=(
                symbol,
                pos_type,
                quantity,
                f"${abs(cost_basis):.2f}" if cost_basis else '$0.00',
                f"${current_price:.2f}",
                f"${abs(current_value):.2f}",
                f"${pl:.2f}",
                f"{pl_pct:.2f}%"
            ), tags=(pl_color,))
        
        # Configurar colores
        self.positions_tree.tag_configure('green', foreground='green')
        self.positions_tree.tag_configure('red', foreground='red')
    
    def filter_history(self):
        """Filtra el historial por fechas"""
        # Implementar filtrado
        messagebox.showinfo("Info", "Función de filtrado en desarrollo")
    
    def export_history(self):
        """Exporta el historial a CSV"""
        if not hasattr(self, 'history_data_events') or not self.history_data_events:
            messagebox.showwarning("Advertencia", "No hay datos para exportar")
            return
        
        try:
            filename = f"historial_cuenta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                f.write("Fecha,Tipo,Descripción,Monto\n")
                for event in self.history_data_events:
                    date = event.get('date', '')
                    event_type = event.get('type', '')
                    description = event.get('description', '').replace(',', ';')
                    amount = event.get('amount', 0)
                    f.write(f"{date},{event_type},{description},{amount}\n")
            
            messagebox.showinfo("Éxito", f"Historial exportado a {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TradierOptionsApp(root)
    root.mainloop()





































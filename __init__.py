    def __init__(self, root):
        self.root = root
        self.root.title("💥 Pandarcade ROM Injector PRO v1.0 [100% RAW & OFFLINE]")
        self.root.geometry("680x540")
        self.root.resizable(False, False)
        
        # Conectamos los componentes del sistema
        self.core = PandarcadeCore(self.log)
        self.detector = SonyFormatDetector(self.log)
        self.db = PandarcadeDatabase()  # Mantiene el mismo nombre de la clase interna
        
        # Variables de control de rutas
        self.ruta_origen = tk.StringVar()
        self.ruta_destino = tk.StringVar()


    def setup_bios_tab(self):
        # Primero cargamos la paleta arcade
        colores = aplicar_estilo_arcade(self.root)
        
        self.tab_bios.configure(bg=colores["bg_principal"])
        
        # Marco de origen usando el estilo TTK
        frame_origen = ttk.LabelFrame(self.tab_bios, text=" 1. PACK DE BIOS REVUELTAS ")
        frame_origen.pack(fill="x", padx=20, pady=10)
        
        entry_origen = tk.Entry(frame_origen, textvariable=self.origen_path, font=colores["fuente_retro"], bg="#121214", fg=colores["cyan"], insertbackground="white")
        entry_origen.pack(side="left", padx=5, expand=True, fill="x")
        
        # Botón Examinar Origen Estilizado
        btn_browse_origen = crear_boton_arcade(frame_origen, "EXAMINAR...", self.seleccionar_origen, colores=colores)
        btn_browse_origen.pack(side="right", padx=5)

        # Botón de Acción Principal (El gran botón verde de la maquinita)
        self.btn_procesar = crear_boton_arcade(
            self.tab_bios, 
            "🕹️ INICIAR INYECCIÓN MAESTRA", 
            self.procesar_bios_ui, 
            es_accion_principal=True, 
            colores=colores
        )
        self.btn_procesar.pack(pady=15)

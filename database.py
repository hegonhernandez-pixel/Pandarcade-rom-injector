import os
import sqlite3

class PandarcadeDatabase:
    def __init__(self, log_callback):
        self.log = log_callback

    def inicializar_base_datos(self, ruta_games_folder):
        """Crea un archivo external_games.db nativo y limpio compatible con Pandora Box"""
        ruta_db = os.path.join(ruta_games_folder, "external_games.db")
        
        # Si ya existe una base de datos previa, la limpia para evitar colisiones
        if os.path.exists(ruta_db):
            try:
                os.remove(ruta_db)
            except Exception as e:
                self.log(f"⚠️ No se pudo limpiar el índice previo: {e}")

        self.log(f"🛠️ Construyendo base de datos SQLite nativa en: {ruta_db}")
        
        try:
            conexion = sqlite3.connect(ruta_db)
            cursor = conexion.cursor()
            
            # Creación de la tabla oficial estructurada que requiere el firmware 40S/Android
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY,
                    game_name TEXT NOT EXISTS,
                    file_name TEXT,
                    emulator_type INTEGER,
                    category INTEGER DEFAULT 0
                )
            ''')
            
            conexion.commit()
            conexion.close()
            self.log("✅ Estructura de tablas SQL inyectada correctamente.")
            return True
        except Exception as e:
            self.log(f"❌ Error crítico de base de datos: {e}")
            return False

    def registrar_juegos_en_db(self, ruta_games_folder, diccionario_juegos):
        """Inserta masivamente las rutas en crudo de los juegos dentro del archivo .db"""
        ruta_db = os.path.join(ruta_games_folder, "external_games.db")
        if not os.path.exists(ruta_db):
            self.inicializar_base_datos(ruta_games_folder)

        try:
            conexion = sqlite3.connect(ruta_db)
            cursor = conexion.cursor()
            
            registrados = 0
            # Mapeo lógico de emuladores para la base de datos interna de la consola
            mapa_id_emuladores = {'fba': 3, 'mame139': 5, 'mame78': 1, 'mame199': 5, 'megadrive': 2, 'nes': 4}

            for nombre_zip, (titulo_bonito, emulador_slug) in diccionario_juegos.items():
                id_emulador_consola = mapa_id_emuladores.get(emulador_slug, 5)
                
                # Inyección SQL directa sin comandos externos de consola
                cursor.execute('''
                    INSERT INTO games (game_name, file_name, emulator_type) 
                    VALUES (?, ?, ?)
                ''', (titulo_bonito, nombre_zip, id_emulador_consola))
                registrados += 1
                
            conexion.commit()
            conexion.close()
            self.log(f"⚡ ¡Base de datos blindada! {registrados} registros SQL inyectados con éxito.")
            return True
        except Exception as e:
            self.log(f"❌ Error al registrar juego en SQL: {e}")
            return False

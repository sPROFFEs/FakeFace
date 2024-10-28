import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from faker import Faker
from decimal import Decimal
from datetime import date, datetime, timedelta
import random
from json import JSONEncoder
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser
import string
import ttkthemes
import pyperclip
import os
import threading
from pathlib import Path
import logging
from ttkthemes import ThemedTk

# Configurar logging
logging.basicConfig(
    filename='identity_generator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Decimal, date, datetime)):
            return str(obj)
        return super().default(obj)

class CustomFaker:
    """Clase personalizada para generar datos de países sin locale"""
    def __init__(self, base_locale, country_data):
        self.faker = Faker(base_locale)
        self.country_data = country_data

    def first_name(self):
        return self.faker.first_name()

    def first_name_male(self):
        return self.faker.first_name_male()

    def first_name_female(self):
        return self.faker.first_name_female()

    def last_name(self):
        return self.faker.last_name()

    def address(self):
        street = random.choice(self.country_data['street_prefixes'])
        number = random.randint(1, 999)
        city = random.choice(self.country_data['city_list'])
        state = random.choice(self.country_data['states'])
        return f"{street} {self.faker.word().capitalize()} {number}\n{city}, {state}"

    def city(self):
        return random.choice(self.country_data['city_list'])

    def state(self):
        return random.choice(self.country_data['states'])

    def phone_number(self):
        digits = [str(random.randint(0, 9)) for _ in range(10)]
        phone_format = self.country_data.get('phone_format', '+{}{}-{}{}{}-{}{}{}{}')
        return phone_format.format(*digits)

    def email(self):
        return self.faker.email()

    def user_name(self):
        return self.faker.user_name()

    def domain_name(self):
        return self.faker.domain_name()

    def free_email_domain(self):
        return self.faker.free_email_domain()

    # Agregar cualquier otro método que necesites
    def __getattr__(self, name):
        """Fallback para cualquier método no implementado"""
        if hasattr(self.faker, name):
            return getattr(self.faker, name)
        raise AttributeError(f"'{self.__class__.__name__}' no tiene el atributo '{name}'")

    def generate_id(self):
        """Generar número de identificación según formato del país"""
        digits = [str(random.randint(0, 9)) for _ in range(10)]
        return self.country_data['id_format'].format(*digits)

    # Delegar otros métodos al Faker base
    def __getattr__(self, name):
        return getattr(self.faker, name)

class IdentityGenerator:
    def initialize_static_data(self):
        """Inicializar datos estáticos con soporte extendido para países"""

        # Países que ya tienen soporte directo en Faker
        self.direct_locales = {
            'Argentina': 'es_AR',
            'Australia': 'en_AU',
            'Austria': 'de_AT',
            'Bélgica': 'nl_BE',
            'Brasil': 'pt_BR',
            'Canadá': 'en_CA',
            'Chile': 'es_CL',
            'China': 'zh_CN',
            'Colombia': 'es_CO',
            'República Checa': 'cs_CZ',
            'Dinamarca': 'da_DK',
            'España': 'es_ES',
            'Estados Unidos': 'en_US',
            'Finlandia': 'fi_FI',
            'Francia': 'fr_FR',
            'Alemania': 'de_DE',
            'India': 'en_IN',
            'Indonesia': 'id_ID',
            'Irlanda': 'en_IE',
            'Italia': 'it_IT',
            'Japón': 'ja_JP',
            'México': 'es_MX',
            'Países Bajos': 'nl_NL',
            'Noruega': 'no_NO',
            'Polonia': 'pl_PL',
            'Portugal': 'pt_PT',
            'Reino Unido': 'en_GB',
            'Rusia': 'ru_RU',
            'Suecia': 'sv_SE',
            'Suiza': 'de_CH',
            'Taiwán': 'zh_TW',
            'Turquía': 'tr_TR'
        }

        self.custom_country_data = {
            'Bulgaria': {
                'phone_format': '+359-{}{}{}-{}{}{}-{}{}{}',
                'postal_code_format': '####',
                'id_format': '{}{}{}{}{}{}{}{}{}{}',  # DNI búlgaro de 10 dígitos
                'city_list': ['Sofía', 'Plovdiv', 'Varna', 'Burgas', 'Ruse', 'Stara Zagora', 
                            'Pleven', 'Sliven', 'Dobrich', 'Shumen'],
                'street_prefixes': ['улица', 'булевард', 'площад'],
                'states': ['Sofía-Ciudad', 'Plovdiv', 'Varna', 'Burgas', 'Ruse', 'Stara Zagora', 
                        'Pleven', 'Sliven', 'Dobrich', 'Razgrad', 'Pernik', 'Shumen', 'Yambol'],
                'locale_base': 'bg_BG'
            },
            'Grecia': {
                'phone_format': '+30-{}{}{}{}-{}{}{}{}{}{}{',
                'postal_code_format': '### ##',
                'id_format': '{} {}{}{}{}{}{}{}',  # Formato del DNI griego
                'city_list': ['Atenas', 'Tesalónica', 'Patras', 'Heraklion', 'Larisa', 
                            'Volos', 'Rodas', 'Ioannina', 'Chania', 'Kavala'],
                'street_prefixes': ['Odos', 'Leoforos', 'Plateia'],
                'states': ['Ática', 'Macedonia Central', 'Creta', 'Epiro', 'Islas Jónicas',
                        'Egeo Meridional', 'Egeo Septentrional', 'Peloponeso', 'Tesalia'],
                'locale_base': 'el_GR'
            },
            'Hong Kong': {
                'phone_format': '+852-{}{}{}{}-{}{}{}{}',
                'postal_code_format': '',  # Hong Kong no usa códigos postales
                'id_format': '{}{}{}{}{}{} ({})'.format,  # HKID format
                'city_list': ['Central and Western', 'Wan Chai', 'Eastern', 'Southern', 
                            'Yau Tsim Mong', 'Sham Shui Po', 'Kowloon City', 'Wong Tai Sin',
                            'Kwun Tong', 'North', 'Tai Po', 'Sha Tin', 'Sai Kung', 'Tsuen Wan',
                            'Tuen Mun', 'Yuen Long', 'Islands'],
                'street_prefixes': ['Street', 'Road', 'Avenue', 'Boulevard'],
                'states': ['Hong Kong Island', 'Kowloon', 'New Territories'],
                'locale_base': 'zh_HK'
            },
            'Hungría': {
                'phone_format': '+36-{}{}-{}{}{}-{}{}{}{}',
                'postal_code_format': '####',
                'id_format': '{}{}{}{}{}{}',  # Formato de ID húngaro
                'city_list': ['Budapest', 'Debrecen', 'Szeged', 'Miskolc', 'Pécs',
                            'Győr', 'Nyíregyháza', 'Kecskemét', 'Székesfehérvár'],
                'street_prefixes': ['utca', 'út', 'tér', 'körút'],
                'states': ['Budapest', 'Pest', 'Baranya', 'Bács-Kiskun', 'Békés', 'Borsod-Abaúj-Zemplén',
                        'Csongrád', 'Fejér', 'Győr-Moson-Sopron', 'Hajdú-Bihar'],
                'locale_base': 'hu_HU'
            },
            'Tailandia': {
                'phone_format': '+66-{}-{}{}{}{}-{}{}{}{}',
                'postal_code_format': '#####',
                'id_format': '{}-{}{}{}{}-{}{}{}{}{}-{}{}-{}',  # Formato de ID tailandés
                'city_list': ['Bangkok', 'Nonthaburi', 'Nakhon Ratchasima', 'Chiang Mai',
                            'Hat Yai', 'Udon Thani', 'Pak Kret', 'Surat Thani'],
                'street_prefixes': ['Thanon', 'Soi', 'Trok'],
                'states': ['Bangkok', 'Chiang Mai', 'Phuket', 'Ayutthaya', 'Chonburi',
                        'Nonthaburi', 'Songkhla', 'Surat Thani', 'Udon Thani'],
                'locale_base': 'th_TH'
            },
            'Ucrania': {
                'phone_format': '+380-{}{}-{}{}{}-{}{}{}{}',
                'postal_code_format': '#####',
                'id_format': '{}{}{}{}{}{}{}{}{}',  # Formato de pasaporte ucraniano
                'city_list': ['Kiev', 'Járkov', 'Odesa', 'Dnipró', 'Donetsk', 'Zaporiyia',
                            'Leópolis', 'Krivói Rog', 'Mykolaiv', 'Mariúpol'],
                'street_prefixes': ['вулиця', 'проспект', 'площа', 'бульвар'],
                'states': ['Kiev', 'Járkov', 'Odesa', 'Dnipró', 'Donetsk', 'Zaporiyia',
                        'Leópolis', 'Crimea', 'Mykolaiv', 'Luhansk'],
                'locale_base': 'uk_UA'
            },
            'Singapur': {
                'phone_format': '+65-{}{}{}{}-{}{}{}{}',
                'postal_code_format': '######',
                'id_format': 'S{}{}{}{}{}{}{}'.format,  # Formato NRIC de Singapur
                'city_list': ['Bedok', 'Jurong West', 'Woodlands', 'Tampines', 'Pasir Ris',
                            'Hougang', 'Sengkang', 'Yishun', 'Ang Mo Kio', 'Clementi'],
                'street_prefixes': ['Street', 'Avenue', 'Road', 'Boulevard'],
                'states': ['Central Region', 'East Region', 'North Region', 'North-East Region', 'West Region'],
                'locale_base': 'zh_SG'
            }
        }

        

        # Combinar locales directos y datos personalizados
        self.countries = {**self.direct_locales}

        # Otros datos estáticos
        self.genders = ['Masculino', 'Femenino', 'Otro']
        self.age_ranges = ['18-25', '26-35', '36-45', '46-55', '56-65', '66+']
        
        self.zodiac_signs = [
            'Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo',
            'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis'
        ]
        
        self.blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        self.personality_types = [
            'INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP',
            'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP'
        ]
        
        self.favorite_colors = [
            'Rojo', 'Azul', 'Verde', 'Amarillo', 'Morado', 'Negro',
            'Blanco', 'Naranja', 'Rosa', 'Marrón', 'Gris', 'Turquesa'
        ]

    def __init__(self):
        # Usar ThemedTk en lugar de Tk para mejor soporte de temas
        self.root = ThemedTk(theme="arc")
        self.root.title("Generador de Identidades")
        
        # Configurar icono (si está disponible)
        try:
            self.root.iconbitmap('identity_icon.ico')
        except:
            pass
        
        # Inicializar datos estáticos
        self.initialize_static_data()
        
        # Configuración de la ventana con mejor escalado
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(1300, screen_width * 0.8)
        window_height = min(900, screen_height * 0.8)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{int(window_width)}x{int(window_height)}+{int(x)}+{int(y)}")
        self.root.minsize(1000, 700)
        
        # Permitir redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Variables para almacenar datos
        self.current_identity = None
        self.photo = None
        self.saved_identities = []
        self.fakers = {}
        
        # Crear directorio para guardar identidades
        self.save_dir = Path.home() / "IdentityGenerator"
        self.save_dir.mkdir(exist_ok=True)
        
        # Configurar la GUI
        self.setup_gui()
        
        # Configurar estilo
        self.setup_styles()

    def setup_gui(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Panel izquierdo para controles
        left_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="5")
        left_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # Panel derecho para resultados con notebook
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        self.setup_controls(left_frame)
        self.setup_result_area(right_frame)

    def setup_styles(self):
        """Configurar estilos personalizados para la interfaz"""
        style = ttk.Style()
        
        # Estilo para botones principales con texto negro
        style.configure(
            'Action.TButton',
            padding=10,
            font=('Helvetica', 10, 'bold'),
            foreground='black'  # Color del texto
        )
        
        # También puedes definir colores para diferentes estados del botón
        style.map('Action.TButton',
            foreground=[
                ('pressed', 'black'),
                ('active', 'black'),
                ('disabled', 'gray')
            ],
            background=[
                ('pressed', '#d9d9d9'),
                ('active', '#ececec')
            ]
        )
        
        # Resto de los estilos...
        style.configure(
            'Header.TLabel',
            font=('Helvetica', 11, 'bold')
        )
        
        style.configure(
            'Card.TFrame',
            padding=10,
            relief='raised'
        )

        # Estilo para LabelFrames
        style.configure(
            'TLabelframe',
            padding=5,
            relief='solid'
        )

        # Estilo para el Notebook (pestañas)
        style.configure(
            'TNotebook',
            tabposition='n',
            padding=2
        )
        
        style.configure(
            'TNotebook.Tab',
            padding=[10, 5],
            font=('Helvetica', 9)
        )

    def setup_result_area(self, parent):
        """Configurar área de resultados con mejor aprovechamiento del espacio"""
        # Panel superior para foto e información básica
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Crear notebook para diferentes vistas
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Vista básica
        basic_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(basic_frame, text="Vista Básica")
        basic_frame.grid_columnconfigure(0, weight=1)
        basic_frame.grid_rowconfigure(1, weight=1)
        
        # Área de foto e info básica
        top_frame = ttk.Frame(basic_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure(1, weight=1)
        
        # Foto
        photo_frame = ttk.LabelFrame(top_frame, text="Foto")
        photo_frame.grid(row=0, column=0, padx=(0, 10), sticky="nw")
        self.photo_label = ttk.Label(photo_frame)
        self.photo_label.pack(padx=10, pady=10)
        
        # Info básica
        info_frame = ttk.LabelFrame(top_frame, text="Información Básica")
        info_frame.grid(row=0, column=1, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)
        
        self.basic_info_text = scrolledtext.ScrolledText(
            info_frame, 
            height=8,
            font=('Consolas', 10)
        )
        self.basic_info_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Vista JSON
        json_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(json_frame, text="JSON Completo")
        json_frame.grid_columnconfigure(0, weight=1)
        json_frame.grid_rowconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(
            json_frame,
            wrap=tk.WORD,
            font=('Consolas', 10)
        )
        self.result_text.grid(row=0, column=0, sticky="nsew")
        
        # Vista amigable
        friendly_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(friendly_frame, text="Vista completa")
        friendly_frame.grid_columnconfigure(0, weight=1)
        friendly_frame.grid_rowconfigure(0, weight=1)
        
        # Crear Treeview con scrollbar
        tree_frame = ttk.Frame(friendly_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(tree_frame, show='tree')
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars para el Treeview
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    def get_faker(self, locale):
        """
        Obtener instancia de Faker para el locale especificado.
        
        Args:
            locale (str): Código de locale (ej: 'en_US', 'es_ES')
            
        Returns:
            Faker: Instancia de Faker configurada para el locale especificado
        """
        try:
            if locale not in self.fakers:
                # Crear nueva instancia de Faker para este locale
                faker_instance = Faker(locale)
                self.fakers[locale] = faker_instance
            return self.fakers[locale]
        except Exception as e:
            logging.error(f"Error al crear Faker para locale {locale}: {str(e)}")
            # Usar el locale en_US como fallback
            if locale != 'en_US':
                logging.info("Intentando usar locale en_US como fallback")
                return self.get_faker('en_US')
            else:
                messagebox.showerror(
                    "Error de Configuración",
                    f"Error al configurar el generador de datos.\n{str(e)}"
                )
                return None

    def update_display(self):
        """Actualizar la GUI con los detalles de la identidad generada."""
        if not self.current_identity:
            return
            
        # Actualizar información básica
        self.basic_info_text.delete(1.0, tk.END)
        personal_data = self.current_identity.get("datos_personales", {})
        
        basic_info = [
            ("Nombre Completo", personal_data.get('nombre_completo', 'N/A')),
            ("Género", personal_data.get('género', 'N/A')),
            ("Fecha de Nacimiento", personal_data.get('fecha_nacimiento', 'N/A')),
            ("Edad", f"{personal_data.get('edad', 'N/A')} años"),
            ("Nacionalidad", personal_data.get('nacionalidad', 'N/A')),
            ("Estado Civil", personal_data.get('estado_civil', 'N/A'))
        ]
        
        for label, value in basic_info:
            self.basic_info_text.insert(tk.END, f"{label}: {value}\n")
        
        # Actualizar vista JSON
        self.result_text.delete(1.0, tk.END)
        formatted_json = json.dumps(self.current_identity, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
        self.result_text.insert(tk.END, formatted_json)
        
        # Colorear el JSON
        self.colorize_json()
        
        # Actualizar vista amigable
        self.tree.delete(*self.tree.get_children())
        self.populate_treeview("", self.current_identity)

    def colorize_json(self):
        """Colorear el JSON para mejor legibilidad"""
        content = self.result_text.get(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        
        # Configurar tags para colores
        self.result_text.tag_configure("key", foreground="#0033CC")
        self.result_text.tag_configure("string", foreground="#CC0000")
        self.result_text.tag_configure("number", foreground="#009900")
        self.result_text.tag_configure("boolean", foreground="#FF6600")
        
        lines = content.split('\n')
        for line in lines:
            # Detectar y colorear diferentes partes del JSON
            if ':' in line:
                key, value = line.split(':', 1)
                self.result_text.insert(tk.END, key + ':', "key")
                
                # Colorear valores según su tipo
                if value.strip().startswith('"'):
                    self.result_text.insert(tk.END, value + '\n', "string")
                elif value.strip() in ['true', 'false', 'null']:
                    self.result_text.insert(tk.END, value + '\n', "boolean")
                elif any(c.isdigit() for c in value.strip()):
                    self.result_text.insert(tk.END, value + '\n', "number")
                else:
                    self.result_text.insert(tk.END, value + '\n')
            else:
                self.result_text.insert(tk.END, line + '\n')

    def populate_treeview(self, parent, dictionary):
        """Poblar el Treeview con los datos de forma jerárquica"""
        for key, value in dictionary.items():
            if isinstance(value, dict):
                node = self.tree.insert(parent, 'end', text=key, open=True)
                self.populate_treeview(node, value)
            elif isinstance(value, list):
                node = self.tree.insert(parent, 'end', text=key, open=True)
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        subnode = self.tree.insert(node, 'end', text=f"Item {i+1}", open=True)
                        self.populate_treeview(subnode, item)
                    else:
                        self.tree.insert(node, 'end', text=str(item))
            else:
                self.tree.insert(parent, 'end', text=f"{key}: {value}")

    def generate_birth_date(self, age_range):
        """
        Genera una fecha de nacimiento basada en el rango de edad seleccionado.
        
        Args:
            age_range (str): Rango de edad en formato '18-25', '26-35', etc.
            
        Returns:
            date: Fecha de nacimiento generada aleatoriamente dentro del rango especificado
        """
        # Convertir rango de edad en fechas
        ranges = {
            '18-25': (18, 25),
            '26-35': (26, 35),
            '36-45': (36, 45),
            '46-55': (46, 55),
            '56-65': (56, 65),
            '66+': (66, 90)
        }
        
        min_age, max_age = ranges[age_range]
        
        today = date.today()
        start_date = today - timedelta(days=max_age*365)
        end_date = today - timedelta(days=min_age*365)
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        
        return start_date + timedelta(days=random_number_of_days)

    def generate_identity(self):
        """Generar identidad con manejo de errores mejorado"""

        def generation_task():
            try:
                country = self.country_combobox.get()
                locale = self.direct_locales.get(country)

                if not locale:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error de País",
                        f"El país {country} no está soportado actualmente."
                    ))
                    return

                fake = self.get_faker(locale)
                if not fake:
                    return

                gender = self.gender_combobox.get()
                age_range = self.age_combobox.get()
                birth_date = self.generate_birth_date(age_range)

                self.current_identity = {
                    "meta": {
                        "generado_el": datetime.now().isoformat(),
                        "version": "2.0",
                        "pais": country,
                        "locale": locale
                    }
                }

                # Generar datos según opciones seleccionadas
                if self.include_options['datos_personales'].get():
                    self.current_identity["datos_personales"] = self.generate_personal_data(fake, gender, birth_date)

                if self.include_options['datos_fisicos'].get():
                    self.current_identity["datos_fisicos"] = self.generate_physical_traits(fake)

                if self.include_options['datos_contacto'].get():
                    self.current_identity["datos_contacto"] = self.generate_contact_info(fake)

                if self.include_options['datos_empleo'].get():
                    self.current_identity["datos_empleo"] = self.generate_employment_info(fake)

                if self.include_options['datos_financieros'].get():
                    self.current_identity["datos_financieros"] = self.generate_financial_info(fake)

                if self.include_options['datos_internet'].get():
                    self.current_identity["datos_internet"] = self.generate_online_presence(fake)

                if self.include_options['datos_vehiculo'].get():
                    self.current_identity["datos_vehiculo"] = self.generate_vehicle_info(fake)

                if self.include_options['datos_rasgos'].get():
                    self.current_identity["datos_rasgos"] = self.generate_personality_traits()

                if self.include_options['datos_tracking'].get():
                    self.current_identity["datos_tracking"] = self.generate_tracking_info(fake)

                # Actualizar la interfaz
                self.root.after(0, self.update_display)

                # Generar foto si está seleccionada
                if self.include_options['foto'].get():
                    self.root.after(0, lambda: self.fetch_and_display_photo(gender))

                self.root.after(0, lambda: messagebox.showinfo("Éxito", "Identidad generada correctamente"))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Error al generar identidad: {str(e)}"
                ))
                logging.error(f"Error generando identidad: {str(e)}", exc_info=True)
            finally:
                self.root.after(0, self.enable_buttons)

        try:
            # Deshabilitar botones durante la generación
            self.disable_buttons()

            # Ejecutar la generación en un hilo separado
            thread = threading.Thread(target=generation_task)
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.enable_buttons()
            messagebox.showerror(
                "Error",
                f"Error al iniciar la generación: {str(e)}"
            )
            logging.error(f"Error al iniciar la generación: {str(e)}", exc_info=True)

            # Ejecutar generación en un hilo separado
            def generation_task():
                try:
                    self._generate_identity_data()
                    self.root.after(0, self._finish_generation, progress_window)
                except Exception as e:
                    self.root.after(0, self._handle_generation_error, str(e), progress_window)
            
            thread = threading.Thread(target=generation_task)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self._handle_generation_error(str(e))
            self.enable_buttons()

    def _generate_identity_data(self):
        """Generar los datos de la identidad"""
        country_locale = self.countries[self.country_combobox.get()]
        fake = self.get_faker(country_locale)
        
        gender = self.gender_combobox.get()
        age_range = self.age_combobox.get()
        
        birth_date = self.generate_birth_date(age_range)
        
        self.current_identity = {
            "meta": {
                "generado_el": datetime.now().isoformat(),
                "version": "2.0",
                "pais": self.country_combobox.get(),
                "locale": country_locale
            }
        }
        
        generation_methods = {
            'datos_personales': lambda: self.generate_personal_data(fake, gender, birth_date),
            'datos_fisicos': lambda: self.generate_physical_traits(fake),
            'datos_contacto': lambda: self.generate_contact_info(fake),
            'datos_empleo': lambda: self.generate_employment_info(fake),
            'datos_financieros': lambda: self.generate_financial_info(fake),
            'datos_internet': lambda: self.generate_online_presence(fake),
            'datos_vehiculo': lambda: self.generate_vehicle_info(fake),
            'datos_rasgos': lambda: self.generate_personality_traits(),
            'datos_tracking': lambda: self.generate_tracking_info(fake)
        }
        
        for key, method in generation_methods.items():
            if self.include_options[key].get():
                self.current_identity[key] = method()

    def _finish_generation(self, progress_window):
        """Finalizar la generación de identidad"""
        self.update_display()
        
        if self.include_options['foto'].get():
            self.fetch_and_display_photo(self.gender_combobox.get())
        
        progress_window.destroy()
        self.enable_buttons()
        messagebox.showinfo("Éxito", "Identidad generada correctamente")

    def _handle_generation_error(self, error_message, progress_window=None):
        """Manejar errores durante la generación"""
        if progress_window:
            progress_window.destroy()
        self.enable_buttons()
        messagebox.showerror("Error", f"Error al generar identidad: {error_message}")
        logging.error(f"Error generando identidad: {error_message}")

    def enable_buttons(self):
        """Habilitar todos los botones"""
        try:
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button):
                            child.configure(state='normal')
                elif isinstance(widget, ttk.Button):
                    widget.configure(state='normal')
        except Exception as e:
            print(f"Error al habilitar botones: {str(e)}")

    def disable_buttons(self):
        """Deshabilitar todos los botones"""
        try:
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button):
                            child.configure(state='disabled')
                elif isinstance(widget, ttk.Button):
                    widget.configure(state='disabled')
        except Exception as e:
            print(f"Error al deshabilitar botones: {str(e)}")

    def _handle_generation_error(self, error_message, progress_window=None):
        """Manejar errores durante la generación"""
        if progress_window:
            progress_window.destroy()
        self.enable_buttons()
        messagebox.showerror("Error", f"Error al generar identidad: {error_message}")
        logging.error(f"Error generando identidad: {error_message}")

    def setup_controls(self, parent):
        """Configurar controles con mejor diseño"""
        # Frame para controles básicos
        basic_frame = ttk.LabelFrame(parent, text="Configuración Básica", padding="5")
        basic_frame.pack(fill=tk.X, padx=5, pady=5)

        # Mejorar el diseño de los controles
        controls = [
            ("País:", self.countries.keys(), "country_combobox"),
            ("Género:", self.genders, "gender_combobox"),
            ("Rango de Edad:", self.age_ranges, "age_combobox")
        ]
        
        for label, values, attr_name in controls:
            frame = ttk.Frame(basic_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(
                frame, 
                text=label, 
                style='Header.TLabel'
            ).pack(side=tk.LEFT)
            
            combo = ttk.Combobox(
                frame,
                values=list(values),
                state='readonly',
                width=25
            )
            combo.pack(side=tk.RIGHT, padx=5)
            combo.current(0)
            setattr(self, attr_name, combo)

        # Opciones de generación mejoradas
        self.setup_generation_options(parent)
        
        # Botones de acción mejorados
        self.setup_action_buttons(parent)

    def setup_generation_options(self, parent):
        """Configurar opciones de generación con diseño mejorado"""
        options_frame = ttk.LabelFrame(parent, text="Opciones de Generación", padding="5")
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        # Crear un frame para contener los checkbuttons
        checks_frame = ttk.Frame(options_frame)
        checks_frame.pack(fill=tk.X, padx=5, pady=5)

        # Variables para checkbuttons con nombres más amigables
        option_names = {
            'foto': 'Foto de Perfil',
            'datos_personales': 'Datos Personales',
            'datos_fisicos': 'Características Físicas',
            'datos_contacto': 'Información de Contacto',
            'datos_empleo': 'Datos Laborales',
            'datos_financieros': 'Información Financiera',
            'datos_internet': 'Presencia en Internet',
            'datos_vehiculo': 'Información de Vehículo',
            'datos_rasgos': 'Rasgos de Personalidad',
            'datos_tracking': 'Datos de Seguimiento'
        }

        self.include_options = {key: tk.BooleanVar(value=True) for key in option_names}

        # Organizar checkbuttons en dos columnas
        for i, (key, name) in enumerate(option_names.items()):
            row = i % 5
            col = i // 5
            
            ttk.Checkbutton(
                checks_frame,
                text=name,
                variable=self.include_options[key],
                padding=(5, 2)
            ).grid(row=row, column=col, sticky='w', padx=5, pady=2)

        checks_frame.columnconfigure(1, weight=1)

    def setup_action_buttons(self, parent):
        """Configurar botones de acción con mejor diseño"""
        buttons_frame = ttk.LabelFrame(parent, text="Acciones", padding="5")
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        # Lista de botones con sus comandos
        buttons = [
            ("Generar Nueva Identidad", self.generate_identity, "generate"),
            ("Guardar Identidad", self.save_identity, "save"),
            ("Copiar al Portapapeles", self.copy_to_clipboard, "copy"),
            ("Abrir Email Temporal", self.open_temp_mail, "email")
        ]

        # Crear cada botón con el estilo mejorado
        for text, command, name in buttons:
            frame = ttk.Frame(buttons_frame)
            frame.pack(fill=tk.X, pady=2)
            
            btn = ttk.Button(
                frame,
                text=text,
                command=command,
                style='Action.TButton',
                width=30  # Ancho fijo para los botones
            )
            btn.pack(expand=True, padx=5, pady=2)
            setattr(self, f"{name}_button", btn)

    def save_identity(self):
        """Guardar identidad con diálogo mejorado"""
        if not self.current_identity:
            messagebox.showwarning(
                "Advertencia",
                "No hay identidad para guardar.\nPor favor, genera una identidad primero."
            )
            return

        try:
            # Crear directorio si no existe
            self.save_dir.mkdir(parents=True, exist_ok=True)

            # Generar nombre de archivo con marca de tiempo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.save_dir / f"identity_{timestamp}.json"

            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(
                    self.current_identity,
                    file,
                    cls=CustomJSONEncoder,
                    indent=4,
                    ensure_ascii=False
                )

            # Mostrar mensaje de éxito con opción para abrir carpeta
            if messagebox.askyesno(
                "Guardado Exitoso",
                f"Identidad guardada en:\n{file_path}\n\n¿Deseas abrir la carpeta?"
            ):
                webbrowser.open(str(self.save_dir))

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al guardar la identidad:\n{str(e)}"
            )
            logging.error(f"Error guardando identidad: {str(e)}")

    def copy_to_clipboard(self):
        """Copiar al portapapeles con feedback mejorado"""
        if not self.current_identity:
            messagebox.showwarning(
                "Advertencia",
                "No hay identidad para copiar.\nPor favor, genera una identidad primero."
            )
            return

        try:
            # Copiar al portapapeles
            formatted_json = json.dumps(
                self.current_identity,
                cls=CustomJSONEncoder,
                indent=4,
                ensure_ascii=False
            )
            pyperclip.copy(formatted_json)

            # Mostrar mensaje temporal
            self.show_temporary_message("Copiado al portapapeles")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al copiar al portapapeles:\n{str(e)}"
            )
            logging.error(f"Error copiando al portapapeles: {str(e)}")

    def show_temporary_message(self, message, duration=2000):
        """Mostrar mensaje temporal en la interfaz"""
        msg_window = tk.Toplevel(self.root)
        msg_window.overrideredirect(True)
        msg_window.attributes('-alpha', 0.9)
        
        # Estilo del mensaje
        label = ttk.Label(
            msg_window,
            text=message,
            padding=10,
            background='#333333',
            foreground='white'
        )
        label.pack()

        # Centrar el mensaje
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        msg_width = label.winfo_reqwidth()
        msg_height = label.winfo_reqheight()
        
        x = root_x + (root_width - msg_width) // 2
        y = root_y + 50
        
        msg_window.geometry(f"+{x}+{y}")
        
        # Cerrar después de duration ms
        self.root.after(duration, msg_window.destroy)

    def open_temp_mail(self):
        """Abrir servicio de email temporal"""
        try:
            webbrowser.open("https://temp-mail.org/")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al abrir el servicio de email temporal:\n{str(e)}"
            )
            logging.error(f"Error abriendo email temporal: {str(e)}")

    def generate_personal_data(self, fake, gender, birth_date):
        """
        Generar datos personales
        """
        try:
            gender_map = {'Masculino': 'male', 'Femenino': 'female'}
            gender_type = gender_map.get(gender, None)

            if gender_type:
                first_name = fake.first_name_male() if gender_type == 'male' else fake.first_name_female()
                last_name = fake.last_name()
            else:
                first_name = fake.first_name()
                last_name = fake.last_name()

            return {
                "nombre": first_name,
                "apellidos": last_name,
                "nombre_completo": f"{first_name} {last_name}",
                "género": gender,
                "fecha_nacimiento": birth_date.isoformat(),
                "edad": (date.today() - birth_date).days // 365,
                "estado_civil": random.choice(['Soltero/a', 'Casado/a', 'Divorciado/a', 'Viudo/a']),
                "lugar_nacimiento": fake.city(),
                "nacionalidad": self.country_combobox.get(),
                "identificación": self.generate_id_number(fake)
            }
        except Exception as e:
            logging.error(f"Error en generate_personal_data: {str(e)}", exc_info=True)
            raise

    def generate_physical_traits(self, fake):
        return {
            "altura": f"{random.randint(150, 190)} cm",
            "peso": f"{random.randint(50, 100)} kg",
            "grupo_sanguíneo": random.choice(self.blood_types),
            "color_ojos": random.choice(['Marrones', 'Azules', 'Verdes', 'Grises', 'Avellana']),
            "color_pelo": random.choice(['Negro', 'Castaño', 'Rubio', 'Pelirrojo', 'Gris']),
            "complexión": random.choice(['Delgada', 'Media', 'Atlética', 'Robusta']),
        }

    def generate_contact_info(self, fake):
        """Generar información de contacto con manejo de casos no soportados"""
        try:
            # Intentar dividir la dirección, con manejo de error
            try:
                address = fake.address().split('\n')
            except:
                address = [fake.street_address()]

            # Obtener el país actual
            current_country = self.country_combobox.get()

            # Verificar si es un país con datos personalizados
            if current_country in self.custom_country_data:
                country_data = self.custom_country_data[current_country]
                return {
                    "dirección": {
                        "calle": random.choice(country_data['street_prefixes']) + " " + fake.word().capitalize(),
                        "ciudad": random.choice(country_data['city_list']),
                        "estado": random.choice(country_data['states']),
                        "código_postal": ''.join(random.choice('0123456789') if c == '#' else c
                                                 for c in country_data['postal_code_format']),
                        "país": current_country
                    },
                    "teléfonos": {
                        "fijo": ''.join(random.choice('0123456789') if c == '{}' else c
                                        for c in country_data['phone_format']),
                        "móvil": ''.join(random.choice('0123456789') if c == '{}' else c
                                         for c in country_data['phone_format']),
                        "trabajo": ''.join(random.choice('0123456789') if c == '{}' else c
                                           for c in country_data['phone_format'])
                    },
                    "email": {
                        "personal": fake.email(),
                        "trabajo": f"{fake.user_name()}@{fake.domain_name()}",
                        "alternativo": f"{fake.user_name()}@{fake.free_email_domain()}"
                    }
                }
            else:
                # Para países con soporte directo de Faker
                try:
                    state = fake.state()
                except:
                    state = "N/A"

                try:
                    postal_code = fake.postcode()
                except:
                    postal_code = str(random.randint(10000, 99999))

                try:
                    phone = fake.phone_number()
                except:
                    phone = f"+{random.randint(1, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

                return {
                    "dirección": {
                        "calle": address[0],
                        "ciudad": fake.city(),
                        "estado": state,
                        "código_postal": postal_code,
                        "país": current_country
                    },
                    "teléfonos": {
                        "fijo": phone,
                        "móvil": phone,
                        "trabajo": phone
                    },
                    "email": {
                        "personal": fake.email(),
                        "trabajo": f"{fake.user_name()}@{fake.domain_name()}",
                        "alternativo": f"{fake.user_name()}@{fake.free_email_domain()}"
                    }
                }

        except Exception as e:
            logging.error(f"Error en generate_contact_info: {str(e)}", exc_info=True)
            # Retornar datos genéricos en caso de error
            return {
                "dirección": {
                    "calle": "Calle Example",
                    "ciudad": "Ciudad Example",
                    "estado": "Estado Example",
                    "código_postal": "12345",
                    "país": current_country
                },
                "teléfonos": {
                    "fijo": "+0-000-0000000",
                    "móvil": "+0-000-0000000",
                    "trabajo": "+0-000-0000000"
                },
                "email": {
                    "personal": "example@example.com",
                    "trabajo": "work@example.com",
                    "alternativo": "alt@example.com"
                }
            }

    def generate_employment_info(self, fake):
        company = fake.company()
        return {
            "empresa": {
                "nombre": company,
                "sector": fake.job(),
                "departamento": random.choice(['Ventas', 'Marketing', 'IT', 'RRHH', 'Finanzas', 'Operaciones', 'I+D']),
                "dirección": fake.address(),
                "teléfono": fake.phone_number(),
                "sitio_web": f"www.{company.lower().replace(' ', '')}.{fake.tld()}"
            },
            "puesto": {
                "título": fake.job(),
                "antigüedad": f"{random.randint(1, 15)} años",
                "tipo_contrato": random.choice(['Indefinido', 'Temporal', 'Freelance', 'Medio tiempo']),
                "salario_anual": f"{random.randint(25, 120)}k €"
            },
            "experiencia_previa": [
                {
                    "empresa": fake.company(),
                    "puesto": fake.job(),
                    "duración": f"{random.randint(1, 5)} años"
                } for _ in range(random.randint(1, 3))
            ]
        }

    def generate_financial_info(self, fake):
        return {
            "tarjetas_crédito": [
                {
                    "tipo": random.choice(['Visa', 'MasterCard', 'American Express']),
                    "número": fake.credit_card_number(),
                    "caducidad": fake.credit_card_expire(),
                    "cvv": fake.credit_card_security_code(),
                    "banco": fake.company()
                } for _ in range(random.randint(1, 3))
            ],
            "cuentas_bancarias": [
                {
                    "banco": fake.company(),
                    "tipo_cuenta": random.choice(['Corriente', 'Ahorro', 'Inversión']),
                    "iban": fake.iban(),
                    "swift": fake.swift(),
                    "saldo": f"{random.randint(1000, 50000)}€"
                } for _ in range(random.randint(1, 2))
            ],
            "inversiones": {
                "acciones": random.choice(['Sí', 'No']),
                "criptomonedas": random.choice(['Sí', 'No']),
                "inmuebles": random.choice(['Sí', 'No']),
                "fondos": random.choice(['Sí', 'No'])
            }
        }

    def generate_online_presence(self, fake):
        username = fake.user_name()
        return {
            "redes_sociales": {
                "facebook": f"facebook.com/{username}",
                "twitter": f"@{username}",
                "instagram": f"@{username}_{random.randint(100, 999)}",
                "linkedin": f"linkedin.com/in/{username}-{random.randint(100, 999)}"
            },
            "credenciales": {
                "usuario": username,
                "contraseña": fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
                "pregunta_seguridad": random.choice([
                    "¿Nombre de tu primera mascota?",
                    "¿Ciudad donde naciste?",
                    "¿Nombre de tu mejor amigo de la infancia?",
                    "¿Marca de tu primer coche?"
                ]),
                "respuesta_seguridad": fake.word()
            },
            "dominios": [
                f"{username}.{fake.tld()}",
                f"{fake.domain_name()}"
            ],
            "cryptocurrency": {
                "bitcoin_wallet": fake.sha256(),
                "ethereum_wallet": f"0x{fake.sha1()}"
            }
        }

    def generate_vehicle_info(self, fake):
        return {
            "actual": {
                "marca": random.choice(['Toyota', 'Volkswagen', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Honda']),
                "modelo": fake.word().capitalize(),
                "año": random.randint(2015, 2024),
                "color": random.choice(['Negro', 'Blanco', 'Gris', 'Azul', 'Rojo', 'Plata']),
                "matrícula": f"{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.randint(1000, 9999)}{random.choice(string.ascii_uppercase)}",
                "vin": fake.ean13(),
                "seguro": {
                    "compañía": fake.company(),
                    "número_póliza": fake.ean8(),
                    "tipo": random.choice(['Todo Riesgo', 'Terceros Ampliado', 'Terceros'])
                }
            },
            "histórico": [
                {
                    "marca": random.choice(['Toyota', 'Volkswagen', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Honda']),
                    "modelo": fake.word().capitalize(),
                    "año": random.randint(2010, 2015)
                } for _ in range(random.randint(0, 2))
            ]
        }

    def generate_personality_traits(self):
        return {
            "tipo_personalidad": random.choice(self.personality_types),
            "signo_zodiacal": random.choice(self.zodiac_signs),
            "color_favorito": random.choice(self.favorite_colors),
            "intereses": random.sample([
                "Lectura", "Viajes", "Deportes", "Música", "Arte", "Cine", "Fotografía",
                "Cocina", "Tecnología", "Naturaleza", "Gaming", "Fitness", "Yoga",
                "Jardinería", "Baile", "Escritura", "Meditación", "Voluntariado"
            ], k=random.randint(3, 6)),
            "habilidades": random.sample([
                "Comunicación", "Liderazgo", "Trabajo en equipo", "Resolución de problemas",
                "Creatividad", "Organización", "Adaptabilidad", "Empatía", "Negociación",
                "Análisis", "Innovación", "Gestión del tiempo"
            ], k=random.randint(3, 5))
        }

    def generate_tracking_info(self, fake):
        return {
            "ubicación": {
                "coordenadas": {
                    "latitud": float(fake.latitude()),
                    "longitud": float(fake.longitude())
                },
                "ip": fake.ipv4(),
                "mac_address": fake.mac_address(),
                "user_agent": fake.user_agent()
            },
            "actividad": {
                "última_conexión": fake.date_time_this_month().isoformat(),
                "dispositivos": random.sample([
                    "iPhone", "MacBook Pro", "iPad", "Samsung Galaxy",
                    "Windows PC", "Android Tablet", "Smart TV"
                ], k=random.randint(2, 4)),
                "navegadores": random.sample([
                    "Chrome", "Firefox", "Safari", "Edge"
                ], k=random.randint(1, 3))
            },
            "preferencias": {
                "idioma": random.choice(['es-ES', 'en-US', 'fr-FR', 'de-DE']),
                "zona_horaria": random.choice(['UTC+1', 'UTC+2', 'UTC-5', 'UTC-8']),
                "moneda": random.choice(['EUR', 'USD', 'GBP'])
            }
        }

    def generate_id_number(self, fake):
        """Genera números de identificación según el país"""
        country_locale = self.countries[self.country_combobox.get()]
        
        if country_locale == 'es_ES':
            # DNI español
            number = str(random.randint(10000000, 99999999))
            letters = "TRWAGMYFPDXBNJZSQVHLCKE"
            return f"{number}{letters[int(number) % 23]}"
        elif country_locale == 'en_US':
            # SSN estadounidense
            return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
        elif country_locale == 'fr_FR':
            # Número de seguridad social francés
            gender = '1' if self.gender_combobox.get() == 'Masculino' else '2'
            return f"{gender}{str(random.randint(0, 99)).zfill(2)}{str(random.randint(1, 12)).zfill(2)}{str(random.randint(1, 95)).zfill(2)}{''.join([str(random.randint(0, 9)) for _ in range(6)])}"
        elif country_locale == 'de_DE':
            # Personalausweis alemán
            return f"{''.join(random.choices(string.ascii_uppercase, k=1))}{''.join(random.choices(string.digits, k=8))}{''.join(random.choices(string.ascii_uppercase, k=1))}"
        else:
            # Formato genérico para otros países
            return f"ID-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"

    def fetch_and_display_photo(self, gender):
        """Fetch a random profile photo based on gender and display it in the GUI."""
        try:
            # Choose a photo category based on gender
            gender_keyword = "men" if gender == "Masculino" else "women"
            url = f"https://randomuser.me/api/portraits/{gender_keyword}/{random.randint(1, 99)}.jpg"
            
            response = requests.get(url, timeout=10)  # Añadir timeout
            response.raise_for_status()  # Verificar respuesta HTTP
            
            image = Image.open(BytesIO(response.content))
            # Usar LANCZOS en lugar de ANTIALIAS
            image = image.resize((120, 120), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            self.photo_label.config(image=self.photo)
            
        except requests.RequestException as e:
            messagebox.showerror("Error de Red", f"No se pudo descargar la imagen: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la imagen: {str(e)}")


# Start the application
if __name__ == "__main__":
    app = IdentityGenerator()
    app.root.mainloop()
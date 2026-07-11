import sys
import ctypes
import os
import configparser
import psycopg2
from datetime import date, datetime
from PyQt6.QtWidgets import (
    QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox, QMessageBox,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMenu, QFileDialog, QStatusBar,
    QFrame, QSplitter, QDateEdit, QTimeEdit
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QDate, QTime
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence, QShortcut, QColor, QBrush, QPainter, QPixmap
from app.turno_manager import (
    agregar_turno,
    obtener_turnos_del_dia,
    obtener_todos_los_turnos,
    buscar_turnos,
    eliminar_turno,
    editar_turno,
    reprogramar_turno,
    avanzar_turno,
    registrar_cambio,
    obtener_historial,
    crear_base_de_datos,
    crear_tablas
)

if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
    INTERNAL_PATH = os.path.join(BASE_PATH, '_internal')
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    INTERNAL_PATH = BASE_PATH

CONFIG_PATH = os.path.join(os.path.expandvars('%APPDATA%'), 'HardAgenda', 'config.ini')
os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

if sys.platform == 'win32':
    myappid = 'com.hardagenda.turnero.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setWindowTitle("Configuracion de la base de datos")
        self.setGeometry(100, 100, 400, 350)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.entry_db_name = self.create_input(layout, "Nombre de la base de datos:", "hardagenda_db")
        self.entry_db_host = self.create_input(layout, "Host de la base de datos:", "localhost")
        self.entry_db_port = self.create_input(layout, "Puerto de la base de datos:", "5432")
        self.entry_db_user = self.create_input(layout, "Usuario de la base de datos:")
        self.entry_db_password = self.create_input(
            layout, "Contrasena de la base de datos:", echo_mode=QLineEdit.EchoMode.Password
        )

        self.check_save_credentials = QCheckBox("Guardar datos de inicio de sesion")
        self.check_create_db = QCheckBox("Crear base de datos")
        self.check_create_tables = QCheckBox("Crear tabla")

        button_login = QPushButton("Iniciar")
        button_login.setFixedHeight(30)
        button_login.clicked.connect(self.login)

        layout.addWidget(self.check_save_credentials)
        layout.addWidget(self.check_create_db)
        layout.addWidget(self.check_create_tables)
        layout.addWidget(button_login)

        self.setLayout(layout)

    def create_input(self, layout, label_text, default_text="", echo_mode=None):
        label = QLabel(label_text)
        label.setFont(QFont("Open Sans", 12))
        entry = QLineEdit()
        entry.setFixedHeight(30)
        entry.setText(default_text)
        if echo_mode:
            entry.setEchoMode(echo_mode)
        layout.addWidget(label)
        layout.addWidget(entry)
        return entry

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            config = configparser.ConfigParser()
            config.read(CONFIG_PATH, encoding='utf-8')
            if config.has_section('database'):
                self.entry_db_name.setText(config.get('database', 'database', fallback='hardagenda_db'))
                self.entry_db_host.setText(config.get('database', 'host', fallback='localhost'))
                self.entry_db_port.setText(config.get('database', 'port', fallback='5432'))
                saved_user = config.get('database', 'user', fallback='')
                saved_pass = config.get('database', 'password', fallback='')
                if saved_user:
                    self.entry_db_user.setText(saved_user)
                    self.entry_db_password.setText(saved_pass)
                    self.check_save_credentials.setChecked(True)

    def verificar_conexion(self, db_host, db_port, db_user, db_password):
        try:
            conn = psycopg2.connect(
                host=db_host, port=db_port, user=db_user,
                password=db_password, dbname="postgres"
            )
            conn.close()
            return True
        except (psycopg2.OperationalError, UnicodeDecodeError, psycopg2.InterfaceError):
            QMessageBox.warning(self, "Error de conexion",
                                "Usuario o contrasena incorrectos o la base de datos no esta disponible.")
            return False

    def ejecutar_script(self, nombre_script):
        if nombre_script == 'create_database.py':
            crear_base_de_datos()
            return "Base de datos creada/verificada"
        elif nombre_script == 'create_tables.py':
            crear_tablas()
            return "Tablas creadas/verificadas"
        raise Exception(f"Script no soportado: {nombre_script}")

    def login(self):
        db_name = self.entry_db_name.text()
        db_user = self.entry_db_user.text()
        db_password = self.entry_db_password.text()
        db_host = self.entry_db_host.text()
        db_port = self.entry_db_port.text()

        if not self.verificar_conexion(db_host, db_port, db_user, db_password):
            return

        if self.check_create_db.isChecked():
            try:
                resultado = self.ejecutar_script('create_database.py')
                QMessageBox.information(self, "Base de datos", resultado)
            except Exception as e:
                QMessageBox.warning(self, "Error al crear la base de datos", str(e))

        if self.check_create_tables.isChecked():
            try:
                resultado = self.ejecutar_script('create_tables.py')
                QMessageBox.information(self, "Tabla", resultado)
            except Exception as e:
                QMessageBox.warning(self, "Error al crear la tabla", str(e))

        config = configparser.ConfigParser()
        config['database'] = {
            'database': db_name,
            'user': db_user,
            'password': db_password,
            'host': db_host,
            'port': db_port
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            config.write(f)

        self.close()
        self.main_window = TurneroApp()
        self.main_window.container.show()


HIGHLIGHT_STYLE = "background-color: #d4edda; font-weight: bold; border-left: 4px solid #28a745;"
NORMAL_STYLE = ""


class TurneroApp(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QTabWidget { border: none; }
            QTabWidget::pane { border-top: none; }
        """)

        self.tab_hoy = QWidget()
        self.tab_nuevo = QWidget()
        self.tab_todos = QWidget()
        self.tab_historial = QWidget()
        self.tab_acerca = QWidget()

        self.addTab(self.tab_hoy, "Hoy")
        self.addTab(self.tab_nuevo, "Nuevo turno")
        self.addTab(self.tab_todos, "Todos los turnos")
        self.addTab(self.tab_historial, "Historial")
        self.addTab(self.tab_acerca, "Acerca de")

        self._turnos_hoy = []

        self.init_tab_hoy()
        self.init_tab_nuevo()
        self.init_tab_todos()
        self.init_tab_historial()
        self.init_tab_acerca()

        self.currentChanged.connect(self._on_tab_changed)

        self.link_cerrar_sesion = QLabel(
            "<a href='#' style='color: grey; text-decoration: underline;'>Cerrar sesion</a>"
        )
        self.link_cerrar_sesion.linkActivated.connect(self.cerrar_sesion)

        self.lbl_stats = QLabel("")
        self.lbl_stats.setFont(QFont("Open Sans", 9))
        self.lbl_stats.setStyleSheet("color: #6b7280;")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self)
        row_bottom = QHBoxLayout()
        row_bottom.addWidget(self.lbl_stats)
        row_bottom.addStretch()
        row_bottom.addWidget(self.link_cerrar_sesion)
        main_layout.addLayout(row_bottom)

        self.container = QWidget()
        self.container.setWindowTitle("HardAgenda - Turnero")
        self.container.setGeometry(100, 100, 600, 650)
        self.container.setLayout(main_layout)

        QShortcut(QKeySequence("Return"), self.container, self._atajo_buscar)
        QShortcut(QKeySequence("Escape"), self.container, self._atajo_escape)
        QShortcut(QKeySequence("Ctrl+n"), self.container, lambda: self.setCurrentIndex(1))

        self._refrescar_hoy()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refrescar_hoy)
        self._timer.start(60000)

    def cerrar_sesion(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH, encoding='utf-8')
        if config.has_section('database'):
            config.set('database', 'user', '')
            config.set('database', 'password', '')
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                config.write(f)

        self.container.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    @staticmethod
    def _usuario_actual():
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH, encoding='utf-8')
        if config.has_section('database'):
            return config.get('database', 'user', fallback='desconocido')
        return 'desconocido'

    def _manejar_error_db(self, error):
        if "no se pudo conectar" in error.lower() or "no existe la tabla" in error.lower() or "does not exist" in error.lower():
            resp = QMessageBox.question(self, "Base de datos o tabla no encontrada",
                "La base de datos o la tabla de turnos no existe.\nDesea crear la base de datos y las tablas?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if resp == QMessageBox.StandardButton.Yes:
                try:
                    crear_base_de_datos()
                except Exception:
                    pass
                try:
                    crear_tablas()
                except Exception:
                    pass
                QMessageBox.information(self, "Listo", "Base de datos y tablas creadas. Intente de nuevo.")
                return True
        QMessageBox.critical(self, "Error", error)
        return False

    def _on_tab_changed(self, index):
        if self.widget(index) == self.tab_hoy:
            self._refrescar_hoy()
        elif self.widget(index) == self.tab_historial:
            self._cargar_historial()
        elif self.widget(index) == self.tab_todos:
            self._refrescar_todos()

    def _atajo_buscar(self):
        if self.currentWidget() == self.tab_todos:
            self.buscar_turnos_tab()
        elif self.currentWidget() == self.tab_hoy:
            self._refrescar_hoy()

    def _atajo_escape(self):
        for w in QApplication.topLevelWidgets():
            if isinstance(w, QWidget) and w.windowFlags() & Qt.WindowType.Dialog:
                w.close()
                return

    def _fmt_hora(self, ts):
        if ts is None:
            return ""
        if isinstance(ts, datetime):
            return ts.strftime("%H:%M")
        return str(ts)

    def _fmt_fecha(self, d):
        if d is None:
            return ""
        if isinstance(d, date):
            return d.strftime("%d/%m/%Y")
        return str(d)

    # ─── TAB HOY ───

    def init_tab_hoy(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_titulo_hoy = QLabel("Turnos del dia")
        self.lbl_titulo_hoy.setFont(QFont("Open Sans", 14, QFont.Weight.Bold))
        layout.addWidget(self.lbl_titulo_hoy)

        self.lista_hoy = QListWidget()
        self.lista_hoy.setFont(QFont("Open Sans", 11))
        self.lista_hoy.setMinimumHeight(300)
        self.lista_hoy.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lista_hoy.customContextMenuRequested.connect(self._menu_contextual_hoy)
        layout.addWidget(self.lista_hoy)

        row_botones = QHBoxLayout()

        btn_siguiente = QPushButton("Siguiente turno")
        btn_siguiente.setFixedHeight(35)
        btn_siguiente.clicked.connect(self._avanzar_turno_actual)

        btn_refrescar = QPushButton("Refrescar")
        btn_refrescar.setFixedHeight(35)
        btn_refrescar.clicked.connect(self._refrescar_hoy)

        row_botones.addWidget(btn_siguiente)
        row_botones.addWidget(btn_refrescar)
        layout.addLayout(row_botones)

        self.lbl_contador_hoy = QLabel("")
        self.lbl_contador_hoy.setFont(QFont("Open Sans", 10))
        self.lbl_contador_hoy.setStyleSheet("color: #6b7280;")
        layout.addWidget(self.lbl_contador_hoy)

        self.tab_hoy.setLayout(layout)

    def _refrescar_hoy(self):
        turnos, error = obtener_turnos_del_dia()
        if error:
            if self._manejar_error_db(error):
                turnos, error = obtener_turnos_del_dia()
            if error:
                return
        self._turnos_hoy = turnos or []
        self._mostrar_turnos_hoy()

    def _mostrar_turnos_hoy(self):
        self.lista_hoy.clear()
        hoy = self._turnos_hoy
        pendientes = [t for t in hoy if t['estado'] == 'pendiente']
        atendidos = [t for t in hoy if t['estado'] == 'atendido']

        if not hoy:
            self.lista_hoy.addItem("No hay turnos para el dia de hoy")
            self.lbl_contador_hoy.setText("Turnos: 0")
            self.lbl_titulo_hoy.setText("Turnos del dia")
            return

        self.lbl_titulo_hoy.setText(f"Turnos del dia - {self._fmt_fecha(date.today())}")

        idx = 0
        for t in pendientes:
            texto = f"{t['nombre']} {t['apellido']}  |  DNI: {t['dni']}  |  Obra Social: {t.get('obra_social') or 'N/A'}  |  {self._fmt_hora(t['hora'])}"
            item = QListWidgetItem(texto)
            item.setData(Qt.ItemDataRole.UserRole, t['id'])
            if idx == 0:
                item.setBackground(QBrush(QColor("#d4edda")))
                item.setForeground(QBrush(QColor("#155724")))
                item.setFont(QFont("Open Sans", 11, QFont.Weight.Bold))
                item.setToolTip("TURNO ACTUAL")
            self.lista_hoy.addItem(item)
            idx += 1

        if atendidos:
            separador = QListWidgetItem("─── Ya atendidos ───")
            separador.setFlags(Qt.ItemFlag.NoItemFlags)
            separador.setForeground(QBrush(QColor("#999999")))
            self.lista_hoy.addItem(separador)
            for t in atendidos:
                texto = f"  {t['nombre']} {t['apellido']}  |  DNI: {t['dni']}  |  {self._fmt_hora(t['hora'])}"
                item = QListWidgetItem(texto)
                item.setForeground(QBrush(QColor("#999999")))
                item.setData(Qt.ItemDataRole.UserRole, t['id'])
                self.lista_hoy.addItem(item)

        total = len(hoy)
        pend = len(pendientes)
        self.lbl_contador_hoy.setText(f"Turnos: {total} total  |  {pend} pendiente(s)")

    def _avanzar_turno_actual(self):
        pendientes = [t for t in self._turnos_hoy if t['estado'] == 'pendiente']
        if not pendientes:
            QMessageBox.information(self, "Sin turnos", "No hay turnos pendientes para hoy")
            return

        turno = pendientes[0]
        confirmacion = QMessageBox.question(
            self, "Avanzar turno",
            f"Marcar como atendido a {turno['nombre']} {turno['apellido']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmacion != QMessageBox.StandardButton.Yes:
            return

        exito, err = avanzar_turno(turno['id'])
        if exito:
            registrar_cambio("turnos", turno['id'], "Atendido",
                             f"{turno['nombre']} {turno['apellido']} (DNI: {turno['dni']})",
                             usuario=self._usuario_actual(),
                             dni=turno['dni'],
                             nombre=turno['nombre'],
                             apellido=turno['apellido'])
            self._refrescar_hoy()
        else:
            QMessageBox.critical(self, "Error", err)

    def _obtener_turno_hoy_de_item(self, item):
        if not item:
            return None
        turno_id = item.data(Qt.ItemDataRole.UserRole)
        if not turno_id:
            return None
        for t in self._turnos_hoy:
            if t['id'] == turno_id:
                return t
        return None

    def _menu_contextual_hoy(self, pos):
        item = self.lista_hoy.itemAt(pos)
        turno = self._obtener_turno_hoy_de_item(item)
        if not turno or turno['estado'] != 'pendiente':
            return

        menu = QMenu(self)

        action_avanzar = QAction("Atender turno", self)
        action_avanzar.triggered.connect(self._avanzar_turno_actual)

        action_reprogramar = QAction("Reprogramar a otro dia", self)
        action_reprogramar.triggered.connect(lambda: self._reprogramar_turno_hoy(turno))

        menu.addAction(action_avanzar)
        menu.addSeparator()
        menu.addAction(action_reprogramar)

        menu.exec(self.lista_hoy.viewport().mapToGlobal(pos))

    def _reprogramar_turno_hoy(self, turno):
        ventana = QWidget(self.container, Qt.WindowType.Dialog)
        ventana.setWindowTitle("Reprogramar turno")
        ventana.setFixedSize(320, 220)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(16, 16, 16, 16)

        v_layout.addWidget(QLabel(f"Turno de: {turno['nombre']} {turno['apellido']}"))

        label_fecha = QLabel("Nueva fecha:")
        label_fecha.setFont(QFont("Open Sans", 11))
        entry_fecha = QDateEdit()
        entry_fecha.setFixedHeight(30)
        entry_fecha.setCalendarPopup(True)
        entry_fecha.setDisplayFormat("dd/MM/yyyy")
        entry_fecha.setDate(QDate.currentDate().addDays(1))

        label_hora = QLabel("Nueva hora:")
        label_hora.setFont(QFont("Open Sans", 11))
        entry_hora = QTimeEdit()
        entry_hora.setFixedHeight(30)
        entry_hora.setDisplayFormat("HH:mm")
        entry_hora.setTime(QTime(9, 0))

        btn_reprogramar = QPushButton("Reprogramar")

        v_layout.addWidget(label_fecha)
        v_layout.addWidget(entry_fecha)
        v_layout.addWidget(label_hora)
        v_layout.addWidget(entry_hora)
        v_layout.addWidget(btn_reprogramar)

        ventana.setLayout(v_layout)

        def confirmar():
            nueva_fecha = entry_fecha.date().toPyDate()
            nueva_hora_dt = datetime.combine(nueva_fecha, entry_hora.time().toPyTime())
            exito, err = reprogramar_turno(turno['id'], nueva_fecha, nueva_hora_dt)
            if exito:
                registrar_cambio("turnos", turno['id'], "Reprogramado",
                                 f"{turno['nombre']} {turno['apellido']} (DNI: {turno['dni']}) -> {nueva_fecha.strftime('%d/%m/%Y')} {entry_hora.time().toString('HH:mm')}",
                                 usuario=self._usuario_actual(),
                                 dni=turno['dni'],
                                 nombre=turno['nombre'],
                                 apellido=turno['apellido'])
                QMessageBox.information(ventana, "Listo", f"Turno reprogramado para el {nueva_fecha.strftime('%d/%m/%Y')} a las {entry_hora.time().toString('HH:mm')}")
                ventana.close()
                self._refrescar_hoy()
            else:
                QMessageBox.critical(ventana, "Error", err)

        btn_reprogramar.clicked.connect(confirmar)
        ventana.show()

    # ─── TAB NUEVO TURNO ───

    def init_tab_nuevo(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        label_nombre = QLabel("Nombre:")
        label_nombre.setFont(QFont("Open Sans", 12))
        self.entry_nombre = QLineEdit()
        self.entry_nombre.setFixedHeight(30)
        self.entry_nombre.setPlaceholderText("Ingrese nombre")

        label_apellido = QLabel("Apellido:")
        label_apellido.setFont(QFont("Open Sans", 12))
        self.entry_apellido = QLineEdit()
        self.entry_apellido.setFixedHeight(30)
        self.entry_apellido.setPlaceholderText("Ingrese apellido")

        label_dni = QLabel("DNI:")
        label_dni.setFont(QFont("Open Sans", 12))
        self.entry_dni = QLineEdit()
        self.entry_dni.setFixedHeight(30)
        self.entry_dni.setPlaceholderText("Ingrese DNI")

        label_obra_social = QLabel("Obra Social:")
        label_obra_social.setFont(QFont("Open Sans", 12))
        self.entry_obra_social = QLineEdit()
        self.entry_obra_social.setFixedHeight(30)
        self.entry_obra_social.setPlaceholderText("Ingrese obra social")

        label_motivo = QLabel("Motivo de consulta:")
        label_motivo.setFont(QFont("Open Sans", 12))
        self.entry_motivo = QLineEdit()
        self.entry_motivo.setFixedHeight(30)
        self.entry_motivo.setPlaceholderText("Ingrese motivo de consulta")

        label_fecha = QLabel("Fecha del turno:")
        label_fecha.setFont(QFont("Open Sans", 12))
        self.entry_fecha = QDateEdit()
        self.entry_fecha.setFixedHeight(30)
        self.entry_fecha.setDate(QDate.currentDate())
        self.entry_fecha.setCalendarPopup(True)
        self.entry_fecha.setDisplayFormat("dd/MM/yyyy")

        label_hora = QLabel("Hora del turno:")
        label_hora.setFont(QFont("Open Sans", 12))
        self.entry_hora = QTimeEdit()
        self.entry_hora.setFixedHeight(30)
        self.entry_hora.setTime(QTime.currentTime())
        self.entry_hora.setDisplayFormat("HH:mm")

        button_registrar = QPushButton("Registrar turno")
        button_registrar.setFixedHeight(35)
        button_registrar.clicked.connect(self.registrar_turno)

        layout.addWidget(label_nombre)
        layout.addWidget(self.entry_nombre)
        layout.addWidget(label_apellido)
        layout.addWidget(self.entry_apellido)
        layout.addWidget(label_dni)
        layout.addWidget(self.entry_dni)
        layout.addWidget(label_obra_social)
        layout.addWidget(self.entry_obra_social)
        layout.addWidget(label_motivo)
        layout.addWidget(self.entry_motivo)
        layout.addWidget(label_fecha)
        layout.addWidget(self.entry_fecha)
        layout.addWidget(label_hora)
        layout.addWidget(self.entry_hora)
        layout.addSpacing(10)
        layout.addWidget(button_registrar)

        self.tab_nuevo.setLayout(layout)

    def registrar_turno(self):
        nombre = self.entry_nombre.text().strip()
        apellido = self.entry_apellido.text().strip()
        dni = self.entry_dni.text().strip()
        obra_social = self.entry_obra_social.text().strip()
        motivo = self.entry_motivo.text().strip()
        fecha = self.entry_fecha.date().toPyDate()
        hora = self.entry_hora.time().toPyTime()
        fecha_hora = datetime.combine(fecha, hora)

        if not (nombre and apellido and dni):
            QMessageBox.warning(self, "Error", "Nombre, apellido y DNI son obligatorios")
            return

        usuario = self._usuario_actual()
        exito, error = agregar_turno(nombre, apellido, dni, obra_social, motivo, usuario,
                                     fecha=fecha, hora=fecha_hora)
        if exito:
            registrar_cambio("turnos", None, "Alta",
                             f"{nombre} {apellido} (DNI: {dni}) - {fecha_hora.strftime('%d/%m/%Y %H:%M')}",
                             usuario=usuario,
                             dni=dni, nombre=nombre, apellido=apellido)
            QMessageBox.information(self, "Registrado", "Turno registrado con exito")
            self.entry_nombre.clear()
            self.entry_apellido.clear()
            self.entry_dni.clear()
            self.entry_obra_social.clear()
            self.entry_motivo.clear()
            self.entry_fecha.setDate(QDate.currentDate())
            self.entry_hora.setTime(QTime.currentTime())
            self._refrescar_hoy()
        else:
            if "no existe la tabla" in error.lower() or "does not exist" in error.lower():
                resp = QMessageBox.question(self, "Tabla no existe",
                    "La tabla de turnos no existe. Desea crearla?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if resp == QMessageBox.StandardButton.Yes:
                    try:
                        crear_tablas()
                        QMessageBox.information(self, "Listo", "Tablas creadas. Intente registrar de nuevo.")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"No se pudieron crear las tablas:\n{e}")
            else:
                QMessageBox.critical(self, "Error", error)

    # ─── TAB TODOS LOS TURNOS ───

    def init_tab_todos(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_buscar = QLabel("Buscar turnos:")
        lbl_buscar.setFont(QFont("Open Sans", 12))
        layout.addWidget(lbl_buscar)

        row_dni = QHBoxLayout()
        row_dni.addWidget(QLabel("DNI:"))
        self.entry_buscar_dni = QLineEdit()
        self.entry_buscar_dni.setFixedHeight(30)
        self.entry_buscar_dni.setPlaceholderText("DNI")
        row_dni.addWidget(self.entry_buscar_dni)
        layout.addLayout(row_dni)

        row_nombre = QHBoxLayout()
        row_nombre.addWidget(QLabel("Nombre:"))
        self.entry_buscar_nombre = QLineEdit()
        self.entry_buscar_nombre.setFixedHeight(30)
        self.entry_buscar_nombre.setPlaceholderText("Nombre")
        row_nombre.addWidget(self.entry_buscar_nombre)
        layout.addLayout(row_nombre)

        row_apellido = QHBoxLayout()
        row_apellido.addWidget(QLabel("Apellido:"))
        self.entry_buscar_apellido = QLineEdit()
        self.entry_buscar_apellido.setFixedHeight(30)
        self.entry_buscar_apellido.setPlaceholderText("Apellido")
        row_apellido.addWidget(self.entry_buscar_apellido)
        layout.addLayout(row_apellido)

        row_botones_buscar = QHBoxLayout()
        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedHeight(30)
        btn_buscar.clicked.connect(self.buscar_turnos_tab)

        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setFixedHeight(30)
        btn_limpiar.clicked.connect(self._limpiar_busqueda)

        row_botones_buscar.addWidget(btn_buscar)
        row_botones_buscar.addWidget(btn_limpiar)
        layout.addLayout(row_botones_buscar)

        self.tabla_todos = QTableWidget()
        self.tabla_todos.setColumnCount(7)
        self.tabla_todos.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Apellido", "DNI", "Obra Social", "Fecha", "Hora"]
        )
        self.tabla_todos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_todos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_todos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_todos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_todos.setSortingEnabled(True)
        self.tabla_todos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_todos.customContextMenuRequested.connect(self._menu_contextual_todos)
        self.tabla_todos.doubleClicked.connect(self._ver_detalle_turno)

        self.lbl_contador_todos = QLabel("Turnos: 0")
        self.lbl_contador_todos.setFont(QFont("Open Sans", 10))
        self.lbl_contador_todos.setStyleSheet("color: #6b7280;")

        btn_refrescar = QPushButton("Refrescar")
        btn_refrescar.setFixedHeight(30)
        btn_refrescar.clicked.connect(self._refrescar_todos)

        layout.addWidget(self.tabla_todos)
        row_bottom = QHBoxLayout()
        row_bottom.addWidget(self.lbl_contador_todos)
        row_bottom.addStretch()
        row_bottom.addWidget(btn_refrescar)
        layout.addLayout(row_bottom)

        self.tab_todos.setLayout(layout)
        self._todos_los_turnos = []

    def _refrescar_todos(self):
        turnos, error = obtener_todos_los_turnos()
        if error:
            if self._manejar_error_db(error):
                turnos, error = obtener_todos_los_turnos()
            if error:
                return
        self._todos_los_turnos = turnos or []
        self._mostrar_turnos_en_tabla(self._todos_los_turnos)

    def _mostrar_turnos_en_tabla(self, turnos):
        self.tabla_todos.setSortingEnabled(False)
        self.tabla_todos.setRowCount(len(turnos))
        for i, t in enumerate(turnos):
            self.tabla_todos.setItem(i, 0, QTableWidgetItem(str(t['id']).zfill(8)))
            self.tabla_todos.setItem(i, 1, QTableWidgetItem(t['nombre']))
            self.tabla_todos.setItem(i, 2, QTableWidgetItem(t['apellido']))
            self.tabla_todos.setItem(i, 3, QTableWidgetItem(t['dni']))
            self.tabla_todos.setItem(i, 4, QTableWidgetItem(t.get('obra_social') or ""))
            self.tabla_todos.setItem(i, 5, QTableWidgetItem(self._fmt_fecha(t.get('fecha'))))
            self.tabla_todos.setItem(i, 6, QTableWidgetItem(self._fmt_hora(t.get('hora'))))
        self.lbl_contador_todos.setText(f"Turnos: {len(turnos)}")
        self.tabla_todos.setSortingEnabled(True)

    def buscar_turnos_tab(self):
        dni = self.entry_buscar_dni.text().strip()
        nombre = self.entry_buscar_nombre.text().strip()
        apellido = self.entry_buscar_apellido.text().strip()

        if not (dni or nombre or apellido):
            QMessageBox.warning(self, "Error", "Ingrese al menos un criterio de busqueda")
            return

        turnos, error = buscar_turnos(dni=dni or None, nombre=nombre or None, apellido=apellido or None)
        if error:
            QMessageBox.warning(self, "Error", error)
            return
        self._todos_los_turnos = turnos
        self._mostrar_turnos_en_tabla(turnos)

    def _limpiar_busqueda(self):
        self.entry_buscar_dni.clear()
        self.entry_buscar_nombre.clear()
        self.entry_buscar_apellido.clear()
        self._refrescar_todos()

    def _obtener_turno_de_fila(self, row):
        if row < 0:
            return None
        id_item = self.tabla_todos.item(row, 0)
        if not id_item:
            return None
        turno_id = int(id_item.text())
        for t in self._todos_los_turnos:
            if t['id'] == turno_id:
                return t
        return None

    def _menu_contextual_todos(self, pos):
        row = self.tabla_todos.rowAt(pos.y())
        if row < 0:
            return

        turno = self._obtener_turno_de_fila(row)
        if not turno:
            return

        menu = QMenu(self)

        action_copiar_dni = QAction("Copiar DNI", self)
        action_copiar_dni.triggered.connect(
            lambda: QApplication.clipboard().setText(turno['dni'])
        )

        action_copiar_nombre = QAction("Copiar nombre completo", self)
        action_copiar_nombre.triggered.connect(
            lambda: QApplication.clipboard().setText(f"{turno['nombre']} {turno['apellido']}")
        )

        menu.addAction(action_copiar_dni)
        menu.addAction(action_copiar_nombre)
        menu.addSeparator()

        action_ver = QAction("Ver detalle", self)
        action_ver.triggered.connect(lambda: self._ver_detalle_turno_directo(turno))

        action_editar = QAction("Editar turno", self)
        action_editar.triggered.connect(lambda: self._editar_turno_directo(turno))

        action_eliminar = QAction("Eliminar turno", self)
        action_eliminar.triggered.connect(lambda: self._eliminar_turno_directo(turno))

        menu.addAction(action_ver)
        menu.addAction(action_editar)
        menu.addSeparator()
        menu.addAction(action_eliminar)

        menu.exec(self.tabla_todos.viewport().mapToGlobal(pos))

    def _ver_detalle_turno(self, index):
        row = index.row()
        turno = self._obtener_turno_de_fila(row)
        if turno:
            self._ver_detalle_turno_directo(turno)

    def _ver_detalle_turno_directo(self, turno):
        ventana = QWidget(self.container, Qt.WindowType.Dialog)
        ventana.setWindowTitle("Detalle del turno")
        ventana.setFixedSize(350, 320)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(16, 16, 16, 16)

        v_layout.addWidget(QLabel(f"Nombre: {turno['nombre']}"))
        v_layout.addWidget(QLabel(f"Apellido: {turno['apellido']}"))
        v_layout.addWidget(QLabel(f"DNI: {turno['dni']}"))
        v_layout.addWidget(QLabel(f"Obra Social: {turno.get('obra_social') or 'N/A'}"))
        v_layout.addWidget(QLabel(f"Fecha: {self._fmt_fecha(turno.get('fecha'))}"))
        v_layout.addWidget(QLabel(f"Hora: {self._fmt_hora(turno.get('hora'))}"))
        v_layout.addWidget(QLabel(f"Estado: {turno.get('estado', 'pendiente')}"))

        motivo_label = QLabel(f"Motivo: {turno.get('motivo_consulta') or 'N/A'}")
        motivo_label.setWordWrap(True)
        v_layout.addWidget(motivo_label)

        v_layout.addSpacing(10)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(ventana.close)
        v_layout.addWidget(btn_cerrar)

        ventana.setLayout(v_layout)
        ventana.show()

    def _editar_turno_directo(self, turno):
        ventana = QWidget(self.container, Qt.WindowType.Dialog)
        ventana.setWindowTitle("Editar turno")
        ventana.setFixedSize(380, 480)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(16, 16, 16, 16)

        entry_nombre = QLineEdit(turno['nombre'])
        entry_apellido = QLineEdit(turno['apellido'])
        entry_dni = QLineEdit(turno['dni'])
        entry_obra_social = QLineEdit(turno.get('obra_social') or "")
        entry_motivo = QLineEdit(turno.get('motivo_consulta') or "")

        entry_fecha = QDateEdit()
        entry_fecha.setFixedHeight(30)
        entry_fecha.setCalendarPopup(True)
        entry_fecha.setDisplayFormat("dd/MM/yyyy")
        if turno.get('hora') and isinstance(turno['hora'], datetime):
            entry_fecha.setDate(QDate(turno['hora'].year, turno['hora'].month, turno['hora'].day))
        elif turno.get('fecha'):
            d = turno['fecha']
            entry_fecha.setDate(QDate(d.year, d.month, d.day))

        entry_hora = QTimeEdit()
        entry_hora.setFixedHeight(30)
        entry_hora.setDisplayFormat("HH:mm")
        if turno.get('hora') and isinstance(turno['hora'], datetime):
            entry_hora.setTime(QTime(turno['hora'].hour, turno['hora'].minute))

        btn_guardar = QPushButton("Guardar cambios")

        v_layout.addWidget(QLabel("Nombre:"))
        v_layout.addWidget(entry_nombre)
        v_layout.addWidget(QLabel("Apellido:"))
        v_layout.addWidget(entry_apellido)
        v_layout.addWidget(QLabel("DNI:"))
        v_layout.addWidget(entry_dni)
        v_layout.addWidget(QLabel("Obra Social:"))
        v_layout.addWidget(entry_obra_social)
        v_layout.addWidget(QLabel("Motivo de consulta:"))
        v_layout.addWidget(entry_motivo)
        v_layout.addWidget(QLabel("Fecha:"))
        v_layout.addWidget(entry_fecha)
        v_layout.addWidget(QLabel("Hora:"))
        v_layout.addWidget(entry_hora)
        v_layout.addSpacing(10)
        v_layout.addWidget(btn_guardar)

        ventana.setLayout(v_layout)

        def guardar():
            nuevo_nombre = entry_nombre.text().strip()
            nuevo_apellido = entry_apellido.text().strip()
            nuevo_dni = entry_dni.text().strip()
            nueva_obra = entry_obra_social.text().strip()
            nuevo_motivo = entry_motivo.text().strip()
            nueva_fecha = entry_fecha.date().toPyDate()
            nueva_hora = entry_hora.time().toPyTime()
            nueva_fecha_hora = datetime.combine(nueva_fecha, nueva_hora)

            if not (nuevo_nombre and nuevo_apellido and nuevo_dni):
                QMessageBox.warning(ventana, "Error", "Nombre, apellido y DNI son obligatorios")
                return

            exito, err = editar_turno(
                turno['id'], nuevo_nombre, nuevo_apellido, nuevo_dni,
                nueva_obra, nuevo_motivo,
                nueva_fecha, nueva_fecha_hora
            )
            if exito:
                registrar_cambio("turnos", turno['id'], "Modificado",
                                 f"{nuevo_nombre} {nuevo_apellido} (DNI: {nuevo_dni}) - {nueva_fecha_hora.strftime('%d/%m/%Y %H:%M')}",
                                 usuario=self._usuario_actual(),
                                 dni=nuevo_dni, nombre=nuevo_nombre, apellido=nuevo_apellido)
                QMessageBox.information(ventana, "Listo", "Turno actualizado")
                ventana.close()
                self._refrescar_todos()
            else:
                QMessageBox.critical(ventana, "Error", err)

        btn_guardar.clicked.connect(guardar)
        ventana.show()

    def _eliminar_turno_directo(self, turno):
        confirmacion = QMessageBox.question(
            self, "Confirmar eliminacion",
            f"Eliminar el turno de {turno['nombre']} {turno['apellido']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmacion != QMessageBox.StandardButton.Yes:
            return

        exito, err = eliminar_turno(turno['id'])
        if exito:
            registrar_cambio("turnos", None, "Baja",
                             f"{turno['nombre']} {turno['apellido']} (DNI: {turno['dni']})",
                             usuario=self._usuario_actual(),
                             dni=turno['dni'],
                             nombre=turno['nombre'],
                             apellido=turno['apellido'])
            QMessageBox.information(self, "Eliminado", "Turno eliminado")
            self._refrescar_todos()
        else:
            QMessageBox.critical(self, "Error", err)

    # ─── TAB HISTORIAL ───

    def init_tab_historial(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(6)
        self.tabla_historial.setHorizontalHeaderLabels(
            ["Fecha", "Accion", "Detalle", "DNI", "Nombre", "Usuario"]
        )
        self.tabla_historial.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_historial.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_historial.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_historial.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        button_refrescar = QPushButton("Refrescar historial")
        button_refrescar.setFixedHeight(30)
        button_refrescar.clicked.connect(self._cargar_historial)

        layout.addWidget(self.tabla_historial)
        layout.addWidget(button_refrescar)

        self.tab_historial.setLayout(layout)
        self._cargar_historial()

    def _cargar_historial(self):
        registros, error = obtener_historial()
        if error:
            if self._manejar_error_db(error):
                registros, error = obtener_historial()
            if error:
                self.tabla_historial.setRowCount(1)
                for c in range(6):
                    self.tabla_historial.setItem(0, c, QTableWidgetItem(""))
                self.tabla_historial.setItem(0, 3, QTableWidgetItem(error))
                return
        if not registros:
            self.tabla_historial.setRowCount(1)
            for c in range(6):
                self.tabla_historial.setItem(0, c, QTableWidgetItem(""))
            self.tabla_historial.setItem(0, 3, QTableWidgetItem("No se registran cambios al dia de la fecha"))
            return
        self.tabla_historial.setRowCount(len(registros))
        for i, r in enumerate(registros):
            fecha_str = r['fecha'].strftime('%d/%m/%Y %H:%M') if r['fecha'] else ""
            nombre_completo = f"{r['nombre'] or ''} {r['apellido'] or ''}".strip()
            self.tabla_historial.setItem(i, 0, QTableWidgetItem(fecha_str))
            self.tabla_historial.setItem(i, 1, QTableWidgetItem(r['accion']))
            self.tabla_historial.setItem(i, 2, QTableWidgetItem(r.get('detalle') or ""))
            self.tabla_historial.setItem(i, 3, QTableWidgetItem(r['dni'] or ""))
            self.tabla_historial.setItem(i, 4, QTableWidgetItem(nombre_completo))
            self.tabla_historial.setItem(i, 5, QTableWidgetItem(r['usuario'] or ""))

    # ─── TAB ACERCA DE ───

    def init_tab_acerca(self):
        main_layout = QHBoxLayout(self.tab_acerca)
        main_layout.setContentsMargins(0, 0, 0, 0)

        text_widget = QWidget()
        layout = QVBoxLayout(text_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_titulo = QLabel("HardAgenda")
        lbl_titulo.setFont(QFont("Open Sans", 18, QFont.Weight.Bold))
        layout.addWidget(lbl_titulo)

        lbl_version = QLabel("Version 1.0.0")
        lbl_version.setFont(QFont("Open Sans", 11))
        lbl_version.setStyleSheet("color: #6b7280;")
        layout.addWidget(lbl_version)

        layout.addSpacing(15)

        lbl_desc = QLabel("Sistema de gestion de turnos basado en Python y PostgreSQL.")
        lbl_desc.setFont(QFont("Open Sans", 11))
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        layout.addSpacing(20)

        lbl_desarrollador = QLabel("Desarrollado por:")
        lbl_desarrollador.setFont(QFont("Open Sans", 11, QFont.Weight.Bold))
        layout.addWidget(lbl_desarrollador)

        lbl_nombre = QLabel("Abel Godoy")
        lbl_nombre.setFont(QFont("Open Sans", 11))
        layout.addWidget(lbl_nombre)

        layout.addSpacing(10)

        lbl_email_titulo = QLabel("Contacto:")
        lbl_email_titulo.setFont(QFont("Open Sans", 11, QFont.Weight.Bold))
        layout.addWidget(lbl_email_titulo)

        link_email = QLabel(
            "<a href='mailto:abelgodoy.1802@gmail.com?subject=REPORTE%20-%20HardAgenda%20V1.0.0' "
            "style='color: #0078d4;'>abelgodoy.1802@gmail.com</a>"
        )
        link_email.setFont(QFont("Open Sans", 11))
        link_email.setOpenExternalLinks(True)
        layout.addWidget(link_email)

        lbl_telefono = QLabel("+54 3795 320959")
        lbl_telefono.setFont(QFont("Open Sans", 11))
        layout.addWidget(lbl_telefono)

        layout.addSpacing(20)

        lbl_soporte_titulo = QLabel("Soporte:")
        lbl_soporte_titulo.setFont(QFont("Open Sans", 11, QFont.Weight.Bold))
        layout.addWidget(lbl_soporte_titulo)

        reporte_body = (
            "REPORTAR PROBLEMA - HardAgenda V1.0.0%0A%0A"
            "--- Descripcion del problema ---%0A"
            "(Describe que hiciste y que esperabas que pasara)%0A%0A"
            "--- Pasos para reproducir ---%0A"
            "1. %0A"
            "2. %0A"
            "3. %0A%0A"
            "--- Comportamiento esperado ---%0A"
            "%0A"
            "--- Comportamiento actual ---%0A"
            "%0A"
            "--- Captura de pantalla (opcional) ---%0A"
            "%0A"
            "--- Datos del sistema ---%0A"
            "SO: %0A"
            "Python: %0A"
            "PostgreSQL: %0A"
        )
        link_reportar = QLabel(
            f"<a href='mailto:abelgodoy.1802@gmail.com?subject=REPORTE%20-%20HardAgenda%20V1.0.0&body={reporte_body}' "
            f"style='color: #0078d4;'>Reportar un problema</a>"
        )
        link_reportar.setFont(QFont("Open Sans", 11))
        link_reportar.setOpenExternalLinks(True)
        layout.addWidget(link_reportar)

        layout.addStretch()

        main_layout.addWidget(text_widget)

        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(BASE_PATH, 'resources', 'logo_default_large.png')
        if os.path.exists(logo_path):
            lbl_logo = QLabel()
            lbl_logo.setPixmap(QIcon(logo_path).pixmap(250, 250))
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_layout.addWidget(lbl_logo)
        main_layout.addWidget(logo_widget)


if __name__ == "__main__":
    def excepcion_no_manejada(tipo, valor, traceback):
        QMessageBox.critical(None, "Error inesperado", f"{tipo.__name__}: {valor}")

    sys.excepthook = excepcion_no_manejada

    app = QApplication(sys.argv)
    icon_path = os.path.join(BASE_PATH, 'resources', 'logo_small.png')
    if not os.path.exists(icon_path):
        icon_path = os.path.join(BASE_PATH, 'resources', 'HardAgenda.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())

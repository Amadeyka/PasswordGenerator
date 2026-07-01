import string
import random
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QPushButton, QLineEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QFileDialog, QSplitter, QSpinBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
import database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор паролей")
        self.resize(950, 600)
        self.setMinimumSize(850, 500)

        # Инициализация БД
        self.db = database.DatabaseManager()
        self.db.init_db()
        self.current_image_path = ""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self._setup_ui()
        self._bind_signals()
        self._refresh_table()

    def _setup_ui(self):
        """Верстка только через менеджеры компоновки (никаких move/setGeometry)"""
        main_layout = QHBoxLayout()
        self.centralWidget().setLayout(main_layout)

        # Левая панель
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Название", "Длина", "Пароль"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        left_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить / Обновить")
        self.btn_delete = QPushButton("Удалить")
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_delete)
        left_layout.addLayout(btn_layout)

        # Правая панель (Форма)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.le_title = QLineEdit()
        self.le_title.setPlaceholderText("Например: VK, Google...")
        
        self.sb_length = QSpinBox()
        self.sb_length.setRange(4, 50) # Валидация по ТЗ (от 4 до 50)
        self.sb_length.setValue(12)
        
        self.cb_upper = QCheckBox("Использовать заглавные")
        self.cb_upper.setChecked(True)
        self.cb_digits = QCheckBox("Использовать цифры")
        self.cb_digits.setChecked(True)
        self.cb_symbols = QCheckBox("Использовать спецсимволы")
        self.cb_exclude = QCheckBox("Исключить 0/O/1/l") # По ТЗ
        
        self.btn_generate = QPushButton("Сгенерировать пароль")
        
        self.le_password = QLineEdit()
        self.lbl_strength = QLabel("Индикатор надёжности: -")

        form_layout.addRow("Название:", self.le_title)
        form_layout.addRow("Длина:", self.sb_length)
        form_layout.addRow("", self.cb_upper)
        form_layout.addRow("", self.cb_digits)
        form_layout.addRow("", self.cb_symbols)
        form_layout.addRow("", self.cb_exclude)
        form_layout.addRow("", self.btn_generate)
        form_layout.addRow("Пароль:", self.le_password)
        form_layout.addRow("", self.lbl_strength)
        
        right_layout.addWidget(form_widget)

        # Блок загрузки иконки
        self.lbl_image = QLabel("Иконка замка/щита")
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.lbl_image.setMinimumHeight(180)
        self.lbl_image.setStyleSheet("background-color: #f5f5f5; border: 2px dashed #bbb; border-radius: 8px;")
        right_layout.addWidget(self.lbl_image)

        self.btn_load_img = QPushButton("Загрузить иконку")
        self.btn_clear = QPushButton("Очистить форму")
        right_layout.addWidget(self.btn_load_img)
        right_layout.addWidget(self.btn_clear)

        # Адаптивный сплиттер
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 400])
        main_layout.addWidget(splitter)

        # Базовая стилизация (QSS)
        self.setStyleSheet("""
            QPushButton { padding: 6px; border-radius: 4px; background-color: #0078D7; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #005A9E; }
            QLineEdit, QSpinBox { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }
        """)

    def _bind_signals(self):
        """Привязка сигналов"""
        self.btn_generate.clicked.connect(self._on_generate)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_load_img.clicked.connect(self._on_load_image)
        self.btn_clear.clicked.connect(self._clear_fields)
        self.table.itemSelectionChanged.connect(self._on_select_row)

    def _on_generate(self):
        """Запуск генерации через неблокирующий таймер (по ТЗ без sleep)"""
        QTimer.singleShot(10, self._logic_generate_password)

    def _logic_generate_password(self):
        """Слой логики: генерация пароля"""
        chars = string.ascii_lowercase
        if self.cb_upper.isChecked(): chars += string.ascii_uppercase
        if self.cb_digits.isChecked(): chars += string.digits
        if self.cb_symbols.isChecked(): chars += string.punctuation

        if self.cb_exclude.isChecked():
            for c in "0O1l":
                chars = chars.replace(c, "")

        if not chars:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один тип символов!")
            return

        pwd = "".join(random.choice(chars) for _ in range(self.sb_length.value()))
        self.le_password.setText(pwd)
        self._update_strength(pwd)

    def _update_strength(self, pwd):
        """Вычисление надёжности"""
        score = sum([
            any(c.islower() for c in pwd),
            any(c.isupper() for c in pwd),
            any(c.isdigit() for c in pwd),
            any(c in string.punctuation for c in pwd)
        ])
        
        if len(pwd) < 8 or score <= 2:
            self.lbl_strength.setText("Надёжность: Слабая")
            self.lbl_strength.setStyleSheet("color: red; font-weight: bold;")
        elif 8 <= len(pwd) < 12 and score == 3:
            self.lbl_strength.setText("Надёжность: Средняя")
            self.lbl_strength.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.lbl_strength.setText("Надёжность: Высокая")
            self.lbl_strength.setStyleSheet("color: green; font-weight: bold;")

    def _on_save(self):
        title = self.le_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка валидации", "Поле 'Название' обязательно для заполнения.")
            return

        data = {
            "title": title,
            "length": self.sb_length.value(),
            "use_upper": int(self.cb_upper.isChecked()),
            "use_digits": int(self.cb_digits.isChecked()),
            "use_symbols": int(self.cb_symbols.isChecked()),
            "password": self.le_password.text().strip(),
            "image_path": self.current_image_path
        }

        selected = self.table.selectionModel().selectedRows()
        if selected:
            data["id"] = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
            self.db.update_record(data)
            QMessageBox.information(self, "Успех", "Запись обновлена.")
        else:
            self.db.insert_record(data)
            QMessageBox.information(self, "Успех", "Запись добавлена.")

        self._refresh_table()

    def _on_delete(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления.")
            return

        if QMessageBox.question(self, "Подтверждение", "Удалить выбранную запись?") == QMessageBox.Yes:
            item_id = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
            self.db.delete_record(item_id)
            self._refresh_table()
            self._clear_fields()

    def _on_select_row(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected: return

        item_id = self.table.item(selected[0].row(), 0).data(Qt.UserRole)
        records = self.db.get_all()
        record = next((r for r in records if r["id"] == item_id), None)

        if record:
            self.le_title.setText(record["title"])
            self.sb_length.setValue(record["length"])
            self.cb_upper.setChecked(bool(record["use_upper"]))
            self.cb_digits.setChecked(bool(record["use_digits"]))
            self.cb_symbols.setChecked(bool(record["use_symbols"]))
            self.le_password.setText(record["password"])
            self._update_strength(record["password"])

            self.current_image_path = record["image_path"] if record["image_path"] else ""
            self._load_pixmap(self.current_image_path)

    def _on_load_image(self):
        """Интеграция с Pillow: загрузка иконки"""
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.current_image_path = path
            self._load_pixmap(path)

    def _load_pixmap(self, path):
        """Безопасная загрузка через PIL и масштабирование без кэширования"""
        if not path:
            self.lbl_image.clear()
            self.lbl_image.setText("Иконка замка/щита")
            return
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((200, 200), Image.LANCZOS)
            qt_img = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGBA8888)
            self.lbl_image.setPixmap(QPixmap.fromImage(qt_img))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить изображение:\n{e}")
            self.current_image_path = ""

    def _refresh_table(self):
        self.table.setRowCount(0)
        for i, rec in enumerate(self.db.get_all()):
            self.table.insertRow(i)
            item_title = QTableWidgetItem(rec["title"])
            item_title.setData(Qt.UserRole, rec["id"]) # Храним ID в невидимой роли (UserRole)
            self.table.setItem(i, 0, item_title)
            self.table.setItem(i, 1, QTableWidgetItem(str(rec["length"])))
            self.table.setItem(i, 2, QTableWidgetItem(rec["password"]))

    def _clear_fields(self):
        self.le_title.clear()
        self.le_password.clear()
        self.lbl_strength.setText("Индикатор надёжности: -")
        self.lbl_strength.setStyleSheet("")
        self.current_image_path = ""
        self._load_pixmap("")
        self.table.clearSelection()

    def closeEvent(self, event):
        """Событие закрытия окна (по ТЗ: не должно оставаться зомби-процессов)"""
        reply = QMessageBox.question(self, "Выход", "Закрыть приложение?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.close() # Обязательное закрытие БД для избежания утечек
            event.accept()
        else:
            event.ignore()
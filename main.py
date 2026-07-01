import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from ui_main import MainWindow

def main():
    # Обязательный sys.argv для корректной передачи аргументов Qt
    app = QApplication(sys.argv)
    
    app.setApplicationName("PasswordCatalog")
    app.setApplicationVersion("1.0")
    
    # Шрифт по умолчанию по ТЗ
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()

    # sys.exit() гарантирует корректное завершение
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
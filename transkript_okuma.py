import sys
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QTableWidget, QTableWidgetItem, 
                             QHBoxLayout, QLineEdit, QLabel)
import pdfplumber

# Harf notları ile 4'lük sistem arasında dönüşüm tablosu
grade_to_gpa = {
    'AA': 4.0, 'BA': 3.5, 'BB': 3.0, 'CB': 2.5,
    'CC': 2.0, 'DC': 1.5, 'DD': 1.0, 'FF': 0.0,
    'DF': 0.0, 'DZ': 0.0, 'GR': 0.0,
}

class TranscriptApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Transkript Okuma Sistemi')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # PDF Yükleme Butonu
        self.upload_button = QPushButton('Transkript Yükle', self)
        self.upload_button.clicked.connect(self.load_pdf)
        layout.addWidget(self.upload_button)

        # Ders Tablosu
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Ders Kodu', 'Ders Adı', 'Kredi', 'Not'])
        layout.addWidget(self.table)

        # Kullanıcı tabloyu değiştirdiğinde GPA güncellensin
        self.table.cellChanged.connect(self.calculate_gpa)

        # Yeni Ders Ekleme Alanı
        add_layout = QHBoxLayout()
        self.course_code_input = QLineEdit(self)
        self.course_code_input.setPlaceholderText('Ders Kodu')
        self.course_name_input = QLineEdit(self)
        self.course_name_input.setPlaceholderText('Ders Adı')
        self.credit_input = QLineEdit(self)
        self.credit_input.setPlaceholderText('Kredi')
        self.grade_input = QLineEdit(self)
        self.grade_input.setPlaceholderText('Not (AA, BA, BB...)')
        self.add_button = QPushButton('Ders Ekle', self)
        self.add_button.clicked.connect(self.add_course)

        add_layout.addWidget(self.course_code_input)
        add_layout.addWidget(self.course_name_input)
        add_layout.addWidget(self.credit_input)
        add_layout.addWidget(self.grade_input)
        add_layout.addWidget(self.add_button)

        layout.addLayout(add_layout)

        # Ders Silme Butonu
        self.delete_button = QPushButton('Seçili Dersi Sil', self)
        self.delete_button.clicked.connect(self.delete_course)
        layout.addWidget(self.delete_button)

        # GPA Hesaplama Alanı
        self.gpa_label = QLabel('Genel Ağırlıklı Not Ortalaması (GPA): 0.00', self)
        layout.addWidget(self.gpa_label)

        self.setLayout(layout)

    def load_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'PDF Dosyası Seç', '', 'PDF Files (*.pdf)')
        if file_name:
            self.read_pdf(file_name)

    def read_pdf(self, file_path):
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() + '\n'
                self.extract_courses(text)
        except Exception as e:
            print(f'Hata oluştu: {e}')

    def extract_courses(self, text):
        self.table.setRowCount(0)
        lines = text.split('\n')

        # Regex ile ders kodu, adı, kredi ve not ayıklama
        pattern = re.compile(r'(\w{3}\s*\d{3})\s+(.+?)\s+(\d+)\s+(AA|BA|BB|CB|CC|DC|DD|FF|DF|DZ|GR)')

        for line in lines:
            match = pattern.search(line)
            if match:
                course_code = match.group(1).strip()
                course_name = match.group(2).strip()
                credit = match.group(3)
                grade = match.group(4)
                self.add_course_to_table(course_code, course_name, credit, grade)

        self.calculate_gpa()

    def add_course(self):
        course_code = self.course_code_input.text()
        course_name = self.course_name_input.text()
        credit = self.credit_input.text()
        grade = self.grade_input.text().upper()

        if course_code and course_name and credit and grade:
            self.add_course_to_table(course_code, course_name, credit, grade)
            self.course_code_input.clear()
            self.course_name_input.clear()
            self.credit_input.clear()
            self.grade_input.clear()
            self.calculate_gpa()

    def add_course_to_table(self, course_code, course_name, credit, grade):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(course_code))
        self.table.setItem(row_position, 1, QTableWidgetItem(course_name))
        self.table.setItem(row_position, 2, QTableWidgetItem(credit))
        self.table.setItem(row_position, 3, QTableWidgetItem(grade))

    def delete_course(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.table.removeRow(selected_row)
            self.calculate_gpa()  # Silinen ders sonrası GPA'yı tekrar hesapla

    def calculate_gpa(self):
        total_credits = 0
        total_points = 0

        for row in range(self.table.rowCount()):
            credit_item = self.table.item(row, 2)
            grade_item = self.table.item(row, 3)

            if credit_item and grade_item:
                try:
                    credit = float(credit_item.text().strip())
                    grade_letter = grade_item.text().strip().upper()
                    grade = grade_to_gpa.get(grade_letter, 0.0)
                    total_credits += credit
                    total_points += credit * grade
                except ValueError:
                    continue  # Hatalı girişleri atla

        gpa = (total_points / total_credits) if total_credits > 0 else 0
        self.gpa_label.setText(f'Genel Ağırlıklı Not Ortalaması (GPA): {gpa:.2f}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TranscriptApp()
    ex.show()
    sys.exit(app.exec_())

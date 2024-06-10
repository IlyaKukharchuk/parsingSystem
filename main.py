import sys
import asyncio
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QHeaderView, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime
from scrapers import parse_category, parse_category_async
from database import Database

class ParserThread(QThread):
    data_collected = pyqtSignal(int, list, str)  # signal to emit when data is collected

    def __init__(self, category_url, is_async):
        super().__init__()
        self.category_url = category_url
        self.is_async = is_async

    def run(self):
        try:
            database = Database('postgres', 'postgres', 'postgres')  # For PostgreSQL (replace placeholders)
            database.create_tables()

            if self.is_async:
                products = asyncio.run(parse_category_async(self.category_url))
            else:
                products = parse_category(self.category_url)

            selection_id = database.add_selection_data(len(products))
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            database.add_product_data(selection_id, products)
            self.data_collected.emit(selection_id, products, timestamp)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            database.close()

class ParserApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(1200, 800)
        self.setMinimumSize(300, 300)

        layout = QVBoxLayout()

        self.label = QLabel('Сategory URL:')
        layout.addWidget(self.label)

        self.urlInput = QLineEdit(self)
        layout.addWidget(self.urlInput)

        self.tableWidgetSelections = QTableWidget()
        self.tableWidgetSelections.setColumnCount(3)
        self.tableWidgetSelections.setHorizontalHeaderLabels(["Selection ID", "Product Count", "Timestamp"])
        layout.addWidget(self.tableWidgetSelections)
        self.tableWidgetSelections.cellClicked.connect(self.selection_clicked)
        self.tableWidgetSelections.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # for row in range(self.tableWidgetSelections.rowCount()):
        #     for column in range(self.tableWidgetSelections.columnCount()):
        #         item = self.tableWidgetSelections.item(row, column)
        #         item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        self.tableWidgetProducts = QTableWidget()
        self.tableWidgetProducts.setColumnCount(3)
        self.tableWidgetProducts.setHorizontalHeaderLabels(["Selection ID", "Name", "Price"])
        layout.addWidget(self.tableWidgetProducts)
        self.tableWidgetProducts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.tableWidgetProducts.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidgetSelections.setEditTriggers(QTableWidget.NoEditTriggers)

         # Включаем отображение индикатора сортировки
        self.tableWidgetProducts.horizontalHeader().setSortIndicatorShown(True)
        self.tableWidgetProducts.horizontalHeader().setSectionsClickable(True)
        self.tableWidgetProducts.horizontalHeader().sortIndicatorChanged.connect(self.sort_table)

        buttons_layout = QHBoxLayout()

        self.parseButton = QPushButton('Parse Normally')
        self.parseButton.clicked.connect(self.parse_normal)
        buttons_layout.addWidget(self.parseButton)

        self.asyncParseButton = QPushButton('Parse Asynchronously')
        self.asyncParseButton.clicked.connect(self.parse_async)
        buttons_layout.addWidget(self.asyncParseButton)

        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.setWindowTitle('Data Parser')
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: #333;
            }
            QLabel {
                font-size: 16px;
                margin-bottom: 10px;
            }
            QLineEdit {
                padding: 5px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 4px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                margin-top: 10px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #ddd;
            }
            QTableWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
        """)
        self.show()
    
    def sort_table(self, logicalIndex):
        self.tableWidgetProducts.sortItems(logicalIndex)

    def parse_normal(self):
        category_url = self.urlInput.text()
        self.thread = ParserThread(category_url, False)
        self.thread.data_collected.connect(self.update_ui)
        self.thread.start()

    def parse_async(self):
        category_url = self.urlInput.text()
        self.thread = ParserThread(category_url, True)
        self.thread.data_collected.connect(self.update_ui)
        self.thread.start()

    def update_ui(self, selection_id, products, timestamp):
        self.tableWidgetSelections.insertRow(self.tableWidgetSelections.rowCount())
        self.tableWidgetSelections.setItem(self.tableWidgetSelections.rowCount()-1, 0, QTableWidgetItem(str(selection_id)))
        self.tableWidgetSelections.setItem(self.tableWidgetSelections.rowCount()-1, 1, QTableWidgetItem(str(len(products))))
        self.tableWidgetSelections.setItem(self.tableWidgetSelections.rowCount()-1, 2, QTableWidgetItem(timestamp))

        self.tableWidgetProducts.setRowCount(0)
        for product in products:
            rowPosition = self.tableWidgetProducts.rowCount()
            self.tableWidgetProducts.insertRow(rowPosition)
            self.tableWidgetProducts.setItem(rowPosition, 0, QTableWidgetItem(str(selection_id)))
            self.tableWidgetProducts.setItem(rowPosition, 1, QTableWidgetItem(product['name']))
            self.tableWidgetProducts.setItem(rowPosition, 2, QTableWidgetItem(product['price']))

    def selection_clicked(self, row, column):
        selection_id = self.tableWidgetSelections.item(row, 0).text()
        self.display_selection_products(selection_id)

    def display_selection_products(self, selection_id):
        try:
            database = Database('postgres', 'postgres', 'postgres')
            products = database.get_products_for_selection(selection_id)
            self.tableWidgetProducts.setRowCount(0)
            for product in products:
                rowPosition = self.tableWidgetProducts.rowCount()
                self.tableWidgetProducts.insertRow(rowPosition)
                self.tableWidgetProducts.setItem(rowPosition, 0, QTableWidgetItem(str(selection_id)))
                self.tableWidgetProducts.setItem(rowPosition, 1, QTableWidgetItem(product['product_name']))
                self.tableWidgetProducts.setItem(rowPosition, 2, QTableWidgetItem(product['price']))
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            database.close()

def get_url():
    response = requests.get('https://life.com.by/_next/data/4-ZlKMqNBSwTq1XtzOtsI/store/smartphones.json?pageLimit=50')
    
    if response.status_code == 200:
        data = response.json()
        count_all = data['pageProps']['pageData']['countAll']
        count_all = 10 * round(count_all/10)
        url = f"https://life.com.by/store/smartphones?pageLimit={count_all}"
        return url
    else:
        print("Error in performing request: ", response.status_code)
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ParserApp()
    url = get_url()
    if url:
        ex.urlInput.setText(url) 
    sys.exit(app.exec_())

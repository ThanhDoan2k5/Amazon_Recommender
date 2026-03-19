from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
from src.model_amazon import get_recommendations

class AmazonRecommenderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛒 Hệ Thống Gợi Ý Sản Phẩm Amazon")
        self.setGeometry(200, 200, 700, 550)

        self.setStyleSheet("""
            QWidget { font-family: Arial, sans-serif; font-size: 16px; background-color: #f8f9fa; }
            QLabel { font-weight: bold; color: #333333; }
            QPushButton { 
                background-color: #ff9900; 
                color: white; 
                border-radius: 6px; 
                padding: 12px; 
                font-weight: bold; 
                font-size: 18px;
            }
            QPushButton:hover { background-color: #e68a00; }
            QLineEdit { border: 2px solid #cccccc; padding: 8px; border-radius: 4px; background-color: white;}
            QLineEdit:focus { border: 2px solid #ff9900; }
            QTextEdit { border: 2px solid #cccccc; padding: 10px; border-radius: 4px; background-color: white; font-size: 15px;}
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        input_layout = QHBoxLayout()

        user_layout = QVBoxLayout()
        user_layout.addWidget(QLabel("Mã Khách Hàng (Nhập 'Tuấn' để test):"))
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Ví dụ: Tuấn, Lan, hoặc nhập ID thật...")
        user_layout.addWidget(self.user_id_input)
        input_layout.addLayout(user_layout, stretch=3)

        top_k_layout = QVBoxLayout()
        top_k_layout.addWidget(QLabel("Top-K:"))
        self.top_k_input = QLineEdit()
        self.top_k_input.setText("5")
        top_k_layout.addWidget(self.top_k_input)
        input_layout.addLayout(top_k_layout, stretch=1)

        main_layout.addLayout(input_layout)

        self.recommend_btn = QPushButton("Phân Tích & Gợi Ý")
        self.recommend_btn.setCursor(Qt.PointingHandCursor)
        self.recommend_btn.clicked.connect(self.on_recommend)
        main_layout.addWidget(self.recommend_btn)

        main_layout.addWidget(QLabel("Kết quả đề xuất:"))
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        main_layout.addWidget(self.result_area)

        self.setLayout(main_layout)

    def on_recommend(self):
        user_id = self.user_id_input.text().strip()
        top_k_text = self.top_k_input.text().strip()

        if not user_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập Mã Khách Hàng để AI phân tích!")
            return

        top_k = int(top_k_text) if top_k_text.isdigit() else 5

        self.result_area.setText(" Đang quét kho dữ liệu Amazon... Vui lòng đợi trong giây lát...")
        QApplication.processEvents()

        try:
            recs = get_recommendations(user_id, top_k)

            if not recs:
                self.result_area.setText(f"Không tìm thấy lịch sử mua hàng của khách: '{user_id}'.")
                return

            if len(recs) == 1 and "Lỗi" in recs[0]["title"]:
                 self.result_area.setText(recs[0]["title"])
                 return

            result_str = ""
            for i, item in enumerate(recs):
                result_str += f"{i+1}.  Tên mặt hàng: {item['title']}\n"
                result_str += f"    Mã ASIN: {item['asin']}\n"
                result_str += f"    Điểm AI dự đoán: {item['score']:.2f} / 5.00 sao\n"
                result_str += f"    Link Amazon: {item['link']}\n"
                result_str += "-" * 80 + "\n"

            self.result_area.setText(result_str)

        except Exception as e:
            self.result_area.setText(f" Đã xảy ra lỗi hệ thống: {str(e)}")

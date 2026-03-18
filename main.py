import sys
from PyQt5.QtWidgets import QApplication
from src.gui import AmazonRecommenderGUI
from src.model_amazon import load_and_train

def main():
    print("==================================================")
    print("ĐANG KHỞI ĐỘNG HỆ THỐNG GỢI Ý AMAZON...")
    print("Vui lòng không tắt cửa sổ đen này.")
    print("==================================================")
    
    success = load_and_train()

    if not success:
        print("\n Khởi động AI thất bại. Vui lòng kiểm tra lại thư mục 'data'.")
        input("Nhấn Enter để thoát...")
        return

    app = QApplication(sys.argv)
    window = AmazonRecommenderGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

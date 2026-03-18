# Hệ Thống Gợi Ý Sản Phẩm Amazon (Amazon Recommendation System)

Đây là một ứng dụng Desktop (GUI) gợi ý sản phẩm được xây dựng bằng Python. Hệ thống sử dụng Mô hình Hồi quy tuyến tính (Linear Regression) để dự đoán và đưa ra các đề xuất mua sắm cá nhân hóa dựa trên lịch sử đánh giá của người dùng và chất lượng tổng thể của sản phẩm.

## Tính năng chính

- Giao diện trực quan: Giao diện người dùng đơn giản, phản hồi nhanh được xây dựng bằng PyQt5.
- Xử lý Dữ liệu lớn (Big Data): Tích hợp kỹ thuật Chunking để xử lý mượt mà bộ dữ liệu Amazon Reviews 2023 khổng lồ (> 7GB) mà không gây tràn bộ nhớ (RAM).
- Tra cứu thông minh: Tự động ánh xạ các tên gọi thân thiện (Ví dụ: Tuấn, Lan, Nam) thành các mã ID khách hàng thực tế trong tập dữ liệu để tiện lợi cho quá trình test và demo.
- Tùy chọn Top-K & Direct Link: Người dùng có thể tùy chỉnh số lượng sản phẩm gợi ý (Top 5, Top 10). Hệ thống tự động trích xuất mã ASIN và tạo URL liên kết trực tiếp đến trang mua hàng thật trên Amazon.

## Công nghệ sử dụng

- Ngôn ngữ: Python 3.x
- Giao diện (GUI): PyQt5
- Xử lý dữ liệu & Học máy: pandas, numpy, scikit-learn
- Dataset: Amazon Reviews 2023 (Electronics.jsonl.gz, meta_Electronics.jsonl.gz)

## Nguyên lý hoạt động (Thuật toán Linear Regression)

Hệ thống tính toán điểm số dự đoán (Predicted Score) cho mỗi sản phẩm mà người dùng chưa từng mua dựa trên các đặc trưng thống kê lịch sử.

1. Trích xuất Đặc trưng (Feature Engineering)
Thay vì sử dụng ma trận thưa (Sparse Matrix) truyền thống, hệ thống tổng hợp dữ liệu thành 4 biến số (Features) cốt lõi cho mỗi lượt đánh giá:
- Đánh giá trung bình của người dùng (user_avg_rating)
- Tổng số lượt đánh giá của người dùng (user_review_count)
- Đánh giá trung bình của sản phẩm (item_avg_rating)
- Tổng số lượt đánh giá của sản phẩm (item_review_count)

2. Mô hình Hồi quy Tuyến tính (Linear Regression)
Mô hình học mối quan hệ giữa các đặc trưng thống kê trên và điểm đánh giá thực tế (overall rating) từ tập dữ liệu. Công thức dự đoán điểm số của mô hình được biểu diễn như sau:

$$\text{Score}_{pred} = \beta_0 + \beta_1 \cdot \text{User}_{avg} + \beta_2 \cdot \text{User}_{count} + \beta_3 \cdot \text{Item}_{avg} + \beta_4 \cdot \text{Item}_{count}$$

Mục đích: Hệ thống sẽ lọc ra toàn bộ các mặt hàng mà User mục tiêu chưa từng mua, đưa các đặc trưng vào phương trình trên để nội suy ra dự đoán.

3. Đưa ra Gợi ý
Điểm số sau khi dự đoán được giới hạn (clip) về dải điểm hợp lệ từ 1.0 đến 5.0. Hệ thống tiến hành sắp xếp (sort) danh sách theo thứ tự điểm giảm dần và trả về Top-K sản phẩm có khả năng được người dùng đó đánh giá cao nhất.

## Hướng dẫn Cài đặt & Sử dụng

1. Chuẩn bị môi trường
Cài đặt các thư viện cần thiết thông qua pip:
pip install pandas numpy scikit-learn PyQt5

2. Chuẩn bị Dữ liệu
Tạo thư mục `data/` ở thư mục gốc của dự án. Tải và đặt 2 file dữ liệu Amazon 2023 vào bên trong:
- Electronics.jsonl.gz
- meta_Electronics.jsonl.gz

3. Khởi chạy ứng dụng
Mở terminal và chạy file thực thi chính:
python main.py
(Lưu ý: Trong lần chạy đầu tiên, hệ thống sẽ mất thời gian để đọc dữ liệu và huấn luyện mô hình. Vui lòng không tắt cửa sổ console).

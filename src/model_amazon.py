import pandas as pd
import numpy as np
import json
import gzip
import os
from sklearn.linear_model import LinearRegression

_DATASET = None
_MODEL = None
_DANH_BA_VIP = {} # Thêm một cuốn "sổ tay" cho danh bạ

def load_and_train():
    """Hàm này khởi động AI và đọc dữ liệu 2023"""
    global _DATASET, _MODEL, _DANH_BA_VIP
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    meta_path = os.path.join(base_dir, 'data', 'meta_Electronics.jsonl.gz') 
    review_path = os.path.join(base_dir, 'data', 'Electronics.jsonl.gz') 

    print(" ĐANG HUẤN LUYỆN DỮ LIỆU LỚN BẢN 2023... VUI LÒNG ĐỢI...")

    asin_to_info = {}
    try:
        with gzip.open(meta_path, 'rt', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    item_id = item.get('parent_asin', item.get('asin'))
                    if item_id and 'title' in item:
                        asin_to_info[item_id] = item['title']
                except:
                    continue
    except Exception as e:
        print(f" Lỗi Meta: {e}")
        return False

    try:
        chunks = []
        reader = pd.read_json(review_path, lines=True, chunksize=500000) 
        for i, chunk in enumerate(reader):
            # Tự động convert data 2023 chuẩn xác
            if 'user_id' in chunk.columns:
                chunk['reviewerID'] = chunk['user_id']
            if 'rating' in chunk.columns:
                chunk['overall'] = chunk['rating']
            if 'parent_asin' in chunk.columns:
                chunk['asin'] = chunk['parent_asin']
                
            chunks.append(chunk[['reviewerID', 'asin', 'overall']])
            print(f"   + Đã nạp vào RAM: { (i+1)*0.5 } triệu lượt đánh giá...")
            if i == 3: # Đọc 2.0 triệu dòng rồi chốt
                break 
        
        df = pd.concat(chunks, ignore_index=True)
        df['product_name'] = df['asin'].map(asin_to_info)
   
        df = df.dropna(subset=['product_name'])
        print(f"   -> SỐ DÒNG KHỚP NHAU HOÀN HẢO: {len(df)} dòng")
        
        if len(df) == 0: 
            print(" LỖI: Dữ liệu review không khớp với tên sản phẩm nào!")
            return False

    except Exception as e:
        print(f" Lỗi Review: {e}")
        return False

    print(" Đang trích xuất đặc trưng và đưa vào mô hình học thuật toán...")
    
    user_stats = df.groupby('reviewerID')['overall'].agg(['mean', 'count']).reset_index()
    user_stats.columns = ['reviewerID', 'user_avg_rating', 'user_review_count']
    
    item_stats = df.groupby('asin')['overall'].agg(['mean', 'count']).reset_index()
    item_stats.columns = ['asin', 'item_avg_rating', 'item_review_count']

    _DATASET = df.merge(user_stats, on='reviewerID', how='inner').merge(item_stats, on='asin', how='inner')
    _DATASET = _DATASET.dropna(subset=['user_avg_rating', 'user_review_count', 'item_avg_rating', 'item_review_count', 'overall'])

    X = _DATASET[['user_avg_rating', 'user_review_count', 'item_avg_rating', 'item_review_count']]
    y = _DATASET['overall']
    
    _MODEL = LinearRegression().fit(X, y)
    print(" ĐÃ HỌC XONG TOÀN BỘ. HỆ THỐNG SẴN SÀNG CHỐT ĐƠN!")
   
    real_ids = df['reviewerID'].unique()[:10]
    ten_tieng_viet = ["Tuấn", "Lan", "Nam", "Hương", "Huy", "Trang", "Hải", "Linh", "Dũng", "Hoa"]
    
    print("\n" + "="*55)
    print(" DANH BẠ 10 KHÁCH HÀNG VIP ĐỂ ĐI BÁO CÁO:")
    for i in range(min(len(real_ids), len(ten_tieng_viet))):
        name = ten_tieng_viet[i]
        _DANH_BA_VIP[name] = real_ids[i]
        _DANH_BA_VIP[name.lower()] = real_ids[i] # Hỗ trợ nhập chữ thường
        print(f"    Nhập '{name}' -> Hệ thống sẽ phân tích ID: {real_ids[i]}")
    print("="*55 + "\n")
    
    return True

def get_recommendations(target_user, top_k=5):
    """Xử lý nút Gợi ý trên giao diện"""
    global _DATASET, _MODEL, _DANH_BA_VIP
    if _DATASET is None or _MODEL is None: return []

    target_user = str(target_user).strip()
 
    if target_user in _DANH_BA_VIP: 
        target_user = _DANH_BA_VIP[target_user]

    if target_user not in _DATASET['reviewerID'].values: return []

    u_data = _DATASET[_DATASET['reviewerID'] == target_user].iloc[0]
    da_mua = _DATASET[_DATASET['reviewerID'] == target_user]['asin'].unique()
    all_items = _DATASET[['asin', 'product_name', 'item_avg_rating', 'item_review_count']].drop_duplicates('asin')
    chua_mua = all_items[~all_items['asin'].isin(da_mua)].copy()

    if chua_mua.empty: return []

    chua_mua['user_avg_rating'] = u_data['user_avg_rating']
    chua_mua['user_review_count'] = u_data['user_review_count']
    X_pred = chua_mua[['user_avg_rating', 'user_review_count', 'item_avg_rating', 'item_review_count']]
    
    chua_mua['score'] = np.clip(_MODEL.predict(X_pred), 1, 5)
    top_list = chua_mua.sort_values(by='score', ascending=False).head(top_k)
    
    results = []
    for _, row in top_list.iterrows():
        ten_sp = str(row['product_name'])
        if len(ten_sp) > 75: ten_sp = ten_sp[:75] + "..."
        link = f"https://www.amazon.com/dp/{row['asin']}"
        
        results.append({
            "title": ten_sp, 
            "asin": row['asin'], 
            "score": row['score'], 
            "link": link
        })
        
    return results

import os
import glob
import json
import datetime

def main():
    print("=== BẮT ĐẦU QUÉT VÀ TẠO BÁO CÁO JSON ===")
    
    # Thư mục chứa các tệp JSON kết quả trong repository
    # (Anh có thể tạo thư mục 'ket_qua_json' trên repo hoặc lưu trực tiếp ở thư mục gốc)
    output_dir = "." # Hoặc đường dẫn thư mục chứa JSON trên repo của anh
    
    # Tìm tất cả các file .json trong thư mục
    json_files = glob.glob(os.path.join(output_dir, "*.json"))
    
    aggregated_data = []
    
    for file_path in json_files:
        # Bỏ qua file cấu hình hoặc file output tổng nếu có
        if "aggregated_output.json" in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                aggregated_data.append({
                    "file_name": os.path.basename(file_path),
                    "content": data,
                    "updated_at": str(datetime.datetime.now())
                })
        except Exception as e:
            print(f"Lỗi khi đọc file {file_path}: {e}")
            
    # Ghi gộp dữ liệu thành file aggregated_output.json để trang web index.html hiển thị
    final_output_path = "aggregated_output.json"
    with open(final_output_path, 'w', encoding='utf-8') as f:
        json.dump(aggregated_data, f, ensure_ascii=False, indent=4)
        
    print(f"=== ĐÃ TẠO XONG BÁO CÁO: Tổng hợp {len(json_files)} tệp JSON ===")

if __name__ == "__main__":
    main()

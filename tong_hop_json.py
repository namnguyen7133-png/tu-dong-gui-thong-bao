import os
import glob
import json
from datetime import datetime, timedelta

thu_muc_json = "KET_QUA_JSON"
file_output = "aggregated_output.json"

def tong_hop_du_lieu():
    now = datetime.now()
    danh_sach_ket_qua = []

    if os.path.exists(thu_muc_json):
        danh_sach_file = glob.glob(os.path.join(thu_muc_json, "*.json"))
        for file_path in danh_sach_file:
            # Bỏ qua các tệp index quản lý cấu hình
            if "index" in file_path.lower():
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Trích xuất toàn bộ dữ liệu bên trong tệp JSON một cách linh hoạt nhất
                    items = []
                    if isinstance(data, list):
                        items = data
                    elif isinstance(data, dict):
                        # Lấy tất cả các danh sách hoặc đối tượng bên trong tệp JSON
                        items.append(data)
                        for key, val in data.items():
                            if isinstance(val, list):
                                items.extend(val)
                            elif isinstance(val, dict):
                                items.append(val)

                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        
                        # Gán nhãn tên nguồn tệp để dễ theo dõi trên web
                        if 'nguon_goc' not in item:
                            item['nguon_goc'] = os.path.basename(file_path)
                            
                        # Chuẩn hóa trường thời gian bắt buộc để web hiển thị
                        if not any(k in item for k in ['thoi_gian', 'ngay_gio', 'time', 'timestamp']):
                            item['thoi_gian'] = now.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            # Đưa về khóa chung 'thoi_gian'
                            t_val = item.get('thoi_gian') or item.get('ngay_gio') or item.get('time') or item.get('timestamp')
                            item['thoi_gian'] = str(t_val)

                        danh_sach_ket_qua.append(item)

            except Exception as e:
                print(f"Lỗi đọc file {file_path}: {e}")

    output_data = {
        "thoi_gian_chay": now.strftime("%Y-%m-%d %H:%M:%S"),
        "tong_so_muc": len(danh_sach_ket_qua),
        "chi_tiet": danh_sach_ket_qua
    }

    with open(file_output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Đã tổng hợp thành công {len(danh_sach_ket_qua)} mục vào {file_output}")

if __name__ == "__main__":
    tong_hop_du_lieu()

import os
import glob
import json
from datetime import datetime

thu_muc_json = "KET_QUA_JSON"
file_output = "aggregated_output.json"

def tong_hop_du_lieu():
    now = datetime.now()
    danh_sach_tab4 = []
    danh_sach_tab5 = []
    danh_sach_tab6 = []
    tong_so_muc = 0

    if os.path.exists(thu_muc_json):
        danh_sach_file = glob.glob(os.path.join(thu_muc_json, "*.json"))
        for file_path in danh_sach_file:
            if "index" in file_path.lower():
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Trích xuất dữ liệu từ cấu trúc chuẩn của các tệp chương trình con
                    if isinstance(data, dict):
                        # Lấy từ phần 'data' nếu có
                        if 'data' in data and isinstance(data['data'], dict):
                            sub_data = data['data']
                            danh_sach_tab4.extend(sub_data.get('thong_ke_tab4', []))
                            danh_sach_tab5.extend(sub_data.get('chia_so_tab5', []))
                            danh_sach_tab6.extend(sub_data.get('so_trung_tab6', []))
                        
                        # Lấy từ phần 'people' hoặc các danh sách nhân sự
                        if 'people' in data:
                            p_val = data['people']
                            if isinstance(p_val, list):
                                danh_sach_tab4.extend(p_val)
                            elif isinstance(p_val, dict):
                                danh_sach_tab4.extend(p_val.get('danh_sach_nhan_su', []))

                    elif isinstance(data, list):
                        danh_sach_tab4.extend(data)

            except Exception as e:
                print(f"Lỗi đọc file {file_path}: {e}")

    tong_so_muc = len(danh_sach_tab4) + len(danh_sach_tab5) + len(danh_sach_tab6)

    # Cấu trúc JSON tổng hợp tương thích tuyệt đối với giao diện web
    output_data = {
        "thoi_gian_chay": now.strftime("%Y-%m-%d %H:%M:%S"),
        "tong_so_muc": tong_so_muc,
        "chi_tiet": danh_sach_tab4,
        "data": {
            "thong_ke_tab4": danh_sach_tab4,
            "chia_so_tab5": danh_sach_tab5,
            "so_trung_tab6": danh_sach_tab6
        }
    }

    with open(file_output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Đã tổng hợp thành công {tong_so_muc} mục vào {file_output}")

if __name__ == "__main__":
    tong_hop_du_lieu()

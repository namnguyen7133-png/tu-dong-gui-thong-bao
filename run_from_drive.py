import os
import glob
import json
from datetime import datetime, timedelta

# Đọc từ thư mục KET_QUA_JSON nằm ngay trong kho GitHub
thu_muc_git = "KET_QUA_JSON" 
file_output = "aggregated_output.json"

def chay_xu_ly():
    now = datetime.now()
    bay_ngay_truoc = now - timedelta(days=7)
    danh_sach_ket_qua = []

    if os.path.exists(thu_muc_git):
        danh_sach_file = glob.glob(os.path.join(thu_muc_git, "*.json"))
        for file_path in danh_sach_file:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    items = data if isinstance(data, list) else (data.get('chi_tiet') or data.get('danh_sach') or [data])
                    
                    for item in items:
                        time_str = item.get('thoi_gian') or item.get('ngay_gio') or item.get('time')
                        if not time_str:
                            continue
                        try:
                            item_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        except:
                            try:
                                item_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                            except:
                                continue
                        
                        # Bộ lọc: Từ 7 ngày trước đến hiện tại, hôm nay chỉ lấy từ giờ phút này trở đi
                        if bay_ngay_truoc <= item_time <= now:
                            if item_time.date() == now.date() and item_time < now:
                                continue
                            danh_sach_ket_qua.append(item)
            except Exception as e:
                print(f"Lỗi đọc file {file_path}: {e}")

    # Xuất ra file chuẩn để trang web index.html đọc
    output_data = {
        "thoi_gian_chay": now.strftime("%Y-%m-%d %H:%M:%S"),
        "tong_so_muc": len(danh_sach_ket_qua),
        "chi_tiet": danh_sach_ket_qua
    }

    with open(file_output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Đã xuất thành công {len(danh_sach_ket_qua)} mục vào {file_output}")

if __name__ == "__main__":
    chay_xu_ly()

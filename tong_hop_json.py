import os
import json
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIRS = [BASE_DIR, os.path.join(BASE_DIR, "KET_QUA_JSON")]
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")

def main():
    json_files = []
    for d in JSON_DIRS:
        if os.path.exists(d):
            json_files.extend(glob.glob(os.path.join(d, "*.json")))

    all_results = []

    for jf in json_files:
        fname = os.path.basename(jf)
        if fname.startswith("config_") or fname.startswith("index_") or fname == "cau_hinh_duong_dan.json" or fname == "aggregated_output.json":
            continue
        try:
            with open(jf, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    found_list = False
                    for k, v in data.items():
                        if isinstance(v, list):
                            items.extend(v)
                            found_list = True
                    if not found_list:
                        items.append(data)

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    
                    item_str = str(item)
                    if "runner/work" in item_str or len(item) < 2:
                        continue

                    # Trích xuất tên đầy đủ
                    ten = (
                        item.get("ten") or item.get("name") or item.get("tieu_de") or 
                        item.get("nguoi_song") or item.get("nguoi_mat") or item.get("ho_va_ten") or 
                        item.get("tinh_huong") or f"Bản ghi từ {fname}"
                    )

                    # Trích xuất ngày tháng và mốc giờ
                    ngay = item.get("ngay") or item.get("date") or item.get("ref_date") or datetime.now().strftime("%Y-%m-%d")
                    gio = (
                        item.get("gio_su_kien") or item.get("play_time") or item.get("gio_phat") or 
                        item.get("gio_mat") or item.get("gio_sinh") or item.get("thoi_gian") or "---"
                    )
                    
                    # Thu thập toàn bộ chi tiết (bao gồm cả số trùng, thông tin cá nhân, tab/thư mục)
                    chi_tiet_list = []
                    for k_sub, v_sub in item.items():
                        if k_sub in ["ten", "name", "tieu_de", "nguoi_song", "nguoi_mat", "ho_va_ten", "gio_su_kien", "play_time", "gio_phat", "link", "url", "metadata"]:
                            continue
                        if v_sub is not None and str(v_sub).strip() != "":
                            v_str = str(v_sub)
                            # Nếu chuỗi dữ liệu quá dài (như danh sách số nguyên tố lớn), rút gọn cho dễ nhìn nhưng vẫn giữ nguyên giá trị
                            if len(v_str) > 150:
                                v_str = v_str[:150] + "..."
                            chi_tiet_list.append(f"<b>{k_sub}:</b> {v_str}")
                    
                    noi_dung_chi_tiet = " | ".join(chi_tiet_list) if chi_tiet_list else "Đang cập nhật chi tiết"
                    
                    # Trích xuất liên kết YouTube
                    link = item.get("link") or item.get("link_video") or item.get("url") or ""
                    if not link and "links" in item:
                        links_val = item.get("links")
                        if isinstance(links_val, list) and len(links_val) > 0:
                            link = str(links_val[0])

                    all_results.append({
                        "ten": str(ten),
                        "ngay": str(ngay),
                        "gio": str(gio),
                        "chi_tiet": noi_dung_chi_tiet,
                        "link": str(link),
                        "file_nguon": fname
                    })
        except Exception:
            pass

    # Tạo giao diện HTML mobile
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tra Cứu Kết Quả - Mobile</title>
    <style>
        body {{ background-color: #121212; color: #E0E0E0; font-family: Arial, sans-serif; margin: 0; padding: 12px; font-size: 16px; }}
        h1 {{ color: #00FFC8; font-size: 20px; text-align: center; margin-bottom: 5px; }}
        .sub-header {{ font-size: 13px; color: #888; text-align: center; margin-bottom: 15px; }}
        .search-box {{ width: 100%; padding: 14px; font-size: 16px; border-radius: 8px; border: 1px solid #444; background-color: #1E1E1E; color: #FFF; box-sizing: border-box; margin-bottom: 15px; }}
        .card {{ background-color: #1E1E2E; border-left: 6px solid #00FFC8; border-radius: 8px; padding: 14px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
        .card-title {{ font-weight: bold; color: #FFD700; font-size: 17px; }}
        .card-time {{ background-color: #FF9800; color: #000; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 13px; }}
        .card-body {{ color: #DDD; margin-top: 6px; font-size: 14px; line-height: 1.5; word-break: break-word; }}
        .card-source {{ font-size: 12px; color: #777; margin-top: 8px; }}
        .link-btn {{ display: inline-block; margin-top: 10px; padding: 10px 16px; background-color: #FF0000; color: #FFFFFF; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>📊 TRA CỨU KẾT QUẢ ĐIỆN THOẠI</h1>
    <div class="sub-header">Cập nhật: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Tổng số: {len(all_results)} kết quả</div>
    <input type="text" id="searchInput" class="search-box" placeholder="🔍 Gõ tìm kiếm tên, ngày, giờ, số..." onkeyup="filterCards()">
    <div id="container">
"""

    for idx, item in enumerate(all_results, 1):
        html_content += f"""
        <div class="card">
            <div class="card-header">
                <span class="card-title">#{idx}. {item['ten']}</span>
                <span class="card-time">📅 {item['ngay']} | ⏰ {item['gio']}</span>
            </div>
            <div class="card-body">📋 {item['chi_tiet']}</div>
            <div class="card-source">📁 Tab/Nguồn: {item['file_nguon']}</div>
            {"<a class='link-btn' href='" + item['link'] + "' target='_blank'>▶ Mở & Phát YouTube</a>" if item['link'] and item['link'].startswith("http") else ""}
        </div>
"""

    html_content += """
    </div>
    <script>
        function filterCards() {
            var input = document.getElementById('searchInput').value.toLowerCase();
            var cards = document.getElementsByClassName('card');
            for (var i = 0; i < cards.length; i++) {
                var text = cards[i].innerText.toLowerCase();
                cards[i].style.display = text.includes(input) ? "" : "none";
            }
        }
    </script>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ Đã cập nhật tệp index.html đầy đủ ngày giờ và liên kết YouTube!")

if __name__ == "__main__":
    main()

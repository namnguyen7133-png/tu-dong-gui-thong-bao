import os
import json
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Quét cả thư mục gốc và thư mục KET_QUA_JSON
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
        # Bỏ qua các tệp cấu hình và chỉ số hệ thống
        if fname.startswith("config_") or fname.startswith("index_") or fname == "cau_hinh_duong_dan.json" or fname == "aggregated_output.json":
            continue
        try:
            with open(jf, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    # Quét toàn bộ các dạng khóa xuất ra từ các tệp Python con
                    for k in ["ket_qua_tong_ket", "SO_SANH", "ket_qua_1_chua_trung_lap", "people", "data", "events", "matched_results"]:
                        v = data.get(k)
                        if isinstance(v, list):
                            items.extend(v)
                        elif isinstance(v, dict):
                            for sub_k, sub_v in v.items():
                                if isinstance(sub_v, list):
                                    items.extend(sub_v)

                for item in items:
                    if isinstance(item, dict):
                        # Trích xuất linh hoạt thông tin Giờ - Tên - Bệnh
                        ten = item.get("ten") or item.get("name") or item.get("nguoi_mat") or item.get("nguoi_song") or "Chưa rõ tên"
                        gio = item.get("gio_su_kien") or item.get("play_time") or item.get("gio_phat") or item.get("gio_mat") or item.get("gio_sinh") or "---"
                        benh = item.get("benh") or item.get("benh_mac") or item.get("ten_benh") or item.get("thong_tin_du") or "Theo dõi sức khỏe"
                        link = item.get("link") or item.get("link_video") or item.get("url") or ""
                        
                        all_results.append({
                            "ten": ten,
                            "gio": gio,
                            "benh": benh,
                            "link": link,
                            "file_nguon": fname
                        })
        except Exception:
            pass

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
        .card-time {{ background-color: #FF9800; color: #000; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 14px; }}
        .card-body {{ color: #DDD; margin-top: 6px; font-size: 15px; }}
        .card-source {{ font-size: 12px; color: #777; margin-top: 8px; }}
        .link-btn {{ display: inline-block; margin-top: 10px; padding: 8px 14px; background-color: #0088CC; color: #FFFFFF; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>📊 TRA CỨU KẾT QUẢ ĐIỆN THOẠI</h1>
    <div class="sub-header">Cập nhật: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Tổng số: {len(all_results)} kết quả</div>
    <input type="text" id="searchInput" class="search-box" placeholder="🔍 Gõ tìm kiếm tên, mốc giờ, bệnh lý..." onkeyup="filterCards()">
    <div id="container">
"""

    for idx, item in enumerate(all_results, 1):
        html_content += f"""
        <div class="card">
            <div class="card-header">
                <span class="card-title">#{idx}. {item['ten']}</span>
                <span class="card-time">⏰ {item['gio']}</span>
            </div>
            <div class="card-body">🩺 <b>Bệnh / Thông tin:</b> {item['benh']}</div>
            <div class="card-source">📄 Nguồn: {item['file_nguon']}</div>
            {"<a class='link-btn' href='" + item['link'] + "' target='_blank'>▶ Xem Video YouTube</a>" if item['link'] and item['link'].startswith("http") else ""}
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
    print("✅ Đã cập nhật thành công index.html!")

if __name__ == "__main__":
    main()

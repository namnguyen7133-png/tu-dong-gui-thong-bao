import os
import json
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "KET_QUA_JSON")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")

def main():
    json_files = glob.glob(os.path.join(JSON_DIR, "*.json"))
    all_results = []

    for jf in json_files:
        if os.path.basename(jf).startswith("config_") or "index_" in os.path.basename(jf):
            continue
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                kq = data.get("ket_qua_tong_ket", [])
                if isinstance(kq, list):
                    all_results.extend(kq)
        except Exception as e:
            print(f"Lỗi đọc file {jf}: {e}")

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tra Cứu Kết Quả - Mobile</title>
    <style>
        body {{
            background-color: #121212;
            color: #E0E0E0;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
            font-size: 16px;
        }}
        h1 {{
            color: #00FFC8;
            font-size: 18px;
            text-align: center;
        }}
        .search-box {{
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border-radius: 6px;
            border: 1px solid #444;
            background-color: #222;
            color: #FFF;
            box-sizing: border-box;
            margin-bottom: 15px;
        }}
        .card {{
            background-color: #1E1E2E;
            border-left: 5px solid #FF9800;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 12px;
        }}
        .card-title {{
            font-weight: bold;
            color: #FFD700;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .alert {{
            color: #FF6B6B;
            font-weight: bold;
            margin-top: 5px;
            background: #2A1515;
            padding: 5px;
            border-radius: 4px;
        }}
        .link-btn {{
            display: inline-block;
            margin-top: 8px;
            padding: 8px 12px;
            background-color: #0088CC;
            color: #FFFFFF;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>📊 TRA CỨU KẾT QUẢ ĐIỆN THOẠI</h1>
    <div style="font-size: 13px; color: #888; text-align: center; margin-bottom: 10px;">
        Cập nhật: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Tổng số: {len(all_results)} kết quả
    </div>

    <input type="text" id="searchInput" class="search-box" placeholder="🔍 Gõ tìm kiếm tên, bệnh lý..." onkeyup="filterCards()">

    <div id="container">
"""

    for idx, item in enumerate(all_results, 1):
        ten = item.get("ten", "Không rõ")
        tab = item.get("tab", "N/A")
        chi_so = item.get("chi_so", "")
        goc = item.get("gia_tri_goc", "")
        phan_nguyen = item.get("phan_nguyen", "")
        mod_1000_nguyen = item.get("mod_1000_nguyen", "")
        thong_tin_du = item.get("thong_tin_du", "")
        canh_bao_col = item.get("canh_bao_col", "")
        link_video = item.get("link_video", "")

        html_content += f"""
        <div class="card">
            <div class="card-title">#{idx} [{tab}] {ten}</div>
            <div>• Chỉ số: {chi_so} (Gốc: {goc})</div>
            <div>• Nguyên: {phan_nguyen} (%1000 = {mod_1000_nguyen})</div>
            <div>• {thong_tin_du}</div>
            <div class="alert">⚠️ {canh_bao_col}</div>
            {"<a class='link-btn' href='" + link_video + "' target='_blank'>▶ Xem Video YouTube</a>" if link_video and link_video != "Không có link" else ""}
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
    print("✅ Đã tạo thành công index.html!")

if __name__ == "__main__":
    main()

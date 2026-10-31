# -*- coding: utf-8 -*-
import os
import sys
import glob
import json
import time
import subprocess
import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import urllib.request

# --- HẰNG SỐ VÀ CẤU HÌNH ĐỘNG (LIÊN KẾT GITHUB & LOCAL WORKSPACE) ---
TEN_SCRIPT = os.path.splitext(os.path.basename(__file__))[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GITHUB_REPO_BASE = "https://github.com/namnguyen7133-png/tu-dong-gui-thong-bao/tree/main"
CONFIG_FILE = os.path.join(BASE_DIR, f"config_{TEN_SCRIPT}.json")
INDEX_FILE = os.path.join(BASE_DIR, f"index_{TEN_SCRIPT}_quan_ly.json")

DEFAULT_DIR = os.path.join(BASE_DIR, "KET_QUA_JSON")
GITHUB_DEFAULT_DIR_URL = f"{GITHUB_REPO_BASE}/KET_QUA_JSON"

# Dữ liệu cung hoàng đạo, thời gian, món ăn và món uống
ZODIAC_DATA = [
    {
        "name": "Bạch Dương",
        "start": (3, 21),
        "end": (4, 19),
        "food": "Món nướng BBQ bốc lửa, vị cay nồng",
        "drink": "Bia tươi lạnh sâu / Nước ép táo gừng",
        "element": "Hỏa",
    },
    {
        "name": "Kim Ngưu",
        "start": (4, 20),
        "end": (5, 20),
        "food": "Bít tết bò Mỹ sốt nấm kiểu Âu sang trọng",
        "drink": "Rượu vang đỏ / Mocktail trái cây đậm vị",
        "element": "Thổ",
    },
    {
        "name": "Song Tử",
        "start": (5, 21),
        "end": (6, 21),
        "food": "Buffet lẩu nhiều vị, các món ăn vặt đa dạng",
        "drink": "Trà sữa trân châu / Trà trái cây nhiệt đới",
        "element": "Khí",
    },
    {
        "name": "Cự Giải",
        "start": (6, 22),
        "end": (7, 22),
        "food": "Cơm gia đình chuẩn vị cua đồng, cá kho tộ",
        "drink": "Nước sắn dây / Trà atiso thanh mát",
        "element": "Thủy",
    },
    {
        "name": "Sư Tử",
        "start": (7, 23),
        "end": (8, 22),
        "food": "Hải sản cao cấp, tôm hùm sốt bơ tỏi",
        "drink": "Rượu vang trắng / Cocktail sủi tăm sang trọng",
        "element": "Hỏa",
    },
    {
        "name": "Xử Nữ",
        "start": (8, 23),
        "end": (9, 22),
        "food": "Món ăn thực dưỡng Clean-eating, Salad ức gà",
        "drink": "Nước ép cần tây táo xanh / Detox chanh sả",
        "element": "Thổ",
    },
    {
        "name": "Thiên Bình",
        "start": (9, 23),
        "end": (10, 23),
        "food": "Mỳ Ý sốt kem, bánh ngọt bài trí tinh tế",
        "drink": "Trà Earl Grey ấm / Rượu vang hồng (Rosé)",
        "element": "Khí",
    },
    {
        "name": "Bọ Cạp",
        "start": (10, 24),
        "end": (11, 21),
        "food": "Lẩu Thái hải sản chua cay đậm vị, lẩu Tứ Xuyên",
        "drink": "Trà đào cam sả / Nước ngọt có ga lạnh",
        "element": "Thủy",
    },
    {
        "name": "Nhân Mã",
        "start": (11, 22),
        "end": (12, 21),
        "food": "Ẩm thực đường phố thế giới, Gà rán Hàn Quốc",
        "drink": "Bia trái cây / Nước mía hoặc soda chanh tươi",
        "element": "Hỏa",
    },
    {
        "name": "Ma Kết",
        "start": (12, 22),
        "end": (1, 19),
        "food": "Món hầm truyền thống, đuôi bò hầm thuốc bắc",
        "drink": "Trà thảo mộc ấm / Rượu mạnh pha nhẹ",
        "element": "Thổ",
    },
    {
        "name": "Bảo Bình",
        "start": (1, 20),
        "end": (2, 18),
        "food": "Món ăn biến tấu mới lạ, Sushi băng chuyền Nhật Bản",
        "drink": "Trà xanh gạo lứt (Genmaicha) / Sake lạnh",
        "element": "Khí",
    },
    {
        "name": "Song Ngư",
        "start": (2, 19),
        "end": (3, 20),
        "food": "Súp cá hồi, các món ăn thanh nhẹ lãng mạn",
        "drink": "Vang trắng ngọt / Trà hoa cúc mật ong ấm",
        "element": "Thủy",
    },
]

def get_zodiac(day, month):
    for z in ZODIAC_DATA:
        s_m, s_d = z["start"]
        e_m, e_d = z["end"]
        if s_m > e_m:
            if (month == s_m and day >= s_d) or (month == e_m and day <= e_d):
                return z
        else:
            if (
                (month == s_m and day >= s_d)
                or (month == e_m and day <= e_d)
                or (s_m < month < e_m)
            ):
                return z
    return ZODIAC_DATA[0]


class FullZodiacApp:
    def __init__(self, root, la_chedo_gui=True):
        self.root = root
        self.la_chedo_gui = la_chedo_gui

        self.nguoi_nha_data = []
        self.nguoi_mat_data = []
        self.video_links = []
        self.cac_file_nguon = []

        print(f"🚀 [INIT] Khởi tạo Script: {TEN_SCRIPT}.py | Chế độ GUI: {self.la_chedo_gui}")
        
        self.tai_cau_hinh_cu()

        if not self.la_chedo_gui:
            self.chay_ngam_chuoi_10_phut()
            return

        self.root.title("Hệ Thống Quản Lý Cung Hoàng Đạo & Đối Chiếu Tự Động")
        self.root.geometry("1100x700")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_chinh = ttk.Frame(self.notebook)
        self.tab_nguoinha = ttk.Frame(self.notebook)
        self.tab_nguoimat = ttk.Frame(self.notebook)
        self.tab_monan = ttk.Frame(self.notebook)
        self.tab_cantrong = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_chinh, text="Quản Lý & Thông Báo")
        self.notebook.add(self.tab_nguoinha, text="DS Người Nhà (.txt)")
        self.notebook.add(self.tab_nguoimat, text="DS Người Mất (.txt)")
        self.notebook.add(self.tab_monan, text="Món Ăn Theo Ngày Hiện Tại & Sắp Tới")
        self.notebook.add(self.tab_cantrong, text="So Sánh, Cẩn Trọng & Xuất JSON")

        self.setup_tab_chinh()
        self.setup_tab_nguoinha()
        self.setup_tab_nguoimat()
        self.setup_tab_monan()
        self.setup_tab_cantrong()

    def tai_cau_hinh_cu(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cac_file_nguon = data.get("nguon_txt", [])
            except Exception as e:
                print(f"❌ [CONFIG ERROR] {e}")

    def quet_6_thu_muc_bang(self):
        """Quét chi tiết các tệp dữ liệu từ muc_1 đến muc_6"""
        danh_sach_so = set()
        print("🔍 [QUÉT BẢNG] Đang kiểm tra các thư mục dữ liệu từ muc_1 đến muc_6...")

        for i in range(1, 7):
            duong_dan_muc = os.path.join(BASE_DIR, f"muc_{i}")
            if os.path.exists(duong_dan_muc) and os.path.isdir(duong_dan_muc):
                files = os.listdir(duong_dan_muc)
                for file in files:
                    duong_dan_file = os.path.join(duong_dan_muc, file)
                    if os.path.isfile(duong_dan_file):
                        try:
                            with open(duong_dan_file, "r", encoding="utf-8", errors="ignore") as f:
                                numbers = re.findall(r"\d+", f.read())
                                for num in numbers:
                                    danh_sach_so.add(int(num))
                        except Exception:
                            pass
        print(f"✅ [QUÉT BẢNG] Tổng số thu thập từ 6 bảng: {len(danh_sach_so)}")
        return danh_sach_so

    def chay_ngam_chuoi_10_phut(self):
        """Tự động quét tất cả các tệp .py trong repo, chạy cách nhau 10 phút và gom kết quả"""
        print("🚀 [HEADLESS / CHUỖI 10 PHÚT] Bắt đầu thực thi tuần tự các tệp Python...")
        try:
            script_hien_tai = os.path.basename(__file__)
            danh_sach_file_py = sorted([f for f in glob.glob("*.py") if f != script_hien_tai])
            print(f"📁 Tìm thấy {len(danh_sach_file_py)} tệp Python: {danh_sach_file_py}")

            lich_su_chay = []
            for i, file_py in enumerate(danh_sach_file_py):
                duong_dan_py = os.path.join(BASE_DIR, file_py)
                print(f"\n▶️ [{i+1}/{len(danh_sach_file_py)}] Đang chạy tệp: {file_py}")
                
                bat_dau = datetime.now()
                trang_thai = "Thành công"
                try:
                    subprocess.run([sys.executable, duong_dan_py], check=True, timeout=300)
                    print(f"✅ Hoàn thành: {file_py}")
                except Exception as e:
                    trang_thai = f"Lỗi: {e}"
                    print(f"❌ Lỗi khi chạy {file_py}: {e}")

                lich_su_chay.append({
                    "tep_python": file_py,
                    "trang_thai": trang_thai,
                    "thoi_gian": bat_dau.strftime("%Y-%m-%d %H:%M:%S")
                })

                if i < len(danh_sach_file_py) - 1:
                    print(f"⏳ Đang chờ đúng 10 phút (600 giây) trước khi chạy tệp tiếp theo...")
                    time.sleep(600)

            # Nạp dữ liệu bảng và THUONGLUU.txt
            so_lieu_bang = self.quet_6_thu_muc_bang()
            tep_thuong_luu = os.path.join(BASE_DIR, "THUONGLUU.txt")
            
            danh_sach_chi_tiet = []
            danh_sach_trung_khop = []

            if os.path.exists(tep_thuong_luu):
                with open(tep_thuong_luu, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 5:
                                phep_tinh = parts[0]
                                ten = parts[1].replace("Tên:", "").strip()
                                thoi_gian = parts[2].strip()
                                benh = parts[3].replace("Bệnh:", "").strip()
                                trang_thai_goc = parts[4].replace("TrạngThái:", "").strip()

                                numbers_in_calc = [int(n) for n in re.findall(r'\d+', phep_tinh)]
                                is_matched = any(num in so_lieu_bang for num in numbers_in_calc)

                                rec = {
                                    "ten": ten,
                                    "thoi_gian_chi_tiet": thoi_gian,
                                    "benh_hoac_noi_dung": benh,
                                    "phep_tinh": phep_tinh,
                                    "trang_thai_goc": trang_thai_goc,
                                    "trung_gio_phut_voi_bang": is_matched
                                }
                                danh_sach_chi_tiet.append(rec)
                                if is_matched:
                                    danh_sach_trung_khop.append(rec)

            now = datetime.now()
            ten_file_json = f"KET_QUA_TONG_HOP_{now.strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(DEFAULT_DIR, exist_ok=True)
            path_save = os.path.join(DEFAULT_DIR, ten_file_json)

            export_payload = {
                "metadata": {
                    "script_su_dung": f"{TEN_SCRIPT}.py",
                    "github_repo": GITHUB_REPO_BASE,
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "tong_so_tep_py": len(danh_sach_file_py),
                    "danh_sach_tep": danh_sach_file_py,
                    "tong_so_ban_ghi_trung": len(danh_sach_trung_khop)
                },
                "lich_su_thuc_thi_cac_tep": lich_su_chay,
                "danh_sach_trung_gio_phut_voi_bang": danh_sach_trung_khop,
                "toan_bo_du_lieu_chi_tiet": danh_sach_chi_tiet
            }

            with open(path_save, "w", encoding="utf-8") as f:
                json.dump(export_payload, f, ensure_ascii=False, indent=4)

            # Cập nhật Index Log
            index_data = {
                "script_su_dung": f"{TEN_SCRIPT}.py",
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "file_json_xuat": path_save,
                "github_file_url": f"{GITHUB_DEFAULT_DIR_URL}/{ten_file_json}"
            }
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump(index_data, f, ensure_ascii=False, indent=4)

            print(f"🎉 [HOÀN TẤT] Đã xuất JSON thành công tại: {path_save}")

        except Exception as e:
            print(f"❌ [ERROR] Lỗi chạy ngầm chuỗi 10 phút: {e}")
            sys.exit(1)

    # --- CÁC TAB GIAO DIỆN TKINTER ---
    def setup_tab_chinh(self):
        input_frame = tk.LabelFrame(self.tab_chinh, text=" Thông tin người dùng ", font=("Arial", 11, "bold"))
        input_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(input_frame, text="Họ tên:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ent_name = tk.Entry(input_frame, font=("Arial", 10), width=18)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Ngày sinh (DD/MM/YYYY):", font=("Arial", 10)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.ent_dob = tk.Entry(input_frame, font=("Arial", 10), width=12)
        self.ent_dob.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Giới tính:", font=("Arial", 10)).grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.cb_gender = ttk.Combobox(input_frame, values=["Nam", "Nữ", "Khác"], font=("Arial", 10), width=8, state="readonly")
        self.cb_gender.grid(row=0, column=5, padx=5, pady=5)
        self.cb_gender.current(0)

        btn_frame = tk.Frame(self.tab_chinh)
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="Thêm người", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=self.add_person).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Xóa đã chọn", bg="#f44336", fg="white", font=("Arial", 9, "bold"), command=self.delete_person).pack(side="left", padx=3)

        table_frame = tk.Frame(self.tab_chinh)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Name", "Gender", "DOB", "Zodiac", "Food", "Drink", "Status/Alert")
        self.tree_chinh = ttk.Treeview(table_frame, columns=columns, show="headings")
        headers = ["Họ tên", "Giới tính", "Ngày sinh", "Cung", "Món ăn gợi ý", "Món uống đi kèm", "Trạng thái / Thông báo"]
        widths = [120, 70, 90, 100, 180, 180, 170]

        for col, head, width in zip(columns, headers, widths):
            self.tree_chinh.heading(col, text=head)
            self.tree_chinh.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_chinh.yview)
        self.tree_chinh.configure(yscrollcommand=scrollbar.set)
        self.tree_chinh.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_tab_nguoinha(self):
        self.tree_nguoinha = ttk.Treeview(self.tab_nguoinha, columns=("Name", "DOB", "Hour", "Gender", "Zodiac"), show="headings")
        for col, head, w in zip(("Name", "DOB", "Hour", "Gender", "Zodiac"), ["Họ Tên", "Ngày Sinh", "Giờ Sinh", "Giới Tính", "Cung Sinh"], [200, 120, 100, 120, 150]):
            self.tree_nguoinha.heading(col, text=head)
            self.tree_nguoinha.column(col, width=w, anchor="w")
        self.tree_nguoinha.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    def setup_tab_nguoimat(self):
        self.tree_nguoimat = ttk.Treeview(self.tab_nguoimat, columns=("Name", "DOB", "DOD", "DOD_Hour", "Z_Birth", "Z_Death"), show="headings")
        for col, head, w in zip(("Name", "DOB", "DOD", "DOD_Hour", "Z_Birth", "Z_Death"), ["Họ Tên", "Ngày Sinh", "Ngày Mất", "Giờ Mất", "Cung Sinh", "Cung Mất"], [180, 110, 110, 90, 130, 130]):
            self.tree_nguoimat.heading(col, text=head)
            self.tree_nguoimat.column(col, width=w, anchor="w")
        self.tree_nguoimat.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    def setup_tab_monan(self):
        self.tree_monan = ttk.Treeview(self.tab_monan, columns=("Zodiac", "Period", "Food", "Drink", "Element"), show="headings")
        for col, head, w in zip(("Zodiac", "Period", "Food", "Drink", "Element"), ["Cung Hoàng Đạo", "Trạng Thái", "Món Ăn", "Thức Uống", "Nguyên Tố"], [150, 180, 250, 250, 100]):
            self.tree_monan.heading(col, text=head)
            self.tree_monan.column(col, width=w, anchor="w")
        self.tree_monan.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    def setup_tab_cantrong(self):
        self.tree_cantrong = ttk.Treeview(self.tab_cantrong, columns=("Name", "Zodiac", "Element", "Warning", "VideoTime", "Link"), show="headings")
        for col, head, w in zip(("Name", "Zodiac", "Element", "Warning", "VideoTime", "Link"), ["Họ Tên", "Cung", "Nguyên Tố", "Cẩn Trọng", "Giờ Phát", "Link"], [150, 100, 90, 300, 100, 200]):
            self.tree_cantrong.heading(col, text=head)
            self.tree_cantrong.column(col, width=w, anchor="w")
        self.tree_cantrong.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    def insert_to_table_chinh(self, name, gender, dob_str):
        try:
            dob = datetime.strptime(dob_str.strip(), "%d/%m/%Y")
        except ValueError:
            return False
        zodiac = get_zodiac(dob.day, dob.month)
        self.tree_chinh.insert("", "end", values=(name, gender, dob_str, zodiac["name"], zodiac["food"], zodiac["drink"], "Bình thường"))
        return True

    def add_person(self):
        name = self.ent_name.get().strip()
        dob_str = self.ent_dob.get().strip()
        gender = self.cb_gender.get()
        if not name or not dob_str:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ họ tên và ngày sinh!")
            return
        if not self.insert_to_table_chinh(name, gender, dob_str):
            messagebox.showerror("Lỗi", "Định dạng ngày sinh phải là DD/MM/YYYY")
            return
        self.ent_name.delete(0, tk.END)
        self.ent_dob.delete(0, tk.END)

    def delete_person(self):
        for item in self.tree_chinh.selection():
            self.tree_chinh.delete(item)


if __name__ == "__main__":
    che_do_gui = "--gui" in sys.argv
    if che_do_gui:
        root = tk.Tk()
        app = FullZodiacApp(root, la_chedo_gui=True)
        root.mainloop()
    else:
        root = tk.Tk()
        root.withdraw()
        FullZodiacApp(root, la_chedo_gui=False)

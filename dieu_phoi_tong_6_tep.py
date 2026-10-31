# -*- coding: utf-8 -*-
# ============================================================
# BỘ ĐIỀU PHỐI TỰ ĐỘNG TOÀN BỘ TỆP PYTHON TRONG REPO (CÁCH 10 PHÚT/TỆP)
# ============================================================

import os
import sys
import glob
import json
import time
import subprocess
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 1. Định danh động theo tên tệp Python hiện tại
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Thư mục lưu kết quả chuẩn trên GitHub / Local
THU_MUC_MAC_DINH = os.path.join(BASE_DIR, "KET_QUA_JSON")
CONFIG_FILE = os.path.join(BASE_DIR, f"config_{SCRIPT_NAME}.json")

class QuanLyVaGieuPhoiFullApp:
    def __init__(self, root, headless=False):
        self.root = root
        self.config = self.load_config()
        self.thu_muc_luu_hien_tai = self.config.get("thu_muc_luu", THU_MUC_MAC_DINH)
        self.template_txt_file = os.path.join(self.thu_muc_luu_hien_tai, f"template_lich_su_{SCRIPT_NAME}.txt")
        self.thuong_luu_txt_file = os.path.join(self.thu_muc_luu_hien_tai, "THUONGLUU.txt")
        self.benh_tat_txt_file = os.path.join(self.thu_muc_luu_hien_tai, "danh_sach_benh.txt")
        self.source_dir_name = os.path.basename(BASE_DIR) or "ThuMucGoc"

        if headless:
            self.run_background_task_voi_chuoi_10_phut()
            return

        self.root.title(f"Hệ Thống Điều Phối & Quản Lý Toàn Bộ Tệp Python ({SCRIPT_NAME}.py)")
        self.root.geometry("1150x900")
        self.setup_ui()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "script_su_dung": SCRIPT_NAME,
            "thu_muc_luu": THU_MUC_MAC_DINH,
        }

    def save_config(self, thu_muc_luu):
        try:
            data = {
                "script_su_dung": SCRIPT_NAME,
                "thu_muc_luu": thu_muc_luu,
                "cap_nhat_moi_nhat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi lưu cấu hình: {e}")

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_main = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_main, text=" 📊 Quản Lý & Lịch Sử ")
        self.setup_tab_main()

        self.tab_calc = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_calc, text=" 📝 Tính Toán & Lưu Trữ THUONGLUU ")
        self.setup_tab_calc()

        self.load_data_to_table()
        self.load_thuongluu_data_to_table()

    def setup_tab_main(self):
        frame_nhap = tk.LabelFrame(self.tab_main, text=" 1. Bộ Lọc, Tìm Kiếm & Thư Mục ", font=("Arial", 10, "bold"))
        frame_nhap.pack(fill="x", padx=10, pady=10, ipady=5)

        tk.Label(frame_nhap, text="Thư mục lưu JSON:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lbl_thumuc = tk.Label(frame_nhap, text=self.thu_muc_luu_hien_tai, fg="blue", font=("Arial", 9))
        self.lbl_thumuc.grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        tk.Button(frame_nhap, text="📁 Đổi Thư Mục Lưu", bg="#607D8B", fg="white", command=self.chon_thu_muc_luu).grid(row=0, column=4, padx=5, pady=5)

        tk.Label(frame_nhap, text="Tìm kiếm tên:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_tim_kiem_ten = tk.Entry(frame_nhap, width=30)
        self.ent_tim_kiem_ten.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.ent_tim_kiem_ten.bind("<KeyRelease>", lambda e: self.filter_table())

        labels = ["Năm", "Quý", "Tháng", "Tuần", "Ngày", "Giờ", "Phút"]
        self.time_entries = {}
        now = datetime.now()
        defaults = [now.year, (now.month - 1) // 3 + 1, now.month, now.isocalendar()[1], now.day, now.hour, now.minute]

        for i, lbl in enumerate(labels):
            r = 2 if i < 4 else 3
            c = (i % 4) * 2
            tk.Label(frame_nhap, text=f"{lbl}:").grid(row=r, column=c, sticky="e", padx=2, pady=2)
            ent = tk.Entry(frame_nhap, width=8)
            ent.insert(0, str(defaults[i]))
            ent.grid(row=r, column=c+1, sticky="w", padx=2, pady=2)
            self.time_entries[lbl.lower()] = ent

        tk.Label(frame_nhap, text="Bệnh bị mắc:", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.ent_benh = tk.Entry(frame_nhap, width=40)
        self.ent_benh.grid(row=4, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        frame_btn = tk.Frame(self.tab_main)
        frame_btn.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_btn, text="💾 Lưu Lịch Sử Vào Tệp Mẫu TXT", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), command=self.luu_vao_file_txt).pack(side="left", padx=5)
        tk.Button(frame_btn, text="🚀 Chạy Toàn Bộ Chuỗi Python (10 Phút/Tệp)", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=lambda: self.run_background_task_voi_chuoi_10_phut()).pack(side="left", padx=5)

        frame_table = tk.LabelFrame(self.tab_main, text=" 2. Bảng Lịch Sử & Kết Quả Tra Cứu ", font=("Arial", 10, "bold"))
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(frame_table, columns=("Ten", "ThoiGian", "BenhLy"), show="headings")
        self.tree.heading("Ten", text="Tên Nhân Sự / Đối Tượng")
        self.tree.heading("ThoiGian", text="Thời Gian (Năm/Quý/Tháng/Tuần/Ngày/Giờ/Phút)")
        self.tree.heading("BenhLy", text="Bệnh Bị Mắc / Nội Dung")

        self.tree.column("Ten", width=180, anchor="w")
        self.tree.column("ThoiGian", width=350, anchor="w")
        self.tree.column("BenhLy", width=250, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scroll = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

    def setup_tab_calc(self):
        frame_top = tk.LabelFrame(self.tab_calc, text=" Nhập Liệu Thời Gian, Tên & Bệnh Tật ", font=("Arial", 10, "bold"))
        frame_top.pack(fill="x", padx=10, pady=10, ipady=5)

        tk.Label(frame_top, text="Giờ (1-1440):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ent_gio = tk.Entry(frame_top, width=10)
        self.ent_gio.insert(0, "1")
        self.ent_gio.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Phút:", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.ent_phut = tk.Entry(frame_top, width=10)
        self.ent_phut.insert(0, datetime.now().strftime("%M"))
        self.ent_phut.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Ngày:", font=("Arial", 9, "bold")).grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.ent_ngay = tk.Entry(frame_top, width=10)
        self.ent_ngay.insert(0, datetime.now().strftime("%d"))
        self.ent_ngay.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Tháng:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ent_thang = tk.Entry(frame_top, width=10)
        self.ent_thang.insert(0, datetime.now().strftime("%m"))
        self.ent_thang.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Năm sinh:", font=("Arial", 9, "bold")).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.ent_nam = tk.Entry(frame_top, width=10)
        self.ent_nam.insert(0, "2000")
        self.ent_nam.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        tk.Label(frame_top, text="Chọn Tên:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.combo_ten = ttk.Combobox(frame_top, width=28, state="readonly")
        self.combo_ten.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.cap_nhat_danh_sach_tab1()

        tk.Label(frame_top, text="Bệnh Tật (TXT):", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.combo_benh = ttk.Combobox(frame_top, width=28)
        self.combo_benh.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.cap_nhat_danh_sach_benh()

        tk.Button(frame_top, text="💾 Lưu Lại Vào THUONGLUU.txt", bg="#FF5722", fg="white", font=("Arial", 10, "bold"), command=self.xu_ly_va_luu_thuongluu).grid(row=4, column=1, columnspan=3, pady=10, sticky="w")

        frame_tbl_thuongluu = tk.LabelFrame(self.tab_calc, text=" Dữ liệu trong THUONGLUU.txt ", font=("Arial", 10, "bold"))
        frame_tbl_thuongluu.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_thuongluu = ttk.Treeview(frame_tbl_thuongluu, columns=("Col1", "Col2", "Col3", "Col4", "Col5"), show="headings")
        self.tree_thuongluu.heading("Col1", text="Cột 1 (Thương tính toán)")
        self.tree_thuongluu.heading("Col2", text="Tên")
        self.tree_thuongluu.heading("Col3", text="Thời Gian Nhập")
        self.tree_thuongluu.heading("Col4", text="Bệnh Tật")
        self.tree_thuongluu.heading("Col5", text="Trạng thái lọc")

        self.tree_thuongluu.column("Col1", width=220, anchor="w")
        self.tree_thuongluu.column("Col2", width=180, anchor="w")
        self.tree_thuongluu.column("Col3", width=200, anchor="w")
        self.tree_thuongluu.column("Col4", width=200, anchor="w")
        self.tree_thuongluu.column("Col5", width=250, anchor="w")
        self.tree_thuongluu.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scroll_tl = ttk.Scrollbar(frame_tbl_thuongluu, orient="vertical", command=self.tree_thuongluu.yview)
        scroll_tl.pack(side="right", fill="y")
        self.tree_thuongluu.configure(yscrollcommand=scroll_tl.set)

    def cap_nhat_danh_sach_tab1(self):
        danh_sach_ten = []
        if os.path.exists(self.template_txt_file):
            try:
                with open(self.template_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 3:
                                ten = parts[0].replace("Tên:", "").strip()
                                if ten and ten not in danh_sach_ten:
                                    danh_sach_ten.append(ten)
            except Exception:
                pass
        if not danh_sach_ten:
            danh_sach_ten = ["Khuyết Danh"]
        self.combo_ten['values'] = danh_sach_ten
        self.combo_ten.current(0)

    def cap_nhat_danh_sach_benh(self):
        danh_sach_b = []
        if os.path.exists(self.benh_tat_txt_file):
            try:
                with open(self.benh_tat_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        b = line.strip()
                        if b and b not in danh_sach_b:
                            danh_sach_b.append(b)
            except Exception:
                pass
        if not danh_sach_b:
            danh_sach_b = ["Cảm cúm", "Đau đầu", "Đau bụng", "Huyết áp"]
        self.combo_benh['values'] = danh_sach_b
        if danh_sach_b:
            self.combo_benh.set(danh_sach_b[0])

    def lay_so_lieu_tu_6_bang(self):
        danh_sach_so = set()
        for i in range(1, 7):
            duong_dan_muc = os.path.join(BASE_DIR, f"muc_{i}")
            if os.path.exists(duong_dan_muc) and os.path.isdir(duong_dan_muc):
                for file in os.listdir(duong_dan_muc):
                    duong_dan_file = os.path.join(duong_dan_muc, file)
                    if os.path.isfile(duong_dan_file):
                        try:
                            with open(duong_dan_file, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                                import re
                                numbers = re.findall(r'\d+', content)
                                for num in numbers:
                                    danh_sach_so.add(int(num))
                        except Exception:
                            pass
        return danh_sach_so

    def xu_ly_va_luu_thuongluu(self):
        ten_chon = self.combo_ten.get().strip()
        benh_chon = self.combo_benh.get().strip()
        if not benh_chon:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hoặc nhập tên bệnh tật!")
            return

        try:
            gio_val = int(self.ent_gio.get().strip())
            phut_val = int(self.ent_phut.get().strip())
            ngay_val = int(self.ent_ngay.get().strip())
            thang_val = int(self.ent_thang.get().strip())
            nam_val = int(self.ent_nam.get().strip())
            
            now = datetime.now()
            dt_sinh = datetime(nam_val, thang_val, ngay_val)
            chenh_lech_ngay = abs((now - dt_sinh).days)

            thuong_nhan_24 = chenh_lech_ngay * 24
            phan_nguyen = thuong_nhan_24 // gio_val if gio_val > 0 else 0
            phan_du = thuong_nhan_24 % gio_val if gio_val > 0 else 0

            du_nguyen = phan_nguyen % 1000
            du_du = phan_du % 1000

            cac_so_co_san = self.lay_so_lieu_tu_6_bang()
            ket_qua_loc = []
            for val in [du_nguyen, du_du]:
                if val in cac_so_co_san:
                    ket_qua_loc.append(f"Trùng ({val}) -> Bỏ")
                else:
                    ket_qua_loc.append(f"Mới ({val}) -> Giữ")

            trang_thai_str = " | ".join(ket_qua_loc)
            cot_1_val = f"Thương: {thuong_nhan_24} | Nguyên:{phan_nguyen}(%{1000}={du_nguyen}) | Dư:{phan_du}(%{1000}={du_du})"
            thoi_gian_nhap_str = f"Ngày {ngay_val}/{thang_val}/{nam_val} - Giờ {gio_val}:{phut_val}"

            dong_ghi = f"{cot_1_val} | Tên:{ten_chon} | {thoi_gian_nhap_str} | Bệnh:{benh_chon} | TrạngThái:{trang_thai_str}\n"

            os.makedirs(os.path.dirname(self.thuong_luu_txt_file), exist_ok=True)
            with open(self.thuong_luu_txt_file, "a", encoding="utf-8") as f:
                f.write(dong_ghi)

            messagebox.showinfo("Thành công", "Đã lưu thành công vào THUONGLUU.txt!")
            self.load_thuongluu_data_to_table()
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def load_thuongluu_data_to_table(self):
        for item in self.tree_thuongluu.get_children():
            self.tree_thuongluu.delete(item)
        if os.path.exists(self.thuong_luu_txt_file):
            try:
                with open(self.thuong_luu_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 5:
                                self.tree_thuongluu.insert("", "end", values=(parts[0], parts[1].replace("Tên:", ""), parts[2], parts[3].replace("Bệnh:", ""), parts[4].replace("TrạngThái:", "")))
            except Exception:
                pass

    def chon_thu_muc_luu(self):
        thu_muc_chon = filedialog.askdirectory(title="Chọn thư mục lưu tệp JSON", initialdir=self.thu_muc_luu_hien_tai)
        if thu_muc_chon:
            self.thu_muc_luu_hien_tai = thu_muc_chon
            self.lbl_thumuc.config(text=thu_muc_chon)
            self.template_txt_file = os.path.join(thu_muc_chon, f"template_lich_su_{SCRIPT_NAME}.txt")
            self.thuong_luu_txt_file = os.path.join(thu_muc_chon, "THUONGLUU.txt")
            self.benh_tat_txt_file = os.path.join(thu_muc_chon, "danh_sach_benh.txt")
            self.save_config(thu_muc_chon)
            messagebox.showinfo("Thành công", "Đã đổi thư mục lưu đích!")
            self.load_data_to_table()
            self.load_thuongluu_data_to_table()

    def luu_vao_file_txt(self):
        ten_tk = self.ent_tim_kiem_ten.get().strip() or "Khuyết Danh"
        t_vals = [self.time_entries[k].get().strip() for k in ["năm", "quý", "tháng", "tuần", "ngày", "giờ", "phút"]]
        time_str = f"Năm:{t_vals[0]} | Quý:{t_vals[1]} | Tháng:{t_vals[2]} | Tuần:{t_vals[3]} | Ngày:{t_vals[4]} | Giờ:{t_vals[5]} | Phút:{t_vals[6]}"
        benh = self.ent_benh.get().strip()
        if not benh:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập thông tin bệnh bị mắc!")
            return

        dong_du_lieu = f"Tên:{ten_tk} | {time_str} | Bệnh:{benh}\n"
        try:
            os.makedirs(os.path.dirname(self.template_txt_file), exist_ok=True)
            with open(self.template_txt_file, "a", encoding="utf-8") as f:
                f.write(dong_du_lieu)
            messagebox.showinfo("Thành công", "Đã lưu lịch sử mẫu!")
            self.load_data_to_table()
            self.cap_nhat_danh_sach_tab1()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ghi tệp: {e}")

    def load_data_to_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if os.path.exists(self.template_txt_file):
            try:
                with open(self.template_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 3:
                                self.tree.insert("", "end", values=(parts[0].replace("Tên:", ""), " | ".join(parts[1:-1]), parts[-1].replace("Bệnh:", "")))
            except Exception:
                pass

    def filter_table(self):
        keyword = self.ent_tim_kiem_ten.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        if os.path.exists(self.template_txt_file):
            try:
                with open(self.template_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 3:
                                ten_val = parts[0].replace("Tên:", "")
                                if keyword in ten_val.lower() or not keyword:
                                    self.tree.insert("", "end", values=(ten_val, " | ".join(parts[1:-1]), parts[-1].replace("Bệnh:", "")))
            except Exception:
                pass

    def run_background_task_voi_chuoi_10_phut(self):
        """Tự động quét tất cả các tệp .py trong repo, chạy tuần tự, chờ 10 phút mỗi tệp và gom toàn bộ kết quả chi tiết"""
        try:
            print("🚀 [CHUỖI TỰ ĐỘNG] Bắt đầu quét toàn bộ tệp Python trong repo...")
            thu_muc_luu = self.thu_muc_luu_hien_tai
            os.makedirs(thu_muc_luu, exist_ok=True)
            self.save_config(thu_muc_luu)

            # 1. Tự động quét toàn bộ tệp .py trong thư mục gốc (trừ file script hiện tại)
            script_hien_tai = os.path.basename(__file__)
            danh_sach_file_py = sorted([f for f in glob.glob("*.py") if f != script_hien_tai])
            print(f"📁 Tìm thấy {len(danh_sach_file_py)} tệp Python cần chạy: {danh_sach_file_py}")

            ket_qua_thuc_thi_cac_file = []

            # 2. Vòng lặp chạy lần lượt từng tệp Python, chờ 10 phút (600 giây) giữa các tệp
            for i, file_py in enumerate(danh_sach_file_py):
                duong_dan_py = os.path.join(BASE_DIR, file_py)
                print(f"\n▶️ [{i+1}/{len(danh_sach_file_py)}] Đang chạy tệp: {file_py}")
                
                start_time = datetime.now()
                status_thuchien = "Thành công"
                try:
                    # Chạy tệp .py ngầm và chờ tối đa 5 phút cho mỗi tệp con
                    subprocess.run([sys.executable, duong_dan_py], check=True, timeout=300)
                    print(f"✅ Hoàn thành tệp: {file_py}")
                except Exception as e:
                    status_thuchien = f"Lỗi: {e}"
                    print(f"❌ Lỗi khi chạy tệp {file_py}: {e}")

                ket_qua_thuc_thi_cac_file.append({
                    "ten_tep": file_py,
                    "trang_thai": status_thuchien,
                    "thoi_gian_chay": start_time.strftime("%Y-%m-%d %H:%M:%S")
                })

                # Nếu chưa phải tệp cuối cùng, tiến hành chờ đúng 10 phút (600 giây)
                if i < len(danh_sach_file_py) - 1:
                    print(f"⏳ Đang chờ 10 phút (600 giây) trước khi chuyển sang tệp Python tiếp theo...")
                    time.sleep(600)

            # 3. Thu thập toàn bộ dữ liệu từ THUONGLUU.txt và template để đóng gói JSON đầy đủ
            now = datetime.now()
            thoi_gian_str = now.strftime("%Y%m%d_%H%M%S")
            default_output_filename = f"TONG_HOP_TOAN_BO_REPO_{thoi_gian_str}.json"

            thuongluu_records = []
            if os.path.exists(self.thuong_luu_txt_file):
                with open(self.thuong_luu_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 5:
                                thuongluu_records.append({
                                    "chi_tiet_tinh_toan": parts[0],
                                    "ten": parts[1].replace("Tên:", ""),
                                    "thoi_gian_nhap": parts[2],
                                    "benh_mac": parts[3].replace("Bệnh:", ""),
                                    "trang_thai_loc": parts[4].replace("TrạngThái:", "")
                                })

            # 4. Đóng gói toàn bộ payload JSON đầy đủ thông tin chi tiết
            payload = {
                "metadata": {
                    "script_dieu_phoi": f"{SCRIPT_NAME}.py",
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "tong_so_tep_python_da_chay": len(danh_sach_file_py),
                    "danh_sach_tep_python": danh_sach_file_py
                },
                "lich_su_thuc_thi_cac_tep": ket_qua_thuc_thi_cac_file,
                "chi_tiet_du_lieu_thuong_luu_va_trung_khop": thuongluu_records
            }

            out_path = os.path.join(thu_muc_luu, default_output_filename)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
            print(f"🎉 [HOÀN TẤT] Đã xuất tệp JSON tổng hợp đầy đủ thông tin tại: {out_path}")

        except Exception as e:
            print(f"❌ Lỗi nghiêm trọng khi chạy chuỗi tự động: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--gui":
        root = tk.Tk()
        app = QuanLyVaGieuPhoiFullApp(root, headless=False)
        root.mainloop()
    else:
        QuanLyVaGieuPhoiFullApp(None, headless=True)

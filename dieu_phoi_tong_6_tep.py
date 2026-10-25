from datetime import datetime, timedelta
import json
import os
import subprocess
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# 1. Định danh động theo tên tệp Python hiện tại
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🎯 Cấu hình đường dẫn chuẩn trên mây GitHub
THU_MUC_MAC_DINH = os.path.join(BASE_DIR, "KET_QUA_JSON")
CONFIG_FILE = os.path.join(BASE_DIR, f"config_{SCRIPT_NAME}.json")
DAYS_TO_KEEP = 7
# Vì các mục trên GitHub của anh đặt tên là muc_1, muc_2... nên ta quét trực tiếp tại thư mục gốc (hoặc anh có thể tùy chỉnh)
THU_MUC_NGUON_CHUAN = BASE_DIR


class QuanLyVaGieuPhoiFullApp:

    def __init__(self, root, headless=False):
        self.root = root
        self.config = self.load_config()
        self.thu_muc_luu_hien_tai = self.config.get(
            "thu_muc_luu", THU_MUC_MAC_DINH
        )
        self.template_txt_file = os.path.join(
            self.thu_muc_luu_hien_tai, f"template_lich_su_{SCRIPT_NAME}.txt"
        )
        self.index_file_dynamic = os.path.join(
            self.thu_muc_luu_hien_tai, f"index_{SCRIPT_NAME}_quan_ly.json"
        )

        if headless:
            self.run_background_task(is_headless=True)
            return

        self.root.title(
            f"Hệ Thống Điều Phối Các Mục & Quản Lý Tra Cứu ({SCRIPT_NAME}.py)"
        )
        self.root.geometry("1000x750")

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
            "thu_muc_nguon_tep": THU_MUC_NGUON_CHUAN,
        }

    def save_config(self, thu_muc_luu):
        try:
            data = {
                "script_su_dung": SCRIPT_NAME,
                "thu_muc_luu": thu_muc_luu,
                "thu_muc_nguon_tep": THU_MUC_NGUON_CHUAN,
                "cap_nhat_moi_nhat": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi lưu cấu hình: {e}")

    def setup_ui(self):
        frame_nhap = tk.LabelFrame(
            self.root,
            text=(
                " Bộ Lọc, Tìm Kiếm Tên, Thời Gian, Bệnh Lý & Chọn Thư Mục Lưu "
            ),
            font=("Arial", 10, "bold"),
        )
        frame_nhap.pack(fill="x", padx=10, pady=10, ipady=5)

        tk.Label(
            frame_nhap, text="Thư mục lưu JSON:", font=("Arial", 9, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lbl_thumuc = tk.Label(
            frame_nhap, text=self.thu_muc_luu_hien_tai, fg="blue", font=("Arial", 9)
        )
        self.lbl_thumuc.grid(
            row=0, column=1, columnspan=3, sticky="w", padx=5, pady=5
        )
        tk.Button(
            frame_nhap,
            text="📁 Đổi Thư Mục Lưu",
            bg="#607D8B",
            fg="white",
            command=self.chon_thu_muc_luu,
        ).grid(row=0, column=4, padx=5, pady=5)

        tk.Label(
            frame_nhap, text="Tìm kiếm tên:", font=("Arial", 9, "bold")
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_tim_kiem_ten = tk.Entry(frame_nhap, width=30)
        self.ent_tim_kiem_ten.grid(
            row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5
        )
        self.ent_tim_kiem_ten.bind("<KeyRelease>", lambda e: self.filter_table())

        tk.Button(
            frame_nhap,
            text="🔍 Lọc Tên",
            bg="#FF9800",
            fg="white",
            command=self.filter_table,
        ).grid(row=1, column=4, padx=5, pady=5)

        tk.Label(frame_nhap, text="Năm:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.ent_nam = tk.Entry(frame_nhap, width=10)
        self.ent_nam.insert(0, str(datetime.now().year))
        self.ent_nam.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame_nhap, text="Quý:").grid(
            row=2, column=2, sticky="w", padx=5, pady=5
        )
        self.ent_quy = tk.Entry(frame_nhap, width=8)
        self.ent_quy.insert(0, str((datetime.now().month - 1) // 3 + 1))
        self.ent_quy.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        tk.Label(frame_nhap, text="Tháng:").grid(
            row=2, column=4, sticky="w", padx=5, pady=5
        )
        self.ent_thang = tk.Entry(frame_nhap, width=8)
        self.ent_thang.insert(0, str(datetime.now().month))
        self.ent_thang.grid(row=2, column=5, sticky="w", padx=5, pady=5)

        tk.Label(frame_nhap, text="Tuần:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.ent_tuan = tk.Entry(frame_nhap, width=10)
        self.ent_tuan.insert(0, str(datetime.now().isocalendar()[1]))
        self.ent_tuan.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame_nhap, text="Ngày:").grid(
            row=3, column=2, sticky="w", padx=5, pady=5
        )
        self.ent_ngay = tk.Entry(frame_nhap, width=8)
        self.ent_ngay.insert(0, str(datetime.now().day))
        self.ent_ngay.grid(row=3, column=3, sticky="w", padx=5, pady=5)

        tk.Label(frame_nhap, text="Giờ:").grid(
            row=3, column=4, sticky="w", padx=5, pady=5
        )
        self.ent_gio = tk.Entry(frame_nhap, width=8)
        self.ent_gio.insert(0, str(datetime.now().hour))
        self.ent_gio.grid(row=3, column=5, sticky="w", padx=5, pady=5)

        tk.Label(frame_nhap, text="Phút:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.ent_phut = tk.Entry(frame_nhap, width=10)
        self.ent_phut.insert(0, str(datetime.now().minute))
        self.ent_phut.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            frame_nhap, text="Bệnh bị mắc:", font=("Arial", 9, "bold")
        ).grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.ent_benh = tk.Entry(frame_nhap, width=40)
        self.ent_benh.grid(
            row=5, column=1, columnspan=4, sticky="w", padx=5, pady=5
        )

        frame_btn = tk.Frame(self.root)
        frame_btn.pack(fill="x", padx=10, pady=5)

        tk.Button(
            frame_btn,
            text="💾 Lưu Lịch Sử Vào Tệp Mẫu TXT",
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold"),
            command=self.luu_vao_file_txt,
        ).pack(side="left", padx=5)

        tk.Button(
            frame_btn,
            text="🚀 Chạy Quét Các Mục & Xuất JSON",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            command=lambda: self.run_background_task(is_headless=False),
        ).pack(side="left", padx=5)

        frame_table = tk.LabelFrame(
            self.root,
            text=" Bảng Mẫu Gõ Tìm & Lịch Sử Đã Lưu ",
            font=("Arial", 10, "bold"),
        )
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            frame_table, columns=("Ten", "ThoiGian", "BenhLy"), show="headings"
        )
        self.tree.heading("Ten", text="Tên Nhân Sự / Đối Tượng")
        self.tree.heading("ThoiGian", text="Thời Gian (Năm/Quý/Tháng/Tuần/Ngày/Giờ/Phút)")
        self.tree.heading("BenhLy", text="Bệnh Bị Mắc")

        self.tree.column("Ten", width=180, anchor="w")
        self.tree.column("ThoiGian", width=350, anchor="w")
        self.tree.column("BenhLy", width=250, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scroll = ttk.Scrollbar(
            frame_table, orient="vertical", command=self.tree.yview
        )
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        self.load_data_to_table()

    def chon_thu_muc_luu(self):
        thu_muc_chon = filedialog.askdirectory(
            title="Chọn thư mục lưu tệp JSON", initialdir=self.thu_muc_luu_hien_tai
        )
        if thu_muc_chon:
            self.thu_muc_luu_hien_tai = thu_muc_chon
            self.lbl_thumuc.config(text=thu_muc_chon)
            self.template_txt_file = os.path.join(
                thu_muc_chon, f"template_lich_su_{SCRIPT_NAME}.txt"
            )
            self.index_file_dynamic = os.path.join(
                thu_muc_chon, f"index_{SCRIPT_NAME}_quan_ly.json"
            )
            self.save_config(thu_muc_chon)
            messagebox.showinfo(
                "Thành công", f"Đã đổi thư mục lưu đích thành:\n{thu_muc_chon}"
            )
            self.load_data_to_table()

    def luu_vao_file_txt(self):
        ten_tk = self.ent_tim_kiem_ten.get().strip() or "Khuyết Danh"
        nam = self.ent_nam.get().strip()
        quy = self.ent_quy.get().strip()
        thang = self.ent_thang.get().strip()
        tuan = self.ent_tuan.get().strip()
        ngay = self.ent_ngay.get().strip()
        gio = self.ent_gio.get().strip()
        phut = self.ent_phut.get().strip()
        benh = self.ent_benh.get().strip()

        if not benh:
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng nhập thông tin bệnh bị mắc trước khi lưu!"
            )
            return

        dong_du_lieu = (
            f"Tên:{ten_tk} | Năm:{nam} | Quý:{quy} | Tháng:{thang} | Tuần:{tuan} |"
            f" Ngày:{ngay} | Giờ:{gio} | Phút:{phut} | Bệnh:{benh}\n"
        )

        try:
            os.makedirs(os.path.dirname(self.template_txt_file), exist_ok=True)
            with open(self.template_txt_file, "a", encoding="utf-8") as f:
                f.write(dong_du_lieu)

            messagebox.showinfo(
                "Thành công",
                f"Đã lưu lịch sử vào tệp mẫu:\n{self.template_txt_file}",
            )
            self.load_data_to_table()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ghi tệp mẫu txt: {e}")

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
                                ten_val = parts[0].replace("Tên:", "")
                                time_val = " | ".join(parts[1:-1])
                                benh_val = parts[-1].replace("Bệnh:", "")
                                self.tree.insert(
                                    "", "end", values=(ten_val, time_val, benh_val)
                                )
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
                                time_val = " | ".join(parts[1:-1])
                                benh_val = parts[-1].replace("Bệnh:", "")
                                if keyword in ten_val.lower() or not keyword:
                                    self.tree.insert(
                                        "",
                                        "end",
                                        values=(ten_val, time_val, benh_val),
                                    )
            except Exception:
                pass

    def thuc_thi_cac_chuong_trinh_con(self, thu_muc_luu):
        """Quét các thư mục muc_1 đến muc_6 và gọi chạy tệp bên trong."""
        dem_thanh_cong = 0
        sub_folders_data = []
        danh_sach_file_quet = []

        # Tự động quét các thư mục bắt đầu bằng 'muc_' hoặc các thư mục con trong kho
        for ten_thu_muc in sorted(os.listdir(THU_MUC_NGUON_CHUAN)):
            if ten_thu_muc.startswith("muc_"):
                duong_dan_con = os.path.join(THU_MUC_NGUON_CHUAN, ten_thu_muc)

                if os.path.isdir(duong_dan_con):
                    sub_folders_data.append(ten_thu_muc)
                    for file in os.listdir(duong_dan_con):
                        file_lower = file.lower()
                        duong_dan_file = os.path.join(duong_dan_con, file)

                        if os

# -*- coding: utf-8 -*-
import os
import sys
import json
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
DAYS_TO_KEEP = 7

class QuanLyVaGieuPhoiFullApp:
    def __init__(self, root, headless=False):
        self.root = root
        self.config = self.load_config()
        self.thu_muc_luu_hien_tai = self.config.get("thu_muc_luu", THU_MUC_MAC_DINH)
        self.template_txt_file = os.path.join(self.thu_muc_luu_hien_tai, f"template_lich_su_{SCRIPT_NAME}.txt")
        self.index_file_dynamic = os.path.join(self.thu_muc_luu_hien_tai, f"index_{SCRIPT_NAME}_quan_ly.json")
        self.source_dir_name = os.path.basename(BASE_DIR) or "ThuMucGoc"

        if headless:
            self.run_background_task(is_headless=True)
            return

        self.root.title(f"Hệ Thống Điều Phối & Quản Lý Tra Cứu ({SCRIPT_NAME}.py)")
        self.root.geometry("1100x850")
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
        frame_nhap = tk.LabelFrame(self.root, text=" 1. Bộ Lọc, Tìm Kiếm Tên, Thời Gian, Bệnh Lý & Thư Mục ", font=("Arial", 10, "bold"))
        frame_nhap.pack(fill="x", padx=10, pady=10, ipady=5)

        tk.Label(frame_nhap, text="Thư mục lưu JSON:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lbl_thumuc = tk.Label(frame_nhap, text=self.thu_muc_luu_hien_tai, fg="blue", font=("Arial", 9))
        self.lbl_thumuc.grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        tk.Button(frame_nhap, text="📁 Đổi Thư Mục Lưu", bg="#607D8B", fg="white", command=self.chon_thu_muc_luu).grid(row=0, column=4, padx=5, pady=5)

        tk.Label(frame_nhap, text="Tìm kiếm tên:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_tim_kiem_ten = tk.Entry(frame_nhap, width=30)
        self.ent_tim_kiem_ten.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.ent_tim_kiem_ten.bind("<KeyRelease>", lambda e: self.filter_table())

        # Ô nhập thời gian chi tiết (Năm, Quý, Tháng, Tuần, Ngày, Giờ, Phút)
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

        frame_btn = tk.Frame(self.root)
        frame_btn.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_btn, text="💾 Lưu Lịch Sử Vào Tệp Mẫu TXT", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), command=self.luu_vao_file_txt).pack(side="left", padx=5)
        tk.Button(frame_btn, text="🚀 Chạy Quét & Xuất JSON (Hộp Thoại Lưu Động)", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=lambda: self.run_background_task(is_headless=False)).pack(side="left", padx=5)

        frame_table = tk.LabelFrame(self.root, text=" 2. Bảng Lịch Sử & Kết Quả Tra Cứu ", font=("Arial", 10, "bold"))
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

        self.load_data_to_table()

    def chon_thu_muc_luu(self):
        thu_muc_chon = filedialog.askdirectory(title="Chọn thư mục lưu tệp JSON", initialdir=self.thu_muc_luu_hien_tai)
        if thu_muc_chon:
            self.thu_muc_luu_hien_tai = thu_muc_chon
            self.lbl_thumuc.config(text=thu_muc_chon)
            self.template_txt_file = os.path.join(thu_muc_chon, f"template_lich_su_{SCRIPT_NAME}.txt")
            self.index_file_dynamic = os.path.join(thu_muc_chon, f"index_{SCRIPT_NAME}_quan_ly.json")
            self.save_config(thu_muc_chon)
            messagebox.showinfo("Thành công", f"Đã đổi thư mục lưu đích thành:\n{thu_muc_chon}")
            self.load_data_to_table()

    def luu_vao_file_txt(self):
        ten_tk = self.ent_tim_kiem_ten.get().strip() or "Khuyết Danh"
        t_vals = [self.time_entries[k].get().strip() for k in ["năm", "quý", "tháng", "tuần", "ngày", "giờ", "phút"]]
        time_str = f"Năm:{t_vals[0]} | Quý:{t_vals[1]} | Tháng:{t_vals[2]} | Tuần:{t_vals[3]} | Ngày:{t_vals[4]} | Giờ:{t_vals[5]} | Phút:{t_vals[6]}"
        benh = self.ent_benh.get().strip()

        if not benh:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập thông tin bệnh bị mắc trước khi lưu!")
            return

        dong_du_lieu = f"Tên:{ten_tk} | {time_str} | Bệnh:{benh}\n"
        try:
            os.makedirs(os.path.dirname(self.template_txt_file), exist_ok=True)
            with open(self.template_txt_file, "a", encoding="utf-8") as f:
                f.write(dong_du_lieu)
            messagebox.showinfo("Thành công", f"Đã lưu lịch sử vào tệp mẫu:\n{self.template_txt_file}")
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
                                self.tree.insert("", "end", values=(ten_val, time_val, benh_val))
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
                                    self.tree.insert("", "end", values=(ten_val, time_val, benh_val))
            except Exception:
                pass

    def thuc_thi_cac_chuong_trinh_con(self):
        dem_thanh_cong = 0
        sub_folders_data = []
        danh_sach_file_quet = []

        # Quét qua muc_1 đến muc_6 trên GitHub
        for i in range(1, 7):
            ten_thu_muc = f"muc_{i}"
            duong_dan_con = os.path.join(BASE_DIR, ten_thu_muc)
            if os.path.exists(duong_dan_con) and os.path.isdir(duong_dan_con):
                sub_folders_data.append(ten_thu_muc)
                for file in os.listdir(duong_dan_con):
                    duong_dan_file = os.path.join(duong_dan_con, file)
                    if os.path.isfile(duong_dan_file):
                        danh_sach_file_quet.append(duong_dan_file)
                    if file.lower().endswith(".py") and not "chay" in file.lower():
                        try:
                            cmd = [sys.executable, duong_dan_file]
                            process = subprocess.Popen(cmd, cwd=duong_dan_con)
                            process.wait(timeout=30)
                            dem_thanh_cong += 1
                        except Exception:
                            pass
        return dem_thanh_cong, sub_folders_data, danh_sach_file_quet

    def run_background_task(self, is_headless=False):
        try:
            thu_muc_luu = self.thu_muc_luu_hien_tai
            os.makedirs(thu_muc_luu, exist_ok=True)
            self.save_config(thu_muc_luu)

            dem_thanh_cong, sub_folders_data, danh_sach_file_quet = self.thuc_thi_cac_chuong_trinh_con()
            if os.path.exists(self.template_txt_file):
                danh_sach_file_quet.append(self.template_txt_file)

            now = datetime.now()
            thoi_gian_str = now.strftime("%Y%m%d_%H%M%S")
            
            # QUY TẮC 2: Chuẩn tên file động bắt buộc: [TênScript]_[TênThưMụcNguồn]_[YYYYMMDD_HHMMSS].json
            default_output_filename = f"{SCRIPT_NAME}_{self.source_dir_name}_{thoi_gian_str}.json"

            lich_su_records = []
            if os.path.exists(self.template_txt_file):
                with open(self.template_txt_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            parts = [p.strip() for p in line.strip().split("|")]
                            if len(parts) >= 3:
                                lich_su_records.append({
                                    "ten": parts[0].replace("Tên:", ""),
                                    "thoi_gian_chi_tiet": " | ".join(parts[1:-1]),
                                    "benh_mac": parts[-1].replace("Bệnh:", "")
                                })

            # Xây dựng khối ket_qua_tong_ket chuẩn theo quy tắc 3
            ket_qua_tong_ket = []
            ref_numbers_all = [123, 456, 789]
            for rec in lich_su_records:
                item_ket_qua = {
                    "tab": "Tab_Tong_Hop",
                    "ten": rec["ten"],
                    "ngay_sinh": "2000-01-01",
                    "gio_sinh": "00:00",
                    "chi_so": "Ngày",
                    "gia_tri_goc": 100,
                    "phan_nguyen": 10,
                    "mod_1000_nguyen": 10,
                    "trung_nguyen": 10 in ref_numbers_all,
                    "phan_du": 0,
                    "mod_1000_du": 0,
                    "trung_du": 0 in ref_numbers_all,
                    "can_bu": 5,
                    "thong_tin_du": f"Hết vòng đến bệnh: {rec['benh_mac']}",
                    "canh_bao_col": "Không cảnh báo",
                    "moc_thoi_gian": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "link_video": "https://www.youtube.com/watch?v=example",
                    "chi_tiet_trung_khop": "Nguyên: 10 (%1000=10) | Dư: 0 (%1000=0)"
                }
                ket_qua_tong_ket.append(item_ket_qua)

            # Khối JSON chuẩn tuyệt đối theo Quy tắc 3
            payload = {
                "metadata": {
                    "script_su_dung": f"{SCRIPT_NAME}.py",
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "date_minus_7_days": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "date_plus_7_days": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "thu_muc_nguon": self.source_dir_name,
                    "file_nguon_quet": danh_sach_file_quet
                },
                "people": lich_su_records,
                "ref_numbers": ref_numbers_all,
                "tabs_data": sub_folders_data,
                "ket_qua_tong_ket": ket_qua_tong_ket
            }

            if is_headless:
                out_path = os.path.join(thu_muc_luu, default_output_filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=4)
                print(f"[{SCRIPT_NAME}.py] Đã tự động xuất JSON ngầm tại: {out_path}")
            else:
                out_path = filedialog.asksaveasfilename(
                    title="Lưu tệp JSON chuẩn",
                    initialdir=thu_muc_luu,
                    initialfile=default_output_filename,
                    defaultextension=".json",
                    filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
                )
                if not out_path:
                    return
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Thành công", f"Đã xuất JSON tại:\n{out_path}")

        except Exception as e:
            if is_headless:
                print(f"[{SCRIPT_NAME}.py] Lỗi chạy ngầm: {e}")
                sys.exit(1)
            else:
                messagebox.showerror("Lỗi", f"Lỗi thực thi: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--gui":
        # Chỉ khi nào có tham số --gui mới bật giao diện Tkinter trên máy tính
        root = tk.Tk()
        app = QuanLyVaGieuPhoiFullApp(root, headless=False)
        root.mainloop()
    else:
        # Khi chạy ngầm trên GitHub Actions, tuyệt đối KHÔNG gọi tk.Tk() để tránh lỗi không có màn hình
        QuanLyVaGieuPhoiFullApp(None, headless=True)

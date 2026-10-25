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

        for ten_thu_muc in sorted(os.listdir(THU_MUC_NGUON_CHUAN)):
            if ten_thu_muc.startswith("muc_"):
                duong_dan_con = os.path.join(THU_MUC_NGUON_CHUAN, ten_thu_muc)

                if os.path.isdir(duong_dan_con):
                    sub_folders_data.append(ten_thu_muc)
                    for file in os.listdir(duong_dan_con):
                        file_lower = file.lower()
                        duong_dan_file = os.path.join(duong_dan_con, file)

                        if os.path.isfile(duong_dan_file):
                            danh_sach_file_quet.append(duong_dan_file)

                        if file_lower.endswith(".py") and file_lower != SCRIPT_NAME + ".py":
                            print(f"-> Đang điều phối chạy tệp: {ten_thu_muc}\\{file}")
                            try:
                                startupinfo = None
                                creationflags = 0
                                if os.name == "nt":
                                    startupinfo = subprocess.STARTUPINFO()
                                    startupinfo.dwFlags |= (
                                        subprocess.STARTF_USESHOWWINDOW
                                    )
                                    startupinfo.wShowWindow = 0
                                    creationflags = subprocess.CREATE_NO_WINDOW

                                cmd = ["python", duong_dan_file, "--outDir", THU_MUC_MAC_DINH]
                                process = subprocess.Popen(
                                    cmd,
                                    cwd=duong_dan_con,
                                    startupinfo=startupinfo,
                                    creationflags=creationflags,
                                )
                                process.wait(timeout=60)
                                dem_thanh_cong += 1
                            except Exception as e:
                                print(f"--> Lỗi chạy tệp {file}: {e}")

        return dem_thanh_cong, sub_folders_data, danh_sach_file_quet

    def ghi_nhan_index_json(self, thong_tin_xuat):
        danh_sach = []
        if os.path.exists(self.index_file_dynamic):
            try:
                with open(self.index_file_dynamic, "r", encoding="utf-8") as f:
                    danh_sach = json.load(f)
            except Exception:
                danh_sach = []

        danh_sach.append(thong_tin_xuat)
        try:
            os.makedirs(os.path.dirname(self.index_file_dynamic), exist_ok=True)
            with open(self.index_file_dynamic, "w", encoding="utf-8") as f:
                json.dump(danh_sach, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi ghi index quản lý: {e}")

    def run_background_task(self, is_headless=False):
        try:
            thu_muc_luu = self.thu_muc_luu_hien_tai
            os.makedirs(thu_muc_luu, exist_ok=True)
            self.save_config(thu_muc_luu)

            dem_thanh_cong, sub_folders_data, danh_sach_file_quet = (
                self.thuc_thi_cac_chuong_trinh_con(thu_muc_luu)
            )

            if os.path.exists(self.template_txt_file):
                danh_sach_file_quet.append(self.template_txt_file)

            now = datetime.now()
            thoi_gian_str = now.strftime("%Y%m%d_%H%M%S")
            ten_thu_muc_nguon = "GitHub_Muc"

            default_output_filename = (
                f"{SCRIPT_NAME}_{ten_thu_muc_nguon}_{thoi_gian_str}.json"
            )

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
                                    "benh_mac": parts[-1].replace("Bệnh:", ""),
                                })

            payload = {
                "metadata": {
                    "script_su_dung": f"{SCRIPT_NAME}.py",
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "date_minus_7_days": (now - timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                    "date_plus_7_days": (now + timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                    "thu_muc_nguon": THU_MUC_NGUON_CHUAN,
                    "danh_sach_thu_muc_con": sub_folders_data,
                    "file_nguon_quet": danh_sach_file_quet,
                },
                "people": {
                    "danh_sach_nhan_su": lich_su_records,
                },
                "ref_numbers": [
                    len(lich_su_records),
                    dem_thanh_cong,
                    len(sub_folders_data),
                ],
                "custom_tabs": {
                    "danh_sach_thu_muc_con": sub_folders_data,
                },
            }

            if is_headless:
                out_path = os.path.join(thu_muc_luu, default_output_filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=4)
                print(
                    f"[{SCRIPT_NAME}.py] Đã tự động xuất JSON ngầm tại: {out_path}"
                )
            else:
                out_path = filedialog.asksaveasfilename(
                    title="Lưu tệp JSON chuẩn",
                    initialdir=thu_muc_luu,
                    initialfile=default_output_filename,
                    defaultextension=".json",
                    filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                )
                if not out_path:
                    return

                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=4)
                messagebox.showinfo(
                    "Thành công",
                    f"Đã điều phối thành công {dem_thanh_cong} tệp con và xuất JSON"
                    f" tại:\n{out_path}",
                )

            self.ghi_nhan_index_json({
                "script_tao": f"{SCRIPT_NAME}.py",
                "file_json_gan_nhap_nhat": out_path,
                "thoi_gian": now.strftime("%Y-%m-%d %H:%M:%S"),
                "so_tep_con_xu_ly": dem_thanh_cong,
                "danh_sach_file_nguon": danh_sach_file_quet,
            })

        except Exception as e:
            if is_headless:
                print(f"[{SCRIPT_NAME}.py] Lỗi chạy ngầm: {e}")
                sys.exit(1)
            else:
                messagebox.showerror("Lỗi", f"Lỗi thực thi: {e}")


if __name__ == "__main__":
    if "--gui" in sys.argv:
        root = tk.Tk()
        app = QuanLyVaGieuPhoiFullApp(root, headless=False)
        root.mainloop()
    else:
        print(
            f"[{SCRIPT_NAME}.py] Đang chạy ngầm điều phối tệp con & xử lý dữ"
            " liệu..."
        )
        root_ao = tk.Tk()
        root_ao.withdraw()
        QuanLyVaGieuPhoiFullApp(root_ao, headless=True)
        root_ao.destroy()
        print(f"[{SCRIPT_NAME}.py] Hoàn tất tiến trình chạy ngầm!")

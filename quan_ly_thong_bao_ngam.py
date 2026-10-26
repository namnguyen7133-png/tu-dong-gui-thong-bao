import os
import time
import json
import threading
import sys
import tkinter as tk
from tkinter import messagebox

# Thư viện khay hệ thống và thông báo đẩy
try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pass

try:
    from plyer import notification
    CO_PLYER = True
except ImportError:
    CO_PLYER = False

THU_MUC_LAM_VIEC = r"G:\My Drive\DANHSACHPHATVIDEO\KET_QUA_JSON"
TEP_JSON_KET_QUA = os.path.join(THU_MUC_LAM_VIEC, "du_lieu_ket_qua_task.json")
TEN_UNG_DUNG = "Quan Ly Thong Bao Ngam"

class UngDungQuanLyNgam:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # Ẩn cửa sổ chính ngay khi khởi động, chỉ chạy ngầm
        
        self.du_lieu_cu = ""
        
        # Tạo khay hệ thống
        self.tao_khay_he_thong()
        
        # Khởi chạy luồng ngầm liên tục kiểm tra tệp JSON do Task cập nhật
        threading.Thread(target=self.vong_lap_kiem_tra_json, daemon=True).start()

    def hien_thong_bao_desktop(self, tiêu_đề, nội_dung):
        """Hệ thống thông báo đẩy góc màn hình Windows"""
        if CO_PLYER:
            try:
                notification.notify(
                    title=tiêu_đề,
                    message=nội_dung,
                    app_name=TEN_UNG_DUNG,
                    timeout=10
                )
                return
            except:
                pass
        # Fallback nếu không có plyer
        print(f"[{tiêu_đề}] {nội_dung}")

    def vong_lap_kiem_tra_json(self):
        """Luồng ngầm kiểm tra xem Tệp 1 (Task) có cập nhật dữ liệu JSON mới không"""
        while True:
            try:
                if os.path.exists(TEP_JSON_KET_QUA):
                    with open(TEP_JSON_KET_QUA, "r", encoding="utf-8") as f:
                        noi_dung_tep = f.read()
                        
                    # Nếu phát hiện nội dung JSON thay đổi (Task vừa chạy xong ghi tệp mới)
                    if noi_dung_tep != self.du_lieu_cu:
                        self.du_lieu_cu = noi_dung_tep
                        data = json.loads(noi_dung_tep)
                        
                        thoi_gian = data.get("thoi_gian_cap_nhat", "")
                        danh_sach_tb = data.get("thong_bao_moi", [])
                        
                        for tb in danh_sach_tb:
                            self.hien_thong_bao_desktop(
                                f"🔔 {tb.get('tieu_de', 'Thông báo hệ thống')}",
                                f"{tb.get('noi_dung', '')}\nThời gian: {thoi_gian}"
                            )
            except Exception as e:
                print(f"Lỗi đọc JSON ngầm: {e}")
            
            # Kiểm tra lại sau mỗi 15 giây
            time.sleep(15)

    def tao_khay_he_thong(self):
        def chay_khay():
            try:
                # Vẽ biểu tượng icon đơn giản cho khay hệ thống
                img = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                draw.ellipse([8, 8, 56, 56], fill="#4CAF50", outline="black", width=2)
                
                icon = pystray.Icon(
                    "QuanLyNgam", img, TEN_UNG_DUNG,
                    pystray.Menu(
                        pystray.MenuItem("Kiểm tra trạng thái JSON", self.thong_bao_trang_thai),
                        pystray.MenuItem("Thoát hoàn toàn", self.thoat_hoan_toan)
                    )
                )
                icon.run()
            except Exception as e:
                print(f"Lỗi khởi tạo khay hệ thống: {e}")
                
        if 'pystray' in sys.modules:
            threading.Thread(target=chay_khay, daemon=True).start()

    def thong_bao_trang_thai(self, icon=None, item=None):
        if os.path.exists(TEP_JSON_KET_QUA):
            self.hien_thong_bao_desktop("Trạng thái", "Tệp JSON vẫn đang hoạt động tốt và được giám sát.")
        else:
            self.hien_thong_bao_desktop("Cảnh báo", "Chưa tìm thấy tệp JSON kết quả từ Task Scheduler!")

    def thoat_hoan_toan(self, icon=None, item=None):
        os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = UngDungQuanLyNgam(root)
    root.mainloop()
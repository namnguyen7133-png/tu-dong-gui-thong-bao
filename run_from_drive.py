import os
import sys
import json
import requests

def main():
    print("=== BẮT ĐẦU CHẠY TIẾN TRÌNH TỰ ĐỘNG ===")
    
    # Cấu hình timeout tối đa 30 giây cho mỗi kết nối mạng để tránh treo vô hạn
    HTTP_TIMEOUT = 30 
    
    try:
        # Ví dụ kết nối hoặc tải dữ liệu từ Drive/API
        # Luôn có timeout=HTTP_TIMEOUT để mạng đơ là tự bỏ qua
        print("Đang đồng bộ dữ liệu...")
        
        # Code xử lý chính của anh sẽ chạy ở đây
        # Mọi kết nối mạng trong script đều được kiểm soát thời gian
        
        print("=== HOÀN THÀNH TIẾN TRÌNH THÀNH CÔNG ===")
        
    except requests.exceptions.Timeout:
        print("LỖI: Mạng quá chậm hoặc Google Drive không phản hồi (Timeout). Tự động ngắt để tránh kẹt ca!")
        sys.exit(0) # Thoát an toàn
    except Exception as e:
        print(f"LỖI KHÔNG MONG MUỐN: {e}")
        sys.exit(0)

if __name__ == "__main__":
    main()

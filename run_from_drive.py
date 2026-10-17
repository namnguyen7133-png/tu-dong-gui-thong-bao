import glob
import json
import os
import subprocess

def main():
    results = []
    # Quét tất cả các file .py trong thư mục scripts/
    python_files = sorted(glob.glob("scripts/*.py"))
    
    for py_file in python_files:
        base_name = os.path.splitext(os.path.basename(py_file))[0]
        json_file = f"data/{base_name}.json"
        
        print(f"Đang chạy: {py_file}...")
        
        try:
            # Thực thi file python
            result = subprocess.run(
                ["python", py_file], capture_output=True, text=True, timeout=300
            )
            
            status = "Thành công" if result.returncode == 0 else "Thất bại"
            
            # Đọc nội dung file JSON sau khi python cập nhật xong
            file_data = {}
            if os.path.exists(json_file):
                with open(json_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
            
            results.append({
                "task": base_name,
                "status": status,
                "output": file_data
            })
            
        except Exception as e:
            print(f"Lỗi khi chạy {py_file}: {e}")
            results.append({"task": base_name, "status": "Lỗi", "error": str(e)})

    # Xuất ra tệp tổng hợp để trang web đọc
    with open("aggregated_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()

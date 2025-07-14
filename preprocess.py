import os

def read_logs(logs_dir="inputRag"):
    content = []
    try:
        for filename in os.listdir(logs_dir):
            if filename.endswith(".log"):
                full_path = os.path.join(logs_dir, filename)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                    content.extend(lines)
    except Exception as e:
        print(f"[ERROR] Problema al leer logs: {e}")
    return content

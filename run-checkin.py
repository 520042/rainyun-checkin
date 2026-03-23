"""
签到脚本运行包装器
将输出写入日志文件，避免控制台 GBK 编码问题
"""
import subprocess
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(SCRIPT_DIR, "checkin-output.log")
summary_path = os.path.join(SCRIPT_DIR, "checkin-summary.txt")

# 查找 python 解释器：优先用当前 python，其次用脚本同目录的 venv
python_exe = sys.executable
checkin_script = os.path.join(SCRIPT_DIR, "rainyun-checkin.py")

start = time.time()
with open(log_path, "w", encoding="utf-8") as log:
    proc = subprocess.Popen(
        [python_exe, checkin_script],
        stdout=log, stderr=subprocess.STDOUT,
        cwd=SCRIPT_DIR
    )
    try:
        proc.wait(timeout=120)
    except subprocess.TimeoutExpired:
        proc.kill()

elapsed = time.time() - start

# 提取关键行输出到 summary
with open(log_path, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

key_lines = []
for line in lines:
    s = line.strip()
    if any(kw in s for kw in ["[OK]", "[ERR]", "[SUCCESS]", "[FAIL]", "[CAP] ===", "Status:", "Result:", "errorCode=", "Exit"]):
        key_lines.append(s.encode("ascii", errors="replace").decode("ascii"))

with open(summary_path, "w", encoding="utf-8") as sf:
    sf.write(f"Exit: {proc.returncode}, Time: {elapsed:.1f}s\n")
    sf.write("\n".join(key_lines))

print(f"Exit={proc.returncode}, Time={elapsed:.1f}s")
print(f"Details in: {summary_path}")
for kl in key_lines:
    print(kl)

"""
雨云每日签到脚本
通过纯HTTP请求完成腾讯TCaptcha验证码并签到
不需要浏览器

配置方式（任选其一）：
  1. 设置环境变量 RAINYUN_API_KEY
  2. 在脚本同目录创建 .env 文件，写入 RAINYUN_API_KEY=your_key
"""
import base64
import hashlib
import json
import time
import sys
import re
import os
import requests
import numpy as np
import cv2

# 导入原始高精度图像识别模块（从脚本所在目录查找）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# 青龙面板兼容性：尝试导入 ICR 模块，如果失败则报错
try:
    import rainyun_src_ICR as ICR
except ImportError as e:
    print(f"[ERR] 无法导入 rainyun_src_ICR 模块: {e}")
    print("      请确保 rainyun_src_ICR.py 与本脚本在同一目录")
    sys.exit(1)

# ============ 配置 ============
# 优先读取环境变量，其次读取同目录 .env 文件
def _load_env():
    env_path = os.path.join(_SCRIPT_DIR, '.env')
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env()

API_KEY = os.environ.get('RAINYUN_API_KEY', '')
if not API_KEY:
    print("[ERR] 未设置 RAINYUN_API_KEY，请配置环境变量或 .env 文件")
    sys.exit(1)

CAPTCHA_AID = "2039519451"
CAPTCHA_BASE = "https://turing.captcha.qcloud.com"
RAINYUN_API = "https://api.v2.rainyun.com"

COMMON_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "referer": "https://app.rainyun.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
}


def find_part_positions(bg_bytes, sprite_bytes):
    """使用原始高精度 ICR 算法找到拼图块在背景图中的中心坐标"""
    matches = ICR.main(bg_bytes, sprite_bytes, 'template', False, False)
    positions = ICR.convert_matches_to_positions(matches)
    for i, m in enumerate(matches):
        x, y, w, h = m['bg_rect']
        print(f"  Sprite {m['sprite_idx']} -> ({x+w/2:.0f}, {y+h/2:.0f}), sim={m['similarity']:.1f}%, angle={m['angle']}")
    return positions

# ============ MD5碰撞 ============
def find_md5_collision(target_md5, prefix):
    start = time.time()
    for num in range(114514 * 1000):
        s = prefix + str(num)
        if hashlib.md5(s.encode()).hexdigest() == target_md5:
            elapsed = int((time.time() - start) * 1000)
            print(f"  MD5 collision found: {s} in {elapsed}ms")
            return s, elapsed
    return prefix, int((time.time() - start) * 1000)

# ============ 获取TDC指纹 ============
def get_collect_and_eks(tdc_content):
    """简化版：直接返回空字符串（腾讯验证码对此要求不严格）"""
    # 实际上需要运行JS，这里用简单值
    return "", ""

# ============ 验证码流程 ============
def get_captcha_data():
    """获取验证码初始化数据"""
    ua_b64 = base64.b64encode(COMMON_HEADERS['user-agent'].encode()).decode()
    params = {
        "aid": CAPTCHA_AID,
        "protocol": "https",
        "accver": "1",
        "showtype": "popup",
        "ua": ua_b64,
        "noheader": "1",
        "fb": "1",
        "aged": "0",
        "enableAged": "0",
        "enableDarkMode": "0",
        "grayscale": "1",
        "clientype": "2",
        "cap_cd": "",
        "uid": "",
        "lang": "zh-cn",
        "entry_url": "https://turing.captcha.gtimg.com/1/template/drag_ele.html",
        "elder_captcha": "0",
        "js": "/tcaptcha-frame.97a921e6.js",
        "login_appid": "",
        "wb": "1",
        "subsid": "9",
        "callback": "",
        "sess": ""
    }
    r = requests.get(f"{CAPTCHA_BASE}/cap_union_prehandle", params=params, headers=COMMON_HEADERS, timeout=15)
    r.raise_for_status()
    text = r.text.strip()
    # 移除括号
    if text.startswith('(') and text.endswith(')'):
        text = text[1:-1]
    elif text.startswith('/*'):
        # 去掉 /* ... */ 前缀
        text = re.sub(r'^/\*.*?\*/', '', text, flags=re.DOTALL).strip()
        if text.startswith('(') and text.endswith(')'):
            text = text[1:-1]
    return json.loads(text)

def get_tdc_path_and_solve(data):
    """获取TDC脚本并计算POW"""
    comm = data['data']['comm_captcha_cfg']
    tdc_path = comm['tdc_path']
    pow_cfg = comm['pow_cfg']
    
    # 下载TDC (可选，简化版跳过)
    tdc_url = CAPTCHA_BASE + tdc_path
    tdc_content = requests.get(tdc_url, headers=COMMON_HEADERS, timeout=10).text
    
    # MD5碰撞
    print(f"  Solving MD5 POW: target={pow_cfg['md5']}, prefix={pow_cfg['prefix']}")
    pow_answer, pow_time = find_md5_collision(pow_cfg['md5'], pow_cfg['prefix'])
    
    return "", "", pow_answer, pow_time  # collect, eks, pow_answer, pow_time

def build_verify_form(data, positions, collect="", eks="", pow_answer="", pow_time=0):
    """构建验证表单"""
    ans = []
    for i, (x, y) in enumerate(positions, start=1):
        ans.append({
            "elem_id": i,
            "type": "DynAnswerType_POS",
            "data": f"{int(x)},{int(y)}"
        })
    return {
        'collect': collect,
        'tlg': str(len(collect)),
        'eks': eks,
        'sess': data.get('sess', ''),
        'ans': json.dumps(ans, separators=(',', ':')),
        'pow_answer': pow_answer,
        'pow_calc_time': str(pow_time)
    }

def complete_captcha(max_retry=5):
    """完整验证码流程，返回 {ticket, randstr}"""
    for attempt in range(max_retry):
        print(f"\n[CAP] === Round {attempt+1}/{max_retry} ===")
        
        # 每次重新获取 session + 图片 + POW（避免 errorCode=50 session 污染）
        print("[CAP] Getting captcha data...")
        data = get_captcha_data()
        sess = data.get('sess', '')
        print(f"  sess: {sess[:20]}...")
        
        # 获取图片URL
        dyn = data['data']['dyn_show_info']
        bg_url = CAPTCHA_BASE + dyn['bg_elem_cfg']['img_url']
        sprite_url = CAPTCHA_BASE + dyn['sprite_url']
        
        # 下载图片
        print("[CAP] Downloading images...")
        bg_bytes = requests.get(bg_url, headers=COMMON_HEADERS, timeout=10).content
        sprite_bytes = requests.get(sprite_url, headers=COMMON_HEADERS, timeout=10).content
        print(f"  BG size: {len(bg_bytes)}, Sprite size: {len(sprite_bytes)}")
        
        # 保存调试图片（仅在本地环境或 DEBUG 模式下保存）
        if os.environ.get('RAINYUN_DEBUG') == '1':
            try:
                with open(f'debug-bg-round{attempt+1}.jpg', 'wb') as f: f.write(bg_bytes)
                with open(f'debug-sprite-round{attempt+1}.jpg', 'wb') as f: f.write(sprite_bytes)
                print(f"  Debug images saved")
            except Exception as e:
                print(f"  Warning: Failed to save debug images: {e}")
        
        # 获取POW（每次重新计算）
        collect, eks, pow_answer, pow_time = get_tdc_path_and_solve(data)
        
        # 图像识别
        print("[CAP] Finding sprite positions...")
        try:
            positions = find_part_positions(bg_bytes, sprite_bytes)
        except Exception as e:
            print(f"  Image matching error: {e}")
            positions = [(170, 122)]  # fallback
        
        print(f"  Positions: {positions}")
        
        # 构建并提交验证
        form = build_verify_form(data, positions, collect, eks, pow_answer, pow_time)
        print("[CAP] Submitting verification...")
        
        r = requests.post(
            f"{CAPTCHA_BASE}/cap_union_new_verify",
            data=form,
            headers=COMMON_HEADERS,
            timeout=15
        )
        r.raise_for_status()
        result = r.json()
        print(f"  Full verify result: {json.dumps(result, ensure_ascii=False)[:300]}")
        print(f"  errorCode={result.get('errorCode')}, ticket={result.get('ticket', '')[:20] if result.get('ticket') else 'N/A'}")
        
        if str(result.get('errorCode', -1)) == '0':
            return {'ticket': result['ticket'], 'randstr': result['randstr']}
        
        # 错误码含义
        err_code = result.get('errorCode')
        if err_code == '50':
            print(f"  [INFO] errorCode=50: session expired/invalid, will retry with new session")
        else:
            print(f"  [INFO] errorCode={err_code}: verification failed, will retry")
        
        # 短暂等待避免频率限制
        if attempt < max_retry - 1:
            wait = 1 + attempt
            print(f"  Waiting {wait}s before next round...")
            time.sleep(wait)
    
    raise Exception("验证码多次尝试失败")

# ============ 签到 ============
def check_in_status():
    """查询签到状态"""
    r = requests.get(
        f"{RAINYUN_API}/user/reward/tasks",
        headers={**COMMON_HEADERS, 'x-api-key': API_KEY},
        timeout=10
    )
    r.raise_for_status()
    data = r.json()
    for task in data.get('data', []):
        if task.get('Name') == '每日签到':
            return task.get('Status')  # 1=可领取, 2=已领取
    return None

def do_check_in(ticket, randstr):
    """执行签到"""
    payload = {
        "task_name": "每日签到",
        "verifyCode": "",
        "vticket": ticket,
        "vrandstr": randstr
    }
    r = requests.post(
        f"{RAINYUN_API}/user/reward/tasks",
        headers={**COMMON_HEADERS, 'x-api-key': API_KEY},
        json=payload,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

# ============ 主流程 ============
def main():
    print("=" * 50)
    print("雨云每日签到脚本 v2.1 (支持青龙面板)")
    print("=" * 50)
    
    # 输出运行环境信息（用于调试）
    print(f"Python 版本: {sys.version}")
    print(f"脚本路径: {_SCRIPT_DIR}")
    print(f"API_KEY 已配置: {'是' if API_KEY else '否'}")
    
    # 1. 检查签到状态
    print("\n[1] 检查签到状态...")
    status = check_in_status()
    print(f"  Status: {status} (1=可领取, 2=已领取)")
    
    if status == 2:
        print("\n[OK] 今日已签到！")
        return True
    
    if status != 1:
        print(f"\n[ERR] 未知状态: {status}")
        return False
    
    print("  -> 尚未签到，开始签到流程...")
    
    # 2. 完成验证码
    print("\n[2] 完成验证码...")
    try:
        verify = complete_captcha()
        print(f"  [OK] 验证码通过: ticket={verify['ticket'][:30]}...")
    except Exception as e:
        print(f"\n[ERR] 验证码失败: {e}")
        return False
    
    # 3. 执行签到
    print("\n[3] 执行签到...")
    result = do_check_in(verify['ticket'], verify['randstr'])
    print(f"  Result: {json.dumps(result, ensure_ascii=False)}")
    
    if result.get('code') == 200 or result.get('status') == 'success' or 'data' in result:
        print("\n[SUCCESS] 签到成功！")
        # 再次查询确认
        time.sleep(1)
        new_status = check_in_status()
        print(f"  最终状态: {new_status} (期望=2)")
        return True
    else:
        print(f"\n[FAIL] 签到失败: {result}")
        return False

if __name__ == '__main__':
    # 青龙面板兼容性：不强制切换工作目录，使用相对路径
    success = main()
    sys.exit(0 if success else 1)

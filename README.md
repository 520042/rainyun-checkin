# Rainyun Daily Auto Check-in

Automated daily check-in for the [Rainyun](https://app.rainyun.com/) platform using pure HTTP requests — no browser required. Automatically solves Tencent TCaptcha sliding-puzzle challenges using OpenCV image matching.

---

## ⚠️ Disclaimer

> **Please read carefully before using this project.**

1. **Educational Purpose Only**  
   This project is provided for **educational and research purposes only**. It demonstrates techniques for HTTP automation, image recognition, and CAPTCHA solving. The author does not encourage or endorse using this tool to violate any platform's Terms of Service.

2. **Use at Your Own Risk**  
   The author and contributors assume **no responsibility** for any consequences arising from the use of this software, including but not limited to: account suspension, data loss, financial loss, or legal disputes. You bear full responsibility for how you use this tool.

3. **Compliance with Platform Terms**  
   Before using this tool, please review the Terms of Service of the Rainyun platform (`https://app.rainyun.com/`). Automated check-in scripts may violate the platform's terms. The author is not liable for any account penalties or restrictions imposed by the platform.

4. **No Warranty**  
   This software is provided "as is", without warranty of any kind, express or implied. The author makes no guarantees that the script will work at all times — the platform may change its API or CAPTCHA mechanism at any time, which may break functionality.

5. **Credential Security**  
   Never share your API key or credentials publicly. The author is not responsible for any security incidents resulting from credential leakage.

6. **Prohibition on Malicious Use**  
   This project must **not** be used for any malicious purposes, including but not limited to: large-scale automated attacks, credential stuffing, bypassing security systems at scale, or any activity that causes harm to others.

7. **License Boundary**  
   The MIT license grants permission to use the code, but does **not** grant permission to use it in ways that violate applicable laws or the terms of third-party platforms.

By using this project, you acknowledge that you have read, understood, and agreed to all of the above terms.

---

## Features

- **Pure HTTP** — No Playwright or Selenium required; fast and lightweight
- **Auto CAPTCHA** — OpenCV image matching to identify TCaptcha puzzle positions
- **Auto Retry** — Up to 5 attempts, each with a fresh session to avoid pollution
- **MD5 Proof-of-Work** — Automatically computes the PoW required by Tencent's CAPTCHA service

## Requirements

- Python 3.8+
- Dependencies: `requests`, `opencv-python`, `numpy`

```bash
pip install requests opencv-python numpy
```

## Configuration

Copy `.env.example` to `.env` and fill in your Rainyun API Key:

```bash
cp .env.example .env
# Edit .env and set RAINYUN_API_KEY
```

Or set the environment variable directly:

```bash
# Windows
set RAINYUN_API_KEY=your_key_here

# Linux / macOS
export RAINYUN_API_KEY=your_key_here
```

Your API Key can be found in the Rainyun Console → Account Settings → API.

## Usage

```bash
# Run directly
python rainyun-checkin.py

# Run via wrapper (output written to log file)
python run-checkin.py
```

## Automation (Daily Schedule)

### Option 1: Qinglong Panel (Recommended)

This project fully supports the [Qinglong Panel](QINGLONG_README.md), which is ideal for managing scheduled tasks centrally.

### Option 2: System Cron / Task Scheduler

Use Linux cron or Windows Task Scheduler:

```bash
# Linux cron example — run at 09:45 every day
45 9 * * * cd /path/to/project && python rainyun-checkin.py
```

## File Overview

| File | Description |
|------|-------------|
| `rainyun-checkin.py` | Main check-in script |
| `rainyun_src_ICR.py` | High-accuracy image recognition module (TCaptcha puzzle matching) |
| `run-checkin.py` | Runner wrapper — writes output to a log file |
| `.env.example` | Environment variable template |
| `QINGLONG_README.md` | Qinglong Panel deployment guide |
| `TEST_QINGLONG.md` | Qinglong Panel compatibility test report |

## How It Works

TCaptcha is Tencent's sliding-puzzle CAPTCHA. The solver needs to find the correct position of each puzzle piece within the background image.

**Recognition pipeline:**

1. Fetch the background image and sprite image (containing puzzle piece outlines)
2. Extract black regions and preprocess both images
3. For each sprite region, rotate from -45° to +45° in 1° steps
4. Use `cv2.matchTemplate` to find the highest-similarity position at each angle
5. Return center coordinates and submit to Tencent's CAPTCHA server

**Typical similarity score:** 68–83%. The first attempt usually succeeds (errorCode=0).

## License

MIT — See [LICENSE](LICENSE) for details.

> ⚠️ The MIT license governs the code itself. It does not grant permission to use this software in violation of applicable laws or third-party platform Terms of Service. See the Disclaimer section above.

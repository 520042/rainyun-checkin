# Qinglong Panel Deployment Guide

This guide explains how to deploy the Rainyun daily check-in script on [Qinglong Panel](https://github.com/whyour/qinglong) (青龙面板).

---

## ⚠️ Disclaimer

This script is provided for educational purposes only. Use it in accordance with Rainyun's Terms of Service and at your own risk. See the main [README](README.md) for the full disclaimer.

---

## Prerequisites

- Qinglong Panel installed and accessible via browser
- Docker-based deployment (standard Qinglong setup)

---

## Step 1: Upload Scripts

1. Log in to Qinglong Panel
2. Go to the **"Scripts"** module
3. Click **"New Script"**
4. Copy and paste the content of each file separately:
   - `rainyun-checkin.py` — main script
   - `rainyun_src_ICR.py` — image recognition module

   Save them with the **exact same filenames**:
   - `rainyun-checkin.py`
   - `rainyun_src_ICR.py`

> ⚠️ Both files must be in the **same directory** inside Qinglong. The main script imports `rainyun_src_ICR` at runtime — if the module is missing, the script will exit with an error.

---

## Step 2: Install Dependencies

In the **"Dependencies"** module of Qinglong Panel, install the following Python packages:

```
requests
opencv-python
numpy
```

Alternatively, install via SSH into the Qinglong container:

```bash
docker exec -it qinglong bash
pip3 install requests opencv-python numpy
```

---

## Step 3: Configure Environment Variables

1. Go to the **"Environment Variables"** module
2. Click **"New Variable"**
3. Add the following:

| Variable Name | Value | Required |
|---------------|-------|----------|
| `RAINYUN_API_KEY` | Your Rainyun API key | ✅ Yes |
| `RAINYUN_DEBUG` | `1` | Optional (enables debug image saving) |

**How to get your API Key:**
- Visit the [Rainyun Console](https://app.rainyun.com/)
- Go to **Account Settings** → **API**
- Create or copy an existing API Key

---

## Step 4: Create a Scheduled Task

1. Go to the **"Cron Jobs"** module
2. Click **"New Task"**
3. Fill in the task details:

   | Field | Value |
   |-------|-------|
   | Name | `Rainyun Daily Check-in` |
   | Command | `python3 rainyun-checkin.py` |
   | Cron Expression | `45 9 * * *` (runs at 09:45 every day) |
   | Status | Active |

### Cron Expression Reference

```
45 9 * * *
│  │ │ │ │
│  │ │ │ └── Day of week (0–6, 0=Sunday)
│  │ │ └──── Month (1–12)
│  │ └────── Day of month (1–31)
│  └──────── Hour (0–23)
└─────────── Minute (0–59)
```

Common examples:
- Daily at 09:45 → `45 9 * * *`
- Daily at 08:00 → `0 8 * * *`
- Daily at 01:00 → `0 1 * * *`

---

## Step 5: Test Run

1. Find the task in the Cron Jobs list
2. Click **"Run"** to trigger it manually
3. Go to **"Logs"** to view the execution result

### Expected Output

```
==================================================
Rainyun Daily Check-in v2.1 (Qinglong Compatible)
==================================================
Python version: 3.9.x
Script path: /ql/scripts
API_KEY configured: Yes

[1] Checking check-in status...
  Status: 1 (1=available, 2=already claimed)
  -> Not checked in yet, starting check-in...

[2] Solving CAPTCHA...
[CAP] === Round 1/5 ===
[CAP] Getting captcha data...
  sess: xxx...
[CAP] Downloading images...
  BG size: 12345, Sprite size: 6789
[CAP] Solving MD5 POW: target=xxx, prefix=xxx
  MD5 collision found: xxx in 123ms
[CAP] Finding sprite positions...
  Sprite 0 -> (123, 456), sim=75.0%, angle=5
  Sprite 1 -> (234, 567), sim=78.5%, angle=-3
  Sprite 2 -> (345, 678), sim=72.0%, angle=0
  Positions: [(123.0, 456.0), (234.0, 567.0), (345.0, 678.0)]
[CAP] Submitting verification...
  errorCode=0, ticket=xxx...
  [OK] CAPTCHA passed: ticket=xxx...

[3] Submitting check-in...
  Result: {"code":200,"data":"ok"}

[SUCCESS] Check-in successful!
  Final status: 2 (expected=2)
```

---

## Debug Mode

To save debug images for troubleshooting image recognition issues, set:

| Variable | Value |
|----------|-------|
| `RAINYUN_DEBUG` | `1` |

Debug images will be saved in the script directory as `debug-bg-roundX.jpg` and `debug-sprite-roundX.jpg`.

---

## Troubleshooting

### ImportError: No module named 'cv2'
**Cause:** `opencv-python` not installed  
**Fix:** Install it via the Dependencies module: `opencv-python`

### RAINYUN_API_KEY not set
**Cause:** Environment variable missing  
**Fix:** Add `RAINYUN_API_KEY` in the Environment Variables module

### Check-in failed — errorCode=50
**Cause:** CAPTCHA session expired  
**Fix:** The script automatically retries up to 5 times with a fresh session each time. This is usually a transient issue.

### Low image recognition similarity
**Cause:** Tencent may have updated their CAPTCHA images  
**Fix:** Let the script auto-retry — it usually succeeds within 2–3 attempts

---

## Notes

1. **API Key Security** — Never expose your API Key in public repositories or logs
2. **Network Access** — Qinglong needs access to:
   - `https://api.v2.rainyun.com` (Rainyun API)
   - `https://turing.captcha.qcloud.com` (Tencent CAPTCHA)
3. **Run Frequency** — Run once per day; avoid excessive scheduling
4. **Log Monitoring** — Periodically review logs to confirm successful check-ins

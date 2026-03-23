# 雨云每日自动签到

纯 HTTP 模式，无需浏览器，自动识别腾讯 TCaptcha 拼图验证码，完成雨云平台每日签到。

## 特性

- **纯 HTTP**：不依赖 Playwright / Selenium，速度快、资源占用低
- **自动验证码**：使用 OpenCV 图像匹配算法识别 TCaptcha 拼图位置
- **自动重试**：最多重试 5 次，每次重新获取新 session 避免污染
- **MD5 POW**：自动计算腾讯验证码要求的 Proof-of-Work

## 环境要求

- Python 3.8+
- 依赖包：`requests`、`opencv-python`、`numpy`

```bash
pip install requests opencv-python numpy
```

## 配置

复制 `.env.example` 为 `.env`，填入你的雨云 API Key：

```bash
cp .env.example .env
# 编辑 .env，填写 RAINYUN_API_KEY
```

也可以直接设置环境变量：

```bash
# Windows
set RAINYUN_API_KEY=your_key_here

# Linux/macOS
export RAINYUN_API_KEY=your_key_here
```

API Key 在雨云控制台 → 账户设置 → API 中获取。

## 使用

```bash
# 直接运行
python rainyun-checkin.py

# 通过包装器运行（输出写入日志）
python run-checkin.py
```

## 自动化（每日定时）

### 方式一：青龙面板（推荐）

本项目已完美支持 [青龙面板](QINGLONG_README.md)，适合需要定时任务和集中管理的场景。

### 方式二：系统定时任务

可配合系统定时任务（Windows 任务计划程序 / Linux cron）每日自动运行：

```bash
# Linux cron 示例（每天 9:45 运行）
45 9 * * * cd /path/to/project && python rainyun-checkin.py
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `rainyun-checkin.py` | 主签到脚本 |
| `rainyun_src_ICR.py` | 高精度图像识别模块（TCaptcha 拼图匹配） |
| `run-checkin.py` | 运行包装器，输出写入日志文件 |
| `.env.example` | 环境变量配置模板 |
| `QINGLONG_README.md` | 青龙面板部署指南（适用于定时任务平台） |

## 算法原理

TCaptcha 是腾讯的拼图式验证码，需要找出若干个拼图块在背景图中的对应位置。

识别流程：
1. 获取背景图和 sprite 图（含拼图块轮廓）
2. 对图像进行黑色区域提取和预处理
3. 对每个 sprite 区域在 -45° ~ +45° 范围内旋转匹配
4. 用 `cv2.matchTemplate` 找到最高相似度位置
5. 返回中心坐标提交给腾讯验证码服务器

## License

MIT

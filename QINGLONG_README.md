# 青龙面板部署指南

## 前提条件

已安装并运行青龙面板（Qinglong），可以通过浏览器访问面板。

## 步骤 1：上传脚本

1. 登录青龙面板
2. 进入 **"脚本管理"** 模块
3. 点击 **"新建脚本"**
4. 将以下两个文件的内容分别复制粘贴：
   - `rainyun-checkin.py` （主脚本）
   - `rainyun_src_ICR.py` （图像识别模块）

   命名为：
   - `rainyun-checkin.py`
   - `rainyun_src_ICR.py`

## 步骤 2：安装依赖

在青龙面板的 **"依赖管理"** 模块中，安装以下 Python 依赖：

```bash
requests
opencv-python
numpy
```

或者通过 SSH 进入青龙容器手动安装：
```bash
docker exec -it qinglong pnpm install
pip3 install requests opencv-python numpy
```

## 步骤 3：配置环境变量

1. 进入 **"环境变量"** 模块
2. 点击 **"新建变量"**
3. 添加以下变量：

| 变量名 | 变量值 | 说明 |
|--------|--------|------|
| `RAINYUN_API_KEY` | `你的雨云API密钥` | 必填，从雨云控制台获取 |

**获取 API Key**：
- 访问 [雨云控制台](https://app.rainyun.com/)
- 进入 **"账户设置"** → **"API"**
- 创建或复制已有的 API Key

## 步骤 4：设置定时任务

1. 进入 **"定时任务"** 模块
2. 点击 **"添加订阅"** 或 **"新建任务"**
3. 填写任务信息：

   - **名称**：`雨云每日签到`
   - **命令**：`python3 rainyun-checkin.py`
   - **Cron 表达式**：`45 9 * * *` （每天 9:45）
   - **状态**：运行中

### Cron 表达式说明

```
45 9 * * *
│  │ │ │ │
│  │ │ │ └─ 星期几 (0-6, 0=周日)
│  │ │ └─── 月份 (1-12)
│  │ └───── 日期 (1-31)
│  └─────── 小时 (0-23)
└─────────── 分钟 (0-59)
```

常用时间示例：
- 每天 9:45：`45 9 * * *`
- 每天 8:00：`0 8 * * *`
- 每天凌晨 1:00：`0 1 * * *`

## 步骤 5：测试运行

1. 在定时任务列表中，找到刚创建的任务
2. 点击 **"运行"** 按钮
3. 进入 **"日志"** 模块查看执行结果

### 预期输出示例

```
==================================================
雨云每日签到脚本 v2.1 (支持青龙面板)
==================================================
Python 版本: 3.9.x
脚本路径: /ql/scripts
API_KEY 已配置: 是

[1] 检查签到状态...
  Status: 1 (1=可领取, 2=已领取)
  -> 尚未签到，开始签到流程...

[2] 完成验证码...
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
  Full verify result: {"errorCode":0,"ticket":"xxx",...}
  errorCode=0, ticket=xxx...
  [OK] 验证码通过: ticket=xxx...

[3] 执行签到...
  Result: {"code":200,"data":"ok"}

[SUCCESS] 签到成功！
  最终状态: 2 (期望=2)
```

## 调试模式

如需保存调试图片（用于排查图像识别问题），设置环境变量：
- 变量名：`RAINYUN_DEBUG`
- 变量值：`1`

调试图片将保存在脚本同目录下（文件名：`debug-bg-roundX.jpg`、`debug-sprite-roundX.jpg`）

## 常见问题

### 1. ImportError: No module named 'cv2'
**原因**：未安装 opencv-python  
**解决**：在依赖管理中安装 `opencv-python`

### 2. 未设置 RAINYUN_API_KEY
**原因**：环境变量未配置  
**解决**：在青龙面板环境变量模块添加 `RAINYUN_API_KEY`

### 3. 签到失败 errorCode=50
**原因**：验证码 session 失效，脚本会自动重试  
**解决**：通常是临时问题，脚本会最多重试 5 次

### 4. 图像识别相似度低
**原因**：腾讯验证码图片可能有变化  
**解决**：等待脚本自动重试，通常第 2-3 次会成功

## 注意事项

1. **API Key 安全**：不要在公开场合泄露你的 API Key
2. **网络环境**：青龙面板需要能访问：
   - `https://api.v2.rainyun.com` （雨云 API）
   - `https://turing.captcha.qcloud.com` （腾讯验证码）
3. **执行频率**：不要设置过于频繁的定时任务，建议每天 1 次
4. **日志查看**：定期查看日志，确认签到是否成功

---
name: local-vision
description: 使用本地 ollama 多模态模型 qwen3.5:4b 识别图片内容。当用户发送图片、截图，或需要读取/描述/翻译图片里的文字（OCR）、识别截图内容、理解图片语义时使用。支持剪贴板截图、全屏截图、图片文件三种输入源。本模型本身不支持图像输入时，用此 skill 调用本地视觉模型代替。速度快（约4-8秒），已关闭思考模式。
---

# Local Vision

当需要读取或理解一张图片（图片文件、截图）的内容时，使用本地 ollama 多模态模型 `qwen3.5:4b` 识别。

## 三种输入模式

### 1. 剪贴板截图（用户刚 Win+Shift+S 截图时）

用户发来截图或说"看下这个截图"时，图片通常在剪贴板，直接读剪贴板最快：
```
python "C:\Users\李兴鱼\.config\opencode\skills\local-vision\vision.py"
python "C:\Users\李兴鱼\.config\opencode\skills\local-vision\vision.py" "问题?"
python "C:\Users\李兴鱼\.config\opencode\skills\local-vision\vision.py" clipboard
```

### 2. 全屏截图（模型自己需要看屏幕时）

```
python "C:\Users\李兴鱼\.config\opencode\skills\local-vision\vision.py" screen
python "C:\Users\李兴鱼\.config\opencode\skills\local-vision\vision.py" screen "屏幕上有哪些报错?"
```

### 3. 图片文件

```
python "C:\Users\李兴鱼\.config\opencode\skills\local-vision\vision.py" <图片路径> [提示词]
```

如果图片路径未知，先查 opencode 数据库提取（从 part 表中 type=file 的 base64）或找临时目录下最新图片。

## 输出模式（最后一个参数）

| 模式 | 说明 | 适用场景 |
|---|---|---|
| `brief`（默认） | 简洁回答 ≤200字 | 一般描述 |
| `detail` | 详细描述 | 深入分析 |
| `ocr` | 三字段分离：逐字OCR原文 / 直接观察 / 视觉推理 | 精确读文字、读报错、读聊天记录、游戏HUD |

OCR 模式的三个字段：
1. **exact_ocr_text** — 逐字转录所有可见文字，不改写不翻译
2. **direct_visual_observations** — 客观观察（物体/数值/状态/位置）
3. **visual_reasoning** — 结合问题的推理（每条标"推测："前缀）

用法示例：
```
python "C:\Users\李兴鱼\.config\opencode\skills\local-vision\vision.py" clipboard "报错信息是什么?" ocr
python "C:\Users\李兴鱼\.config\opencode\skills\local-vision\vision.py" <图片路径> ocr
```

## 提示词建议

- 默认简洁回答（≤200字），需要详细时在提示词里写"请详细描述"或直接说 detail
- OCR：`请逐字读出图片中所有文字内容，按原始布局排列`
- 截图理解：`这是用户的一张截图，请详细说明里面有哪些界面元素和文字`
- 提示词含空格要用引号包裹（PowerShell 下）

## 配置

编辑同目录 `config.json` 可改模型、超时、温度。环境变量可覆盖：
`OLLAMA_VISION_MODEL`、`OLLAMA_HOST`、`OLLAMA_TIMEOUT`

## 性能说明（已优化）

- `think: false` 关闭思考模式，识别耗时约4-8秒（相比开启时快约6倍）
- 默认简洁输出，进一步提速
- 模型常驻 GPU 时无需冷启动加载

## 注意

- 依赖：ollama 已安装 + 已拉取 `qwen3.5:4b` + Python 已装 Pillow（截图/剪贴板需要）
- 剪贴板无图片时脚本会报错提示，此时改用文件模式或先让用户截图
- 脚本输出为 UTF-8 编码，PowerShell 直接显示中文可能乱码，但 opencode 捕获到的是正确内容

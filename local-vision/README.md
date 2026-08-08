# Local Vision

给纯文本 LLM（如 DeepSeek）提供本地视觉能力的 **opencode / Claude Code skill**。通过本地 Ollama 多模态模型识别图片，无需联网、无需 API Key、数据不出本机。

> 当你的主模型不支持图像输入时，用它调用本地视觉模型（默认 `qwen3.5:4b`）代替。

## 功能特性

- 🖼️ **三种输入源**：剪贴板截图、全屏截图、指定图片文件
- ⚡ **快**：关闭模型思考模式（`think: false`），识别耗时约 4-8 秒（相比开启时快约 6 倍）
- 📝 **OCR 与视觉推理分离**：`ocr` 模式按三字段输出——逐字原文 / 直接观察 / 视觉推理，客观事实与推测互不混淆
- 🔧 **可配置**：`config.json` 改模型/超时/温度，环境变量可覆盖
- 🔒 **100% 本地**：图片从不离开你的电脑
- 🪟 **Windows 适配**：自动处理中文编码、补齐 `OLLAMA_HOST` 缺失的 `http://` 前缀

## 目录结构

```
local-vision/
├── vision.py       # 核心脚本：多输入源捕获 + Ollama 视觉调用
├── SKILL.md        # Skill 说明（opencode/Claude Code 读取的指令）
├── config.json     # 用户配置：模型、host、超时、温度
├── README.md       # 本文件
└── LICENSE         # MIT
```

## 环境要求

- Python 3.10+（Windows 需额外装 Pillow）
- [Ollama](https://ollama.com) 已安装并运行
- 已拉取视觉模型（推荐）：

```bash
ollama pull qwen3.5:4b
```

安装 Python 依赖：

```bash
pip install Pillow
```

## 安装为 Skill

### opencode

把整个文件夹复制到全局 skill 目录：

```
~/.config/opencode/skills/local-vision/
```

重启 opencode 后，当需要读取图片时模型会自动调用。

### Claude Code

```
~/.claude/skills/local-vision/
```

## 用法

### 输入模式（第一个参数决定图片来源）

| 命令 | 说明 |
|---|---|
| `python vision.py` | 读剪贴板图片（用户刚 Win+Shift+S 截图） |
| `python vision.py "问题?"` | 读剪贴板 + 指定问题 |
| `python vision.py clipboard` | 显式读剪贴板 |
| `python vision.py screen` | 截取整个屏幕 |
| `python vision.py screen "有什么报错?"` | 截屏 + 指定问题 |
| `python vision.py <图片路径>` | 识别指定图片文件 |
| `python vision.py - < image.png` | 从 stdin 读原始字节 |

### 输出模式（最后一个参数）

| 模式 | 说明 | 适用场景 |
|---|---|---|
| `brief`（默认） | 简洁回答 ≤200字，无 markdown | 一般描述 |
| `detail` | 详细描述 | 深入分析 |
| `ocr` | 三字段分离：逐字OCR原文 / 直接观察 / 视觉推理 | 精确读文字、报错、聊天记录、游戏HUD |

示例：

```bash
# 读剪贴板截图，OCR 模式
python vision.py clipboard "报错信息是什么?" ocr

# 全屏截图，详细模式
python vision.py screen "屏幕上有什么" detail

# 识别文件
python vision.py ./screenshot.png ocr
```

## OCR 与视觉推理分离

`ocr` 模式借鉴了 [MM-Bridge](https://github.com/gpdev-Pilcothink/Pilco-mmbridge) 的字段约定，输出分三部分：

```
## 1. exact_ocr_text（逐字OCR原文）
所有可见文字逐字转录，不改写、不翻译、不总结

## 2. direct_visual_observations（直接观察）
客观直接可见的内容：物体、数值、状态、颜色、位置

## 3. visual_reasoning（视觉推理）
结合问题的推理分析，每条标注"推测："前缀
```

这样后面的文本模型能清楚区分"实际看到的"和"模型猜的"。

## 配置

编辑同目录 `config.json`：

```json
{
  "ollama_host": "http://localhost:11434",
  "vision_model": "qwen3.5:4b",
  "timeout_seconds": 120,
  "temperature": 0.1
}
```

环境变量可覆盖配置（优先级更高）：

| 环境变量 | 对应配置 |
|---|---|
| `OLLAMA_HOST` | `ollama_host` |
| `OLLAMA_VISION_MODEL` | `vision_model` |
| `OLLAMA_TIMEOUT` | `timeout_seconds` |

## 性能优化说明

本项目经过了 3 轮优化，测量结果：

| 版本 | 耗时 | 优化点 |
|---|---|---|
| v1 | ~24s | 基础版 |
| v2 | ~4.7s | 关闭思考模式 `think: false` |
| v3 | ~4-8s | 多输入源 + OCR分离 + URL scheme 修复 |

核心提速手段：

1. **`think: false`**：qwen3.5 系列默认思考模式会生成大量推理 token，视觉描述场景下收益低、耗时长，关闭后快约 6 倍
2. **默认 `brief` 模式**：限制输出 ≤200 字、禁用 markdown
3. **模型常驻 GPU**：`ollama ps` 确认模型已加载，避免每次冷启动

## 常见问题

| 问题 | 解决 |
|---|---|
| 无法连接 Ollama | 运行 `ollama serve` 确认服务在跑 |
| 剪贴板无图片 | 先按 Win+Shift+S 截图，或改用文件模式 |
| 模型不存在 | `ollama pull qwen3.5:4b` |
| 报错 unknown url type | 你的 `OLLAMA_HOST` 缺 `http://` 前缀，脚本已自动补全 |
| PowerShell 中文乱码 | 正常现象，脚本输出为 UTF-8，程序捕获到的是正确内容 |

## 致谢

- 输入源（剪贴板/截图/文件）设计参考 [LocalEyes](https://github.com/NoPainNullGain/LocalEyes)
- OCR 与视觉推理分离的字段约定参考 [MM-Bridge](https://github.com/gpdev-Pilcothink/Pilco-mmbridge)

## License

[MIT](./LICENSE)

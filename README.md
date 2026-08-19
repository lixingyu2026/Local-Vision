# Local Vision

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

给纯文本大语言模型提供本地视觉能力的 AI Agent Skill。主模型（如 DeepSeek、Qwen-Coder、CodeLlama 等）不支持图像输入时，通过本地 Ollama 多模态模型识别图片并转成文字，让主模型"看得见"。

全程 100% 本地运行：图片不离开你的电脑，无云端上传、无 API Key、无数据隐私风险。

## 开发背景

在 AI Agent 实际使用中发现三大痛点：

1. **主模型"失明"**：DeepSeek 等推理模型擅长逻辑思考，但完全无法读取图片，收到截图只能报错。
2. **云端方案隐私风险**：传统做法是把图片上传到 GPT-4/Gemini 等云端模型识别，图片暴露在第三方服务器。
3. **流程割裂**：手动把图片给其他工具识别再粘贴结果，打断 Agent 自动化工作流。

Local Vision 用"本地小模型换视觉、主模型做推理"的分工模式解决以上问题。

## 核心功能

### 三种输入源

| 输入方式 | 命令 |
|---|---|
| 剪贴板 | `python vision.py` |
| 全屏截图 | `python vision.py screen` |
| 图片文件 | `python vision.py <路径>` |
| stdin 字节 | `python vision.py -` |

### 三种输出模式

| 模式 | 说明 |
|---|---|
| `brief`（默认） | 简洁回答 ≤200字 |
| `detail` | 详细描述 |
| `ocr` | 三字段分离输出 |

### OCR 与视觉推理分离

借鉴 MM-Bridge 设计，`ocr` 模式强制模型分三字段输出，客观事实与主观推测互不混淆：

- `exact_ocr_text`：逐字转录所有可见文字，不改写不翻译
- `direct_visual_observations`：客观观察（物体/数值/状态/位置）
- `visual_reasoning`：结合问题的推理（每条标注"推测："前缀）

## 性能优化历程

| 版本 | 耗时 |
|---|---|
| v1 | ~24s |
| v2 | ~4.7s |
| v3 | ~4-8s |

关键优化：

- `think: false`：qwen3.5 默认思考模式生成大量推理 token，视觉描述场景收益低、耗时高，关闭后大幅提速
- 默认 `brief` 模式：限制输出 ≤200 字、禁用 markdown
- 模型常驻 GPU：确认模型已加载，避免每次冷启动

## 架构设计

```
用户 / Agent
    │
    ▼
主模型（纯文本，如 DeepSeek）
    │ 需要看图时
    ▼
Local Vision (vision.py)
    │ 捕获图片（剪贴板/截图/文件）
    │ Base64 编码
    ▼
Ollama 视觉模型（qwen3.5:4b）
    │ 返回文字描述
    ▼
主模型读取描述，继续推理
```

设计原则：

- **零 context 开销**：仅在需要时调用，不常驻占用 token
- **分层清晰**：捕获（输入源）与推理（模型调用）解耦，易扩展
- **配置驱动**：模型、host、超时、温度均通过 `config.json` 管理，环境变量可覆盖

## 技术栈

- **Python 3.10+**：主脚本语言
- **Pillow**：截图、剪贴板捕获（ImageGrab）
- **Ollama**：本地模型运行时，通过 `/api/chat` 接口交互
- **Qwen3.5-4B**：默认视觉模型（原生多模态，支持图片输入）
- **兼容平台**：Windows 10/11（完整测试），macOS / Linux（应可用）

## 安装与使用

### 环境准备

```bash
pip install Pillow
ollama pull qwen3.5:4b
```

### 复制到 skill 目录

```bash
# opencode
~/.config/opencode/skills/local-vision/

# Claude Code
~/.claude/skills/local-vision/
```

### 用法

```bash
python vision.py                          # 识别剪贴板截图
python vision.py screen                   # 截全屏识别
python vision.py 图片.png "问题?" ocr     # 文件 + OCR 模式
```

## 局限与展望

**当前局限：**

- OCR 准确度受图片清晰度影响，小字/密集文本可能误读
- 三字段分离靠提示词约束，未做严格 JSON Schema 校验
- 依赖本机硬件，无 GPU 时 4B 模型推理较慢

**未来方向：**

- 图片预处理（裁剪/放大/去噪）提升 OCR 精度
- 多模型动态切换（快速小模型 + 精确大模型）
- 严格结构化输出校验
- 支持视频帧提取

## Contributing

欢迎贡献！请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解分支策略、提交规范与 PR 流程。遇到问题请先搜索 [Issues](https://github.com/lixingyu2026/Local-Vision/issues)。

## License

[MIT](./LICENSE)

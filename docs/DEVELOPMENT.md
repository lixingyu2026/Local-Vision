# 开发指南

Local Vision 的本地开发环境搭建与常用工作流。

## 环境要求

- Python 3.10+
- [Ollama](https://ollama.com/) 已安装并启动
- 视觉模型 `qwen3.5:4b`（或其他 Ollama 多模态模型）

## 安装依赖

```bash
pip install -r requirements.txt
ollama pull qwen3.5:4b
```

## 运行与调试

```bash
# 识别剪贴板截图
python vision.py

# 全屏截图
python vision.py screen

# 指定图片文件 + OCR 模式
python vision.py 图片.png "问题?" ocr
```

### 调试技巧

- 脚本输出为 UTF-8；PowerShell 直接显示中文可能乱码，重定向到文件或通过代理捕获即可
- 修改 `config.json` 可调整 host、模型、超时、温度；环境变量 `OLLAMA_HOST`、`OLLAMA_VISION_MODEL`、`OLLAMA_TIMEOUT` 可覆盖
- 剪贴板无图片时脚本会报错提示，此时改用文件模式

## 手动验证清单

提交前请确认：

- [ ] 三种输入源（剪贴板 / 截图 / 文件）均可正常工作
- [ ] `brief` / `detail` / `ocr` 三种模式输出符合预期
- [ ] `ocr` 模式三字段（`exact_ocr_text` / `direct_visual_observations` / `visual_reasoning`）正确分离
- [ ] 配置与环境变量覆盖生效

## 提交与发布

遵循 `CONTRIBUTING.md` 中的分支策略与 Conventional Commits 规范。

版本号更新：修改 `pyproject.toml` 中的 `version`，并同步 `docs/CHANGELOG.md`。

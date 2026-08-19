# 贡献指南

欢迎为 Local Vision 贡献力量！无论是报告问题、提交功能、还是改进文档，都感谢你的参与。

## 如何开始

1. **Fork 本仓库** 到你的 GitHub 账号
2. **克隆** 到本地：`git clone https://github.com/<你的用户名>/Local-Vision.git`
3. **创建特性分支**（见下方分支策略）
4. 提交修改并推送到你的 fork，然后创建 **Pull Request**

## 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 拉取视觉模型（如未拉取）
ollama pull qwen3.5:4b

# 确保 Ollama 服务已启动
ollama serve
```

## 分支策略

从 `main` 分支创建特性分支，命名遵循以下约定：

| 类型 | 前缀 | 示例 |
|---|---|---|
| 功能 | `feat/` | `feat/ocr-preprocessing` |
| 修复 | `fix/` | `fix/clipboard-error` |
| 文档 | `docs/` | `docs/readme-update` |
| 重构 | `refactor/` | `refactor/config-loading` |

## 提交规范

使用 **Conventional Commits** 风格：

```
<type>(<scope>): <subject>

<可选 body>
```

常见类型：`feat`、`fix`、`docs`、`refactor`、`perf`、`test`、`chore`。

示例：`feat: 支持图片预处理提升 OCR 精度`

## Pull Request 流程

1. 确保基于最新的 `main`：`git pull --rebase origin main`
2. 自测改动（见下方测试要求）
3. 填写 PR 模板，关联相关 Issue
4. 等待 review，按反馈修改

## 测试要求

本项目为轻量 CLI 脚本，尚无自动化测试框架。请在提交前人工验证：

- `python vision.py <图片路径>` 能正常输出描述
- 剪贴板 / 截图 / 文件三种输入源均可用
- 修改 `config.json` 后配置能正确生效

如果新增了需要自动化测试的逻辑，欢迎补上 `pytest` 测试并说明运行方式。

## 编码规范

- 遵循 Python 3.10+ 语法，保持代码风格与现有 `vision.py` 一致
- 函数命名使用 `snake_case`，模块级常量使用 `UPPER_SNAKE_CASE`
- 新功能需同步更新 README 中的对应说明
- 保持脚本对 Windows / macOS / Linux 的兼容性

## 报告问题

遇到问题请先搜索 [Issues](https://github.com/lixingyu2026/Local-Vision/issues) 是否已有相关记录，没有再新建，并填写 Issue 模板。

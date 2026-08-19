# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 约定，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added

- 开源仓库完善：`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`、`SECURITY.md`
- GitHub Issue / PR 模板（`.github/`）
- `pyproject.toml` 项目元数据
- `docs/DEVELOPMENT.md` 开发指南

## [1.0.0] - 2026-08-19

首个公开版本。

### Added

- 三种输入源：剪贴板、全屏截图、图片文件、stdin 字节
- 三种输出模式：`brief`（默认）、`detail`、`ocr`
- OCR 与视觉推理分离（借鉴 MM-Bridge 字段约定）
- `think: false` 关闭思考模式，识别耗时降至约 4-8 秒
- 配置驱动：`config.json` + 环境变量覆盖

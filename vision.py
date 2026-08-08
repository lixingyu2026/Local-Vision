#!/usr/bin/env python3
"""
Local Vision — 给纯文本模型提供本地视觉能力（基于 Ollama 多模态模型）。

四种输入模式：
  1. 剪贴板（用户刚 Win+Shift+S 截图）:
     python vision.py                         → 读用户剪贴板图片
     python vision.py "问题?"                 → 读剪贴板 + 指定问题
     python vision.py clipboard "问题?"       → 同上，显式模式
  2. 全屏截图（模型自己截屏看）:
     python vision.py screen                  → 截全屏并识别
     python vision.py screen "什么错误?"      → 截屏 + 指定问题
  3. 指定图片文件:
     python vision.py <图片路径> [提示词] [brief|detail|ocr]
  4. stdin 原始字节:
     python vision.py - < image.png

  模式说明:
    brief  (默认) 简洁回答 ≤200字，无 markdown
    detail         详细描述
    ocr            按三字段分离输出: 逐字OCR原文 / 直接观察 / 视觉推理

配置（config.json，可用环境变量覆盖）:
  ollama_host / OLLAMA_HOST
  vision_model / OLLAMA_VISION_MODEL
  timeout_seconds / OLLAMA_TIMEOUT
  temperature
"""

import sys
import os
import io
import json
import base64
import urllib.request
import urllib.error
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent


# ── 配置加载：硬编码默认值 → config.json → 环境变量 ───────────────────────────

def _load_config() -> dict:
    cfg = {}
    config_path = BASE_DIR / "config.json"
    try:
        if config_path.is_file():
            with open(config_path, encoding="utf-8") as f:
                cfg.update(json.load(f))
    except (json.JSONDecodeError, OSError):
        pass
    env_map = {
        "OLLAMA_HOST": "ollama_host",
        "OLLAMA_VISION_MODEL": "vision_model",
        "OLLAMA_TIMEOUT": "timeout_seconds",
    }
    for env_var, cfg_key in env_map.items():
        val = os.environ.get(env_var)
        if val:
            cfg[cfg_key] = val
    return cfg


_cfg = _load_config()

OLLAMA_HOST = _cfg.get("ollama_host", "http://localhost:11434")
if OLLAMA_HOST and not OLLAMA_HOST.startswith("http"):
    OLLAMA_HOST = f"http://{OLLAMA_HOST}"
OLLAMA_MODEL = _cfg.get("vision_model", "qwen3.5:4b")
TIMEOUT_SECONDS = int(_cfg.get("timeout_seconds", 120))
TEMPERATURE = float(_cfg.get("temperature", 0.1))

DEFAULT_PROMPT = "请描述这张图片的内容。"

# OCR 与视觉推理分离模式提示词（借鉴 MM-Bridge 的字段约定）
OCR_PROMPT = """请对这张图片按以下三个字段输出，字段之间用分隔线隔开：

## 1. exact_ocr_text（逐字OCR原文）
把图片中所有可见文字逐字转录出来。不翻译、不改正、不总结、不推断。\
保留原始布局顺序（从上到下，从左到右）。若某处文字不清晰，标注[不清晰]。\
如果图片没有文字，写"无文字"。

## 2. direct_visual_observations（直接观察）
只描述客观直接可见的内容：物体、数值、状态、颜色、位置（如"左上角有红色进度条"）。\
不要加入任何推测或解释。

## 3. visual_reasoning（视觉推理）
结合用户问题（如果有）对图片内容进行推理分析。每条推理都要明确标注"推测："前缀，\
与客观事实区分开。若无需推理，写"无"。

【注意】逐字转录场景下，exact_ocr_text 必须使用原文，禁止用翻译或改写代替。"""


# ── 图片来源 ─────────────────────────────────────────────────────────────────

def _capture_screen() -> bytes:
    """截取整个屏幕，返回 PNG 字节。"""
    try:
        from PIL import ImageGrab
    except ImportError:
        sys.exit("错误: 需要 Pillow，请执行 pip install Pillow")
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _clipboard_image():
    """从系统剪贴板读取图片，返回 PNG 字节或 None。"""
    try:
        from PIL import ImageGrab
    except ImportError:
        sys.exit("错误: 需要 Pillow，请执行 pip install Pillow")
    img = ImageGrab.grabclipboard()
    if img is None:
        return None
    if isinstance(img, list):
        if img and os.path.isfile(str(img[0])):
            return Path(str(img[0])).read_bytes()
        return None
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _load_image_bytes(source: str) -> bytes:
    """把来源字符串解析为图片字节。"""
    if source in ("screen", "screenshot", "s"):
        return _capture_screen()
    if source in ("clipboard", "c"):
        data = _clipboard_image()
        if data is None:
            sys.exit("错误: 剪贴板中没有图片。请先按 Win+Shift+S 截图。")
        return data
    if source == "-":
        return sys.stdin.buffer.read()
    path = Path(source)
    if not path.is_file():
        sys.exit(f"错误: 文件不存在 — '{source}'")
    return path.read_bytes()


# ── Ollama 调用 ──────────────────────────────────────────────────────────────

def describe_image(image_bytes: bytes, prompt: str) -> str:
    """把图片发给 Ollama 视觉模型，返回文字描述。"""
    img_b64 = base64.b64encode(image_bytes).decode()

    body = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "think": False,  # 关键提速：关闭思考模式，约快6倍
        "options": {"temperature": TEMPERATURE},
        "messages": [{"role": "user", "content": prompt, "images": [img_b64]}],
    }
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["message"].get("content", "")
        if not content:
            thinking = data["message"].get("thinking", "")
            return f"模型未输出内容。thinking: {thinking[:300]}"
        return content
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "refused" in reason.lower() or "61" in reason:
            sys.exit(f"错误: 无法连接 Ollama {OLLAMA_HOST}。请先运行 ollama serve")
        sys.exit(f"连接 Ollama 失败: {reason}")
    except KeyError:
        sys.exit("Ollama 返回格式异常。")
    except Exception as e:
        sys.exit(f"Ollama API 错误: {e}")


# ── 主入口 ───────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    mode = "brief"

    # 解析模式参数（最后一个参数若是 brief/detail/ocr 则提取）
    if args and args[-1] in ("brief", "detail", "ocr"):
        mode = args[-1]
        args = args[:-1]

    # 无参数 = 读剪贴板
    if not args:
        source, prompt = "clipboard", DEFAULT_PROMPT
    elif args[0] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)
    elif args[0] in ("screen", "screenshot", "s", "clipboard", "c", "-"):
        source = args[0]
        prompt = args[1] if len(args) > 1 else DEFAULT_PROMPT
    elif Path(args[0]).is_file():
        source = args[0]
        prompt = args[1] if len(args) > 1 else DEFAULT_PROMPT
    else:
        # 单个非文件参数 → 视为问题，配剪贴板
        source = "clipboard"
        prompt = " ".join(args)

    if mode == "ocr":
        detail = f"{OCR_PROMPT}\n用户问题: {prompt if prompt != DEFAULT_PROMPT else '请描述这张图片的内容'}"
    elif mode == "detail":
        detail = prompt
    else:
        # brief 默认：限制输出长度
        detail = f"{prompt}\n请用简洁的语言回答，不超过200字，不要使用markdown格式。"

    image_bytes = _load_image_bytes(source)
    description = describe_image(image_bytes, detail)
    print(description)


if __name__ == "__main__":
    main()

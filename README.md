# 面试录音转 Markdown 文字稿

把面试录音（`.mp3` / `.m4a` 等）转写成 **Markdown 文字稿**，方便复制给大模型（如 Claude、ChatGPT）来评估你的面试表现。

- 🔒 **本地离线**：用 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在你自己的电脑上转写，录音**不外传**。
- 🀄 **中英混合**：忠实转写以中文为主、夹杂英文的内容，**不翻译**。
- 📝 **按句子断行**：默认输出纯文字稿，自动按完整句子换行，读起来更顺。
- 🕒 **时间戳可开关**：需要时加上 `--timestamps` 即可。
- 🧩 **无需单独装 ffmpeg**：faster-whisper 自带音频解码。

---

## 1. 环境要求

- Python 3.9 或更高版本
- 联网一次（首次自动下载模型，之后可离线使用）

## 2. 安装

建议使用虚拟环境，避免污染系统 Python：

```bash
# 进入项目目录
cd Audio_to_Text

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 3. 使用

把录音放进 `recordings/` 文件夹，然后运行：

```bash
python transcribe.py recordings/interview.m4a
```

转写完成后，结果会保存到 `transcripts/interview.md`。

> 首次运行会自动下载所选模型（默认 `large-v3-turbo` 约 0.8GB），需要几分钟；之后离线可用。

### 常用选项

| 命令 | 作用 |
|------|------|
| `python transcribe.py recordings/x.m4a` | 默认：`large-v3-turbo` 模型 + 纯文字稿（按句子断行） |
| `python transcribe.py recordings/x.m4a --timestamps` | 在每行文字前加时间戳 |
| `python transcribe.py recordings/x.m4a --model large-v3` | 用最高精度模型（更慢） |
| `python transcribe.py recordings/x.m4a --model small` | 用更小更快的模型（准确率略低） |
| `python transcribe.py recordings/x.m4a --language zh` | 指定中文（默认自动检测） |
| `python transcribe.py recordings/x.m4a --output out/my.md` | 自定义输出路径 |

查看全部参数：

```bash
python transcribe.py --help
```

> **改默认模型**：直接在命令行用 `--model` 临时切换即可；如果想永久改默认值，编辑 `transcribe.py` 里 `--model` 参数的 `default=` 一行。

### 模型选择

| 模型 | 大小(int8) | 速度 | 准确率 | 说明 |
|------|-----------|------|--------|------|
| `tiny` / `base` | 最小 | 最快 | 一般 | 仅供快速试跑 |
| `small` | ~0.5GB | 快 | 不错 | 电脑较慢时的折中 |
| `large-v3-turbo` ⭐默认 | ~0.8GB | 快 | 高（接近 large-v3） | **速度与精度的最佳平衡** |
| `large-v3` | ~1.6GB | 最慢 | 最高 | 口音重 / 嘈杂 / 要求极致精度 |

`large-v3-turbo` 是 `large-v3` 的加速版，准确率接近但快 5–8 倍。在 CPU（如 Apple 芯片 Mac）上转写长录音时，turbo 体验明显更好。

## 4. 输出示例

默认（纯文字稿，按完整句子断行）：

```markdown
# 面试录音转写：interview

- **时长**: 00:42:15
- **检测语言**: zh
- **生成时间**: 2026-06-11 18:30

---

你好，请先简单做个自我介绍。

好的，我叫……我之前在一家 startup 做 backend developer。
```

加上 `--timestamps` 则每段前带 `[hh:mm:ss → hh:mm:ss]` 时间戳。

## 5. 发给大模型评估（提示词模板）

把生成的 Markdown 文字稿粘贴到下面这段提示词后面，发给大模型即可：

```text
你是一位资深的技术面试官 / 面试教练。下面是我一场面试的录音文字稿（中文为主，可能夹杂英文）。
请帮我做一次复盘评估：

1. 总体表现打分（1–10）并说明理由。
2. 我回答得好的地方（具体引用文字稿内容）。
3. 明显的不足或可改进之处（沟通、结构、深度、技术准确性等）。
4. 针对每个问题，给出更好的回答思路或示例。
5. 下次面试可以重点准备的 3 件事。

文字稿如下：
---
（在这里粘贴 transcripts/ 里的 Markdown 内容）
```

## 6. 隐私说明

- 录音和转写稿分别放在 `recordings/` 和 `transcripts/`，已在 `.gitignore` 中**排除**，不会被上传到 GitHub。
- 仓库里只会包含代码、README 和配置；你的面试内容**只留在本地**。
- 是否把文字稿发给第三方大模型由你自己决定——发送前请确认其中不含你不愿分享的敏感信息。

## 7. 目录结构

```
Audio_to_Text/
├── transcribe.py        # 主程序
├── requirements.txt     # 依赖
├── README.md            # 本文件
├── .gitignore           # 忽略录音 / 转写稿 / 缓存
├── recordings/          # 放录音（本地保留）
└── transcripts/         # 输出 Markdown（本地保留）
```

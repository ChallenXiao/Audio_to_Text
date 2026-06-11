# 面试录音转 Markdown 文字稿

把面试录音（`.mp3` / `.m4a` 等）转写成 **Markdown 文字稿**，方便复制给大模型（如 Claude、ChatGPT）来评估你的面试表现。

- 🔒 **本地离线**：用 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在你自己的电脑上转写，录音**不外传**。
- 🀄 **中英混合**：忠实转写以中文为主、夹杂英文的内容，**不翻译**。
- 🕒 **时间戳可开关**：默认带时间戳，也可输出纯文字稿。
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

> 首次运行会自动下载所选模型（`medium` 约 1.5GB），需要几分钟；之后离线可用。

### 常用选项

| 命令 | 作用 |
|------|------|
| `python transcribe.py recordings/x.m4a` | 默认：`medium` 模型 + 带时间戳 |
| `python transcribe.py recordings/x.m4a --no-timestamps` | 输出纯文字稿（更适合直接喂给大模型） |
| `python transcribe.py recordings/x.m4a --model small` | 用更小更快的模型（准确率略低） |
| `python transcribe.py recordings/x.m4a --language zh` | 指定中文（默认自动检测） |
| `python transcribe.py recordings/x.m4a --output out/my.md` | 自定义输出路径 |

查看全部参数：

```bash
python transcribe.py --help
```

### 模型选择

| 模型 | 大小 | 速度 | 准确率 |
|------|------|------|--------|
| `tiny` / `base` | 最小 | 最快 | 一般 |
| `small` | 较小 | 较快 | 不错 |
| `medium` ⭐默认 | 中等 | 中等 | 好 |
| `large-v3` | 最大 | 最慢 | 最好 |

录音较长、电脑较慢时，可先用 `--model small` 试一遍。

## 4. 输出示例

带时间戳（默认）：

```markdown
# 面试录音转写：interview

- **时长**: 00:42:15
- **检测语言**: zh
- **生成时间**: 2026-06-11 18:30

---

**[00:00:00 → 00:00:06]** 你好，请先简单做个自我介绍。

**[00:00:06 → 00:00:24]** 好的，我叫……我之前在一家 startup 做 backend developer。
```

加上 `--no-timestamps` 则去掉每行前的时间戳，输出纯文字段落。

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

# 面试录音转 Markdown 文字稿 — 设计文档

- **日期**: 2026-06-11
- **状态**: 待用户确认

## 目标

把本地的面试录音(`.mp3` / `.m4a`)转写成带可选时间戳的 Markdown 文字稿,
方便把文字稿发给大模型来评估面试表现。代码可上传 GitHub,录音与转写稿保留在本地。

## 关键决策(已确认)

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 转写引擎 | 本地 `faster-whisper` | 离线、免费、隐私(录音不外传) |
| 是否需要 ffmpeg | 否 | faster-whisper 经 PyAV 自带音频解码 |
| 任务类型 | `transcribe`(忠实转写) | 以中文为主、夹杂英文时准确保留原文,**不翻译** |
| 默认模型 | `medium` | 准确率与速度的平衡,适合中英混合 |
| 语言 | 默认自动检测,可用 `--language zh` 指定 | 中文为主夹杂英文,自动检测通常即可 |
| 说话人区分 | 不做 | 保持简单可靠;由大模型在评估时自行推断 |
| 时间戳 | 可开关,默认开启 | 关闭后输出纯文字稿,更适合直接喂给大模型 |

## 目录结构

```
Audio_to_Text/
├── transcribe.py        # 主程序
├── requirements.txt     # 依赖(faster-whisper)
├── README.md            # 使用说明 + 给大模型的评估提示词
├── .gitignore           # 忽略录音、转写结果、Python 缓存、虚拟环境
├── recordings/          # 放录音(本地保留,不上传)
│   └── .gitkeep
├── transcripts/         # 输出 markdown(本地保留,不上传)
│   └── .gitkeep
└── docs/                # 本设计文档
```

## 命令行接口

```
python transcribe.py <音频路径> [选项]
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `audio`(位置参数) | 必填 | 音频文件路径,如 `recordings/interview.m4a` |
| `--model` | `medium` | 模型大小:tiny/base/small/medium/large-v3,越大越准越慢 |
| `--language` | `auto` | 语言代码,如 `zh`、`en`;`auto` 为自动检测 |
| `--output` | `transcripts/<同名>.md` | 自定义输出路径 |
| `--timestamps / --no-timestamps` | `--timestamps` | 是否在每行文字前加 `[hh:mm:ss → hh:mm:ss]` |
| `--device` | `auto` | `cpu` / `cuda` / `auto` |

## 处理流程

1. 校验音频文件存在且后缀为 `.mp3` / `.m4a`(其他常见格式也放行,给出提示)。
2. 加载 faster-whisper 模型(首次运行自动下载到本地缓存,几百 MB;之后离线可用)。
3. 调用 `model.transcribe(audio, task="transcribe", language=...)`,得到段落生成器。
4. 遍历段落,实时打印进度(当前时间点 / 已转写文字),收集结果。
5. 按 `--timestamps` 决定是否在每段前加时间戳,生成 Markdown。
6. 写入输出文件,打印输出路径与检测到的语言、总时长。

## 模块划分(单文件,函数清晰隔离)

- `parse_args()` — 解析命令行参数。
- `format_timestamp(seconds) -> str` — 秒数转 `hh:mm:ss`。
- `transcribe_audio(path, model, language, device) -> (segments, info)` — 调用 faster-whisper,返回段落列表与元信息。
- `render_markdown(segments, info, source_name, with_timestamps) -> str` — 生成 Markdown 文本。
- `main()` — 串联:校验 → 转写(带进度) → 渲染 → 写文件。

每个函数职责单一、可单独测试;转写与渲染解耦,方便日后改输出格式。

## Markdown 输出格式

带时间戳(默认):

```markdown
# 面试录音转写：interview

- **时长**: 00:42:15
- **模型**: medium
- **检测语言**: zh
- **生成时间**: 2026-06-11 18:30

---

**[00:00:00 → 00:00:06]** 你好，请先简单做个自我介绍。

**[00:00:06 → 00:00:24]** 好的，我叫……我之前在一家 startup 做 backend developer。
```

不带时间戳(`--no-timestamps`):

```markdown
# 面试录音转写：interview

- **时长**: 00:42:15
- **模型**: medium
- **检测语言**: zh
- **生成时间**: 2026-06-11 18:30

---

你好，请先简单做个自我介绍。

好的，我叫……我之前在一家 startup 做 backend developer。
```

## 错误处理

- 文件不存在 → 清晰报错并退出(非零退出码)。
- 缺少依赖(`faster-whisper` 未安装)→ 捕获 ImportError,提示 `pip install -r requirements.txt`。
- 不支持的后缀 → 警告但仍尝试转写(Whisper 支持多种格式)。
- 转写过程异常 → 打印异常信息并以非零码退出。

## .gitignore 策略

忽略:
- `recordings/*` 与 `transcripts/*`(保留各自的 `.gitkeep`)
- `__pycache__/`、`*.pyc`
- `.venv/`、`venv/`、`env/`
- 常见系统/编辑器文件(`.DS_Store`、`.idea/`、`.vscode/`)

效果:代码、README、配置上 GitHub;录音与转写稿留本地。

## README 内容

- 简介与功能
- 环境要求(Python 3.9+;无需单独装 ffmpeg)
- 安装步骤(建议虚拟环境 + `pip install -r requirements.txt`)
- 使用示例(基础用法、换模型、关时间戳、指定语言)
- 输出说明
- 一段可直接复制、发给大模型的「面试评估提示词」模板
- 隐私说明(录音不外传、.gitignore 已配置)

## 不做的事(YAGNI)

- 不做说话人区分(diarization)。
- 不做翻译。
- 不做图形界面 / 批量目录扫描(后续需要再加)。
- 不做云端 API 后端。

## 测试策略

- `format_timestamp` 与 `render_markdown` 为纯函数,用构造的假 segment 做单元测试(不依赖真实音频/模型)。
- 转写主流程用一段很短的样例音频做一次手动冒烟测试。
```
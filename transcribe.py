#!/usr/bin/env python3
"""把面试录音（.mp3 / .m4a 等）转写成带可选时间戳的 Markdown 文字稿。

使用本地的 faster-whisper，离线运行、录音不外传。
忠实转写（不翻译），适合以中文为主、夹杂英文的面试录音。

示例：
    python transcribe.py recordings/interview.m4a
    python transcribe.py recordings/interview.mp3 --model small --no-timestamps
    python transcribe.py recordings/interview.m4a --language zh
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 这些后缀会被正常处理；其他后缀会给出提示但仍尝试转写。
COMMON_AUDIO_SUFFIXES = {".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg", ".opus", ".mp4"}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="把面试录音转写成 Markdown 文字稿（本地、离线、不翻译）。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("audio", help="音频文件路径，如 recordings/interview.m4a")
    parser.add_argument(
        "--model",
        default="medium",
        help="模型大小：tiny / base / small / medium / large-v3，越大越准越慢",
    )
    parser.add_argument(
        "--language",
        default="auto",
        help="语言代码，如 zh、en；auto 表示自动检测",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出 Markdown 路径，默认 transcripts/<同名>.md",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="计算设备；auto 在普通电脑上使用 CPU",
    )

    ts = parser.add_mutually_exclusive_group()
    ts.add_argument(
        "--timestamps",
        dest="timestamps",
        action="store_true",
        help="在每行文字前加时间戳（默认）",
    )
    ts.add_argument(
        "--no-timestamps",
        dest="timestamps",
        action="store_false",
        help="不加时间戳，输出纯文字稿（更适合直接喂给大模型）",
    )
    parser.set_defaults(timestamps=True)

    return parser.parse_args(argv)


def format_timestamp(seconds):
    """把秒数格式化成 hh:mm:ss。"""
    if seconds is None or seconds < 0:
        seconds = 0
    total = int(round(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def resolve_device(device):
    """把 auto 解析成具体设备与计算精度。

    普通电脑（含 Apple 芯片 Mac）走 CPU + int8，速度最佳且到处可用。
    需要 GPU 时显式传 --device cuda。
    """
    if device == "cuda":
        return "cuda", "float16"
    # auto 或 cpu 都落到 CPU；int8 在 CPU 上明显更快
    return "cpu", "int8"


def transcribe_audio(audio_path, model_size, language, device):
    """调用 faster-whisper 转写，返回 (segments, info)。

    segments 是一个段落列表，每个元素有 start / end / text。
    info 含检测到的语言与音频时长。
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:  # 依赖缺失时给出可操作提示
        raise SystemExit(
            "未找到 faster-whisper，请先安装依赖：\n    pip install -r requirements.txt"
        ) from exc

    ct2_device, compute_type = resolve_device(device)
    lang = None if language == "auto" else language

    print(f"加载模型：{model_size}（{ct2_device} / {compute_type}）……")
    print("首次运行会自动下载模型，可能需要几分钟，之后离线可用。")
    model = WhisperModel(model_size, device=ct2_device, compute_type=compute_type)

    print(f"开始转写：{audio_path}")
    segment_iter, info = model.transcribe(
        str(audio_path),
        task="transcribe",  # 忠实转写，不翻译
        language=lang,
        beam_size=5,
        vad_filter=True,  # 跳过长静音，输出更干净
    )

    duration = getattr(info, "duration", 0) or 0
    detected = getattr(info, "language", None) or (lang or "未知")
    print(f"检测语言：{detected}    总时长：{format_timestamp(duration)}")

    segments = []
    for seg in segment_iter:
        segments.append(seg)
        # 实时进度：以当前段落结束时间相对总时长估算
        if duration:
            pct = min(100, int(seg.end / duration * 100))
            print(f"\r进度 {pct:3d}%  [{format_timestamp(seg.end)}]", end="", flush=True)
    print()  # 进度行收尾换行

    return segments, info


def render_markdown(segments, info, source_name, with_timestamps):
    """根据转写结果生成 Markdown 文本。"""
    duration = getattr(info, "duration", 0) or 0
    detected = getattr(info, "language", None) or "未知"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# 面试录音转写：{source_name}",
        "",
        f"- **时长**: {format_timestamp(duration)}",
        f"- **检测语言**: {detected}",
        f"- **生成时间**: {now}",
        "",
        "---",
        "",
    ]

    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        if with_timestamps:
            stamp = f"[{format_timestamp(seg.start)} → {format_timestamp(seg.end)}]"
            lines.append(f"**{stamp}** {text}")
        else:
            lines.append(text)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    args = parse_args(argv)

    audio_path = Path(args.audio)
    if not audio_path.is_file():
        raise SystemExit(f"找不到音频文件：{audio_path}")

    if audio_path.suffix.lower() not in COMMON_AUDIO_SUFFIXES:
        print(f"提示：后缀 {audio_path.suffix} 不在常见列表中，仍会尝试转写。")

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("transcripts") / f"{audio_path.stem}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        segments, info = transcribe_audio(
            audio_path, args.model, args.language, args.device
        )
    except SystemExit:
        raise
    except Exception as exc:  # 转写过程中的其他异常
        raise SystemExit(f"转写失败：{exc}") from exc

    markdown = render_markdown(
        segments, info, audio_path.stem, with_timestamps=args.timestamps
    )
    output_path.write_text(markdown, encoding="utf-8")

    print(f"完成！已写入：{output_path}")
    print("把该 Markdown 内容连同 README 里的「评估提示词」一起发给大模型即可。")


if __name__ == "__main__":
    main()

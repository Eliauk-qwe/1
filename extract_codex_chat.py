import json
from pathlib import Path


source_file = Path(
    "/home/wly/.codex/sessions/2026/06/22/"
    "rollout-2026-06-22T16-33-04-"
    "019eee76-3553-7862-a030-87aadc43a5ba.jsonl"
)

output_file = Path("记录/codex-dialogue-2026-06-22.md")


def extract_text(content: object) -> str:
    """从 Codex 消息内容中提取纯文本。"""

    if isinstance(content, str):
        return content.strip()

    if not isinstance(content, list):
        return ""

    text_parts: list[str] = []

    for item in content:
        if not isinstance(item, dict):
            continue

        item_type = item.get("type")

        if item_type in {"input_text", "output_text", "text"}:
            text = item.get("text", "")
            if isinstance(text, str) and text.strip():
                text_parts.append(text.strip())

    return "\n\n".join(text_parts)


dialogue: list[str] = []

with source_file.open("r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()

        if not line:
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        payload = record.get("payload", record)

        if not isinstance(payload, dict):
            continue

        if payload.get("type") != "message":
            continue

        role = payload.get("role")

        if role not in {"user", "assistant"}:
            continue

        text = extract_text(payload.get("content"))

        if not text:
            continue

        speaker = "我" if role == "user" else "Codex"

        dialogue.append(f"## {speaker}\n\n{text}\n")


output_file.parent.mkdir(parents=True, exist_ok=True)

output_file.write_text(
    "# 我和 Codex 的对话记录\n\n" + "\n---\n\n".join(dialogue),
    encoding="utf-8",
)

print(f"已提取 {len(dialogue)} 条对话")
print(f"输出文件：{output_file}")

#!/usr/bin/env python3
"""Check Chinese-only onboarding, section layout, and preview budgets."""
from pathlib import Path
import re
import struct

root = Path(__file__).resolve().parents[1]
cn = (root / "README.md").read_text()
assert cn == (root / "README.zh-CN.md").read_text()
assert "# AI 火柴人动画画风大全" in cn
assert "## 你的作品，也可以成为下一个案例" not in cn
assert "## 下一种火柴人，你来点" in cn
community = cn.split("## 下一种火柴人，你来点", 1)[1].split("## Star 增长曲线", 1)[0]
assert community.count("[Issues]") == 1, "Use one combined community entry"
assert community.index("想看新画风、分享作品或反馈问题") > community.index("风格 9")
assert "## 从文案到视频，五步走" not in cn
assert "## 你会拿到什么" not in cn
assert "## 它帮你做什么" in cn and "## 开始使用" in cn
install = cn.split("### 1. 安装 Skill", 1)[1].split("<!-- readme:workflow -->", 1)[0]
assert "帮我安装这个 Skill：\nhttps://github.com/kaomei/stickman-video-director" in install
assert len(install.strip()) < 130, "Keep the installation entry short"
for unnecessary in ("$skill-installer", "重启", "官方安装说明", "<details>", "WorkBuddy", "git clone", "references"):
    assert unnecessary not in install, unnecessary
topic = cn.split("### 2. 给一个话题", 1)[1].split("### 3.", 1)[0]
assert "把话题、文案或文章直接发给 AI" in topic
assert "帮我做一个《人类的第一份工作是怎么来的？》的火柴人视频。" in topic
for preset in ("$directing", "16:9", "美式男声", "先给我导演提案", "想换个画风"):
    assert preset not in topic, "Topic entry must not require a prefilled production request"
assert "### 3. 跟着引导，确认提案" in cn
assert "Skill 会主动询问；时长可指定，默认 60 秒" in cn
assert "你确认后，它才输出最终分段提示词" in cn
guided_demo = cn.split("### 3. 跟着引导，确认提案", 1)[1].split("### 4.", 1)[0]
for required in ("《人类的第一份工作是怎么来的？》", "横屏 16:9", "风格 3 史前黑色幽默", "制作前确认的分镜提案", "| 时间 | 画面与动作 | 配音文案 |"):
    assert required in guided_demo, required
storyboard_rows = re.findall(r"^\| \*\*(?:0–10|10–20|20–30)s：.*$", guided_demo, re.MULTILINE)
assert len(storyboard_rows) == 3, "Show three concise ten-second storyboard rows"
assert all(row.count("|") == 4 for row in storyboard_rows)
approved_voiceover = (
    "Ten thousand years ago, one man finally solved all his problems. He shut them outside.",
    "Then someone offered him food… in exchange for a small favor. Congratulations. Employment was invented.",
    "The reward got smaller. The workload got bigger. And somehow… they called that progress.",
)
for row, voiceover in zip(storyboard_rows, approved_voiceover):
    assert voiceover in row, "Preserve the approved sample narration verbatim"
for removed in ("简化对话示意", "> **AI", "> **你", "首段英文旁白", "中文参考", "搬石头", "下面按已有样片整理", "洞口能挡住野兽", "英文配音"):
    assert removed not in guided_demo, removed
assert guided_demo.index("选好设置") < guided_demo.index("| 时间 |") < guided_demo.index("你确认后，它才输出最终分段提示词")
assert "### 4. 生成视频，剪辑成片" in cn
assert "## 最近更新" in cn and "CHANGELOG.zh-CN.md" in cn
assert "## Star 增长曲线" in cn and "[MIT License](LICENSE)" in cn
assert cn.count("<details>") == cn.count("</details>")
assert cn.count('<div align="center">') == cn.count("</div>")

for removed in ("样片同款主题，直接试", "example-overthinking", "展开看已有导演预案节选", "你给的内容："):
    assert removed not in cn, "Removed example must not leave text or dangling links"
assert (root / "skills/directing-stickman-videos/references/examples.md").exists()
tips = cn.split("## 使用小贴士", 1)[1].split("## 最近更新", 1)[0]
assert "<details>" not in tips and "<summary>" not in tips
assert tips.index("**选横屏还是竖屏？**") < tips.index("| 比例 | 适合平台 | 构图重点 |") < tips.index("- 人物、道具和旁白设定")

for link in re.findall(r"\]\(([^)]+)\)", cn):
    if "://" not in link and not link.startswith("#"):
        assert (root / link.split("#")[0]).exists(), link

previews = sorted(set(re.findall(r'src="(assets/readme/previews/[^" ]+\.gif)"', cn)))
assert len(previews) == 8
old_bytes = new_bytes = 0
for preview in previews:
    optimized = root / preview
    original = root / "assets/readme" / optimized.name
    assert optimized.exists()
    header = optimized.read_bytes()[:10]
    assert header[:6] in (b"GIF87a", b"GIF89a")
    assert struct.unpack("<HH", header[6:10]) == (400, 225)
    assert optimized.stat().st_size < original.stat().st_size
    old_bytes += original.stat().st_size
    new_bytes += optimized.stat().st_size
assert new_bytes < old_bytes * 0.6, "Preview total should shrink by at least 40%"

for lang in ("en", "ja", "ko", "pt-BR"):
    text = (root / f"README.{lang}.md").read_text()
    assert "assets/readme/previews/" in text, "Localized pages use the same lightweight previews"

print(f"Chinese onboarding passed; previews {old_bytes:,} -> {new_bytes:,} bytes ({1-new_bytes/old_bytes:.1%} smaller).")

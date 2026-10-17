#!/usr/bin/env python3
"""Check locale parity without requiring literal translations."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
source = (root / "README.md").read_text()
preview_pattern = r'src="(assets/readme/previews/[^" ]+\.gif)"'
expected_previews = set(re.findall(preview_pattern, source))
assert len(expected_previews) == 8
approved_voiceover = (
    "Ten thousand years ago, one man finally solved all his problems. He shut them outside.",
    "Then someone offered him food… in exchange for a small favor. Congratulations. Employment was invented.",
    "The reward got smaller. The workload got bigger. And somehow… they called that progress.",
)
locales = {
    "en": ("English", "# AI Stickman Animation Style Library", "### Style", "Cozy Storytelling", "Both are in Chinese"),
    "ja": ("日本語", "# AI棒人間アニメのスタイル集", "### スタイル", "ほっとする日常ストーリー", "どちらも中国語"),
    "ko": ("한국어", "# AI 스틱맨 애니메이션 스타일 모음", "### 스타일", "따뜻한 일상 이야기", "두 글 모두 중국어"),
    "pt-BR": ("Português do Brasil", "# Bonecos de palito com IA: biblioteca de estilos", "### Estilo", "Histórias acolhedoras", "Os dois estão em chinês"),
}
common_links = (
    "https://github.com/kaomei/stickman-video-director",
    "https://github.com/kaomei/stickman-video-director/issues",
    "https://x.com/CrazyKaomei/status/2102311241046008268",
    "https://x.com/CrazyKaomei/status/2093893997223923822?s=20",
    "https://flow.google.com/",
)
for locale, (label, title, style_prefix, style_four, tutorial_language) in locales.items():
    path = root / f"README.{locale}.md"
    text = path.read_text()
    assert not re.search(r"monixin888|2109651037850325112", text, re.IGNORECASE), path.name
    assert title in text, path.name
    assert f"[**{label}**]({path.name})" in text
    assert set(re.findall(preview_pattern, text)) == expected_previews
    assert text.count('width="90%"') == 4
    assert text.count('width="360"') == 8
    assert len(re.findall(rf"^{re.escape(style_prefix)} [1-4]:|^{re.escape(style_prefix)}[1-4]：", text, re.MULTILINE)) == 4
    assert style_four in text
    assert tutorial_language in text
    for link in common_links:
        assert link in text, (path.name, link)
    for voiceover in approved_voiceover:
        assert text.count(voiceover) == 1, (path.name, voiceover)
    rows = [line for line in text.splitlines() if any(vo in line for vo in approved_voiceover)]
    assert len(rows) == 3 and all(row.count("|") == 4 for row in rows)
    assert all(len(row.split("|")[2].strip()) > 80 for row in rows)
    for date in ("2026-10-15", "2026-10-14", "2026-10-13", "2026-10-12"):
        assert date in text
    assert "api.star-history.com/svg" in text
    assert "CHANGELOG.zh-CN.md" in text
    assert text.count('<div align="center">') == text.count("</div>")
    assert text.count("<table") == text.count("</table>")
    assert text.count("<tr>") == text.count("</tr>")
    assert text.count("<td ") == text.count("</td>")
    assert not any(old in text for old in ("git clone", "$skill-installer", "$directing-stickman-videos", 'href="assets/readme/'))
    # The two code blocks remain a short installation request and a topic.
    code_blocks = re.findall(r"```text\n(.*?)```", text, re.DOTALL)
    assert len(code_blocks) == 2
    assert code_blocks[0].strip().splitlines()[-1] == common_links[0]
    assert len(code_blocks[0].strip().splitlines()) == 2
    assert len(code_blocks[1].strip().splitlines()) == 1
    assert all(preset not in code_blocks[1] for preset in ("16:9", "9:16", "$directing"))
    markers = (
        "<!-- readme:demos -->", "<!-- readme:advantages -->",
        "<!-- readme:install -->", "<!-- readme:workflow -->",
        "<!-- readme:reliability -->", "<!-- readme:contribute -->",
    )
    assert [text.index(marker) for marker in markers] == sorted(text.index(marker) for marker in markers)
    ids = set(re.findall(r'<a id="([^"]+)"></a>', text))
    for anchor in re.findall(r'\]\(#([^)]+)\)|href="#([^"]+)"', text):
        assert next(part for part in anchor if part) in ids, (path.name, anchor)
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if "://" not in link and not link.startswith("#"):
            assert (root / link.split("#")[0]).exists(), (path.name, link)
    print(f"{path.name}: style/asset parity, original narration, links and onboarding passed.")

assert source == (root / "README.zh-CN.md").read_text()
assert not re.search(r"monixin888|2109651037850325112", source, re.IGNORECASE)
assert "# AI 火柴人动画画风大全" in source
assert "[**简体中文**](README.zh-CN.md) · [English](README.en.md)" in source
print("Chinese remains the default homepage.")

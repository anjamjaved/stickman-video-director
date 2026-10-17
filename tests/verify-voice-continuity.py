#!/usr/bin/env python3
"""Instruction regression only; this does not listen to or score generated audio."""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/directing-stickman-videos"
REFS = SKILL / "references"


def prompt_blocks(text):
    return re.findall(r"```text\n(.*?)\n```", text, re.S)


def check_video(prompts):
    """Check a single-narrator fixture or package, not multi-speaker dialogue."""
    assert prompts, "No prompts"
    voices = []
    for prompt in prompts:
        matches = re.findall(r"^One off-screen adult .* narrator throughout\..*$", prompt, re.M)
        assert len(matches) == 1, "Missing, abbreviated or duplicate complete narrator block"
        block = matches[0]
        for field in ("accent", "voice" if "female" in block else "baritone", "resonance",
                      "raspiness", "breathiness", "delivery", "pitch variation",
                      "speaking pace", "studio sound", "vocal timbre, register",
                      "Emotional progression belongs to the visuals and music"):
            assert field in block, f"Incomplete profile: {field}"
        assert "..." not in block and "[" not in block, "Unresolved/abbreviated voice"
        voices.append(block)
    assert len(set(voices)) == 1, "Voice profiles drift within this video"
    return voices[0]


voice_doc = (REFS / "voice-continuity.md").read_text()
male = prompt_blocks(voice_doc)[0]
assert check_video([male] * 3) == male
for mutation in ("Same narrator as clip 1.", male.replace("medium-low pitch", "high pitch")):
    try:
        check_video([male, mutation, male])
    except AssertionError:
        pass
    else:
        raise AssertionError("Voice drift/shortcut was not rejected")

examples = (REFS / "examples.md").read_text()
example_prompts = prompt_blocks(examples)
assert len(example_prompts) == 9
female = check_video(example_prompts[:6])
assert "adult female" in female and "baritone" not in female
assert check_video(example_prompts[6:]) == male
assert female != male, "Different videos cannot choose different voices"

for filename in ("SKILL.md", "references/style-catalog.md", "references/storyboard-template.md",
                 "references/omni-flash-prompt-contract.md", "references/prehistoric-dark-comedy.md",
                 "references/cozy-storytelling.md"):
    assert "voice-continuity.md" in (SKILL / filename).read_text(), f"Missing shared route: {filename}"
assert "Style 1 Light/Dark, Style 2A, Style 2B and Style 3" in voice_doc
assert "Style 4 Cozy Storytelling" in voice_doc
assert "multi-speaker" in voice_doc and "explicitly silent video" in voice_doc
assert "Other voice profiles and styles have not had separate provider-backed audio comparisons" in voice_doc

# Ensure this release changes example audio only, not prior visual actions or spoken words.
old_examples = subprocess.check_output([
    "git", "show", "origin/main:skills/directing-stickman-videos/references/examples.md"
], cwd=REPO, text=True)
for old, new in zip(prompt_blocks(old_examples), example_prompts):
    for prefix in ("Character:", "Environment:", "First frame:", "[0–3s]", "[3–7s]", "[7–10s]",
                   "Audio-only dialogue", "Do not generate", "Negative constraints:"):
        old_lines = [line for line in old.splitlines() if line.startswith(prefix)]
        new_lines = [line for line in new.splitlines() if line.startswith(prefix)]
        assert old_lines == new_lines, f"Non-voice example content changed: {prefix}"

if len(sys.argv) > 1:
    check_video(prompt_blocks(Path(sys.argv[1]).read_text()))
    print("Supplied single-narrator package voice-block equality passed.")
print("Shared voice instruction regression passed; no generated-audio score claimed.")

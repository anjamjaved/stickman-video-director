#!/usr/bin/env python3
"""Semantic planning fixtures and routing checks, not generated-video certification."""
from copy import deepcopy
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/directing-stickman-videos"
REF = SKILL / "references/cozy-storytelling.md"


def validate_plan(plan):
    clips = plan["clips"]
    assert clips, "Missing clips"
    if not plan.get("single_location_requested"):
        assert all(a["scene"] != b["scene"] for a, b in zip(clips, clips[1:])), \
            "New segments must establish different locations by default"
    assert len({c["character_anchor"] for c in clips}) == 1, "Character design drift"
    assert len({c["voice_profile"] for c in clips}) == 1, "Voice identity drift"
    for clip in clips:
        assert not any("location" in design for design in clip["prop_designs"].values()), \
            "Initial prop positions do not belong in immutable designs"
        departed = set()
        for frame in clip["frames"]:
            assert frame["arms"] == 2 and frame["legs"] == 2, "Extra anatomy"
            assert set(frame["effects"]) <= set(clip["allowed_effects"]), "Effect leakage"
            for name, state in frame["props"].items():
                locations = state["locations"]
                assert len(locations) == 1, "Simultaneous prop copies"
                location = locations[0]
                if name in departed:
                    assert location == "outside", "Departed prop restored in ending"
                if location == "outside":
                    departed.add(name)
                if state.get("screen_down"):
                    assert state["visible_face"] == "back", "Screen-down surface is wrong"
    for before, after in zip(clips, clips[1:]):
        for name in plan["continuing_props"]:
            outgoing = before["frames"][-1]["props"][name]
            incoming = after["frames"][0]["props"][name]
            assert outgoing["locations"] == incoming["locations"], "Unplanned prop handoff"


def frame(phone_place, face="front", screen_down=False, effects=()):
    return {"arms": 2, "legs": 2, "effects": list(effects), "props": {
        "phone": {"locations": [phone_place], "visible_face": face,
                  "screen_down": screen_down}}}


anchor = re.search(r"```text\n(.*?)\n```", REF.read_text(), re.S).group(1)
voice = re.search(r"```text\n(.*?)\n```", (SKILL / "references/voice-continuity.md").read_text(), re.S).group(1)
plan = {"single_location_requested": False, "continuing_props": ["phone"], "clips": []}
for scene, frames, effects in (
    ("office", [frame("office_table"), frame("right_hand")], ["red_circle"]),
    ("platform", [frame("right_hand"), frame("right_hand")], ["red_circle"]),
    ("outdoor_cafe", [frame("right_hand"), frame("cafe_table", "back", True)], ["steam", "leaves"]),
):
    plan["clips"].append({"scene": scene, "character_anchor": anchor,
                          "voice_profile": voice, "prop_designs": {"phone": {"shape": "rectangle"}},
                          "frames": frames, "allowed_effects": effects})

validate_plan(plan)  # Different tables/backgrounds are correct, not an error.
single = deepcopy(plan)
single["single_location_requested"] = True
for c in single["clips"]:
    c["scene"] = "cafe"
validate_plan(single)  # Honor the explicit one-location exception.

bad_cases = []
repeated = deepcopy(plan)
for c in repeated["clips"]:
    c["scene"] = "same_desk"
bad_cases.append(repeated)
duplicate = deepcopy(plan)
duplicate["clips"][0]["frames"][-1]["props"]["phone"]["locations"].append("office_table")
bad_cases.append(duplicate)
wrong_face = deepcopy(plan)
wrong_face["clips"][-1]["frames"][-1]["props"]["phone"]["visible_face"] = "front"
bad_cases.append(wrong_face)
reset = deepcopy(plan)
reset["clips"][-1]["frames"].extend([frame("outside"), frame("cafe_table")])
bad_cases.append(reset)
extra_arm = deepcopy(plan)
extra_arm["clips"][1]["frames"][0]["arms"] = 3
bad_cases.append(extra_arm)
recast = deepcopy(plan)
recast["clips"][1]["voice_profile"] = "Same narrator."
bad_cases.append(recast)
scope = deepcopy(plan)
scope["clips"][0]["prop_designs"]["phone"]["location"] = "office_table"
bad_cases.append(scope)
leak = deepcopy(plan)
leak["clips"][-1]["frames"][-1]["effects"] = ["red_circle"]
bad_cases.append(leak)
for bad in bad_cases:
    try:
        validate_plan(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError("Expected invalid fixture was accepted")

for path in ("SKILL.md", "references/style-catalog.md", "references/storyboard-template.md",
             "references/omni-flash-prompt-contract.md"):
    assert "cozy-storytelling.md" in (SKILL / path).read_text(), "Missing style route: " + path
assert "voice-continuity.md" in REF.read_text()
assert "Cozy Storytelling / 治愈故事风" in REF.read_text()
assert len(list(SKILL.rglob("SKILL.md"))) == 1, "Unexpected nested skill entry"
for asset in ("style-4-cozy-station", "style-4-cozy-cafe"):
    gif = ROOT / "assets/readme" / (asset + ".gif")
    assert gif.is_file() and gif.stat().st_size < 10 * 1024 * 1024, "Missing/oversized GIF"
    assert gif.read_bytes()[:6] in (b"GIF87a", b"GIF89a"), "Invalid GIF header"
    assert (ROOT / "assets/readme" / (asset + ".mp4")).is_file()
print("Style 4 rules: two valid plans and eight invalid mutations passed.")
print("Routing and inline assets passed; no generated-video or audio score claimed.")

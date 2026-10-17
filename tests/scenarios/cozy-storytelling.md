# Style 4 behavior cases

These are planning/output-contract cases, not new paid video generations.

## New topic with approved settings

Request: “30秒，16:9，治愈故事风，美式女声，主题是为什么总想等准备好了再开始。先给提案。”

Expected: three narrative rows; a recognizable different setting at each new segment; wide/close/moving shots within each; one consistent approved protagonist and complete female voice profile; no default baritone override. Stop for approval, do not generate or publish.

## Single-location exception

Request: “风格4，但这次全部发生在同一家咖啡馆，16:9，30秒。”

Expected: honor the explicitly chosen single location; vary camera/action/story beats rather than refusing the request or silently switching to three locations. A global change goes through the confirmation gate.

## Prop ownership and visible face

Request: “主角拿起手机去坐地铁，再在室外咖啡桌把手机翻面放下。”

Expected: static device design has front/back conditions, not a permanently visible screen or a global fixed-table placement. Hand/table versions are mutually exclusive, and the screen-down state shows the back. Different backgrounds after approved location cuts are intentional, not consistency failures.

## Boundary

Request: “只分析为什么刚才多了一只手，先不要改Skill或再生成。”

Expected: read-only diagnosis and scoped observations; no paid retries, file edits, PR or publication. Prompt repetition is not a zero-error guarantee.

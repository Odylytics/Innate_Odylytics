"""Lớp chấm điểm. Bản baseline do backend viết; Người 1 thay từng file, giữ nguyên chữ ký hàm.

features.extract(raw)                 -> dict[str, float]
owner.build_template(list[features])  -> template
owner.score(features, template)       -> (owner_match | None, z-scores)
owner.update(template, features)      -> template
human.score(features)                 -> (human_score, bot_reasons)
fusion.fuse(...)                      -> (risk_score, action, parts)
explain.explain(...)                  -> (reasons, explanation_vi)
"""

"""Refresh freshness/GTA+ notices without changing weekly headers or recommendations."""
from pathlib import Path

try:
    from scripts.content_safety import insert_freshness, displayed_payload, reset_window, week_id
    from scripts.generate_dashboard import (replace_marker_block,
                                           render_gta_plus_benefits, extract_marker_block)
    from scripts.generate_pixel_dashboard import render_pixel_gta_plus
    from scripts.gta_plus_intake import select_monthly
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.content_safety import insert_freshness, displayed_payload, reset_window, week_id
    from scripts.generate_dashboard import (replace_marker_block,
                                           render_gta_plus_benefits, extract_marker_block)
    from scripts.generate_pixel_dashboard import render_pixel_gta_plus
    from scripts.gta_plus_intake import select_monthly


def refresh_status(root):
    monthly, state = select_monthly(root / "data")
    for name, marker, render in (("dashboard.html", "gta_plus_benefits", lambda p: render_gta_plus_benefits(p, {})),
                                 ("pixel-dashboard.html", "pixel_gta_plus", render_pixel_gta_plus)):
        path = root / name
        text = path.read_text(encoding="utf-8")
        payload = displayed_payload(root, text, "pixel_header_meta" if name.startswith("pixel") else "header_meta")
        text = insert_freshness(text, payload)
        if name.startswith("pixel") and payload.get("week", {}).get("id") != week_id(reset_window()[0]):
            block = extract_marker_block(text, "pixel_header_meta")
            if block is not None:
                block = block.replace("READY TO RUN", "STALE DATA").replace("พร้อมเล่น", "ข้อมูลหมดอายุ")
                text = replace_marker_block(text, "pixel_header_meta", block)
        for old_note in ("Thursday 08:00 Bangkok", "Thursday 20:00 Bangkok · reviewed publication",
                         "Thursday 10:00 Bangkok · reviewed publication"):
            text = text.replace(old_note, "Disabled · manual reviewed publication only")
        if extract_marker_block(text, marker) is not None:
            text = replace_marker_block(text, marker, render(monthly))
        path.write_text(text, encoding="utf-8")
    print(state)


if __name__ == "__main__":
    refresh_status(Path(__file__).resolve().parents[1])

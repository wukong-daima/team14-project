"""deck.json → deck.html (1280×720 슬라이드 12장, 인쇄용). Playwright 로 PDF 출력."""
import html, json
from pathlib import Path
D = Path(__file__).parent
deck = json.loads((D / "deck.json").read_text(encoding="utf-8"))
e = html.escape
def bl(items, cls="bl"):
    out = []
    for it in items:
        if isinstance(it, list): out.append(f'<li><b>{e(it[0])}</b> {e(it[1])}</li>')
        else: out.append(f'<li>{e(it)}</li>')
    return f'<ul class="{cls}">' + "".join(out) + "</ul>"
def foot(t): return f'<div class="foot">{e(t)}</div>' if t else ""
parts = []
for i, s in enumerate(deck["slides"], 1):
    k = s["kind"]
    if k == "title":
        body = f'<div class="title-slide"><div class="meta">{e(s["meta"][0])}</div><h1>{e(s["title"])}</h1><div class="sub">{e(s["subtitle"])}</div><div class="meta2">{e(s["meta"][1])}</div><div class="url">{e(s["url"])}</div></div>'
        parts.append(f'<section class="slide dark">{body}</section>'); continue
    head = f'<h2>{e(s["title"])}</h2>'
    if k == "statement":
        body = f'<p class="lead">{e(s["lead"])}</p><p class="sublead">{e(s["sub"])}</p><div class="formula-row"><div class="formula">{e(s["formula"])}</div><div class="fnote">{e(s["formula_note"])}</div></div>' + bl(s["bullets"], "bl small")
    elif k == "bullets":
        body = bl(s["bullets"]) + foot(s.get("foot"))
    elif k == "two-col":
        body = f'<div class="cols"><div class="col"><h3 class="b">{e(s["left_title"])}</h3>{bl(s["left"],"bl small")}</div><div class="col"><h3 class="p">{e(s["right_title"])}</h3>{bl(s["right"],"bl small")}</div></div>' + foot(s.get("foot"))
    elif k == "table":
        rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in s["rows"])
        body = f'<table><thead><tr>{"".join(f"<th>{e(h)}</th>" for h in s["header"])}</tr></thead><tbody>{rows}</tbody></table>' + foot(s.get("foot"))
    elif k == "diagram":
        boxes = "".join(f'<div class="box c{j}"><div class="bt">{e(b[0])}</div><div class="bb">{e(b[1]).replace(chr(10),"<br>")}</div></div>' + ('<div class="arr">→</div>' if j < len(s["boxes"]) - 1 else "") for j, b in enumerate(s["boxes"]))
        body = f'<div class="diagram">{boxes}</div>' + foot(s.get("foot"))
    elif k == "image" and s.get("wide"):
        body = f'<div class="wide">{bl(s["bullets"],"bl small two")}<img class="imgw" src="{e(s["image"])}"><div class="cap">{e(s.get("caption",""))}</div></div>'
    elif k == "image":
        img2 = f'<img class="img2" src="{e(s["image2"])}">' if s.get("image2") else ""
        body = f'<div class="imgrow"><div class="imgs"><img class="img1" src="{e(s["image"])}"><div class="cap">{e(s.get("caption",""))}</div></div><div class="side">{bl(s["bullets"],"bl small")}{img2}</div></div>'
    parts.append(f'<section class="slide">{head}{body}<div class="chrome"><span>EvoLecture · 14조 · 최신딥러닝이론및응용</span><span>{i}</span></div></section>')
CSS = """
@page { size: 1280px 720px; margin: 0; }
* { box-sizing: border-box; } html, body { margin: 0; background: #fff; }
body { font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; color: #16202e; }
.slide { width: 1280px; height: 720px; padding: 44px 58px 40px; position: relative; page-break-after: always; break-after: page; overflow: hidden; }
.slide.dark { background: #16202e; color: #fff; }
.slide.dark::before { content: ""; position: absolute; left: 0; top: 0; width: 34px; height: 100%; background: #2d5bff; }
h2 { font-size: 30px; margin: 0 0 22px; padding-left: 18px; border-left: 10px solid #2d5bff; line-height: 1.25; }
.title-slide { padding: 50px 40px 0 70px; } .title-slide .meta { color: #9aa8bb; font-size: 16px; margin-bottom: 60px; }
.title-slide h1 { font-size: 36px; line-height: 1.35; margin: 0 0 18px; white-space: pre-line; } .title-slide .sub { color: #ff8a3d; font-size: 24px; margin-bottom: 90px; }
.title-slide .meta2 { font-size: 18px; } .title-slide .url { color: #9aa8bb; font-size: 14px; margin-top: 8px; }
.lead { font-size: 30px; font-weight: 700; margin: 30px 0 10px; line-height: 1.35; } .sublead { font-size: 22px; color: #5b6b7f; margin: 0 0 40px; }
.formula-row { display: flex; align-items: center; gap: 28px; margin-bottom: 44px; }
.formula { background: #e6ecff; color: #2d5bff; font-size: 52px; font-weight: 700; padding: 22px 48px; border-radius: 12px; font-family: Helvetica, Arial, sans-serif; }
.fnote { color: #5b6b7f; font-size: 19px; max-width: 560px; }
ul.bl { margin: 0; padding-left: 26px; font-size: 20px; line-height: 1.55; } ul.bl li { margin: 0 0 18px; } ul.bl li b { color: #2d5bff; margin-right: 6px; }
ul.bl.small { font-size: 16.5px; } ul.bl.small li { margin: 0 0 10px; }
.cols { display: flex; gap: 22px; } .col { flex: 1; background: #f7f8fb; border: 1px solid #d9dfe8; border-radius: 12px; padding: 16px 20px; min-height: 440px; }
.col h3 { margin: 0 0 10px; font-size: 18px; } .col h3.b { color: #2d5bff; } .col h3.p { color: #7b4dff; }
table { width: 100%; border-collapse: collapse; font-size: 15px; } th { background: #2d5bff; color: #fff; padding: 9px 12px; text-align: left; }
td { border: 1px solid #d9dfe8; padding: 8px 12px; vertical-align: top; } td:first-child { background: #f7f8fb; font-weight: 700; white-space: nowrap; }
.foot { position: absolute; left: 58px; right: 58px; bottom: 58px; background: #f7f8fb; border: 1px solid #d9dfe8; border-radius: 10px; padding: 10px 16px; font-size: 14px; }
.diagram { display: flex; align-items: stretch; gap: 10px; margin-top: 70px; } .box { flex: 1; border: 3px solid; border-radius: 14px; padding: 26px 16px; min-height: 300px; text-align: center; background: #fff; display: flex; flex-direction: column; justify-content: center; }
.box .bt { font-weight: 700; font-size: 24px; margin-bottom: 18px; } .box .bb { font-size: 17px; line-height: 1.6; } .arr { font-size: 36px; color: #5b6b7f; align-self: center; }
.c0 { border-color: #2d5bff; } .c0 .bt { color: #2d5bff; } .c1 { border-color: #7b4dff; } .c1 .bt { color: #7b4dff; } .c2 { border-color: #ff8a3d; } .c2 .bt { color: #ff8a3d; } .c3 { border-color: #1f9d6a; } .c3 .bt { color: #1f9d6a; }
.imgrow { display: flex; gap: 26px; } .imgs { width: 560px; display: flex; flex-direction: column; gap: 8px; } .imgs .img1 { width: 560px; max-height: 500px; object-fit: contain; object-position: left top; border: 1px solid #d9dfe8; border-radius: 10px; background: #fff; }
.imgs .cap { font-size: 12px; color: #5b6b7f; } .side { flex: 1; display: flex; flex-direction: column; gap: 14px; } .side .img2 { width: 100%; max-height: 265px; object-fit: contain; object-position: left top; border: 1px solid #d9dfe8; border-radius: 10px; }
.wide ul.two { columns: 2; column-gap: 40px; } .wide ul.two li { break-inside: avoid; } .wide .imgw { width: 100%; max-height: 330px; object-fit: contain; object-position: left top; border: 1px solid #d9dfe8; border-radius: 10px; margin-top: 8px; } .wide .cap { font-size: 12px; color: #5b6b7f; margin-top: 4px; }
.chrome { position: absolute; left: 58px; right: 58px; bottom: 18px; display: flex; justify-content: space-between; font-size: 11px; color: #5b6b7f; }
"""
(D / "deck.html").write_text(f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{e(deck["title"])}</title><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet"><style>{CSS}</style></head><body>{"".join(parts)}</body></html>', encoding="utf-8")
print("deck.html", len(parts), "slides")

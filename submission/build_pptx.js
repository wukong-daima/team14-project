// deck.json → <output>.pptx (pptxgenjs). 16:9, 한국어. 슬라이드 notes 는 발표자 노트로 들어간다.
const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const deck = JSON.parse(fs.readFileSync(path.join(__dirname, "deck.json"), "utf8"));
const C = { ink: "16202E", muted: "5B6B7F", line: "D9DFE8", blue: "2D5BFF", blueSoft: "E6ECFF", orange: "FF8A3D", purple: "7B4DFF", purpleSoft: "F0EAFF", bg: "F7F8FB", white: "FFFFFF", green: "1F9D6A" };
const FONT = "Apple SD Gothic Neo"; // Windows 에서는 맑은 고딕으로 자동 대체됨
const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pptx.author = "Team14"; pptx.title = deck.title; pptx.lang = "ko-KR";
const W = 13.33, H = 7.5, M = 0.6;

function chrome(slide, n, title) {
  slide.background = { color: C.white };
  if (title) {
    slide.addShape(pptx.ShapeType.rect, { x: M, y: 0.55, w: 0.12, h: 0.55, fill: { color: C.blue }, line: { color: C.blue } });
    slide.addText(title, { x: M + 0.25, y: 0.42, w: W - 2 * M - 0.25, h: 0.8, fontFace: FONT, fontSize: 26, bold: true, color: C.ink, valign: "middle" });
  }
  slide.addText(`EvoLecture · 14조 · 최신딥러닝이론및응용`, { x: M, y: H - 0.45, w: 8, h: 0.3, fontFace: FONT, fontSize: 9, color: C.muted });
  slide.addText(String(n), { x: W - M - 1, y: H - 0.45, w: 1, h: 0.3, fontFace: FONT, fontSize: 9, color: C.muted, align: "right" });
}
function foot(slide, text) {
  if (!text) return;
  slide.addShape(pptx.ShapeType.rect, { x: M, y: H - 1.25, w: W - 2 * M, h: 0.6, fill: { color: C.bg }, line: { color: C.line, width: 0.5 } });
  slide.addText(text, { x: M + 0.15, y: H - 1.25, w: W - 2 * M - 0.3, h: 0.6, fontFace: FONT, fontSize: 11, color: C.ink, valign: "middle" });
}
function bulletRuns(items, size) {
  // items: string | [label, text]
  return items.map((it) => {
    if (Array.isArray(it)) return [
      { text: it[0] + "  ", options: { bold: true, color: C.blue, fontSize: size, breakLine: false, bullet: { code: "25A0" } } },
      { text: it[1], options: { fontSize: size, color: C.ink, breakLine: true } },
    ];
    return [{ text: it, options: { fontSize: size, color: C.ink, bullet: true, breakLine: true } }];
  }).flat();
}

deck.slides.forEach((s, i) => {
  const n = i + 1;
  const slide = pptx.addSlide();
  if (s.notes) slide.addNotes(s.notes);
  if (s.kind === "title") {
    slide.background = { color: C.ink };
    slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.35, h: H, fill: { color: C.blue }, line: { color: C.blue } });
    slide.addText(s.meta[0], { x: 1, y: 0.9, w: 11, h: 0.4, fontFace: FONT, fontSize: 14, color: "9AA8BB" });
    slide.addText(s.title, { x: 1, y: 1.8, w: 11.3, h: 2.1, fontFace: FONT, fontSize: 30, bold: true, color: C.white, valign: "top" });
    slide.addText(s.subtitle, { x: 1, y: 3.95, w: 11, h: 0.6, fontFace: FONT, fontSize: 20, color: C.orange });
    slide.addText(s.meta[1], { x: 1, y: 5.3, w: 11, h: 0.4, fontFace: FONT, fontSize: 15, color: C.white });
    slide.addText(s.url, { x: 1, y: 5.8, w: 11, h: 0.4, fontFace: FONT, fontSize: 12, color: "9AA8BB" });
    return;
  }
  chrome(slide, n, s.title);
  if (s.kind === "statement") {
    slide.addText(s.lead, { x: M, y: 1.6, w: W - 2 * M, h: 1.1, fontFace: FONT, fontSize: 26, bold: true, color: C.ink });
    slide.addText(s.sub, { x: M, y: 2.7, w: W - 2 * M, h: 0.6, fontFace: FONT, fontSize: 19, color: C.muted });
    slide.addShape(pptx.ShapeType.roundRect, { x: M, y: 3.6, w: 5.2, h: 1.3, fill: { color: C.blueSoft }, line: { color: C.blueSoft }, rectRadius: 0.1 });
    slide.addText(s.formula, { x: M, y: 3.6, w: 5.2, h: 1.3, fontFace: "Helvetica", fontSize: 40, bold: true, color: C.blue, align: "center", valign: "middle" });
    slide.addText(s.formula_note, { x: M + 5.4, y: 3.6, w: 6.5, h: 1.3, fontFace: FONT, fontSize: 15, color: C.muted, valign: "middle" });
    slide.addText(bulletRuns(s.bullets, 14), { x: M, y: 5.15, w: W - 2 * M, h: 1.1, fontFace: FONT, color: C.ink, paraSpaceAfter: 6 });
  } else if (s.kind === "bullets") {
    slide.addText(bulletRuns(s.bullets, 16), { x: M, y: 1.5, w: W - 2 * M, h: 4.4, fontFace: FONT, valign: "top", paraSpaceAfter: 12 });
    foot(slide, s.foot);
  } else if (s.kind === "two-col") {
    const cw = (W - 2 * M - 0.4) / 2;
    [["left", M], ["right", M + cw + 0.4]].forEach(([k, x]) => {
      slide.addShape(pptx.ShapeType.roundRect, { x, y: 1.45, w: cw, h: 4.55, fill: { color: C.bg }, line: { color: C.line, width: 0.5 }, rectRadius: 0.08 });
      slide.addText(s[k + "_title"], { x: x + 0.2, y: 1.55, w: cw - 0.4, h: 0.45, fontFace: FONT, fontSize: 15, bold: true, color: k === "left" ? C.blue : C.purple });
      slide.addText(bulletRuns(s[k], 13), { x: x + 0.2, y: 2.05, w: cw - 0.4, h: 3.85, fontFace: FONT, valign: "top", paraSpaceAfter: 8 });
    });
    foot(slide, s.foot);
  } else if (s.kind === "table") {
    const rows = [s.header.map((h) => ({ text: h, options: { bold: true, color: C.white, fill: { color: C.blue }, fontFace: FONT, fontSize: 13 } }))]
      .concat(s.rows.map((r) => r.map((c, j) => ({ text: c, options: { fontFace: FONT, fontSize: 12, color: C.ink, bold: j === 0, fill: { color: j === 0 ? C.bg : C.white } } }))));
    const colW = s.header.length === 2 ? [2.4, W - 2 * M - 2.4] : [2.2, W - 2 * M - 2.2 - 1.8, 1.8];
    slide.addTable(rows, { x: M, y: 1.45, w: W - 2 * M, colW, border: { type: "solid", color: C.line, pt: 0.5 }, rowH: 0.42, valign: "middle" });
    foot(slide, s.foot);
  } else if (s.kind === "diagram") {
    const n4 = s.boxes.length, gap = 0.45, bw = (W - 2 * M - gap * (n4 - 1)) / n4, by = 1.9, bh = 3.4;
    s.boxes.forEach((b, j) => {
      const x = M + j * (bw + gap);
      const col = [C.blue, C.purple, C.orange, C.green][j % 4];
      slide.addShape(pptx.ShapeType.roundRect, { x, y: by, w: bw, h: bh, fill: { color: C.white }, line: { color: col, width: 2 }, rectRadius: 0.1 });
      slide.addText(b[0], { x, y: by + 0.35, w: bw, h: 0.6, fontFace: FONT, fontSize: 20, bold: true, color: col, align: "center" });
      slide.addText(b[1], { x: x + 0.15, y: by + 1.1, w: bw - 0.3, h: bh - 1.4, fontFace: FONT, fontSize: 14, color: C.ink, align: "center", valign: "top" });
      if (j < n4 - 1) slide.addText("→", { x: x + bw - 0.05, y: by + bh / 2 - 0.3, w: gap + 0.1, h: 0.6, fontFace: "Helvetica", fontSize: 26, color: C.muted, align: "center" });
    });
    foot(slide, s.foot);
  } else if (s.kind === "image" && s.wide) {
    const has = (p) => fs.existsSync(path.join(__dirname, p));
    slide.addText(bulletRuns(s.bullets, 13), { x: M, y: 1.4, w: W - 2 * M, h: 2.3, fontFace: FONT, valign: "top", paraSpaceAfter: 6 });
    if (has(s.image)) slide.addImage({ path: path.join(__dirname, s.image), x: M, y: 3.75, w: W - 2 * M, h: 2.45, sizing: { type: "contain", w: W - 2 * M, h: 2.45 } });
    if (s.caption) slide.addText(s.caption, { x: M, y: 6.22, w: 8, h: 0.3, fontFace: FONT, fontSize: 9, color: C.muted });
  } else if (s.kind === "image") {
    const imgW = 5.7, imgH = 4.7, rx = M + imgW + 0.35, rw = W - 2 * M - imgW - 0.35;
    const has = (p) => fs.existsSync(path.join(__dirname, p));
    if (has(s.image)) slide.addImage({ path: path.join(__dirname, s.image), x: M, y: 1.45, w: imgW, h: imgH, sizing: { type: "contain", w: imgW, h: imgH } });
    const bulletH = s.image2 ? 2.5 : 4.7;
    slide.addText(bulletRuns(s.bullets, 13), { x: rx, y: 1.45, w: rw, h: bulletH, fontFace: FONT, valign: "top", paraSpaceAfter: 8 });
    if (s.image2 && has(s.image2)) slide.addImage({ path: path.join(__dirname, s.image2), x: rx, y: 1.45 + bulletH + 0.1, w: rw, h: 2.1, sizing: { type: "contain", w: rw, h: 2.1 } });
    if (s.caption) slide.addText(s.caption, { x: M, y: 1.45 + imgH + 0.05, w: imgW, h: 0.3, fontFace: FONT, fontSize: 9, color: C.muted });
  }
});
// 출력 파일명은 deck.json 의 "output" (없으면 Team14). 중간발표는 Team14_mid.
pptx.writeFile({ fileName: path.join(__dirname, (deck.output || "Team14") + ".pptx") }).then((f) => console.log("wrote", f));

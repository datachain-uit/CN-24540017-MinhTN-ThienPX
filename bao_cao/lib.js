// Helpers for building the revised report with docx-js
const { Paragraph, TextRun, Table, TableRow, TableCell, AlignmentType, LevelFormat, HeadingLevel,
  WidthType, ShadingType, BorderStyle, ImageRun } = require('docx');
const fs = require('fs');

const FONT = 'Times New Roman';
const numConfigs = [{ reference: 'bul', levels: [
  { level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
  { level: 1, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1000, hanging: 270 } } } }] }];
let numRef = 0;

function runs(text, base = {}) {
  const out = []; const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g; let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const s = m[0];
    if (s.startsWith('**')) out.push(new TextRun({ text: s.slice(2, -2), bold: true, ...base }));
    else out.push(new TextRun({ text: s.slice(1, -1), italics: true, ...base }));
    last = m.index + s.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}
const P = (text, opt = {}) => new Paragraph({ children: runs(text, opt.run || {}), alignment: opt.align || AlignmentType.JUSTIFIED,
  spacing: { after: opt.after ?? 120, line: 288, before: opt.before ?? 0 }, ...(opt.extra || {}) });
const H = (lvl, t) => new Paragraph({ heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4][lvl - 1], children: [new TextRun(t)] });
const B = (text, level = 0) => new Paragraph({ numbering: { reference: 'bul', level }, children: runs(text), alignment: AlignmentType.JUSTIFIED, spacing: { after: 80, line: 276 } });
function numbered(items) {
  const ref = 'num' + (numRef++);
  numConfigs.push({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] });
  return items.map(t => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(t), alignment: AlignmentType.JUSTIFIED, spacing: { after: 80, line: 276 } }));
}
const Caption = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 }, children: runs(t, { italics: true, size: 22 }) });
const TCap = (t) => new Paragraph({ alignment: AlignmentType.LEFT, spacing: { before: 120, after: 60 }, keepNext: true, children: runs(t, { italics: true, size: 22 }) });
const Marker = (id) => new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun(`[[${id}]]`)] });

const border = { style: BorderStyle.SINGLE, size: 4, color: '808080' };
const borders = { top: border, bottom: border, left: border, right: border };
function cell(content, width, opt = {}) {
  const texts = Array.isArray(content) ? content : [content];
  return new TableCell({ borders, width: { size: width, type: WidthType.DXA }, columnSpan: opt.span,
    shading: opt.shade ? { fill: opt.shade, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: texts.map(t => new Paragraph({ alignment: opt.align || AlignmentType.LEFT, spacing: { after: 30 }, children: runs(String(t), { size: opt.size || 20, bold: opt.bold || undefined }) })) });
}
function table(widths, header, rows, opt = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const trs = [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, widths[i], { shade: 'D9E2F3', bold: true, align: AlignmentType.CENTER, size: opt.size })) })];
  for (const r of rows) {
    const cells = []; let ci = 0;
    for (const c of r) {
      if (c && typeof c === 'object' && !Array.isArray(c) && c.span) {
        const w = widths.slice(ci, ci + c.span).reduce((a, b) => a + b, 0);
        cells.push(cell(c.text, w, { span: c.span, shade: c.shade, size: opt.size })); ci += c.span;
      } else if (c && typeof c === 'object' && !Array.isArray(c) && c.shade) {
        cells.push(cell(c.text, widths[ci], { shade: c.shade, size: opt.size })); ci += 1;
      } else { cells.push(cell(c, widths[ci], { size: opt.size })); ci += 1; }
    }
    trs.push(new TableRow({ children: cells }));
  }
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: trs });
}
function image(path, wInch, hInch) {
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 }, keepNext: true,
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(path), transformation: { width: Math.round(wInch * 96), height: Math.round(hInch * 96) },
      altText: { title: path.split('/').pop(), description: path.split('/').pop(), name: path.split('/').pop() } })] });
}
module.exports = { FONT, numConfigs, runs, P, H, B, numbered, Caption, TCap, Marker, table, image, AlignmentType };

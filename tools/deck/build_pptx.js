// Editable PowerPoint version of the HTML deck: same slides, same positions (read by extract_layout.js).
//   node tools/deck/extract_layout.js docs/deck/EDS-Portal-Walkthrough.html layout.json
//   NODE_PATH=<dir with pptxgenjs + sharp> node tools/deck/build_pptx.js layout.json docs/deck/EDS-Portal-Walkthrough.pptx
//   node <pptx skill>/scripts/apply_theme.js docs/deck/EDS-Portal-Walkthrough.pptx tools/deck/theme.json
// 1280 x 720 px slide = 13.333 x 7.5 in (96 px per inch); CSS px font sizes x 0.75 = points.
const pptxgen = require('pptxgenjs');
const sharp = require('sharp');
const fs = require('fs');

const [src, out] = process.argv.slice(2);
const deck = JSON.parse(fs.readFileSync(src, 'utf8'));
const I = px => +(px / 96).toFixed(3);
const PT = px => +(px * 0.75).toFixed(1);
const HEAD = 'Arial Narrow', BODY = 'Arial';
const Y = 'FCB026', INK = '111111', INK2 = '333333', MUTE = '6B6B6B', LINE = 'E6E4DF', SOFT = 'F6F5F2', WHITE = 'FFFFFF';
const box = (r, extra) => Object.assign({ x: I(r.x), y: I(r.y), w: I(r.w), h: I(r.h) }, extra || {});
const b64 = uri => Buffer.from(uri.split(',')[1], 'base64');

// object-fit: cover, anchored top (or top-left): crop the screenshot to the box's shape like the browser does
async function cover(uri, w, h) {
  const img = sharp(b64(uri)), m = await img.metadata();
  const want = w / h;
  let cw = m.width, ch = Math.round(m.width / want);
  if (ch > m.height) { ch = m.height; cw = Math.round(m.height * want); }
  const buf = await img.extract({ left: 0, top: 0, width: cw, height: ch }).jpeg({ quality: 86 }).toBuffer();
  return 'image/jpeg;base64,' + buf.toString('base64');
}
const raw = uri => 'image/jpeg;base64,' + uri.split(',')[1];

async function hexPattern() {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><defs><pattern id="p" width="120" height="104" patternUnits="userSpaceOnUse">
    <path d="M30 2L58 18V50L30 66L2 50V18Z M90 54L118 70V102L90 118L62 102V70Z" fill="none" stroke="#000" stroke-opacity="0.06" stroke-width="2"/></pattern></defs>
    <rect width="1280" height="720" fill="#${Y}"/><rect width="1280" height="720" fill="url(#p)"/></svg>`;
  return 'image/png;base64,' + (await sharp(Buffer.from(svg)).png().toBuffer()).toString('base64');
}

function logo(slide, x, y, w, h, big) {
  slide.addShape('roundRect', { x: I(x), y: I(y), w: I(w), h: I(h), rectRadius: big ? 0.08 : 0.05, fill: { color: INK },
    line: { color: WHITE, width: big ? 3 : 1.5 }, objectName: 'JCB logo' });
  const q = big ? 16 : 7;
  slide.addShape('rect', { x: I(x + (big ? 12 : 6)), y: I(y + (big ? 12 : 6)), w: I(q), h: I(q), fill: { color: Y },
    line: { color: WHITE, width: big ? 1.5 : 0.75 }, objectName: 'JCB logo square' });
  slide.addText('JCB', { x: I(x + (big ? 34 : 15)), y: I(y), w: I(w - (big ? 38 : 17)), h: I(h), margin: 0, align: 'center',
    valign: 'middle', fontFace: HEAD, bold: true, fontSize: big ? 40 : 14, color: WHITE, isTextBox: true, objectName: 'JCB logo text' });
}

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.author = 'Gaurav Shelke';
  pres.company = 'JCB India · EDS Lab, Pune';
  pres.title = 'EDS Lab Material Portal · Walkthrough';
  pres.theme = { headFontFace: HEAD, bodyFontFace: BODY };

  pres.defineSlideMaster({
    title: 'CONTENT', background: { color: WHITE },
    objects: [
      { line: { x: I(48), y: I(674), w: I(1184), h: 0, line: { color: LINE, width: 0.75 } } },
      { placeholder: { options: { name: 'title', type: 'title', x: I(48), y: I(52), w: I(1184), h: I(46), margin: 0, fontFace: HEAD,
        bold: true, fontSize: 32, color: INK, align: 'left', valign: 'top' }, text: '' } },
    ],
    slideNumber: { x: I(1080), y: I(686), w: I(80), h: I(22), fontFace: BODY, fontSize: 9, color: MUTE, align: 'right', bold: true },
  });
  pres.defineSlideMaster({ title: 'TITLE', background: { color: Y }, objects: [] });

  const pattern = await hexPattern();
  let section = null;
  for (let k = 0; k < deck.length; k++) {
    const d = deck[k];
    const sec = d.cls === 'div-s' || section === 'Appendix' ? 'Appendix' : 'Main deck';
    if (sec !== section) { pres.addSection({ title: sec }); section = sec; }
    if (d.title) {
      const s = pres.addSlide({ masterName: 'TITLE', sectionTitle: sec });
      s.addImage({ data: pattern, x: 0, y: 0, w: 13.333, h: 7.5, objectName: 'Hex pattern' });
      s.addText(d.title.h1.text.toUpperCase(), { x: I(84), y: I(250), w: I(1150), h: I(110), margin: 0, fontFace: HEAD, bold: true,
        fontSize: 60, color: INK, valign: 'bottom', isTextBox: true, objectName: 'Title' });
      s.addText(d.title.h2.text.toUpperCase(), { x: I(88), y: I(372), w: I(1000), h: I(36), margin: 0, fontFace: HEAD, bold: true,
        fontSize: 21, color: INK, isTextBox: true, objectName: 'Subtitle' });
      d.title.meta.forEach((m, j) => s.addText(m.text, box(m, { w: I(m.w + 60), margin: 0, fontFace: BODY, fontSize: 15, color: INK,
        isTextBox: true, objectName: j ? 'Date' : 'Presenter' })));
      logo(s, d.title.logo.x, d.title.logo.y, d.title.logo.w, d.title.logo.h, true);
      s.addNotes(d.notes);
      continue;
    }
    const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: sec });
    logo(s, 1174, 684, 56, 28, false);
    if (d.foot) s.addText(d.foot.left, { x: I(48), y: I(686), w: I(700), h: I(22), margin: 0, fontFace: BODY, fontSize: 9, bold: true,
      color: MUTE, valign: 'middle', isTextBox: true, objectName: 'Footer' });
    if (d.kick) s.addText(d.kick.text.toUpperCase(), box(d.kick, { y: I(30), h: I(20), margin: 0, fontFace: BODY, bold: true,
      fontSize: 10, charSpacing: 1.2, color: MUTE, isTextBox: true, objectName: 'Kicker' }));
    s.addText(d.hd.text.toUpperCase(), { placeholder: 'title', align: 'left' });
    s.addShape('rect', box(d.rule, { fill: { color: Y }, line: { type: 'none' }, objectName: 'Title rule' }));
    if (d.cls === 'div-s') s.addShape('rect', { x: 0, y: 0, w: I(18), h: 7.5, fill: { color: Y }, line: { type: 'none' }, objectName: 'Band' });
    if (d.lead) s.addText(d.cls === 'div-s' ? 'One slide per page, for questions. Click a page name to jump to it.' : d.lead.text,
      box(d.lead, { y: I(d.lead.y - 2), h: I(28), margin: 0, fontFace: BODY, fontSize: PT(d.cls === 'div-s' ? 18 : 19), color: INK2,
        isTextBox: true, objectName: 'Lead' }));

    // ---- flow (Phase 1 at a glance)
    for (const f of d.flow) {
      s.addShape('roundRect', box(f.no, { rectRadius: 0.1, fill: { color: Y }, line: { type: 'none' } }));
      s.addText(f.no.text.toUpperCase(), box(f.no, { margin: 0, align: 'center', valign: 'middle', fontFace: HEAD, bold: true,
        fontSize: 10.5, color: INK, isTextBox: true }));
      s.addText(f.h3.text.toUpperCase(), box(f.h3, { margin: 0, fontFace: HEAD, bold: true, fontSize: 15, color: INK, valign: 'top', isTextBox: true }));
      s.addImage(box(f.img, { data: await cover(f.img.src, f.img.w, f.img.h), shadow: { type: 'outer', color: '000000', opacity: 0.18,
        blur: 8, offset: 3, angle: 90 }, line: { color: 'CCCCCC', width: 0.75 }, altText: f.h3.text + ' screen' }));
      s.addText(f.p.text, box(f.p, { h: I(f.p.h + 6), margin: 0, fontFace: BODY, fontSize: 10.5, color: INK2, valign: 'top', isTextBox: true }));
    }
    // ---- two columns of bullets
    for (const c of d.cols) {
      s.addText(c.h3.text.toUpperCase(), box(c.h3, { h: I(34), margin: 0, fontFace: HEAD, bold: true, fontSize: 19.5, color: INK, isTextBox: true }));
      s.addShape('line', { x: I(c.h3.x), y: I(c.h3.y + c.h3.h - 2), w: I(c.h3.w), h: 0, line: { color: INK, width: 1.5 } });
      for (const li of c.li) {
        s.addShape('rect', { x: I(li.x), y: I(li.y + 8), w: I(11), h: I(11), fill: { color: Y }, line: { type: 'none' } });
        s.addText(li.text, { x: I(li.x + 26), y: I(li.y), w: I(li.w - 26), h: I(li.h), margin: 0, fontFace: BODY, fontSize: 13.5,
          color: INK, valign: 'top', isTextBox: true });
      }
    }
    // ---- thumbnail grids (click = jump to the page's appendix slide)
    for (const g of d.grid) {
      const link = g.go ? { slide: g.go, tooltip: 'Open ' + g.h3.text } : undefined;
      s.addImage(box(g.img, { data: await cover(g.img.src, g.img.w, g.img.h), hyperlink: link, line: { color: 'CCCCCC', width: 0.75 },
        shadow: { type: 'outer', color: '000000', opacity: 0.16, blur: 8, offset: 3, angle: 90 }, altText: g.h3.text + ' screen' }));
      const big = d.grid.length > 6;
      s.addText(g.h3.text.toUpperCase(),
        box(g.h3, { h: I(g.h3.h + 4), margin: 0, fontFace: HEAD, bold: true, fontSize: big ? 13.5 : 15.5, color: INK, valign: 'top', isTextBox: true }));
      s.addText(g.p.text, box(g.p, { h: I(g.p.h + 4), margin: 0, fontFace: BODY, fontSize: big ? 9.5 : 10, color: INK2, valign: 'top', isTextBox: true }));
    }
    // ---- appendix index
    for (const x of d.index) {
      s.addShape('roundRect', box(x, { rectRadius: 0.06, fill: { color: WHITE }, line: { color: LINE, width: 0.75 } }));
      s.addText([{ text: x.no + '   ', options: { fontFace: HEAD, bold: true, color: INK } },
                 { text: x.text, options: { bold: true, hyperlink: { slide: x.go, tooltip: 'Open ' + x.text } } }],
        { x: I(x.x + 10), y: I(x.y), w: I(x.w - 130), h: I(x.h), margin: 0, valign: 'middle', fontFace: BODY, fontSize: 11, color: INK, isTextBox: true });
      s.addText(x.role, { x: I(x.x + x.w - 130), y: I(x.y), w: I(120), h: I(x.h), margin: 0, align: 'right', valign: 'middle',
        fontFace: BODY, fontSize: 9, color: MUTE, isTextBox: true });
    }
    // ---- screen slide: screenshot + numbered hotspots + click list + result
    if (d.shot) {
      s.addImage(box(d.shot, { data: raw(d.shot.src), line: { color: 'CFCFCF', width: 0.75 }, altText: d.hd.text + ' screen',
        shadow: { type: 'outer', color: '000000', opacity: 0.22, blur: 12, offset: 4, angle: 90 } }));
      for (const t of d.dots) {
        s.addShape('ellipse', box(t, { fill: { color: Y }, line: { color: INK, width: 2.25 }, objectName: 'Hotspot ' + t.n,
          shadow: { type: 'outer', color: '000000', opacity: 0.5, blur: 4, offset: 1, angle: 90 } }));
        s.addText(t.n, box(t, { margin: 0, align: 'center', valign: 'middle', fontFace: HEAD, bold: true, fontSize: 12, color: INK, isTextBox: true }));
      }
      s.addText(d.side.h4.text.toUpperCase(), box(d.side.h4, { margin: 0, fontFace: HEAD, bold: true, fontSize: PT(d.side.h4.h > 24 ? 20 : 18),
        color: INK, valign: 'top', isTextBox: true }));
      const wide = d.shot.w > 800;
      for (const it of d.side.items) {
        s.addShape('ellipse', box(it.b, { fill: { color: it.nd ? WHITE : Y }, line: { color: INK, width: 1.5, dashType: it.nd ? 'dash' : 'solid' } }));
        s.addText(it.n, box(it.b, { margin: 0, align: 'center', valign: 'middle', fontFace: HEAD, bold: true, fontSize: 10.5, color: INK, isTextBox: true }));
        s.addText([{ text: it.head, options: { bold: true, color: INK, breakLine: true } }, { text: it.text, options: { color: INK2 } }],
          box(it.t, { h: I(it.t.h + 4), margin: 0, fontFace: BODY, fontSize: wide ? 9.75 : 10, valign: 'top', isTextBox: true }));
      }
      const r = d.side.res;
      if (r) {
        s.addShape('rect', box(r, { fill: { color: SOFT }, line: { type: 'none' } }));
        s.addShape('rect', { x: I(r.x), y: I(r.y), w: I(8), h: I(r.h), fill: { color: Y }, line: { type: 'none' } });
        s.addText([{ text: r.head.toUpperCase(), options: { fontFace: HEAD, bold: true, fontSize: 11.5, breakLine: true } },
                   { text: r.body, options: { fontSize: wide ? 10.5 : 11.5 } }],
          { x: I(r.x + 22), y: I(r.y + 10), w: I(r.w - 34), h: I(r.h - 18), margin: 0, fontFace: BODY, color: INK, valign: 'top', isTextBox: true });
      }
    }
    if (d.banner) {
      s.addShape('rect', box(d.banner, { fill: { color: SOFT }, line: { type: 'none' } }));
      s.addShape('rect', { x: I(d.banner.x), y: I(d.banner.y), w: I(8), h: I(d.banner.h), fill: { color: Y }, line: { type: 'none' } });
      s.addText(d.banner.text, { x: I(d.banner.x + 26), y: I(d.banner.y), w: I(d.banner.w - 40), h: I(d.banner.h), margin: 0,
        fontFace: BODY, fontSize: 12, color: INK, valign: 'middle', isTextBox: true });
    }
    s.addNotes(d.notes);
  }
  await pres.writeFile({ fileName: out });
  console.log('wrote', out, deck.length, 'slides');
})();

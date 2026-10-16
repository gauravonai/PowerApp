// Reads the HTML deck in Chromium and dumps every slide's boxes (px on the 1280x720 slide) for build_pptx.js.
//   node tools/deck/extract_layout.js docs/deck/EDS-Portal-Walkthrough.html <out.json>
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1300, height: 770 } });
  await p.goto('file://' + path.resolve(src));
  await p.waitForTimeout(300);
  const n = await p.evaluate(() => slides.length);
  const deck = [];
  for (let i = 0; i < n; i++) {
    await p.evaluate(k => show(k), i);
    await p.waitForTimeout(450);
    deck.push(await p.evaluate(() => {
      const s = document.querySelector('.slide.on'), o = document.querySelector('.deck').getBoundingClientRect();
      const sc = o.width / 1280;
      const R = e => { const r = e.getBoundingClientRect(); return { x: (r.left - o.left) / sc, y: (r.top - o.top) / sc, w: r.width / sc, h: r.height / sc }; };
      const T = e => e ? e.textContent.replace(/\s+/g, ' ').trim() : '';
      const all = (q, f) => [...s.querySelectorAll(q)].map(f);
      const own = e => [...e.childNodes].filter(c => c.nodeType === 3).map(c => c.textContent).join('').replace(/\s+/g, ' ').trim();
      const d = { cls: s.className.replace('slide', '').replace('on', '').trim(), notes: s.dataset.notes || '' };
      const one = (q) => { const e = s.querySelector(q); return e ? Object.assign(R(e), { text: T(e) }) : null; };
      d.kick = one(':scope > .kick'); d.hd = one(':scope > .hd'); d.rule = one(':scope > .rule'); d.lead = one(':scope > .lead');
      d.banner = one(':scope > .banner');
      d.foot = s.querySelector('.foot') ? { left: T(s.querySelector('.foot span')) } : null;
      d.title = s.querySelector('h1') ? { h1: one('h1'), h2: one('h2'), meta: all('.meta span', e => Object.assign(R(e), { text: T(e) })), logo: one('.logo') } : null;
      d.flow = all('.fs', e => ({ no: Object.assign(R(e.querySelector('.no')), { text: T(e.querySelector('.no')) }),
        h3: Object.assign(R(e.querySelector('h3')), { text: T(e.querySelector('h3')) }),
        img: Object.assign(R(e.querySelector('img')), { src: e.querySelector('img').src }),
        p: Object.assign(R(e.querySelector('p')), { text: T(e.querySelector('p')) }) }));
      d.cols = all('.bc', e => ({ h3: Object.assign(R(e.querySelector('h3')), { text: T(e.querySelector('h3')) }),
        li: all2(e, 'li') }));
      function all2(e, q) { return [...e.querySelectorAll(q)].map(x => Object.assign(R(x), { text: T(x) })); }
      d.grid = all('.gc', e => ({ go: +e.dataset.go, img: Object.assign(R(e.querySelector('img')), { src: e.querySelector('img').src }),
        h3: Object.assign(R(e.querySelector('h3')), { text: T(e.querySelector('h3')) }),
        p: Object.assign(R(e.querySelector('p')), { text: T(e.querySelector('p')) }) }));
      d.index = all('.ix', e => Object.assign(R(e), { go: +e.dataset.go, no: T(e.querySelector('b')), text: own(e), role: T(e.querySelector('i')) }));
      const shot = s.querySelector('.shot');
      if (shot) {
        d.shot = Object.assign(R(shot), { src: shot.querySelector('img').src });
        d.dots = all('.dot:not(.off)', e => Object.assign(R(e), { n: T(e) }));
        d.side = { h4: one('.side h4'), items: all('.it', e => ({ b: R(e.querySelector('b')), nd: e.classList.contains('nd'), n: T(e.querySelector('b')),
          head: T(e.querySelector('i')), text: own(e.querySelector('.t')), t: R(e.querySelector('.t')) })),
          res: one('.res') ? Object.assign(one('.res'), { head: T(s.querySelector('.res b')), body: own(s.querySelector('.res')) }) : null };
      }
      return d;
    }));
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(deck));
  console.log('layout of', n, 'slides ->', out);
})();

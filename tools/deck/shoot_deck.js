// Screenshot every slide of the deck and export the PDF.  node tools/deck/shoot_deck.js <deck.html> <pngDir> [pdf]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [src, dst, pdf] = process.argv.slice(2);
  fs.mkdirSync(dst, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1300, height: 770 } });
  await p.goto('file://' + path.resolve(src));
  await p.waitForTimeout(300);
  const n = await p.evaluate(() => slides.length);
  for (let i = 0; i < n; i++) {
    await p.evaluate(k => show(k), i);
    await p.waitForTimeout(450);
    await p.locator('.deck').screenshot({ path: path.join(dst, String(i + 1).padStart(2, '0') + '.png') });
  }
  if (pdf) {
    await p.emulateMedia({ media: 'print' });
    await p.pdf({ path: pdf, width: '1280px', height: '720px', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  }
  await b.close();
  console.log('shot', n, 'slides');
})();

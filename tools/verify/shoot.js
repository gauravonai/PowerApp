// Screenshot every preview page. Usage: node shoot.js <htmlDir> <pngDir> [full]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [src, dst, full] = process.argv.slice(2);
  fs.mkdirSync(dst, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1366, height: 768 } });
  for (const f of fs.readdirSync(src).filter(f => f.endsWith('.html'))) {
    await p.goto('file://' + path.resolve(src, f));
    await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(dst, f.replace('.html', '.png')), fullPage: !!full });
  }
  await b.close();
})();

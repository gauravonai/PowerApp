// Drive the HTA (as a web page, demo data) through: request on-hand+10, reserve, release, check the shortfall book.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  for (const f of process.argv.slice(2)) {
    const html = '/tmp/claude-0/hta-under-test.html';
    fs.copyFileSync(f, html);
    const p = await b.newPage();
    await p.goto('file://' + html); await p.waitForTimeout(800);
    const r = await p.evaluate(() => {
      boot({e:'eng.one', n:'Engineer One', r:'Engineer', b:'EDS'});
      var part = null; for (var i=0;i<DB.parts.length;i++){ var x=bal(DB.parts[i].id); if (x.on>=10 && x.on<=200 && x.res===0){ part=DB.parts[i]; break; } }
      var on = bal(part.id).on;
      BOM = parseBom(part.pn + "\t" + (on + 10));
      VIEW='newreq'; render();
      [['f_mach','3CX'],['f_pcode','P1'],['f_harn','405/F8525'],['f_cc','IDC1'],['f_buc','A'],['f_dcc','B'],['f_circ','48'],['f_scope','test']].forEach(function(a){ document.getElementById(a[0]).value=a[1]; });
      document.getElementById('submitreq').click();
      var no = reqList()[0].no;
      boot({e:'gaurav.shelke', n:'Gaurav Shelke', r:'Lab Admin', b:'EDS'});
      act('reserve', no);
      openReq(no); act('release', no);
      var r = reqIndex()[no], l = r.lines[0];
      var book = shortageBook().filter(function(s){ return s.pn===part.pn; });
      return {part: part.pn, onHandBefore: on, requested: l.q, reserved: l.resv, released: l.rel, status: r.status,
              shortfallInBook: book.length ? book[0].qty : 0, onHandAfter: bal(part.id).on};
    });
    console.log(f.split('/').pop(), JSON.stringify(r));
    await p.close();
  }
  await b.close();
})();

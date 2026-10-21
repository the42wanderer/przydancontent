import { chromium } from 'playwright';
const [,, out, ...tags] = process.argv;
import fs from 'fs';
const browser = await chromium.launch();
const ctx = await browser.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141 Safari/537.36', viewport:{width:1280,height:900} });
const res = {};
for (const tag of tags) {
  const page = await ctx.newPage(); const items = [];
  page.on('response', async r => { const u=r.url(); if (/item_list|challenge\/item_list|search\/item/.test(u)) { try { const j = await r.json(); (j.itemList||j.item_list||[]).forEach(i=>items.push(i)); } catch {} } });
  try { await page.goto('https://www.tiktok.com/tag/'+tag, {waitUntil:'domcontentloaded', timeout:45000}); } catch(e) { console.log(tag,'goto fail',e.message); }
  for (let k=0;k<6;k++){ await page.waitForTimeout(2500); await page.mouse.wheel(0,3000); }
  res[tag] = items.map(i=>({id:i.id,author:i.author?.uniqueId,desc:i.desc,plays:i.stats?.playCount,saves:i.stats?.collectCount,shares:i.stats?.shareCount,date:i.createTime,music:i.music?.title+' — '+i.music?.authorName,dur:i.video?.duration}));
  console.log(tag, items.length, (await page.title()));
  await page.close();
}
fs.writeFileSync(out, JSON.stringify(res));
await browser.close();

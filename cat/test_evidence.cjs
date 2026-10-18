const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const url=process.env.CAT_FIXTURE_URL;assert(url&&!/:8765(?:\/|$)/.test(url));
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
  const page=await browser.newPage(), errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);
  assert.equal(await page.locator('#tab-evidence, #panel-evidence, script[src*="evidence"]').count(),0);
  for(const path of ['/evidence.js','/api/evidence','/api/practice']) assert.equal((await page.request.get(url+path)).status(),404);
  assert.deepEqual(errors,[]);console.log('PASS evidence removed: no tab, panel, script or API');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

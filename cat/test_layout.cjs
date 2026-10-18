// PLAYWRIGHT_MODULE may point at an existing Playwright installation.
// Run only against a disposable server containing at least two segments.
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
(async () => {
 const url = process.env.CAT_FIXTURE_URL;
 assert(url && !/:(8765)(?:\/|$)/.test(url), 'Set CAT_FIXTURE_URL to an isolated fixture');
 const out = process.env.CAT_TEST_OUTPUT || '.ekko-tmp/layout-verification';
 fs.mkdirSync(out,{recursive:true});
 const browser = await chromium.launch({headless:true, channel:'chrome'});
 try {
 const page = await browser.newPage({viewport:{width:1600,height:1000}});
 const errors=[]; page.on('pageerror', e=>errors.push(e.message));
 await page.goto(url); await page.waitForSelector('.segment-row');
 const box = selector => page.locator(selector).boundingBox();
 const near = (a,b) => assert(Math.abs(a-b)<2, `${a} != ${b}`);
 const check = async () => {
  const w=await box('#workspace'), d=await box('#discussion-pane'), e=await box('#editor-column'), dock=await box('#resource-dock');
  near(w.y,d.y);near(w.height,d.height);near(e.x,dock.x);near(e.width,dock.width);
  assert(dock.x+dock.width<=d.x);
  const form=await box('#chat-form');assert(form.y+form.height<=d.y+d.height+1);assert(form.y+form.height>d.y+d.height-10);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth), 'No horizontal page overflow');
 };
 await check();
 for(const [handle,pane,axis,delta] of [['discussion-splitter','editor-column','x',-90],['editor-splitter','editor-pane','y',-65],['resource-splitter','details-pane','x',-50]]) {
  const before=await box('#'+pane), h=await box('#'+handle), x=h.x+h.width/2,y=h.y+h.height/2;
  await page.mouse.move(x,y);await page.mouse.down();
  assert(await page.locator('#'+handle).evaluate(el=>el.hasPointerCapture(1)), 'Pointer captured');
  await page.mouse.move(x+(axis==='x'?delta:0),y+(axis==='y'?delta:0),{steps:8});await page.mouse.up();
  const after=await box('#'+pane);near(after[axis==='x'?'width':'height'],before[axis==='x'?'width':'height']+delta);
 }
 await check();
 // Exercise a long conversation without calling an external agent.
 await page.locator('#conversation').evaluate(el=>{el.textContent='Long conversation. '.repeat(2000);el.scrollTop=el.scrollHeight;});
 await check();
 assert(await page.locator('#conversation').evaluate(el=>el.scrollHeight>el.clientHeight),'Conversation scrolls internally');
 const dimensions=await Promise.all(['#editor-column','#editor-pane','#details-pane'].map(box));
 await page.reload();await page.waitForSelector('.segment-row');
 for(const [i,sel] of ['#editor-column','#editor-pane','#details-pane'].entries()){const b=await box(sel);near(b.width,dimensions[i].width);near(b.height,dimensions[i].height);}
 for(const [id,arrow] of [['discussion-splitter','ArrowLeft'],['editor-splitter','ArrowUp'],['resource-splitter','ArrowLeft']]) {
  const h=page.locator('#'+id);await h.focus();const v=Number(await h.getAttribute('aria-valuenow'));await h.press(arrow);near(Number(await h.getAttribute('aria-valuenow')),v-10);
  await h.press('Home');assert.equal(await h.getAttribute('aria-valuenow'),await h.getAttribute('aria-valuemin'));
  await h.press('End');assert.equal(await h.getAttribute('aria-valuenow'),await h.getAttribute('aria-valuemax'));await h.press('Enter');
 }
 await page.locator('.segment-row textarea').first().focus();
 await page.locator('#tab-notes').click();await page.waitForFunction(()=>!document.querySelector('#segment-note').disabled);
 await page.locator('#segment-note').fill('Isolated layout note ' + Date.now());await page.locator('#save-note').click();await page.getByText('备注已保存',{exact:true}).waitFor();
 await page.locator('#tab-history').click();await page.locator('.history-entry').first().waitFor();
 await page.locator('#tab-tm').click();await page.locator('#panel-tm input').first().waitFor();await page.locator('#panel-terms input').first().waitFor();
 await page.reload();await page.waitForSelector('.segment-row');await page.waitForTimeout(800);
 console.log(await page.evaluate(fs.readFileSync('cat/test_selection.js','utf8')));
 await page.waitForTimeout(900);
 await page.screenshot({path:out+'/desktop.png',fullPage:true});
 await page.setViewportSize({width:960,height:600});await page.waitForTimeout(100);await check();
 await page.evaluate(()=>localStorage.setItem('folio.workspace.layout.v1',JSON.stringify({discussion:999,editor:-999,resource:999})));
 await page.reload();await page.waitForSelector('.segment-row');await check();
 for(const id of ['discussion','editor','resource']){const h=page.locator('#'+id+'-splitter'),v=Number(await h.getAttribute('aria-valuenow'));assert(v>=Number(await h.getAttribute('aria-valuemin'))&&v<=Number(await h.getAttribute('aria-valuemax')));}
 await page.screenshot({path:out+'/clamped.png',fullPage:true});
 for(const width of [800,390]){await page.setViewportSize({width,height:844});await page.waitForTimeout(100);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Narrow viewport overflow');for(const id of ['editor-pane','details-pane','terminology-pane','discussion-pane'])assert((await box('#'+id)).height>=300);}
 await page.screenshot({path:out+'/mobile.png',fullPage:true});
 await page.setViewportSize({width:1600,height:1000});
 await page.evaluate(()=>localStorage.setItem('folio.workspace.layout.v1','{broken'));
 await page.reload();await page.waitForSelector('.segment-row');await check();
 await page.addInitScript(()=>{Storage.prototype.getItem=()=>{throw Error('blocked')};Storage.prototype.setItem=()=>{throw Error('blocked')};});
 await page.reload();await page.waitForSelector('.segment-row');await check();await page.locator('#discussion-splitter').press('ArrowLeft');
 assert.deepEqual(errors,[]);console.log('PASS: 3 drags/capture, keyboard bounds/reset, reload persistence, restored clamps, shrink, 390px stack, resources, real note save/history, pinned input, malformed/blocked storage');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

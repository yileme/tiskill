// Run against a disposable CAT server only. No external agent requests.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const url=process.env.CAT_FIXTURE_URL;assert(url&&!/:8765(?:\/|$)/.test(url));
 const out=process.env.CAT_TEST_OUTPUT;fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
 const page=await browser.newPage({viewport:{width:1600,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/api/term-search',r=>r.fulfill({json:{reply:'[Evidence](https://example.com) <img src=x>'}}));
 await page.goto(url);await page.waitForSelector('.segment-row');await page.waitForTimeout(800);
 const term=page.locator('#terminology-pane'),search=term.getByRole('searchbox',{name:'检索术语'});
 const icon=name=>term.getByRole('button',{name,exact:true});
 assert(await icon('编辑所选术语').isDisabled());assert(await icon('插入所选术语').isDisabled());
 for(const b of await term.locator('.resource-icon').all()){assert(await b.getAttribute('aria-label'));assert(await b.getAttribute('title'));}
 await icon('手动添加术语').click();
 const dialog=page.locator('#term-dialog');await dialog.getByLabel('原文术语').fill('药品监管');await dialog.getByLabel('译文术语').fill('drug regulation');await dialog.locator('summary').click();await dialog.getByLabel('备注').fill('<img src=x onerror=alert(1)> verified note');
 await dialog.getByRole('button',{name:'保存术语'}).click();await dialog.waitFor({state:'hidden'});
 await search.fill('药品监管');await search.press('Enter');await term.locator('.term-pair').waitFor();
 await term.locator('.term-pair').focus();await page.keyboard.press('Space');
 assert.equal(await term.locator('.term-pair').getAttribute('aria-pressed'),'true');assert(!(await icon('编辑所选术语').isDisabled()));
 await term.locator('.term-detail summary').click();await term.locator('.term-detail-body').waitFor();assert(await term.locator('.term-detail-body').isVisible());assert.equal(await term.locator('img').count(),0);
 await icon('编辑所选术语').click();assert(await dialog.getByLabel('原文术语').getAttribute('readonly')!==null);
 await dialog.getByLabel('译文术语').fill('pharmaceutical regulation');
 let patch;page.on('request',r=>{if(r.method()==='PATCH'&&r.url().endsWith('/api/resources'))patch=r.postDataJSON();});
 await dialog.getByRole('button',{name:'保存术语'}).click();await dialog.waitFor({state:'hidden'});assert.equal(patch.expectedTarget,'drug regulation');assert.equal(typeof patch.expectedVersion,'number');
 await term.locator('.term-pair').click();
 const input=page.locator('.segment-row textarea').first();await input.fill('Before ');await input.evaluate(el=>el.setSelectionRange(7,7));await icon('插入所选术语').click();assert.equal(await input.inputValue(),'Before pharmaceutical regulation');
 // Preserve stale-edit input on a real backend conflict.
 await icon('编辑所选术语').click();await dialog.getByLabel('译文术语').fill('draft retained');
 await page.request.patch(url+'/api/resources',{headers:{Origin:url},data:{...patch,target:'concurrent change',expectedTarget:'pharmaceutical regulation',expectedVersion:patch.expectedVersion+1}});
 await dialog.getByRole('button',{name:'保存术语'}).click();await page.waitForTimeout(250);assert(await dialog.isVisible());assert.equal(await dialog.getByLabel('译文术语').inputValue(),'draft retained');assert.equal(await dialog.locator('[data-error=true]').count(),1);await dialog.getByRole('button',{name:'取消'}).click();
 await icon('术语库设置').click();assert.equal(await icon('术语库设置').getAttribute('aria-expanded'),'true');
 await term.getByLabel('新资源库名称').fill('Fixture CSV');await term.getByLabel('导入 CSV 文件').setInputFiles({name:'terms.csv',mimeType:'text/csv',buffer:Buffer.from('source,target,sourceLocale,targetLocale\n药品监管,drug regulation,zh-CN,en\n')});
 await term.getByRole('button',{name:'导入并挂载资源库'}).click();await term.getByRole('checkbox',{name:'Fixture CSV'}).waitFor();assert(await term.getByRole('checkbox',{name:'Fixture CSV'}).isChecked());
 await term.getByRole('checkbox',{name:'Fixture CSV'}).uncheck();await page.waitForTimeout(200);await term.getByRole('checkbox',{name:'Fixture CSV'}).check();await page.waitForTimeout(200);
 await icon('搜索设置').click();await search.fill('no-such-term-123');await search.press('Enter');await page.waitForTimeout(300);assert.equal(await term.locator('.term-pair').count(),0);assert(await icon('编辑所选术语').isDisabled());assert.match(await term.locator('.panel-pad > .resource-status').innerText(),/暂无匹配/);
 await search.fill('药品监管');await search.press('Enter');await page.waitForTimeout(300);await icon('在线查证术语').click();await term.locator('.term-online-result a').waitFor();assert.equal(await term.locator('.term-online-result img').count(),0);
 await icon('清空检索').click();assert.equal(await search.inputValue(),'');assert(await icon('在线查证术语').isDisabled());
 await search.fill('药品监管');await search.press('Enter');await page.waitForTimeout(300);await term.locator('.term-pair').first().click();
await icon('手动添加术语').click();assert.equal(await dialog.evaluate(el=>el.tagName),'SECTION');assert.equal(await page.locator(':modal').count(),0);assert.equal(await dialog.locator('details').getAttribute('open'),null);
await dialog.getByLabel('原文术语').fill('未保存草稿');await dialog.getByLabel('译文术语').fill('retained draft');
await page.locator('.segment-row textarea').nth(1).click();await page.waitForTimeout(500);
assert(await page.locator('.segment-row').nth(1).evaluate(el=>el.classList.contains('is-current')));
await icon('选区添加术语').click();assert.equal(await dialog.getByLabel('译文术语').inputValue(),'retained draft');
const a=await dialog.getByLabel('原文术语').boundingBox(),b=await dialog.getByLabel('译文术语').boundingBox();assert(Math.abs(a.y-b.y)<2);
await page.screenshot({path:out+'/terminology-desktop.png',fullPage:true});
await dialog.getByRole('button',{name:'取消'}).click();assert(await icon('手动添加术语').evaluate(el=>el===document.activeElement));
await icon('手动添加术语').click();await dialog.getByLabel('原文术语').fill('无需备注');await dialog.getByLabel('译文术语').fill('without note');await dialog.getByRole('button',{name:'保存术语'}).click();await dialog.waitFor({state:'hidden'});

 await page.locator('#resource-splitter').press('End');await page.waitForTimeout(100);
 assert(await term.evaluate(el=>el.scrollWidth<=el.clientWidth),'pane overflow');assert(await page.locator('#panel-terms').evaluate(el=>el.scrollWidth<=el.clientWidth),'body overflow');
 await icon('搜索设置').click();assert(await page.locator('#panel-terms').evaluate(el=>el.scrollWidth<=el.clientWidth),'settings overflow');
 await page.screenshot({path:out+'/terminology-narrow-settings.png',fullPage:true});
 await icon('搜索设置').click();
 await page.setViewportSize({width:390,height:844});await icon('手动添加术语').click();assert(await dialog.evaluate(el=>el.scrollWidth<=el.clientWidth));await page.screenshot({path:out+'/composer-mobile.png',fullPage:true});await dialog.getByLabel('原文术语').press('Escape');await dialog.waitFor({state:'hidden'});
 console.log(await page.evaluate(fs.readFileSync('cat/test_selection.js','utf8')));
 assert.deepEqual(errors,[]);console.log('PASS terminology: create/search/keyboard selection/edit/conflict/insert, CSV mount, empty state, labels, safe text, narrow settings, selection regression');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});

// Isolated fixture only; all agent requests intercepted, never sent to a backend.
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
  const url = process.env.CAT_FIXTURE_URL;
  assert(url && !/:(8765)(?:\/|$)/.test(url), 'Set an isolated CAT_FIXTURE_URL');
  const out = process.env.CAT_TEST_OUTPUT || '.ekko-tmp/chat-verification';
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({headless:true, channel:'chrome'});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:900}});
    const errors=[]; page.on('pageerror',e=>errors.push(e.message));
    let pending, calls=0;
    await page.route('**/api/chat',route=>{pending=route;calls++;});
    await page.goto(url); await page.waitForSelector('.segment-row');
    await page.clock.install();
    const input=page.locator('#chat-input'), bubble=page.locator('.chat-pending');
    const send=async text=>{pending=null;await input.fill(text);await page.locator('#chat-send').click();await bubble.waitFor();while(!pending)await new Promise(r=>setTimeout(r,10));};
    const reply=async body=>{await pending.fulfill({json:body});await bubble.waitFor({state:'detached'});};
    await send('请检查译文，保留数字 20 / 60。');
    assert.equal(await page.locator('#conversation > :last-child').getAttribute('class'),'chat-entry assistant chat-pending');
    assert.equal(await page.locator('#chat-form').getAttribute('aria-busy'),'true');
    assert.equal(await input.isDisabled(),true);
    assert.equal(await bubble.locator('[role=status]').getAttribute('aria-live'),'polite');
    await page.clock.fastForward(21000);
    assert.match(await bubble.innerText(),/21 秒/);assert.match(await bubble.innerText(),/仍在等待/);
    await page.screenshot({path:out+'/waiting.png',fullPage:true});
    await page.locator('.segment-row textarea').nth(1).focus();
    assert.equal(await bubble.count(),0);assert.equal(await page.locator('#chat-form').getAttribute('aria-busy'),'false');
    await page.clock.fastForward(40000);
    await page.locator('.segment-row textarea').first().focus();await bubble.waitFor();
    assert.match(await bubble.innerText(),/61 秒/);assert.match(await bubble.innerText(),/耗时较长/);
    await page.emulateMedia({reducedMotion:'reduce'});
    assert.equal(await bubble.locator('i').first().evaluate(el=>getComputedStyle(el).animationName),'none');
    await page.emulateMedia({reducedMotion:'no-preference'});
    const markdown='**需要修改： 无。 **\n\n保留数字 20 / 60，*自然表达*，以及 [词典](https://example.com/usage?q=1)。\n\n- 第一条 **建议**\n- 第二条\n\n1. 核对条件\n2. 保留原意\n\n> 引文与上下文\n\n`<safe>`\n\n```html\n<script>window.pwned=1</script>\n```\n\n<img src=x onerror="window.pwned=1"> [bad](javascript:alert(1)) [data](data:text/html,evil) [relative](/evil)';
    await reply({reply:markdown});
    assert.equal(await page.locator('#chat-form').getAttribute('aria-busy'),'false');assert.equal(await input.isDisabled(),false);
    const md=page.locator('.chat-markdown');
    assert.equal(await md.locator('strong').first().innerText(),'需要修改： 无。 ');
    assert.equal(await md.locator('em').innerText(),'自然表达');
    assert.equal(await md.locator('ul li').count(),2);assert.equal(await md.locator('ol li').count(),2);
    assert.equal(await md.locator('blockquote').innerText(),'引文与上下文');assert.equal(await md.locator('pre code').count(),1);
    assert.equal(await md.locator('a').count(),1);assert.equal(await md.locator('a').getAttribute('target'),'_blank');
    assert.equal(await md.locator('a').getAttribute('rel'),'noopener noreferrer');
    assert.equal(await md.locator('script,img,iframe,svg').count(),0);assert.equal(await page.evaluate(()=>window.pwned),undefined);
    // More URL/HTML attacks and nested emphasis are tested on the real renderer.
    const security=await page.evaluate(()=>{
      const node=FolioMarkdown.render('**outer *inner*** [x](JaVaScRiPt:evil) [x](//evil) [x](https://example.com) <svg onload=alert(1)> &lt;script&gt; `**literal**`');
      return {links:[...node.querySelectorAll('a')].map(a=>a.protocol),html:node.querySelectorAll('svg,script,img').length,text:node.textContent};
    });
    assert.deepEqual(security.links,['https:']);assert.equal(security.html,0);assert.match(security.text,/\*\*literal\*\*/);
    await page.locator('#conversation').evaluate(el=>el.scrollTop=0);
    await page.screenshot({path:out+'/markdown.png',fullPage:true});
    await send('失败后请保留这个问题');
    await page.locator('#conversation').evaluate(el=>el.scrollTop=0);
    await page.clock.fastForward(2000);assert.equal(await page.locator('#conversation').evaluate(el=>el.scrollTop),0);
    await pending.fulfill({status:502,json:{error:'Fixture upstream unavailable'}});await bubble.waitFor({state:'detached'});
    assert.equal(await page.locator('#conversation').evaluate(el=>el.scrollTop),0);
    assert.equal(await input.inputValue(),'失败后请保留这个问题');assert.equal(await input.isDisabled(),false);
    await page.clock.fastForward(10000);
    assert.match(await page.locator('#conversation').innerText(),/请求失败：Fixture upstream unavailable/);
    await page.reload();await page.waitForSelector('.segment-row');
    assert.match(await page.locator('#conversation').innerText(),/请求失败：Fixture upstream unavailable/);
    // Completion on another segment must not move focus or show the wrong response.
    await send('后台回复归属测试');await page.locator('.segment-row textarea').nth(1).focus();
    await pending.fulfill({json:{reply:'第一段独有回复'}});
    await page.waitForFunction(()=>!document.querySelector('#chat-input').disabled);
    assert.equal(await bubble.count(),0);assert.doesNotMatch(await page.locator('#conversation').innerText(),/第一段独有回复/);
    assert.equal(await page.locator('.segment-row textarea').nth(1).evaluate(el=>el===document.activeElement),true);
    await page.locator('.segment-row textarea').first().focus();
    assert.match(await page.locator('#conversation').innerText(),/第一段独有回复/);
    assert.equal(calls,3);assert.deepEqual(errors,[]);
    console.log('PASS: safe Markdown and malicious fixtures; pending order; elapsed 21/61s; segment switching; reduced motion; success/error cleanup; persistent error and restored input; scroll retention; background response focus. 3 intercepted requests, zero real agent requests.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

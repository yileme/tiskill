(() => {
  'use strict';
  const input = document.querySelector('#segment-note'), save = document.querySelector('#save-note');
  const status = document.querySelector('#note-status'), history = document.querySelector('#segment-history');
  const selected = () => document.querySelector('.segment-row.is-current:not(.is-hidden)')?.dataset.id || null;
  const drafts = new Map();
  let current = null, epoch = 0, busy = false;
  const tabs = [...document.querySelectorAll('[data-detail]')];
  function activate(tab) {
    for (const item of tabs) {
      const on = item === tab;
      item.setAttribute('aria-selected', String(on)); item.tabIndex = on ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !on;
    }
  }
  for (const tab of tabs) {
    tab.addEventListener('click', () => activate(tab));
    tab.addEventListener('keydown', event => {
      let index = tabs.indexOf(tab);
      if (event.key === 'ArrowRight') index = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') index = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = tabs.length - 1;
      else return;
      event.preventDefault(); activate(tabs[index]); tabs[index].focus();
    });
  }
  document.querySelector('.details-pane').addEventListener('keydown', event => event.stopPropagation());
  function render() {
    const draft = drafts.get(current);
    input.disabled = !draft;
    input.value = draft?.text || '';
    save.disabled = !draft || draft.saving || draft.text === draft.base;
    status.textContent = draft?.message || (draft ? '备注独立保存，不改变译文版本。' : '选择段落后可添加备注。');
  }
  input.addEventListener('input', () => {
    const draft = drafts.get(current);
    if (!draft || selected() !== current) return;
    draft.text = input.value; draft.message = '尚未保存';
    save.disabled = draft.saving || draft.text === draft.base; status.textContent = draft.message;
  });
  async function request(url, options) {
    const response = await fetch(url, {cache: 'no-store', ...options});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '读取失败');
    return data;
  }
  save.addEventListener('click', async () => {
    const id = current, draft = drafts.get(id), generation = epoch;
    if (!draft || selected() !== id || draft.saving) return;
    const text = draft.text; draft.saving = true; render();
    try {
      await request(`/api/segments/${encodeURIComponent(id)}/note`, {method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({note: text, expectedNote: draft.base, projectId: draft.projectId})});
      draft.base = text; draft.message = draft.text === text ? '备注已保存' : '已保存上一版；当前输入尚未保存';
    } catch (error) { draft.message = error.message + ' 输入已保留；请复制后刷新并合并。'; }
    finally {
      draft.saving = false;
      if (generation === epoch && current === id && selected() === id) render();
    }
  });
  function drawHistory(items) {
    history.replaceChildren();
    if (!items.length) { history.textContent = '暂无可撤销的译文修改。'; return; }
    for (const [index, item] of [...items].reverse().entries()) {
      const card = document.createElement('article'); card.className = 'history-entry';
      const heading = document.createElement('small');
      heading.textContent = `撤销快照 ${items.length - index} · ${{empty:'未开始',draft:'已编辑',confirmed:'已确认'}[item.status] || item.status}`;
      const text = document.createElement('p'); text.textContent = item.target || '（空译文）';
      card.append(heading, text); history.append(card);
    }
  }
  async function poll() {
    const id = selected();
    if (current !== id) { current = id; history.replaceChildren(); render(); }
    document.querySelector('#details-segment').textContent = id ? `第 ${id} 段` : '未选择段落';
    if (!id || busy || document.hidden) return;
    busy = true; const generation = epoch;
    try {
      const data = await request(`/api/segments/${encodeURIComponent(id)}/details`);
      if (generation !== epoch || selected() !== id || current !== id) return;
      let draft = drafts.get(id);
      if (!draft || draft.projectId !== data.projectId) {
        draft = {text: data.note, base: data.note, projectId: data.projectId, saving: false}; drafts.set(id, draft); render();
      } else if (!draft.saving && draft.text === draft.base && draft.base !== data.note) {
        draft.text = draft.base = data.note; draft.message = ''; render();
      }
      drawHistory(data.history);
    } catch (error) { if (generation === epoch && current === id && selected() === id) status.textContent = error.message; }
    finally { busy = false; }
  }
  window.addEventListener('folio:project-changed', () => { epoch++; drafts.clear(); current = null; render(); });
  window.addEventListener('beforeunload', event => {
    if ([...drafts.values()].some(d => d.text !== d.base || d.saving)) { event.preventDefault(); event.returnValue = ''; }
  });
  activate(tabs[0]); void poll();
  const timer = setInterval(poll, 400);
  window.addEventListener('pagehide', () => clearInterval(timer), {once: true});
})();

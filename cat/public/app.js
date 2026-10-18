(() => {
  'use strict';

  const $ = (selector) => document.querySelector(selector);
  const els = {
    docTitle: $('#doc-title'), docMeta: $('#doc-meta'), rows: $('#segments'), filterNote: $('#filter-note'),
    toolStats: $('#tool-stats'), save: $('#save-indicator'), quickFind: $('#quick-find'),
    confirmBtn: $('#confirm-segment'), undoBtn: $('#undo-segment'),
    prevBtn: $('#prev-segment'), nextBtn: $('#next-segment'),
    contextNumber: $('#context-number'), contextSource: $('#context-source'),
    conversation: $('#conversation'), chatForm: $('#chat-form'), chatInput: $('#chat-input'), chatSend: $('#chat-send'),
    concInput: $('#concordance-input'), concResults: $('#concordance-results'), concCount: $('#concordance-count'),
    statusSegment: $('#status-segment'), statusState: $('#status-state'), statusCounts: $('#status-counts'),
    statusWords: $('#status-words'), progressBar: $('#progress-bar'), progressFill: $('#progress-fill'),
    progressConfirmed: $('#progress-confirmed'), progressPercent: $('#progress-percent'), progressLabel: $('#progress-label'),
    unconfirmedCount: $('#unconfirmed-count'), nextUnconfirmed: $('#next-unconfirmed'), menu: $('#row-menu'),
    exportOpen: $('#export-open'), exportMenu: $('#export-menu'),
    dialog: $('#import-dialog'), importForm: $('#import-form'), importText: $('#import-text'), importTitle: $('#import-title-input'), importSubmit: $('#import-submit'),
    shortcutDialog: $('#shortcut-dialog'), toast: $('#toast')
  };

  const STATES = {
    empty: { label: '未开始', cls: 'st-empty' },
    draft: { label: '已编辑', cls: 'st-draft' },
    confirmed: { label: '已确认', cls: 'st-confirmed' }
  };

  let project = null;
  let selectedId = null;
  let activeFilter = 'all';
  let query = '';
  let loadingChat = false;
  let pendingChatId = null;
  let pendingStarted = 0;
  let waitingTimer;
  let drawnChatId = null;
  const chatScroll = new Map();
  let toastTimer;
  const threads = new Map();
  const writes = new Map();
  const timers = new Map();
  let sourceCounts = new Map();
  const threadStoreKey = 'folio.segment-conversations.v1';

  const displayKey = 'folio.display';
  const display = { density: 'cozy', font: 15 };

  /* ── helpers ───────────────────────────── */
  const words = (text) => (text.match(/[\p{L}\p{N}]+(?:['\u2019-][\p{L}\p{N}]+)*/gu) || []).length;
  const chars = (text) => text.replace(/\s/g, '').length;
  function segment(id) { return project?.segments.find((item) => String(item.id) === String(id)); }
  function rowEl(id) { return els.rows.querySelector(`.segment-row[data-id="${CSS.escape(String(id))}"]`); }
  function editor(id) { return rowEl(id)?.querySelector('.target-input'); }
  function indexOf(id) { return project.segments.findIndex((item) => String(item.id) === String(id)); }
  function numberFor(id) { return indexOf(id) + 1; }
  function isRepetition(item) { return (sourceCounts.get(normalize(item.source)) || 0) > 1; }
  function normalize(text) { return text.trim().replace(/\s+/g, ' ').toLowerCase(); }
  function savedState(item) { return STATES[item.status] ? item.status : 'empty'; }
  function countSources() {
    sourceCounts = new Map();
    for (const item of project?.segments || []) {
      const key = normalize(item.source);
      sourceCounts.set(key, (sourceCounts.get(key) || 0) + 1);
    }
  }
  function visible(item) {
    if (activeFilter === 'repetition') { if (!isRepetition(item)) return false; }
    else if (activeFilter !== 'all' && savedState(item) !== activeFilter) return false;
    if (query) {
      const needle = query.toLowerCase();
      if (!item.source.toLowerCase().includes(needle) && !(item.target || '').toLowerCase().includes(needle)) return false;
    }
    return true;
  }
  function visibleIds() { return (project?.segments || []).filter(visible).map((item) => item.id); }

  /* ── messaging ─────────────────────────── */
  function notice(message) {
    els.toast.textContent = message;
    els.toast.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => els.toast.classList.remove('visible'), 3600);
  }
  function saveState(text, state = 'ready') {
    els.save.lastChild.textContent = text;
    els.save.dataset.state = state;
  }
  function showError(error) {
    saveState('操作失败', 'error');
    notice(error.message || '出了点问题，请重试。');
  }
  async function request(path, options = {}) {
    let response;
    try {
      response = await fetch(path, {
        ...options,
        headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers }
      });
    } catch {
      throw new Error('无法连接服务器，请检查连接后重试。');
    }
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      const error = new Error(body?.error || body?.message || `请求失败（${response.status}）。`);
      error.status = response.status;
      throw error;
    }
    return response.json();
  }

  /* ── bars ──────────────────────────────── */
  function refreshProgress() {
    const all = project?.segments || [];
    const done = all.filter((item) => (item.target || '').trim()).length;
    const confirmed = all.filter((item) => savedState(item) === 'confirmed').length;
    const percent = all.length ? Math.round(done / all.length * 100) : 0;
    const confirmedPercent = all.length ? Math.round(confirmed / all.length * 100) : 0;
    const counts = { empty: 0, draft: 0, confirmed: 0 };
    for (const item of all) counts[savedState(item)] += 1;
    const open = counts.empty + counts.draft;
    els.toolStats.textContent = `已确认 ${confirmed} / ${all.length}`;
    els.nextUnconfirmed.disabled = open === 0;
    els.unconfirmedCount.textContent = String(open);
    els.unconfirmedCount.dataset.zero = String(open === 0);
    els.statusCounts.textContent = `未开始 ${counts.empty} · 已编辑 ${counts.draft} · 已确认 ${counts.confirmed}`;
    els.progressFill.style.width = `${percent}%`;
    els.progressConfirmed.style.width = `${confirmedPercent}%`;
    els.progressPercent.textContent = `${confirmedPercent}%`;
    els.progressBar.setAttribute('aria-valuenow', String(confirmedPercent));
    els.progressLabel.textContent = `已译 ${percent}% · 已确认 ${confirmedPercent}%`;
    const targetText = all.map((item) => item.target || '').join(' ');
    els.statusWords.textContent = `译文 ${words(targetText)} 词 · ${chars(targetText)} 字符`;
  }
  function refreshStatusBar() {
    const total = project?.segments.length || 0;
    const item = segment(selectedId);
    els.statusSegment.textContent = item ? `第 ${numberFor(item.id)} 段 / 共 ${total} 段` : `第 0 段 / 共 ${total} 段`;
    const state = item ? savedState(item) : 'empty';
    els.statusState.className = `state-pill ${STATES[state].cls}`;
    els.statusState.textContent = item ? STATES[state].label : '未选择';
    els.confirmBtn.disabled = !item;
    els.undoBtn.disabled = !item || (!item.target && !item.version);
    els.prevBtn.disabled = !item || indexOf(item.id) === 0;
    els.nextBtn.disabled = !item || indexOf(item.id) === total - 1;
  }

  /* ── rows ──────────────────────────────── */
  function updateRow(item, { preserveDraft = false, skipBars = false } = {}) {
    const element = rowEl(item.id);
    if (!element) return;
    const input = element.querySelector('.target-input');
    if (!preserveDraft) input.value = item.target || '';
    const dirty = input.value !== (item.target || '');
    const state = dirty ? 'draft' : savedState(item);
    const pill = element.querySelector('.state-pill');
    pill.className = `state-pill ${STATES[state].cls}`;
    pill.textContent = STATES[state].label;
    element.classList.toggle('st-confirmed', state === 'confirmed');
    element.querySelector('.seg-count').textContent = input.value ? `${words(input.value)} 词` : '';
    element.querySelector('.row-undo').disabled = !item.target && !item.version;
    if (skipBars) return;
    refreshProgress();
    if (String(selectedId) === String(item.id)) refreshStatusBar();
  }
  function drawRows() {
    els.rows.replaceChildren();
    if (!project.segments.length) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.textContent = '还没有文稿，导入原文后即可开始。';
      els.rows.append(empty);
      select(null); refreshProgress();
      return;
    }
    const fragment = document.createDocumentFragment();
    project.segments.forEach((item, index) => {
      const line = document.createElement('div');
      line.className = 'segment-row';
      line.dataset.id = String(item.id);
      line.setAttribute('role', 'listitem');
      line.setAttribute('aria-label', `第 ${index + 1} 段：${item.source}`);

      const no = document.createElement('div');
      no.className = 'col-no';
      no.tabIndex = 0;
      no.setAttribute('role', 'button');
      no.setAttribute('aria-label', `定位第 ${index + 1} 段`);
      const number = document.createElement('span');
      number.textContent = String(index + 1);
      no.append(number);
      if (isRepetition(item)) {
        const repeat = document.createElement('span');
        repeat.className = 'row-repetition';
        repeat.textContent = '重复';
        repeat.title = '本文稿中出现多次相同原文';
        no.append(repeat);
      }

      const statusCell = document.createElement('div');
      statusCell.className = 'col-status';
      const pill = document.createElement('span');
      pill.className = 'state-pill st-empty';
      pill.textContent = STATES.empty.label;
      statusCell.append(pill);

      const source = document.createElement('div');
      source.className = 'col-source';
      const sourceText = document.createElement('p');
      sourceText.className = 'source-text';
      sourceText.textContent = item.source;
      source.append(sourceText);

      const targetCell = document.createElement('div');
      targetCell.className = 'col-target';
      const input = document.createElement('textarea');
      input.className = 'target-input';
      input.rows = 2;
      input.value = item.target || '';
      input.placeholder = '在这里写译文…';
      input.setAttribute('aria-label', `第 ${index + 1} 段译文`);
      const foot = document.createElement('div');
      foot.className = 'target-foot';
      const count = document.createElement('span');
      count.className = 'seg-count';
      const undo = document.createElement('button');
      undo.className = 'row-undo';
      undo.type = 'button';
      undo.textContent = '撤销';
      undo.setAttribute('aria-label', `撤销第 ${index + 1} 段的上次修改`);
      undo.addEventListener('click', () => void undoChange(item.id));
      foot.append(count, undo);
      targetCell.append(input, foot);

      line.append(no, statusCell, source, targetCell);
      line.addEventListener('mousedown', (event) => { if (!event.target.closest('.target-input')) select(item.id, { focus: false }); });
      source.addEventListener('click', () => { if (window.getSelection()?.toString()) return; select(item.id); });
      no.addEventListener('click', () => select(item.id, { focus: false }));
      no.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(item.id); input.focus(); }
      });
      input.addEventListener('focus', () => select(item.id, { focus: false }));
      input.addEventListener('input', () => { updateRow(item, { preserveDraft: true }); scheduleSave(item.id); });
      input.addEventListener('blur', () => { clearTimeout(timers.get(item.id)); void saveTarget(item.id).catch(showError); });
      input.addEventListener('keydown', (event) => inputKeydown(event, item.id));
      fragment.append(line);
    });
    els.rows.append(fragment);
    project.segments.forEach((item) => updateRow(item, { skipBars: true }));
    applyVisibility();
    select(selectedId && segment(selectedId) ? selectedId : project.segments[0]?.id ?? null, { focus: false });
    refreshProgress();
  }
  function inputKeydown(event, id) {
    const meta = event.metaKey || event.ctrlKey;
    if (meta && event.key === 'Enter') {
      event.preventDefault();
      void confirmSegment(id, !event.shiftKey);
      return;
    }
    if (meta && event.shiftKey && event.key.toLowerCase() === 'c') {
      event.preventDefault();
      void copySource(id);
      return;
    }
    if (meta && event.shiftKey && (event.key === 'Backspace' || event.key === 'Delete')) {
      event.preventDefault();
      void clearTarget(id);
      return;
    }
    if (event.key === 'Tab' && !event.isComposing) {
      event.preventDefault();
      moveSelection(event.shiftKey ? -1 : 1, { focusEditor: true });
      return;
    }
    if (event.altKey && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      event.preventDefault();
      moveSelection(event.key === 'ArrowDown' ? 1 : -1, { focusEditor: true });
      return;
    }
    if (event.key === 'Escape') {
      const item = segment(id);
      const input = editor(id);
      if (item && input && input.value !== (item.target || '')) {
        input.value = item.target || '';
        updateRow(item, { preserveDraft: true });
        notice('已放弃本段未保存的编辑。');
      }
      input?.blur();
    }
  }

  /* ── selection & navigation ────────────── */
  function select(id, { focus = false } = {}) {
    selectedId = id;
    els.rows.querySelectorAll('.segment-row').forEach((element) => {
      element.classList.toggle('is-current', element.dataset.id === String(id));
    });
    const item = segment(id);
    els.contextNumber.textContent = item ? `第 ${numberFor(id)} 段` : '未选择段落';
    els.contextSource.textContent = item?.source || '选择段落后可以讨论译法。';
    els.chatInput.disabled = !item || loadingChat;
    els.chatSend.disabled = !item || loadingChat;
    refreshStatusBar();
    drawConversation();
    if (focus && item) editor(id)?.focus();
  }
  function moveSelection(delta, { focusEditor = false } = {}) {
    const ids = visibleIds();
    if (!ids.length) return;
    const current = ids.indexOf(String(selectedId));
    const nextIndex = current < 0 ? (delta > 0 ? 0 : ids.length - 1) : Math.max(0, Math.min(ids.length - 1, current + delta));
    const id = ids[nextIndex];
    select(id, { focus: false });
    if (focusEditor) editor(id)?.focus();
    else rowEl(id)?.querySelector('.col-no')?.focus();
    rowEl(id)?.scrollIntoView({ block: 'nearest' });
  }
  function jumpTo(id, { focusEditor = false } = {}) {
    select(id, { focus: false });
    rowEl(id)?.scrollIntoView({ block: 'center' });
    if (focusEditor) editor(id)?.focus();
    else rowEl(id)?.querySelector('.col-no')?.focus();
  }

  /* ── filtering ─────────────────────────── */
  function applyVisibility() {
    if (!project) return;
    let shown = 0;
    for (const item of project.segments) {
      const element = rowEl(item.id);
      if (!element) continue;
      const ok = visible(item);
      element.classList.toggle('is-hidden', !ok);
      if (ok) shown += 1;
    }
    const filtering = activeFilter !== 'all' || !!query;
    els.filterNote.hidden = !filtering || shown > 0;
    if (filtering && shown === 0) {
      els.filterNote.textContent = query
        ? `没有段落同时满足当前过滤条件与「${query}」。`
        : '当前过滤条件下没有段落。';
    }
  }

  /* ── saving ────────────────────────────── */
  function queueWrite(id, operation) {
    const key = String(id);
    const previous = writes.get(key) || Promise.resolve();
    const pending = previous.catch(() => {}).then(operation);
    writes.set(key, pending);
    pending.finally(() => { if (writes.get(key) === pending) writes.delete(key); }).catch(() => {});
    return pending;
  }
  function scheduleSave(id) {
    clearTimeout(timers.get(id));
    timers.set(id, setTimeout(() => { timers.delete(id); void saveTarget(id).catch(showError); }, 700));
  }
  function patchSegment(id, body) {
    return queueWrite(id, async () => {
      saveState('正在保存…', 'busy');
      const data = await request(`/api/segments/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(body) });
      const current = segment(id);
      Object.assign(current, data.segment);
      project.revision += 1;
      persistThreads();
      saveState('已保存');
      return current;
    });
  }
  function saveTarget(id, { status } = {}) {
    clearTimeout(timers.get(id)); timers.delete(id);
    const input = editor(id);
    const value = input?.value ?? segment(id)?.target ?? '';
    return queueWrite(id, async () => {
      const current = segment(id);
      if (!current) throw new Error('段落不存在');
      const changed = value !== (current.target || '');
      const nextStatus = status || (changed ? (value.trim() ? 'draft' : 'empty') : savedState(current));
      if (!changed && nextStatus === savedState(current)) return current;
      saveState('正在保存…', 'busy');
      const data = await request(`/api/segments/${encodeURIComponent(id)}`, {
        method: 'PATCH', body: JSON.stringify({target: value, status: nextStatus, expectedVersion: current.version})
      });
      Object.assign(current, data.segment); project.revision += 1;
      updateRow(current, {preserveDraft: input?.value !== value});
      persistThreads(); saveState('已保存'); return current;
    });
  }
  async function confirmSegment(id, moveNext) {
    try {
      clearTimeout(timers.get(id));
      const input = editor(id);
      const value = input?.value ?? segment(id)?.target ?? '';
      if (!value.trim()) { notice('译文为空，先写译文再确认。'); input?.focus(); return; }
      const updated = await saveTarget(id, { status: 'confirmed' });
      updateRow(updated);
      const stale = repetitionPeers(id).filter((peer) => (peer.target || '') !== (updated.target || ''));
      notice(stale.length
        ? `已确认。另有 ${stale.length} 处相同原文，可右键「同步到相同原文」。`
        : (moveNext ? '已确认，进入下一段。' : '已确认当前段落。'));
      if (moveNext) moveSelection(1, { focusEditor: true });
      else input?.focus();
    } catch (error) { showError(error); }
  }
  async function undoChange(id) {
    try {
      clearTimeout(timers.get(id));
      await saveTarget(id);
      await queueWrite(id, async () => {
        saveState('正在撤销…', 'busy');
        const data = await request('/api/undo', { method: 'POST', body: JSON.stringify({ segmentId: id, expectedVersion: segment(id).version }) });
        const current = segment(id);
        Object.assign(current, data.segment);
        project.revision += 1;
        persistThreads();
        updateRow(current);
        saveState('已保存');
      });
      notice('已撤销上次修改。');
    } catch (error) { showError(error); }
  }

  /* ── segment operations ────────────────── */
  function repetitionPeers(id) {
    const item = segment(id);
    if (!item) return [];
    const key = normalize(item.source);
    return project.segments.filter((peer) => String(peer.id) !== String(id) && normalize(peer.source) === key);
  }
  async function flushDirty() {
    const jobs = [];
    for (const item of project.segments) {
      const input = editor(item.id);
      if (input && input.value !== (item.target || '')) {
        clearTimeout(timers.get(item.id));
        jobs.push(saveTarget(item.id));
      }
    }
    await Promise.all([...writes.values(), ...jobs]);
  }
  async function copySource(id) {
    try {
      const item = segment(id);
      if (!item) return;
      const input = editor(id);
      if (input) input.value = item.source;
      updateRow(item, { preserveDraft: true });
      await saveTarget(id);
      notice('已把原文填入译文，请按需改写。');
    } catch (error) { showError(error); }
  }
  async function clearTarget(id) {
    try {
      const input = editor(id);
      if (input) input.value = '';
      clearTimeout(timers.get(id));
      const updated = await saveTarget(id, { status: 'empty' });
      updateRow(updated);
      notice('已清空本段译文。');
    } catch (error) { showError(error); }
  }
  async function syncRepetitions(id) {
    try {
      await flushDirty();
      const item = segment(id);
      const peers = repetitionPeers(id).filter((peer) => (peer.target || '') !== (item.target || ''));
      if (!peers.length) { notice('没有内容不同的相同原文段落。'); return; }
      for (const peer of peers) {
        const updated = await patchSegment(peer.id, { target: item.target || '', status: item.target ? 'draft' : 'empty', expectedVersion: peer.version });
        updateRow(updated);
      }
      notice(`已把本段译文同步到另外 ${peers.length} 处相同原文。`);
    } catch (error) { showError(error); }
  }
  function moveToUnconfirmed() {
    const ids = (project?.segments || []).filter((item) => savedState(item) !== 'confirmed').map((item) => item.id);
    if (!ids.length) { notice('没有未确认的段落。'); return; }
    const current = ids.indexOf(String(selectedId));
    const id = ids[(current + 1) % ids.length];
    if (activeFilter !== 'all' || query) { activeFilter = 'all'; query = ''; els.quickFind.value = ''; syncFilterChips(); applyVisibility(); }
    jumpTo(id, { focusEditor: true });
  }
  function findInConcordance(id) {
    const item = segment(id);
    if (!item) return;
    document.querySelector('#panel-search')?.scrollIntoView({block:'nearest'});
    els.concInput.value = item.source.trim();
    drawConcordance();
  }

  /* ── panels: concordance ───────────────── */
  function highlight(text, needle) {
    const fragment = document.createDocumentFragment();
    if (!needle) { fragment.append(text); return fragment; }
    const lower = text.toLowerCase();
    const target = needle.toLowerCase();
    let cursor = 0;
    while (true) {
      const at = lower.indexOf(target, cursor);
      if (at < 0) break;
      if (at > cursor) fragment.append(text.slice(cursor, at));
      const mark = document.createElement('mark');
      mark.textContent = text.slice(at, at + needle.length);
      fragment.append(mark);
      cursor = at + needle.length;
    }
    fragment.append(text.slice(cursor));
    return fragment;
  }
  function drawConcordance() {
    const needle = els.concInput.value.trim();
    els.concResults.replaceChildren();
    if (!needle) { els.concCount.textContent = '输入关键词后显示命中位置。'; return; }
    const hits = (project?.segments || []).filter((item) =>
      item.source.toLowerCase().includes(needle.toLowerCase()) ||
      (item.target || '').toLowerCase().includes(needle.toLowerCase()));
    els.concCount.textContent = hits.length
      ? `命中 ${hits.length} 段（含原文与译文）。`
      : '本文稿中没有匹配内容。';
    for (const item of hits.slice(0, 80)) {
      const card = document.createElement('button');
      card.className = 'hit';
      card.type = 'button';
      const head = document.createElement('div');
      head.className = 'hit-head';
      const no = document.createElement('span');
      no.textContent = `第 ${numberFor(item.id)} 段`;
      const state = document.createElement('span');
      state.textContent = STATES[savedState(item)].label;
      head.append(no, state);
      const src = document.createElement('span');
      src.className = 'hit-src';
      src.append(highlight(item.source, needle));
      const tgt = document.createElement('span');
      tgt.className = 'hit-tgt';
      tgt.append(item.target ? highlight(item.target, needle) : '（尚无译文）');
      card.append(head, src, tgt);
      card.addEventListener('click', () => jumpTo(item.id, { focusEditor: true }));
      els.concResults.append(card);
    }
    if (hits.length > 80) {
      const more = document.createElement('p');
      more.className = 'panel-count';
      more.textContent = `另有 ${hits.length - 80} 段未显示，请细化关键词。`;
      els.concResults.append(more);
    }
  }

  /* ── chat ──────────────────────────────── */
  function documentSignature(data) {
    return JSON.stringify([data.id, data.title, data.segments.map((item) => [item.id, item.source])]);
  }
  function persistThreads() {
    if (!project) return;
    try {
      localStorage.setItem(threadStoreKey, JSON.stringify({
        signature: documentSignature(project), revision: project.revision,
        threads: Object.fromEntries(threads)
      }));
    } catch { /* Browser storage may be unavailable; chat still works until refresh. */ }
  }
  function restoreThreads() {
    threads.clear();
    try {
      const saved = JSON.parse(localStorage.getItem(threadStoreKey));
      if (saved?.signature !== documentSignature(project) ||
          !Number.isInteger(saved.revision) || saved.revision !== project.revision ||
          !saved.threads || typeof saved.threads !== 'object') return;
      for (const [id, messages] of Object.entries(saved.threads)) {
        if (!segment(id) || !Array.isArray(messages)) continue;
        threads.set(id, messages.filter((message) =>
          message && ['user', 'assistant'].includes(message.kind) &&
          typeof message.text === 'string'
        ).map((message) => {
          const proposal = message.proposal;
          const validProposal = proposal && String(proposal.segmentId) === id &&
            typeof proposal.after === 'string' &&
            Number.isInteger(proposal.expectedVersion);
          return {
            kind: message.kind, text: message.text,
            proposal: validProposal ? proposal : null,
            resolution: typeof message.resolution === 'string' ? message.resolution :
              validProposal && proposal.expectedVersion !== segment(id).version ? '译文已变化，建议已失效' : undefined
          };
        }));
      }
    } catch { /* Ignore damaged or blocked browser storage. */ }
  }
  function entry(kind, text) {
    const wrapper = document.createElement('div');
    wrapper.className = `chat-entry ${kind}`;
    const label = document.createElement('div');
    label.className = 'speaker';
    label.textContent = kind === 'user' ? '你' : 'CODEX AGENT';
    const body = kind === 'assistant' ? window.FolioMarkdown.render(text) : document.createElement('p');
    if (kind !== 'assistant') body.textContent = text;
    wrapper.append(label, body);
    return wrapper;
  }
  function updateWaiting() {
    const bubble = els.conversation.querySelector('.chat-pending');
    if (!bubble || !loadingChat || String(pendingChatId) !== String(selectedId)) return;
    const seconds = Math.floor((Date.now() - pendingStarted) / 1000);
    const wording = seconds >= 60 ? '仍在等待回复，耗时较长。你可以先查看其他段落。'
      : seconds >= 20 ? '仍在等待 Codex Agent 回复…' : '正在等待 Codex Agent 回复…';
    const status = bubble.querySelector('[role="status"]');
    if (status.textContent !== wording) status.textContent = wording;
    bubble.querySelector('.waiting-elapsed').textContent = `已等待 ${seconds} 秒`;
  }
  function drawConversation() {
    clearInterval(waitingTimer);
    const key = String(selectedId);
    const sameThread = drawnChatId === key;
    const oldTop = els.conversation.scrollTop;
    const atBottom = els.conversation.scrollHeight - oldTop - els.conversation.clientHeight < 40;
    if (drawnChatId !== null) chatScroll.set(drawnChatId, oldTop);
    drawnChatId = key;
    const busy = loadingChat && String(pendingChatId) === key;
    els.chatForm.setAttribute('aria-busy', String(busy));
    els.conversation.replaceChildren();
    const messages = threads.get(String(selectedId)) || [];
    if (!messages.length) {
      const empty = document.createElement('div');
      empty.className = 'chat-empty';
      empty.innerHTML = '<span class="chat-glyph" aria-hidden="true">“</span><p>从一个问题开始。</p><small>聊聊语气、原意，或更自然的说法。</small>';
      els.conversation.append(empty);
    }
    for (const message of messages) {
      if (message.proposal && !message.resolution &&
          message.proposal.expectedVersion !== segment(message.proposal.segmentId)?.version) {
        message.resolution = '译文已变化，建议已失效';
        persistThreads();
      }
      els.conversation.append(entry(message.kind, message.text));
      if (message.proposal) {
        const proposal = message.proposal;
        const card = document.createElement('div');
        card.className = 'proposal';
        const heading = document.createElement('div');
        heading.className = 'proposal-label';
        heading.textContent = '修改建议';
        const before = document.createElement('del');
        before.textContent = proposal.before || '（暂无译文）';
        const after = document.createElement('ins');
        after.textContent = proposal.after || '（暂无译文）';
        const reason = document.createElement('p');
        reason.className = 'proposal-reason';
        reason.textContent = proposal.reason || '';
        card.append(heading, before, after, reason);
        if (message.resolution) {
          const resolved = document.createElement('p');
          resolved.className = 'proposal-resolved';
          resolved.textContent = message.resolution;
          card.append(resolved);
        } else {
          const actions = document.createElement('div');
          actions.className = 'proposal-actions';
          const accept = document.createElement('button');
          accept.className = 'button button-dark';
          accept.type = 'button';
          accept.textContent = '应用修改';
          accept.addEventListener('click', () => void resolveProposal(message, true));
          const reject = document.createElement('button');
          reject.className = 'button button-quiet';
          reject.type = 'button';
          reject.textContent = '忽略';
          reject.addEventListener('click', () => void resolveProposal(message, false));
          actions.append(accept, reject);
          card.append(actions);
        }
        els.conversation.append(card);
      }
    }
    if (busy) {
      const bubble = document.createElement('div'); bubble.className = 'chat-entry assistant chat-pending';
      const dots = document.createElement('span'); dots.className = 'waiting-dots'; dots.setAttribute('aria-hidden', 'true');
      for (let i = 0; i < 3; i++) dots.append(document.createElement('i'));
      const status = document.createElement('span'); status.setAttribute('role', 'status');
      status.setAttribute('aria-live', 'polite');
      const elapsed = document.createElement('small'); elapsed.className = 'waiting-elapsed';
      elapsed.setAttribute('aria-live', 'off');
      bubble.append(dots, status, elapsed); els.conversation.append(bubble);
      updateWaiting(); waitingTimer = setInterval(updateWaiting, 1000);
    }
    els.conversation.scrollTop = sameThread
      ? (atBottom ? els.conversation.scrollHeight : oldTop)
      : (chatScroll.get(key) ?? els.conversation.scrollHeight);
  }
  async function resolveProposal(message, accept) {
    if (message.resolution) return;
    if (!accept) {
      message.resolution = '已忽略建议';
      persistThreads();
      drawConversation();
      return;
    }
    const proposal = message.proposal;
    const id = proposal.segmentId;
    const current = segment(id);
    if (!current) return showError(new Error('这条建议属于另一份文稿。'));
    const input = editor(id);
    if (input && input.value !== (current.target || '')) return showError(new Error('请先保存当前译文，再应用建议。'));
    try {
      await queueWrite(id, async () => {
        if (input && input.value !== (current.target || '')) throw new Error('请先保存当前译文，再应用建议。');
        saveState('正在应用…', 'busy');
        const data = await request('/api/proposals/apply', { method: 'POST', body: JSON.stringify({ proposal }) });
        Object.assign(current, data.segment);
        project.revision += 1;
        persistThreads();
        updateRow(current);
        saveState('已保存');
      });
      message.resolution = '已应用修改';
      persistThreads();
      if (String(selectedId) === String(id)) drawConversation();
      notice('已应用修改。');
    } catch (error) { showError(error); }
  }

  /* ── row context menu ──────────────────── */
  let menuSegmentId = null;
  function openRowMenu(id, x, y) {
    const item = segment(id);
    if (!item) return;
    menuSegmentId = id;
    select(id, { focus: false });
    const input = editor(id);
    const peers = repetitionPeers(id);
    const stale = peers.filter((peer) => (peer.target || '') !== ((input?.value ?? item.target) || ''));
    const state = {
      'copy-source': false,
      clear: !(input?.value ?? item.target),
      confirm: !((input?.value ?? item.target) || '').trim(),
      undo: !item.target && !item.version,
      sync: stale.length === 0
    };
    for (const button of els.menu.querySelectorAll('.row-menu-item')) {
      const action = button.dataset.action;
      button.disabled = !!state[action];
      button.textContent = action === 'sync'
        ? (stale.length ? `同步到相同原文（${stale.length} 处）` : '同步到相同原文')
        : { 'copy-source': '复制原文到译文', clear: '清空译文', confirm: '确认本段', undo: '撤销修改', find: '在检索中查找' }[action];
    }
    els.menu.hidden = false;
    const box = els.menu.getBoundingClientRect();
    els.menu.style.left = `${Math.max(8, Math.min(x, window.innerWidth - box.width - 8))}px`;
    els.menu.style.top = `${Math.max(8, Math.min(y, window.innerHeight - box.height - 8))}px`;
    els.menu.querySelector('.row-menu-item:not(:disabled)')?.focus();
  }
  function closeRowMenu() {
    if (els.menu.hidden) return;
    els.menu.hidden = true;
    menuSegmentId = null;
  }

  /* ── load & import ─────────────────────── */
  async function loadProject() {
    const data = await request('/api/project');
    project = data;
    window.dispatchEvent(new CustomEvent("folio:project-changed"));
    countSources();
    restoreThreads();
    els.docTitle.textContent = data.title || '未命名文稿';
    els.docMeta.textContent = `本地项目 · 共 ${data.segments.length} 段 · 改动自动保存`;
    document.title = `${data.title || '未命名文稿'} — Folio`;
    drawRows();
    drawConcordance();
    saveState('已保存');
  }
  els.importForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const lines = els.importText.value.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    if (!lines.length) return notice('请至少输入一行原文。');
    els.importSubmit.disabled = true;
    try {
      await flushDirty();
      const title = els.importTitle.value.trim() || '未命名文稿';
      if (project?.segments.length && !window.confirm('确定替换当前文稿？如需留存，请先导出。')) return;
      await request('/api/project', { method: 'POST', body: JSON.stringify({ title, segments: lines.map((source) => ({ source })), confirmReplace: !!project?.segments.length }) });
      selectedId = null;
      threads.clear();
      try { localStorage.removeItem(threadStoreKey); } catch { /* Storage may be unavailable. */ }
      els.dialog.close();
      els.importForm.reset();
      await loadProject();
      notice(`已导入 ${lines.length} 段。`);
    } catch (error) { showError(error); }
    finally { els.importSubmit.disabled = false; }
  });

  /* ── wiring ────────────────────────────── */
  els.chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const text = els.chatInput.value.trim();
    const id = selectedId;
    if (!text || id == null || loadingChat) return;
    loadingChat = true; pendingChatId = id; pendingStarted = Date.now();
    const messages = threads.get(String(id)) || [];
    threads.set(String(id), messages);
    messages.push({ kind: 'user', text });
    persistThreads();
    els.chatInput.value = '';
    drawConversation();
    els.chatInput.disabled = true;
    els.chatSend.disabled = true;
    try {
      await saveTarget(id);
      const data = await request('/api/chat', { method: 'POST', body: JSON.stringify({ segmentId: id, message: text, action: els.chatForm.dataset.action || "discussion" }) });
      messages.push({ kind: 'assistant', text: data.reply || '', proposal: data.proposal || null });
      persistThreads();
    } catch (error) {
      const messages = threads.get(String(id)) || [];
      messages.push({kind:'assistant', text:`请求失败：${error.message}。请检查后重试。`});
      threads.set(String(id), messages); persistThreads(); showError(error);
      if (String(selectedId) === String(id) && !els.chatInput.value) els.chatInput.value = text;
    }
    finally {
      loadingChat = false; pendingChatId = null; delete els.chatForm.dataset.action; drawConversation();
      els.chatInput.disabled = selectedId == null;
      els.chatSend.disabled = selectedId == null;
      if (!els.chatInput.disabled && String(selectedId) === String(id) &&
          (document.activeElement === document.body || els.chatForm.contains(document.activeElement))) els.chatInput.focus({ preventScroll: true });
    }
  });
  document.addEventListener('click', (event) => {
    const button=event.target.closest('[data-chat-action]');
    if (!button || loadingChat) return;
    els.chatForm.dataset.action=button.dataset.chatAction;
    els.chatInput.value={collocation:'请检查当前译文的搭配与假英语风险。用真实词典、语料证据和链接说明，区分错误、可选优化、待核实。',plain:'请按本段读者和用途改清楚译文，适用于公众、教育、健康、行政、商务及技术文本。默认最小修改，删无新增信息的重复；保留原文全部事实、条件、否定、数字、术语及义务强度。已简洁则保留，只解释关键改动。',ambiguity:'请检查本段原文和译文是否有歧义，说明不同解读以及保留原意的最小修改。'}[button.dataset.chatAction];
    els.chatForm.requestSubmit();
  });
  els.chatInput.addEventListener('keydown' , (event) => {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      els.chatForm.requestSubmit();
    }
  });
  els.confirmBtn.addEventListener('click', () => { if (selectedId != null) void confirmSegment(selectedId, true); });
  els.undoBtn.addEventListener('click', () => { if (selectedId != null) void undoChange(selectedId); });
  els.prevBtn.addEventListener('click', () => moveSelection(-1, { focusEditor: true }));
  els.nextBtn.addEventListener('click', () => moveSelection(1, { focusEditor: true }));
  els.quickFind.addEventListener('input', () => { query = els.quickFind.value.trim(); applyVisibility(); });
  function syncFilterChips() {
    document.querySelectorAll('.filter-group .chip').forEach((chip) => {
      chip.classList.toggle('is-on', chip.dataset.filter === activeFilter);
    });
  }
  document.querySelectorAll('.filter-group .chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      activeFilter = chip.dataset.filter;
      syncFilterChips();
      applyVisibility();
    });
  });
  els.concInput.addEventListener('input', drawConcordance);
  $('#import-open').addEventListener('click', () => els.dialog.showModal());
  $('#import-close').addEventListener('click', () => els.dialog.close());
  $('#import-cancel').addEventListener('click', () => els.dialog.close());
  $('#shortcut-open').addEventListener('click', () => els.shortcutDialog.showModal());
  $('#shortcut-close').addEventListener('click', () => els.shortcutDialog.close());
  $('#shortcut-done').addEventListener('click', () => els.shortcutDialog.close());
  function applyDisplay() {
    document.documentElement.dataset.density = display.density;
    document.documentElement.style.setProperty('--grid-font-size', `${display.font}px`);
    document.querySelectorAll('.display-group [data-density]').forEach((chip) => {
      chip.classList.toggle('is-on', chip.dataset.density === display.density);
    });
    const size = `${display.font.toFixed(1).replace(/\.0$/, '')} px`;
    $('#font-down').title = `缩小译文字号（当前 ${size}）`;
    $('#font-up').title = `放大译文字号（当前 ${size}）`;
    try { localStorage.setItem(displayKey, JSON.stringify(display)); } catch { /* Storage may be unavailable. */ }
  }
  function restoreDisplay() {
    try {
      const saved = JSON.parse(localStorage.getItem(displayKey));
      if (saved && ['compact', 'cozy', 'roomy'].includes(saved.density)) display.density = saved.density;
      if (saved && typeof saved.font === 'number' && Number.isFinite(saved.font)) {
        display.font = Math.min(19, Math.max(11, saved.font));
      }
    } catch { /* Ignore damaged browser storage. */ }
    applyDisplay();
  }
  document.querySelectorAll('.display-group [data-density]').forEach((chip) => {
    chip.addEventListener('click', () => { display.density = chip.dataset.density; applyDisplay(); });
  });
  $('#font-down').addEventListener('click', () => { display.font = Math.max(11, display.font - 0.5); applyDisplay(); });
  $('#font-up').addEventListener('click', () => { display.font = Math.min(19, display.font + 0.5); applyDisplay(); });
  els.nextUnconfirmed.addEventListener('click', moveToUnconfirmed);
  els.rows.addEventListener('contextmenu', (event) => {
    const line = event.target.closest('.segment-row');
    if (!line) return;
    event.preventDefault();
    closeExportMenu();
    openRowMenu(line.dataset.id, event.clientX, event.clientY);
  });
  els.menu.addEventListener('click', (event) => {
    const button = event.target.closest('.row-menu-item');
    if (!button || button.disabled) return;
    const id = menuSegmentId;
    closeRowMenu();
    if (id == null) return;
    if (button.dataset.action === 'copy-source') void copySource(id);
    else if (button.dataset.action === 'clear') void clearTarget(id);
    else if (button.dataset.action === 'confirm') void confirmSegment(id, false);
    else if (button.dataset.action === 'undo') void undoChange(id);
    else if (button.dataset.action === 'sync') void syncRepetitions(id);
    else if (button.dataset.action === 'find') findInConcordance(id);
  });
  els.menu.addEventListener('keydown', (event) => {
    const items = [...els.menu.querySelectorAll('.row-menu-item:not(:disabled)')];
    const index = items.indexOf(document.activeElement);
    if (event.key === 'Escape') { event.preventDefault(); closeRowMenu(); rowEl(selectedId)?.querySelector('.col-no')?.focus(); return; }
    if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
    event.preventDefault();
    const step = event.key === 'ArrowDown' ? 1 : -1;
    const next = items[(index + step + items.length) % items.length];
    next?.focus();
  });
  function openExportMenu() {
    els.exportMenu.hidden = false;
    els.exportOpen.setAttribute('aria-expanded', 'true');
    const box = els.exportOpen.getBoundingClientRect();
    const width = els.exportMenu.offsetWidth;
    els.exportMenu.style.left = `${Math.max(8, Math.min(box.right - width, window.innerWidth - width - 8))}px`;
    els.exportMenu.style.top = `${box.bottom + 6}px`;
    els.exportMenu.querySelector('.row-menu-item')?.focus();
  }
  function closeExportMenu() {
    if (els.exportMenu.hidden) return;
    els.exportMenu.hidden = true;
    els.exportOpen.setAttribute('aria-expanded', 'false');
  }
  els.exportOpen.addEventListener('click', () => { if (els.exportMenu.hidden) { closeRowMenu(); openExportMenu(); } else closeExportMenu(); });
  els.exportMenu.addEventListener('click', async (event) => {
    const link = event.target.closest('a.row-menu-item');
    if (!link) return;
    event.preventDefault(); closeExportMenu();
    try {
      await flushDirty();
      const response = await fetch(link.href);
      if (!response.ok) throw new Error('导出失败，请重试');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const download = document.createElement('a');
      const encoded = response.headers.get('Content-Disposition')?.split("filename*=UTF-8''")[1];
      download.href = url; download.download = encoded ? decodeURIComponent(encoded) : 'export.docx';
      document.body.append(download); download.click(); download.remove();
      setTimeout(() => URL.revokeObjectURL(url), 30000);
      notice('已导出最新保存的译稿');
    } catch (error) { showError(error); }
  });
  els.exportMenu.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') { event.preventDefault(); closeExportMenu(); els.exportOpen.focus(); }
  });
  document.addEventListener('mousedown', (event) => {
    if (!event.target.closest('#row-menu')) closeRowMenu();
    if (!event.target.closest('#export-menu') && !event.target.closest('#export-open')) closeExportMenu();
  });
  document.addEventListener('scroll', () => { closeRowMenu(); closeExportMenu(); }, true);
  window.addEventListener('resize', () => { closeRowMenu(); closeExportMenu(); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') { closeRowMenu(); closeExportMenu(); } });

  document.addEventListener('keydown', (event) => {
    if (event.defaultPrevented || els.dialog.open || els.shortcutDialog.open || !els.menu.hidden || !els.exportMenu.hidden) return;
    const inField = event.target.closest('textarea, input');
    const meta = event.metaKey || event.ctrlKey;
    if (meta && event.key.toLowerCase() === 'a' && !inField && selectedId != null) {
      event.preventDefault();
      const input = editor(selectedId);
      if (input) { input.focus(); input.select(); }
      return;
    }
    if (meta && event.shiftKey && event.key.toLowerCase() === 'c' && selectedId != null) {
      event.preventDefault();
      void copySource(selectedId);
      return;
    }
    if (meta && event.shiftKey && (event.key === 'Backspace' || event.key === 'Delete') && selectedId != null) {
      event.preventDefault();
      void clearTarget(selectedId);
      return;
    }
    if (inField) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      moveSelection(event.key === 'ArrowDown' ? 1 : -1);
      return;
    }
    if (event.key === 'PageDown' || event.key === 'PageUp') {
      event.preventDefault();
      moveSelection(event.key === 'PageDown' ? 8 : -8);
      return;
    }
    if (event.key === 'Home' || event.key === 'End') {
      event.preventDefault();
      const ids = visibleIds();
      if (!ids.length) return;
      jumpTo(event.key === 'Home' ? ids[0] : ids[ids.length - 1]);
      return;
    }
    if (event.key === 'Enter' && selectedId != null) {
      event.preventDefault();
      editor(selectedId)?.focus();
    }
  });
  window.addEventListener('beforeunload', (event) => {
    const pending = [...writes.values()].length > 0 || [...timers.values()].length > 0;
    if (!pending) return;
    event.preventDefault();
    event.returnValue = '';
  });

  restoreDisplay();
  loadProject().catch((error) => {
    els.rows.innerHTML = '<div class="empty-state">文稿加载失败，请刷新重试。</div>';
    showError(error);
  });
})();

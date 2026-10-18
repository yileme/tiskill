(() => {
  'use strict';
  // app.js owns segment editing, confirmation, chat, and concordance.
  const selected = () => document.querySelector('.segment-row.is-current:not(.is-hidden)');
  const editor = () => selected()?.querySelector('.target-input');
  const panels = [];
  let project = null, projectBusy = false, lastProjectAt = 0, projectSignature = null;
  let libraries = [], librarySequence = 0, termDialog;
  const segmentSelections = new Map();
  const selectionsFor = (id) => {
    if (!segmentSelections.has(id)) segmentSelections.set(id, {source: null, target: null});
    return segmentSelections.get(id);
  };
  function resetSelections() {
    segmentSelections.clear();
    if (termDialog && !termDialog.hidden) termDialog.dismiss(false);
    for (const panel of panels) { panel.key = ''; panel.onlineSequence++; panel.onlineResult?.replaceChildren(); }
  }
  function acceptProject(data) {
    const signature = JSON.stringify([data.id, data.title, data.segments?.map(item => [item.id, item.source])]);
    if (projectSignature !== null && signature !== projectSignature) {
      resetSelections();
      libraries = [];
      for (const state of panels) state.renderLibraries();
      void refreshLibraries().catch(error => { for (const state of panels) state.status.textContent = error.message; });
    }
    projectSignature = signature; project = data;
  }
  function captureSource() {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed || !selection.rangeCount) return;
    const range = selection.getRangeAt(0), start = range.startContainer;
    const source = (start.nodeType === 1 ? start : start.parentElement)?.closest('.source-text');
    if (!source || !source.contains(range.endContainer)) return;
    const text = selection.toString().trim();
    if (text) { const id = source.closest('.segment-row').dataset.id; selectionsFor(id).source = {text, segmentId: id}; }
  }
  function captureTarget(event) {
    const input = event?.target?.matches?.('.target-input') ? event.target : document.activeElement;
    if (!input?.matches?.('.target-input')) return;
    const text = input.value.slice(input.selectionStart, input.selectionEnd).trim();
    if (text) { const id = input.closest('.segment-row').dataset.id; selectionsFor(id).target = {text, segmentId: id}; }
  }
  document.addEventListener('selectionchange', () => { captureSource(); captureTarget(); });
  for (const type of ['select', 'keyup', 'pointerup', 'blur']) document.addEventListener(type, captureTarget, true);
  for (const type of ['pointerup', 'click']) document.addEventListener(type, captureSource, true);
  window.addEventListener('folio:project-changed', () => { resetSelections(); void refreshProject(); });
  const grid = document.querySelector('#segments');
  if (grid) new MutationObserver(records => {
    if (records.some(record => [...record.removedNodes].some(el => el.nodeType === 1 && el.matches('.segment-row')))) resetSelections();
  }).observe(grid, {childList: true});
  function renderReply(root, text) {
    root.replaceChildren();
    const pattern = /\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/g;
    let cursor = 0;
    for (const match of text.matchAll(pattern)) {
      root.append(document.createTextNode(text.slice(cursor, match.index)));
      try {
        const url = new URL(match[2]);
        if (!['http:', 'https:'].includes(url.protocol)) throw new Error('Invalid link');
        const link = node('a', match[1]); link.href = url.href;
        link.target = '_blank'; link.rel = 'noopener noreferrer'; root.append(link);
      } catch { root.append(document.createTextNode(match[0])); }
      cursor = match.index + match[0].length;
    }
    root.append(document.createTextNode(text.slice(cursor)));
  }
  async function refreshLibraries() {
    const sequence = ++librarySequence, data = await request('/api/libraries');
    if (sequence !== librarySequence) return;
    if (!Array.isArray(data.items)) throw new Error('资源库列表格式无效。');
    libraries = data.items;
    for (const state of panels) state.renderLibraries();
  }
  function node(tag, text, cls) {
    const el = document.createElement(tag);
    if (text != null) el.textContent = text;
    if (cls) el.className = cls;
    return el;
  }
  async function request(url, body, method = 'POST') {
    const response = await fetch(url, {cache: 'no-store', ...(body ? {
      method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)
    } : {})});
    const data = await response.json().catch(() => null);
    if (!response.ok) throw new Error(data?.error || `请求失败（${response.status}）`);
    if (!data) throw new Error('服务器未返回有效数据。');
    return data;
  }
  async function refreshProject() {
    if (projectBusy) return;
    projectBusy = true;
    try { acceptProject(await request('/api/project')); }
    catch { project = null; }
    finally { projectBusy = false; lastProjectAt = Date.now(); }
  }
  function currentSaved() {
    return project?.segments?.find(item => String(item.id) === selected()?.dataset.id);
  }
  function confirmed() {
    const saved = currentSaved();
    return saved?.status === 'confirmed' && saved.source === selected()?.querySelector('.source-text')?.textContent
      && saved.target === editor()?.value && !!saved.target.trim()
      && selected()?.classList.contains('st-confirmed');
  }
  function field(parent, label, value = '', tag = 'input') {
    const wrap = node('label', label);
    const input = node(tag);
    input.value = value;
    if (tag === 'input') input.type = 'text';
    wrap.append(input); parent.append(wrap);
    return input;
  }
  function button(text, handler) {
    const icons = {'编辑所选术语':'✎', '插入所选术语':'↵', '术语库设置':'▤', '搜索设置':'⚙', '清空检索':'×', '检索':'⌕', '使用当前原文':'↖', '选区添加术语':'⊕', '手动添加术语':'+', '在线查证术语':'◎', '刷新资源库列表':'↻', '将当前已确认段落存入记忆库':'⇥', '在光标处插入术语':'↵', '填入当前译文':'↵'};
    const el = node('button', icons[text] || text, 'button button-quiet' + (icons[text] ? ' resource-icon' : ''));
    if (icons[text]) { el.title = text; el.setAttribute('aria-label', text); }
    el.type = 'button'; el.addEventListener('click', handler); return el;
  }
  for (const kind of ['terms', 'tm']) {
    const root = document.querySelector(`#panel-${kind}`);
    if (!root) continue;
    const pad = node('div', null, 'panel-pad');
    const settings = node('details', null, 'resource-settings');
    settings.append(node('summary', '语言方向与资源库管理'));
    const locales = node('div', null, 'resource-locales');
    const sourceLocale = field(locales, '原文语言', 'zh-CN');
    const targetLocale = field(locales, '译文语言', 'en');
    for (const input of [sourceLocale, targetLocale]) {
      input.required = true; input.maxLength = 64; input.spellcheck = false;
      input.pattern = '[A-Za-z]{2,8}(-[A-Za-z0-9]{1,8})*';
      input.title = '语言标签，例如 zh-CN、en、en-US';
    }
    settings.append(locales);
    const libraryList = node('div', null, 'library-list'); settings.append(libraryList);
    const importForm = node('form');
    const libraryName = field(importForm, '新资源库名称'); libraryName.required = true; libraryName.maxLength = 160;
    const upload = field(importForm, '导入 CSV 文件'); upload.type = 'file'; upload.accept = '.csv,text/csv'; upload.required = true;
    const importButton = node('button', '导入并挂载资源库', 'button button-quiet'); importButton.type = 'submit';
    importForm.append(importButton); settings.append(importForm, button('刷新资源库列表', () => { void refreshLibraries().catch(error => tell(error.message, true)); }));
    const writeLibrary = field(kind === 'terms' ? settings : pad, '写入资源库', '', 'select');
    const query = field(pad, '检索词句（换段时跟随原文）');
    query.type = 'search'; query.maxLength = 20000;
    if (kind === 'terms') {
      query.parentElement.className = 'term-query';
      query.parentElement.firstChild.textContent = '';
      query.setAttribute('aria-label', '检索术语'); query.placeholder = '搜索术语…';
      settings.id = 'term-settings';
    }
    const actions = node('div', null, 'resource-actions');
    const status = node('p', '选择段落或输入词句，查询本地资源。', 'resource-status');
    status.setAttribute('role', 'status');
    const results = node('div', null, 'resource-results');
    const state = {kind, root, sourceLocale, targetLocale, query, status, results, sequence: 0, onlineSequence: 0, timer: null, key: '', save: null};
    const tell = (text, error = false) => { status.textContent = text; status.dataset.error = String(error); };
    let selectedTerm = null, selectedApply = null;
    const resetTerm = () => { selectedTerm = null; selectedApply = null; state.updateTerm?.(); };
    const localeValues = () => {
      for (const input of [sourceLocale, targetLocale]) if (!input.reportValidity()) throw new Error('请填写有效的原文及译文语言。');
      return {sourceLocale: sourceLocale.value.trim(), targetLocale: targetLocale.value.trim()};
    };
    function libraryId() {
      const item = libraries.find(item => String(item.id) === writeLibrary.value && item.kind === kind && item.mounted);
      if (!item) throw new Error('请先挂载并选择要写入的资源库。');
      return item.id;
    }
    state.renderLibraries = () => {
      const previous = writeLibrary.value; writeLibrary.replaceChildren(); libraryList.replaceChildren();
      const placeholder = node('option', '请选择已挂载的写入库'); placeholder.value = ''; writeLibrary.append(placeholder);
      const available = libraries.filter(item => item.kind === kind);
      for (const item of available) {
        if (item.mounted) { const option = node('option', item.name); option.value = String(item.id); writeLibrary.append(option); }
        const row = node('div', null, 'library-row'), label = node('label'), toggle = node('input');
        toggle.type = 'checkbox'; toggle.checked = !!item.mounted; label.append(toggle, document.createTextNode(item.name));
        const link = node('a', '导出 CSV'); link.href = `/api/library.csv?id=${encodeURIComponent(item.id)}`; link.download = '';
        link.setAttribute('aria-label', `导出 ${item.name} CSV`); row.append(label, link); libraryList.append(row);
        toggle.addEventListener('change', async () => {
          toggle.disabled = true;
          try { await request('/api/libraries', {libraryId: item.id, mounted: toggle.checked}, 'POST'); await refreshLibraries(); await search(); }
          catch (error) { toggle.checked = !!item.mounted; tell(error.message, true); }
          finally { toggle.disabled = false; }
        });
      }
      if ([...writeLibrary.options].some(option => option.value === previous && previous)) writeLibrary.value = previous;
      else if (writeLibrary.options.length === 2) writeLibrary.selectedIndex = 1;
      state.updateTerm?.();
      if (!available.length) libraryList.append(node('p', '暂无资源库，可在下方导入 CSV。', 'field-hint'));
    };
    importForm.addEventListener('submit', async event => {
      event.preventDefault(); importButton.disabled = true;
      try {
        const file = upload.files[0]; if (!file) throw new Error('请选择 CSV 文件。');
        await request('/api/libraries', {kind, name: libraryName.value.trim(), csvContent: await file.text()});
        await refreshLibraries(); await search(); importForm.reset(); tell('资源库已导入并挂载。');
      } catch (error) { tell(error.message, true); }
      finally { importButton.disabled = false; }
    });
    async function search() {
      const seq = ++state.sequence;
      results.replaceChildren(); resetTerm();
      try {
        const pair = localeValues();
        tell('正在检索…');
        const data = await request('/api/resources?' + new URLSearchParams({kind, ...pair, query: query.value}));
        if (seq !== state.sequence) return;
        if (!Array.isArray(data.items)) throw new Error('资源列表格式无效。');
        tell(data.items.length ? `显示 ${data.items.length} / ${data.total ?? data.items.length} 条。` : '此语言方向暂无匹配资源。可调整检索词或添加资源。');
        for (const item of data.items) {
          const card = node('article', null, 'resource-card');
          if (kind !== 'terms') card.append(node('p', item.source), node('p', item.target));
          const label = item.match === 'exact' ? '规范化原文完全匹配' : item.match === 'fuzzy'
            ? `规范化字符相似度 ${(item.similarity * 100).toFixed(1)}%`
            : item.match === 'substring' ? '包含匹配' : '已存条目（未计算匹配度）';
          if (kind !== 'terms') card.append(node('small', label));
          const apply = button(kind === 'terms' ? '在光标处插入术语' : '填入当前译文', () => {
            const input = editor();
            if (!input) return tell('请先选择一个可见段落。', true);
            if (kind === 'tm' && input.value && input.value !== item.target &&
                !window.confirm('用这条记忆库译文覆盖当前译文？')) return;
            const start = input.selectionStart, end = input.selectionEnd;
            input.focus();
            if (kind === 'terms') input.setRangeText(item.target, start, end, 'end');
            else { input.value = item.target; input.setSelectionRange(input.value.length, input.value.length); }
            input.dispatchEvent(new Event('input', {bubbles: true}));
            tell(kind === 'terms' ? '已插入术语；译文按现有流程自动保存。' : '已填入译文，请审阅后确认。');
          });
          // Keep the textarea caret when applying with the mouse.
          apply.addEventListener('mousedown', event => event.preventDefault());
          if (kind === 'terms') {
            card.className = 'term-row';
            const pick = node('button', null, 'term-pair'); pick.type = 'button';
            pick.append(node('span', item.source, 'term-source'), node('span', item.target, 'term-target'));
            pick.setAttribute('aria-pressed', 'false');
            pick.addEventListener('click', () => {
              for (const row of results.children) {
                row.classList.remove('is-selected'); row.querySelector('.term-pair')?.setAttribute('aria-pressed', 'false');
              }
              selectedTerm = item; selectedApply = apply;
              card.classList.add('is-selected'); pick.setAttribute('aria-pressed', 'true'); state.updateTerm();
            });
            card.append(pick);
            const library = libraries.find(lib => String(lib.id) === String(item.libraryId));
            if (library || item.note) {
              const detail = node('details', null, 'term-detail'), summary = node('summary', 'ⓘ');
              summary.title = '术语详情'; summary.setAttribute('aria-label', '术语详情');
              detail.append(summary);
              const body = node('div', null, 'term-detail-body');
              if (library) body.append(node('p', library.name));
              if (item.note) body.append(node('p', item.note));
              detail.append(body); card.append(detail);
            }
          } else {
            card.append(apply);
            if (item.note) card.append(node('p', item.note, 'resource-note'));
          }
          results.append(card);
        }
      } catch (error) { if (seq === state.sequence) tell(error.message, true); }
    }
    state.search = search;
    const schedule = () => {
      ++state.sequence; results.replaceChildren(); resetTerm(); state.updateTerm?.(); clearTimeout(state.timer);
      state.timer = setTimeout(search, 250);
    };
    actions.append(button('检索', () => { clearTimeout(state.timer); void search(); }));
    if (kind !== 'terms') actions.append(button('使用当前原文', () => {
      query.value = selected()?.querySelector('.source-text')?.textContent || ''; void search();
    }));
    pad.append(actions);
    if (kind === 'terms') {
      termDialog = node('section', null, 'term-composer'); termDialog.hidden = true; termDialog.id = 'term-dialog'; termDialog.setAttribute('aria-labelledby', 'term-dialog-title');
      const form = node('form', null, 'term-compose-form'), heading = node('h2', '添加术语'); heading.id = 'term-dialog-title';
      const context = node('p', '', 'term-compose-context'); form.append(heading, context);
      const fields = node('div', null, 'term-compose-fields'); form.append(fields);
      const optional = node('details'); optional.append(node('summary', '备注（可选）'));
      const source = field(fields, '原文术语'); source.required = true; source.maxLength = 10000;
      const target = field(fields, '译文术语'); target.required = true; target.maxLength = 20000;
      const note = field(optional, '备注（可选，最多 500 字）', '', 'textarea'); note.maxLength = 500; note.rows = 2; form.append(optional);
      const dialogStatus = node('p', '', 'resource-status'); dialogStatus.setAttribute('role', 'status'); form.append(dialogStatus);
      const save = node('button', '保存术语', 'button button-dark'); save.type = 'submit';
      let returnFocus, saving = false;
      termDialog.dismiss = (restore = true) => { termDialog.hidden = true; if (restore) (returnFocus?.isConnected && !returnFocus.disabled ? returnFocus : editor())?.focus({preventScroll:true}); };
      const dialogActions = node('div', null, 'term-compose-actions'); dialogActions.append(button('取消', () => { if (!saving) termDialog.dismiss(); }), save); form.append(dialogActions);
      termDialog.append(form); pad.append(termDialog);
      let editing = null, pairAtOpen, libraryAtOpen, signatureAtOpen;
      state.openTerm = (item = null, manual = false) => {
        if (!termDialog.hidden) { dialogStatus.textContent = '已保留当前草稿，请先保存或取消。'; target.focus(); return; }
        if (!manual) { captureSource(); captureTarget(); }
        const selections = selectionsFor(selected()?.dataset.id);
        if (!item && !manual && selections.source && selections.target && selections.source.segmentId !== selections.target.segmentId) {
          tell('原文与译文选区来自不同段落，不能配对。请重新选择同一段，或使用「手动添加术语」。', true); return;
        }
        try { pairAtOpen = item ? {sourceLocale: item.sourceLocale, targetLocale: item.targetLocale} : localeValues(); libraryAtOpen = item ? item.libraryId : libraryId(); }
        catch (error) { tell(error.message, true); return; }
        editing = item; signatureAtOpen = projectSignature; heading.textContent = item ? '编辑术语译文' : '添加术语';
        source.value = item?.source ?? (manual ? '' : selections.source?.text ?? ''); source.readOnly = !!item;
        target.value = item?.target ?? (manual ? '' : selections.target?.text ?? '');
        note.value = item?.note ?? ''; note.disabled = !!item;
        dialogStatus.dataset.error = 'false';
        dialogStatus.textContent = item ? '仅更新译文；并发修改会提示冲突。' : `写入：${libraries.find(lib => lib.id === libraryAtOpen)?.name || ''}`;
        context.textContent = `${pairAtOpen.sourceLocale} → ${pairAtOpen.targetLocale} · 写入：${libraries.find(lib => String(lib.id) === String(libraryAtOpen))?.name || libraryAtOpen}`;
        optional.open = false; if (!item) dialogStatus.textContent = ''; returnFocus = document.activeElement; termDialog.hidden = false; (source.value ? target : source).focus();
      };
      form.addEventListener('submit', async event => {
        event.preventDefault(); if (saving) return; saving = true; save.disabled = true;
        try {
          if (signatureAtOpen !== projectSignature) throw new Error('文稿已变化，请重新添加术语。');
          const pair = localeValues();
          if (pair.sourceLocale !== pairAtOpen.sourceLocale || pair.targetLocale !== pairAtOpen.targetLocale) throw new Error('语言方向已变化，请恢复或取消后重试。');
          if (!libraries.some(lib => String(lib.id) === String(libraryAtOpen) && lib.kind === kind && lib.mounted) || (!editing && String(libraryId()) !== String(libraryAtOpen))) throw new Error('写入库已变化，请恢复或取消后重试。');
          const body = editing ? {id: editing.id, libraryId: editing.libraryId, kind: 'terms', target: target.value, expectedVersion: editing.version, expectedTarget: editing.target, ...pairAtOpen}
            : {kind, source: source.value, target: target.value, note: note.value, libraryId: libraryAtOpen, ...pairAtOpen};
          const data = await request('/api/resources', body, editing ? 'PATCH' : 'POST');
          termDialog.dismiss(termDialog.contains(document.activeElement)); segmentSelections.clear(); await search();
          tell(editing ? '术语译文已更新。' : data.created === false ? '相同术语已存在。' : '术语已保存。');
        } catch (error) { dialogStatus.textContent = error.message; dialogStatus.dataset.error = 'true'; }
        finally { saving = false; save.disabled = false; }
      });
      termDialog.addEventListener('keydown', event => { event.stopPropagation(); if (event.key === 'Escape' && !saving) { event.preventDefault(); termDialog.dismiss(); } });
      const toolbar = node('div', null, 'term-toolbar'); toolbar.setAttribute('role', 'group'); toolbar.setAttribute('aria-label', '术语工具');
      const addSelection = button('选区添加术语', () => state.openTerm());
      const addManual = button('手动添加术语', () => state.openTerm(null, true));
      const editSelected = button('编辑所选术语', () => { if (selectedTerm) state.openTerm(selectedTerm); });
      const insertSelected = button('插入所选术语', () => selectedApply?.click());
      insertSelected.addEventListener('mousedown', event => event.preventDefault());
      const toggleSettings = () => { settings.open = !settings.open; for (const control of [librarySettings, searchSettings]) control.setAttribute('aria-expanded', String(settings.open)); if (settings.open) settings.scrollIntoView({block:'nearest'}); };
      const librarySettings = button('术语库设置', toggleSettings), searchSettings = button('搜索设置', toggleSettings);
      for (const control of [librarySettings, searchSettings]) { control.setAttribute('aria-controls', settings.id); control.setAttribute('aria-expanded', 'false'); }
      settings.addEventListener('toggle', () => { for (const control of [librarySettings, searchSettings]) control.setAttribute('aria-expanded', String(settings.open)); });
      toolbar.append(addSelection, addManual, editSelected, insertSelected, librarySettings);
      document.querySelector('#heading-terms').prepend(toolbar);
      const clear = button('清空检索', () => { query.value = ''; state.onlineSequence++; state.onlineResult.replaceChildren(); clearTimeout(state.timer); void search(); query.focus(); });
      actions.append(clear);
      state.updateTerm = () => {
        const writable = libraries.some(lib => lib.kind === kind && lib.mounted && String(lib.id) === writeLibrary.value);
        addSelection.disabled = !writable || !selected(); addManual.disabled = !writable;
        editSelected.disabled = !selectedTerm;
        insertSelected.disabled = !selectedTerm || !editor() || editor().disabled || editor().readOnly;
        clear.disabled = !query.value;
        online.disabled = onlineBusy || !query.value.trim() || query.value.trim().length > 200;
      };
      writeLibrary.addEventListener('change', () => state.updateTerm());
      query.addEventListener('keydown', event => { if (event.key === 'Enter') { event.preventDefault(); clearTimeout(state.timer); void search(); } });
      document.querySelector('#add-selection-term')?.addEventListener('click', () => state.openTerm());
      state.onlineResult = node('div', null, 'term-online-result'); state.onlineResult.setAttribute('role', 'status');
      let onlineBusy = false;
      const online = button('在线查证术语', async () => {
        const text = query.value.trim(); if (!text || text.length > 200) return tell('请输入 1–200 字的术语进行在线查证。', true);
        const seq = ++state.onlineSequence, segmentId = selected()?.dataset.id ?? null;
        onlineBusy = true; state.updateTerm(); state.onlineResult.textContent = '正在在线查证…';
        try {
          const data = await request('/api/term-search', {query: text, segmentId});
          if (seq !== state.onlineSequence) return;
          if (typeof data.reply !== 'string') throw new Error('服务器未返回查证结果。');
          renderReply(state.onlineResult, data.reply);
        } catch (error) { if (seq === state.onlineSequence) state.onlineResult.textContent = error.message; }
        finally { onlineBusy = false; state.updateTerm(); }
      });
      actions.append(online, searchSettings);
      const searchbar = node('div', null, 'term-searchbar');
      searchbar.append(query.parentElement, actions); pad.prepend(searchbar); pad.append(state.onlineResult);
      state.updateTerm();
      const fallback = node('p', null, 'field-hint');
      const site = node('a', '热词译网站（手动查询）'); site.href = 'https://www.reciyi.com/'; site.target = '_blank'; site.rel = 'noopener noreferrer';
      fallback.append(site, document.createTextNode(' · 仅为查询入口，不是已核实证据。')); settings.append(fallback);
    } else {
      pad.append(node('p', '相似度按规范化后的字符计算，仅作检索提示。记忆库仅通过下方按钮保存已确认段落。', 'field-hint'));
      let saving = false;
      state.save = button('将当前已确认段落存入记忆库', async () => {
        if (saving) return;
        saving = true; state.save.disabled = true;
        const row = selected(), input = editor(), value = input?.value;
        try {
          const pair = localeValues(), destination = libraryId();
          const latest = await request('/api/project'); acceptProject(latest);
          if (selected() !== row || input?.value !== value || !confirmed()) throw new Error('请选择已保存且已确认的段落，再存入记忆库。');
          const saved = currentSaved();
          const data = await request('/api/resources', {kind, ...pair, libraryId: destination, source: saved.source, target: saved.target,
            segmentId: saved.id, expectedVersion: saved.version});
          await search(); tell(data.created ? '已将确认段落存入记忆库。' : '相同记忆条目已存在。');
        } catch (error) { tell(error.message, true); }
        finally { saving = false; state.save.disabled = !confirmed(); }
      });
      state.updateSave = () => { state.save.disabled = saving || !confirmed(); };
      actions.append(state.save);
    }
    pad.append(status, settings); root.prepend(pad, results); panels.push(state);
    query.addEventListener('input', schedule);
    for (const input of [sourceLocale, targetLocale]) input.addEventListener('input', schedule);
    // Prevent app.js grid navigation shortcuts from capturing resource form keys.
    root.addEventListener('keydown', event => event.stopPropagation());
  }
  function poll() {
    if (document.hidden) return;
    const row = selected();
    const source = row?.querySelector('.source-text')?.textContent || '';
    const key = JSON.stringify([row?.dataset.id, source]);
    for (const state of panels) {
      if (state.key !== key) {
        state.key = key; state.query.value = source; ++state.sequence;
        state.onlineSequence++; state.onlineResult?.replaceChildren();
        state.results.replaceChildren();
        void state.search();
      }
      state.updateSave?.(); state.updateTerm?.();
    }
    if (Date.now() - lastProjectAt > 2000) void refreshProject();
  }
  void refreshLibraries().catch(error => { for (const state of panels) { state.status.textContent = error.message; state.status.dataset.error = 'true'; } });
  void refreshProject(); poll();
  const timer = setInterval(poll, 400);
  window.addEventListener('pagehide', () => clearInterval(timer), {once: true});
})();

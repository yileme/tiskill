/* Nested workspace sizing. Only layout preferences are stored here. */
(() => {
  'use strict';
  const key = 'folio.workspace.layout.v1';
  const defaults = {discussion: .70, editor: .64, resource: .56};
  let saved;
  try { saved = JSON.parse(localStorage.getItem(key)); } catch (_) { /* unavailable or malformed */ }
  const sizes = {...defaults};
  for (const name of Object.keys(defaults)) {
    if (typeof saved?.[name] === 'number' && Number.isFinite(saved[name]))
      sizes[name] = Math.max(0, Math.min(1, saved[name]));
  }
  const narrow = matchMedia('(max-width: 900px)');
  const specs = [
    ['discussion', 'workspace', 'discussion-splitter', 'x', 440, 280],
    ['editor', 'editor-column', 'editor-splitter', 'y', 160, 140],
    ['resource', 'resource-dock', 'resource-splitter', 'x', 200, 200]
  ].map(([name, parent, handle, axis, minFirst, minLast]) => ({
    name, parent: document.getElementById(parent), handle: document.getElementById(handle),
    axis, minFirst, minLast
  }));
  const persist = () => { try { localStorage.setItem(key, JSON.stringify(sizes)); } catch (_) { /* private browsing / quota */ } };
  function bounds(s) {
    const total = Math.max(1, (s.axis === 'x' ? s.parent.clientWidth : s.parent.clientHeight) - 8);
    const scale = Math.min(1, total / (s.minFirst + s.minLast));
    return {total, min: s.minFirst * scale, max: total - s.minLast * scale};
  }
  function apply(s) {
    const b = bounds(s);
    const value = Math.max(b.min, Math.min(b.max, sizes[s.name] * b.total));
    s.value = value;
    s.parent.style.setProperty('--split-size', value + 'px');
    for (const [attr, number] of Object.entries({valuemin:b.min, valuemax:b.max, valuenow:value}))
      s.handle.setAttribute('aria-' + attr, String(Math.round(number)));
    s.handle.setAttribute('aria-valuetext', `${Math.round(value / b.total * 100)}%`);
  }
  function refresh() {
    for (const s of specs) {
      s.handle.tabIndex = narrow.matches ? -1 : 0;
      if (!narrow.matches) apply(s);
    }
  }
  function set(s, pixels) {
    const b = bounds(s);
    sizes[s.name] = Math.max(b.min, Math.min(b.max, pixels)) / b.total;
    refresh();
  }
  for (const s of specs) {
    let drag = null;
    const position = event => s.axis === 'x' ? event.clientX : event.clientY;
    s.handle.addEventListener('pointerdown', event => {
      if (event.button !== 0 || narrow.matches || drag) return;
      event.preventDefault(); s.handle.focus();
      drag = {id: event.pointerId, start: position(event), value: s.value};
      s.handle.setPointerCapture(event.pointerId);
      s.handle.classList.add('is-dragging');
    });
    s.handle.addEventListener('pointermove', event => {
      if (drag?.id === event.pointerId) set(s, drag.value + position(event) - drag.start);
    });
    const finish = event => {
      if (drag?.id !== event.pointerId) return;
      drag = null; s.handle.classList.remove('is-dragging');
      if (s.handle.hasPointerCapture(event.pointerId)) s.handle.releasePointerCapture(event.pointerId);
      persist();
    };
    for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) s.handle.addEventListener(event, finish);
    const reset = () => { sizes[s.name] = defaults[s.name]; refresh(); persist(); };
    s.handle.addEventListener('dblclick', reset);
    s.handle.addEventListener('keydown', event => {
      event.stopPropagation();
      const negative = s.axis === 'x' ? 'ArrowLeft' : 'ArrowUp';
      const positive = s.axis === 'x' ? 'ArrowRight' : 'ArrowDown';
      if (![negative, positive, 'Home', 'End', 'Enter'].includes(event.key)) return;
      event.preventDefault();
      if (event.key === 'Enter') return reset();
      const b = bounds(s), step = event.shiftKey ? 40 : 10;
      set(s, event.key === 'Home' ? b.min : event.key === 'End' ? b.max : s.value + (event.key === negative ? -step : step));
      persist();
    });
  }
  const observer = new ResizeObserver(refresh);
  for (const s of specs) observer.observe(s.parent);
  narrow.addEventListener('change', refresh);
  refresh();
})();

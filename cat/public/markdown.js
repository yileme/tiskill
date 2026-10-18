/* Deliberate Markdown subset, not CommonMark: paragraphs, flat lists, quotes,
 * fenced/inline code, **strong**, *emphasis*, and explicit HTTP(S) links.
 * Unsupported syntax stays text. Never parse HTML or decode HTML entities. */
(() => {
  'use strict';
  function inline(parent, text, depth = 0) {
    if (depth > 12) { parent.append(text); return; }
    const tokens = /\\([\\`*\[\]])|`([^`\n]+)`|\[([^\]\n]+)\]\(([^\s)]+)\)|\*\*([^`\n]+?)\*\*(?!\*)|\*([^*`\n]+)\*/g;
    let start = 0;
    for (const m of text.matchAll(tokens)) {
      parent.append(text.slice(start, m.index));
      let node;
      if (m[1]) parent.append(m[1]);
      else if (m[2]) { node = document.createElement('code'); node.textContent = m[2]; }
      else if (m[3]) {
        let url;
        try { url = new URL(m[4]); } catch { /* Invalid links remain literal. */ }
        if (url && /^https?:$/.test(url.protocol) && /^https?:\/\//i.test(m[4])) {
          node = document.createElement('a'); node.href = url.href;
          node.target = '_blank'; node.rel = 'noopener noreferrer';
          inline(node, m[3], depth + 1);
        } else parent.append(m[0]);
      } else {
        node = document.createElement(m[5] ? 'strong' : 'em');
        // Accept whitespace inside emphasis delimiters without rewriting text.
        inline(node, m[5] || m[6], depth + 1);
      }
      if (node) parent.append(node);
      start = m.index + m[0].length;
    }
    parent.append(text.slice(start));
  }
  function render(text) {
    const root = document.createElement('div'); root.className = 'chat-markdown';
    const lines = String(text).replace(/\r\n?/g, '\n').split('\n');
    const list = line => line.match(/^\s{0,3}([-+*]|\d+\.)\s+(.+)$/);
    const special = line => /^\s*$|^```|^>\s?/.test(line) || list(line);
    for (let i = 0; i < lines.length;) {
      if (!lines[i].trim()) { i++; continue; }
      let node;
      if (/^```/.test(lines[i])) {
        node = document.createElement('pre'); const code = document.createElement('code');
        const content = []; i++;
        while (i < lines.length && !/^```\s*$/.test(lines[i])) content.push(lines[i++]);
        if (i < lines.length) i++;
        code.textContent = content.join('\n'); node.append(code);
      } else if (/^>\s?/.test(lines[i])) {
        node = document.createElement('blockquote'); const content = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) content.push(lines[i++].replace(/^>\s?/, ''));
        inline(node, content.join('\n'));
      } else if (list(lines[i])) {
        const ordered = /^\d/.test(list(lines[i])[1]);
        node = document.createElement(ordered ? 'ol' : 'ul');
        if (ordered) node.start = Number.parseInt(list(lines[i])[1], 10);
        while (i < lines.length && list(lines[i]) && /^\d/.test(list(lines[i])[1]) === ordered) {
          const li = document.createElement('li'); inline(li, list(lines[i++])[2]); node.append(li);
        }
      } else {
        node = document.createElement('p'); const content = [lines[i++]];
        while (i < lines.length && !special(lines[i])) content.push(lines[i++]);
        inline(node, content.join('\n'));
      }
      root.append(node);
    }
    return root;
  }
  window.FolioMarkdown = { render };
})();

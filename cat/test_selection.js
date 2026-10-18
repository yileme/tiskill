// Run in the browser console on an isolated CAT fixture with two segments.
(async () => {
  const assert = (ok, message) => { if (!ok) throw new Error(message); };
  const rows = [...document.querySelectorAll('.segment-row')];
  assert(rows.length >= 2, 'Requires two fixture segments');
  const selectSource = (row, end) => {
    const range = document.createRange();
    range.setStart(row.querySelector('.source-text').firstChild, 0);
    range.setEnd(row.querySelector('.source-text').firstChild, end);
    window.getSelection().removeAllRanges(); window.getSelection().addRange(range);
    document.dispatchEvent(new Event('selectionchange'));
  };
  const first = rows[0].querySelector('textarea'); first.focus();
  first.value = 'The device supports clinical trials.';
  first.dispatchEvent(new Event('input', {bubbles:true}));
  first.setSelectionRange(4,10); first.dispatchEvent(new Event('select', {bubbles:true}));
  first.blur(); selectSource(rows[0],2);
  document.querySelector('#add-selection-term').click();
  assert(document.querySelector('#term-dialog').tagName === 'SECTION', 'Nonmodal section');
  assert(document.querySelector('#panel-terms').contains(document.querySelector('#term-dialog')), 'Inline containment');
  let fields = document.querySelectorAll('#term-dialog input');
  assert(fields[0].value === rows[0].querySelector('.source-text').textContent.slice(0,2), 'source selection: ' + fields[0].value);
  assert(fields[1].value === 'device', 'independent target selection');
  document.querySelector('#term-dialog .term-compose-actions button').click(); window.getSelection().removeAllRanges();
  rows[1].querySelector('textarea').focus();
  document.querySelector('#add-selection-term').click();
  fields = document.querySelectorAll('#term-dialog input');
  assert(!fields[0].value && !fields[1].value, 'No selections leak to another segment');
  document.querySelector('#term-dialog .term-compose-actions button').click(); first.focus();
  document.querySelector('#add-selection-term').click();
  fields = document.querySelectorAll('#term-dialog input');
  assert(fields[1].value === 'device', 'Selection retained for original segment');
  document.querySelector('#term-dialog .term-compose-actions button').click();
  assert(!document.querySelector('.side-tab,#segment-info'), 'Obsolete panels removed');
  assert(document.querySelectorAll('[data-chat-action]').length === 3, 'Three discussion actions');
  return 'PASS: independent selections, per-segment retention/isolation, removed panels, actions';
})()

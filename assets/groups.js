/* crabucate — Gruppen-Zufallsgenerator im Browser.
 *
 * Alles passiert auf dieser Seite: Namen werden weder gesendet noch
 * gespeichert. Die Texte stehen als data-Attribute am <section class="gg">,
 * damit dieselbe Datei für Deutsch und Englisch reicht.
 *
 * Verteilung: Fisher-Yates mit crypto.getRandomValues, danach reihum auf die
 * Gruppen. So unterscheiden sich die Gruppen höchstens um eine Person.
 */
(function () {
  'use strict';

  var root = document.querySelector('.gg');
  if (!root) return;
  var T = root.dataset;
  var $ = function (sel) { return root.querySelector(sel); };

  var input = $('#gg-names');
  var count = $('.gg-count');
  var out = $('#gg-n');
  var note = $('.gg-stepper-note');
  var error = $('.gg-error');
  var go = $('[data-act="draw"]');
  var result = $('.gg-result');
  var groupsEl = $('.gg-groups');
  var summary = $('.gg-summary');
  var fsBtn = $('[data-act="fullscreen"]');
  var copyBtn = $('[data-act="copy"]');
  var copyLabel = copyBtn.querySelector('span');

  var mode = 'groups';
  var value = { groups: 4, size: 3 };
  var last = null;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Eine Zeile pro Name. Steht alles in einer Zeile, trennen Komma oder Semikolon. */
  function names() {
    var text = input.value.trim();
    if (!text) return [];
    var parts = text.indexOf('\n') >= 0 ? text.split(/\n+/) : text.split(/[;,]+/);
    return parts.map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function randInt(n) {
    var buf = new Uint32Array(1);
    var limit = Math.floor(0x100000000 / n) * n;
    do { crypto.getRandomValues(buf); } while (buf[0] >= limit);
    return buf[0] % n;
  }

  function shuffle(list) {
    var a = list.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = randInt(i + 1), t = a[i];
      a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function groupCount(n) {
    if (mode === 'groups') return Math.min(value.groups, n);
    return Math.max(1, Math.min(n, Math.round(n / value.size)));
  }

  function split(list, k) {
    var groups = [];
    for (var g = 0; g < k; g++) groups.push([]);
    list.forEach(function (name, i) { groups[i % k].push(name); });
    return groups;
  }

  function fmt(s, vars) {
    return s.replace(/\{(\w+)\}/g, function (_, k) { return vars[k]; });
  }

  function refresh() {
    var n = names().length;
    count.textContent = n;
    var max = Math.max(2, n);
    if (value[mode] > max && n >= 2) value[mode] = max;
    out.textContent = value[mode];
    $('[data-act="dec"]').disabled = value[mode] <= 2;
    $('[data-act="inc"]').disabled = n >= 2 && value[mode] >= max;
    if (n >= 2) {
      var k = groupCount(n);
      var lo = Math.floor(n / k), hi = Math.ceil(n / k);
      note.textContent = fmt(lo === hi ? T.noteEven : T.noteRange,
        { k: k, lo: lo, hi: hi });
    } else {
      note.textContent = '';
    }
  }

  function card(i, members) {
    var li = members.map(function (m) { return '<li>' + esc(m) + '</li>'; }).join('');
    return '<div class="gg-card"><h3>' + esc(T.groupLabel) + ' ' + (i + 1) +
      '<span>' + members.length + '</span></h3><ul>' + li + '</ul></div>';
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function render(groups) {
    groupsEl.innerHTML = groups.map(function (g, i) { return card(i, g); }).join('');
  }

  function draw() {
    var list = names();
    if (list.length < 2) {
      error.textContent = T.errFew;
      input.focus();
      return;
    }
    error.textContent = '';
    var k = groupCount(list.length);
    last = split(shuffle(list), k);
    summary.textContent = fmt(T.summary, { n: list.length, k: k });
    result.hidden = false;

    if (reduced) { render(last); return; }

    /* Sichtbar mischen: kurz zufällige Namen in den Karten, dann das Ergebnis. */
    go.classList.add('is-rolling');
    go.disabled = true;
    var ticks = 0;
    var timer = setInterval(function () {
      render(split(shuffle(list), k));
      groupsEl.querySelectorAll('.gg-card').forEach(function (c) { c.classList.add('is-rolling'); });
      if (++ticks >= 9) {
        clearInterval(timer);
        render(last);
        groupsEl.querySelectorAll('.gg-card').forEach(function (c, i) {
          c.style.animationDelay = (i * 60) + 'ms';
          c.classList.add('is-in');
        });
        go.classList.remove('is-rolling');
        go.disabled = false;
      }
    }, 75);
    if (ticks === 0 && result.getBoundingClientRect().top > window.innerHeight * 0.8) {
      result.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function asText() {
    return last.map(function (g, i) {
      return T.groupLabel + ' ' + (i + 1) + ': ' + g.join(', ');
    }).join('\n');
  }

  root.addEventListener('click', function (ev) {
    var b = ev.target.closest('button');
    if (!b || !root.contains(b)) return;
    var act = b.dataset.act;
    if (b.dataset.mode) {
      mode = b.dataset.mode;
      root.querySelectorAll('[data-mode]').forEach(function (x) {
        x.setAttribute('aria-checked', String(x === b));
      });
      refresh();
    } else if (act === 'dec') { value[mode] = Math.max(2, value[mode] - 1); refresh(); }
    else if (act === 'inc') { value[mode] += 1; refresh(); }
    else if (act === 'sample') { input.value = T.sample.split('|').join('\n'); refresh(); input.focus(); }
    else if (act === 'draw' || act === 'again') { draw(); }
    else if (act === 'copy' && last) {
      navigator.clipboard.writeText(asText()).then(function () {
        copyLabel.textContent = T.copied;
        setTimeout(function () { copyLabel.textContent = T.copy; }, 1600);
      });
    } else if (act === 'fullscreen') {
      var req = result.requestFullscreen || result.webkitRequestFullscreen;
      if (req) req.call(result);
    }
  });

  input.addEventListener('input', function () { error.textContent = ''; refresh(); });
  input.addEventListener('keydown', function (ev) {
    if (ev.key === 'Enter' && (ev.metaKey || ev.ctrlKey)) { ev.preventDefault(); draw(); }
  });

  if (!(document.fullscreenEnabled || document.webkitFullscreenEnabled)) fsBtn.hidden = true;
  if (!navigator.clipboard) copyBtn.hidden = true;
  refresh();
})();

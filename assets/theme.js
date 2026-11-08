/* crabucate — Theme-Umschalter.
 *
 * Zwei Zustaende: hell und dunkel. Solange niemand klickt, folgt die Seite dem
 * Betriebssystem (kein data-theme, kein Eintrag in localStorage). Ein Klick
 * schaltet auf das Gegenteil dessen, was gerade zu sehen ist, und merkt sich
 * die Wahl.
 *
 * Das Setzen von data-theme passiert NICHT hier, sondern in einem kurzen
 * Inline-Script im <head> jeder Seite. Eine externe Datei wuerde erst nach
 * einem Roundtrip laufen und die Seite bis dahin im falschen Theme zeigen.
 */
(function () {
  'use strict';

  var root = document.documentElement;
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;

  /* Die Sprachen der Seite. /bestiary/ gibt es in zehn, /ruhe/ in neunzehn,
   * der Rest in zwei — ein unbekanntes root.lang faellt auf Deutsch zurueck. */
  var TEXTS = {
    de: { light: 'Design: hell', dark: 'Design: dunkel' },
    en: { light: 'Theme: light', dark: 'Theme: dark' },
    fr: { light: 'Thème : clair', dark: 'Thème : sombre' },
    es: { light: 'Tema: claro', dark: 'Tema: oscuro' },
    it: { light: 'Tema: chiaro', dark: 'Tema: scuro' },
    'pt-BR': { light: 'Tema: claro', dark: 'Tema: escuro' },
    nl: { light: 'Thema: licht', dark: 'Thema: donker' },
    da: { light: 'Tema: lyst', dark: 'Tema: mørkt' },
    sv: { light: 'Tema: ljust', dark: 'Tema: mörkt' },
    nb: { light: 'Tema: lyst', dark: 'Tema: mørkt' },
    fi: { light: 'Teema: vaalea', dark: 'Teema: tumma' },
    pl: { light: 'Motyw: jasny', dark: 'Motyw: ciemny' },
    cs: { light: 'Vzhled: světlý', dark: 'Vzhled: tmavý' },
    tr: { light: 'Tema: açık', dark: 'Tema: koyu' },
    uk: { light: 'Тема: світла', dark: 'Тема: темна' },
    ru: { light: 'Тема: светлая', dark: 'Тема: тёмная' },
    id: { light: 'Tema: terang', dark: 'Tema: gelap' },
    ja: { light: 'テーマ: ライト', dark: 'テーマ: ダーク' },
    ko: { light: '테마: 밝게', dark: '테마: 어둡게' },
    'zh-Hans': { light: '主题：浅色', dark: '主题：深色' },
    'zh-Hant': { light: '主題：淺色', dark: '主題：深色' }
  };
  var labels = TEXTS[root.lang] || TEXTS.de;
  var darkQuery = window.matchMedia('(prefers-color-scheme: dark)');

  function systemTheme() {
    return darkQuery.matches ? 'dark' : 'light';
  }

  /* Was gerade zu sehen ist: die gespeicherte Wahl oder das System. */
  function current() {
    return root.dataset.theme || systemTheme();
  }

  /* <picture>-Quellen und die theme-color-Metas haengen an Media Queries und
   * wuerden sonst weiter dem Betriebssystem folgen statt der manuellen Wahl. */
  function mediaFor(mode, isDark) {
    return isDark === (mode === 'dark') ? 'all' : 'not all';
  }

  function apply(mode) {
    root.dataset.theme = mode;
    try { localStorage.setItem('theme', mode); } catch (e) {}

    document.querySelectorAll('picture source').forEach(function (source) {
      source.media = mediaFor(mode, /\/dark\//.test(source.srcset));
    });
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (meta) {
      meta.media = mediaFor(mode, meta.content.toUpperCase() === '#17120E');
    });
    label();
  }

  function label() {
    btn.title = labels[current()];
    btn.setAttribute('aria-label', labels[current()]);
  }

  btn.addEventListener('click', function () { apply(current() === 'dark' ? 'light' : 'dark'); });
  if (root.dataset.theme) apply(root.dataset.theme);
  else label();
  /* Ohne eigene Wahl folgt die Seite dem System; die Beschriftung zieht mit. */
  darkQuery.addEventListener('change', function () { if (!root.dataset.theme) label(); });
})();

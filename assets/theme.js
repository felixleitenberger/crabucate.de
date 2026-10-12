/* crabucate — Theme-Umschalter.
 *
 * Drei Zustaende: auto (kein data-theme), light, dark. Gespeichert wird nur
 * eine ausdrueckliche Wahl; "auto" loescht den Eintrag wieder.
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
    de: { auto: 'Design: automatisch', light: 'Design: hell', dark: 'Design: dunkel' },
    en: { auto: 'Theme: auto', light: 'Theme: light', dark: 'Theme: dark' },
    fr: { auto: 'Thème : automatique', light: 'Thème : clair', dark: 'Thème : sombre' },
    es: { auto: 'Tema: automático', light: 'Tema: claro', dark: 'Tema: oscuro' },
    it: { auto: 'Tema: automatico', light: 'Tema: chiaro', dark: 'Tema: scuro' },
    'pt-BR': { auto: 'Tema: automático', light: 'Tema: claro', dark: 'Tema: escuro' },
    nl: { auto: 'Thema: automatisch', light: 'Thema: licht', dark: 'Thema: donker' },
    da: { auto: 'Tema: automatisk', light: 'Tema: lyst', dark: 'Tema: mørkt' },
    sv: { auto: 'Tema: automatiskt', light: 'Tema: ljust', dark: 'Tema: mörkt' },
    nb: { auto: 'Tema: automatisk', light: 'Tema: lyst', dark: 'Tema: mørkt' },
    fi: { auto: 'Teema: automaattinen', light: 'Teema: vaalea', dark: 'Teema: tumma' },
    pl: { auto: 'Motyw: automatyczny', light: 'Motyw: jasny', dark: 'Motyw: ciemny' },
    cs: { auto: 'Vzhled: automaticky', light: 'Vzhled: světlý', dark: 'Vzhled: tmavý' },
    tr: { auto: 'Tema: otomatik', light: 'Tema: açık', dark: 'Tema: koyu' },
    uk: { auto: 'Тема: автоматично', light: 'Тема: світла', dark: 'Тема: темна' },
    ja: { auto: 'テーマ: 自動', light: 'テーマ: ライト', dark: 'テーマ: ダーク' },
    ko: { auto: '테마: 자동', light: '테마: 밝게', dark: '테마: 어둡게' },
    'zh-Hans': { auto: '主题：自动', light: '主题：浅色', dark: '主题：深色' },
    'zh-Hant': { auto: '主題：自動', light: '主題：淺色', dark: '主題：深色' }
  };
  var labels = TEXTS[root.lang] || TEXTS.de;
  var darkQuery = window.matchMedia('(prefers-color-scheme: dark)');

  function systemTheme() {
    return darkQuery.matches ? 'dark' : 'light';
  }

  /* Reihenfolge haengt vom Systemtheme ab, damit der erste Klick immer
   * sichtbar umschaltet. Bei hellem System waere auto -> light sonst ein
   * Nulldurchgang und man muesste zweimal klicken. */
  function nextMode() {
    var current = root.dataset.theme;
    var system = systemTheme();
    if (!current) return system === 'dark' ? 'light' : 'dark';
    if (current !== system) return system;
    return 'auto';
  }

  /* <picture>-Quellen und die theme-color-Metas haengen an Media Queries und
   * wuerden sonst weiter dem Betriebssystem folgen statt der manuellen Wahl. */
  function mediaFor(mode, isDark) {
    if (mode === 'auto') {
      return isDark ? '(prefers-color-scheme: dark)' : '(prefers-color-scheme: light)';
    }
    return isDark === (mode === 'dark') ? 'all' : 'not all';
  }

  function apply(mode) {
    if (mode === 'auto') {
      delete root.dataset.theme;
      try { localStorage.removeItem('theme'); } catch (e) {}
    } else {
      root.dataset.theme = mode;
      try { localStorage.setItem('theme', mode); } catch (e) {}
    }

    document.querySelectorAll('picture source').forEach(function (source) {
      source.media = mediaFor(mode, /\/dark\//.test(source.srcset));
    });
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (meta) {
      meta.media = mediaFor(mode, meta.content.toUpperCase() === '#17120E');
    });

    btn.title = labels[mode];
    btn.setAttribute('aria-label', labels[mode]);
  }

  btn.addEventListener('click', function () { apply(nextMode()); });
  apply(root.dataset.theme || 'auto');
})();

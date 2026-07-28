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

  var TEXTS = {
    de: { auto: 'Design: automatisch', light: 'Design: hell', dark: 'Design: dunkel' },
    en: { auto: 'Theme: auto', light: 'Theme: light', dark: 'Theme: dark' }
  };
  var labels = TEXTS[root.lang === 'en' ? 'en' : 'de'];
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

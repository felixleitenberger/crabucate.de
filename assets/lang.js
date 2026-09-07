/* crabucate — Sprachwaehler.
 *
 * Das Auf- und Zuklappen macht <details> von allein; ohne JavaScript
 * funktioniert der Waehler also vollstaendig. Hier kommt nur dazu, was das
 * Element nicht mitbringt: Schliessen bei einem Klick daneben und mit Escape.
 *
 * Ausserdem merkt sich die Seite eine ausdrueckliche Wahl zwischen Deutsch und
 * Englisch — die Startseite leitet danach um (das Inline-Script in ihrem
 * <head>). Die uebrigen acht Sprachen gibt es nur unter /bestiary/ und sie
 * wuerden dort nichts steuern, deshalb landen sie nicht im Speicher.
 */
(function () {
  'use strict';

  var menu = document.querySelector('.lang-menu');
  if (!menu) return;

  document.addEventListener('click', function (event) {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && menu.open) {
      menu.open = false;
      var summary = menu.querySelector('summary');
      if (summary) summary.focus();
    }
  });

  menu.addEventListener('click', function (event) {
    var link = event.target.closest('a[hreflang]');
    if (!link) return;
    var lang = link.getAttribute('hreflang');
    if (lang !== 'de' && lang !== 'en') return;
    try { localStorage.setItem('lang', lang); } catch (e) {}
  });
})();

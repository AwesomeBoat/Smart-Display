// =====================================================================
// icons.js — the design system's 24px line icons
// 1.6px stroke, round caps, currentColor (the colour comes from CSS).
// The SVG strings are constants written here, never user data.
// =====================================================================

const PATHS = {
  calendar: '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>',
  tasks:    '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="m8 12 3 3 5-6"/>',
  habits:   '<path d="M6 20v-8M12 20V5M18 20v-6"/>',
  wind:     '<path d="M3 8h10a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h7"/>',
  suncloud: '<circle cx="9" cy="9" r="3.6"/><path d="M9 2v1.6M2 9h1.6M4 4l1.1 1.1M14 4l-1.1 1.1"/><path d="M8.5 21h8.5a4 4 0 0 0 .3-8 5.5 5.5 0 0 0-10.3 1.7A3.2 3.2 0 0 0 8.5 21z"/>',
  thermo:   '<path d="M14 14.8V4.5a2 2 0 0 0-4 0v10.3a4 4 0 1 0 4 0z"/><path d="M12 11v6"/>',
  flame:    '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
  spark:    '<path d="M12 3.5l1.7 5 5 1.7-5 1.7-1.7 5-1.7-5-5-1.7 5-1.7z"/>',
  phone:    '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18h2"/>',
  plus:     '<path d="M12 5v14M5 12h14"/>',
  screen:   '<rect x="2.5" y="4" width="19" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
  trash:    '<path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 13h9l1-13"/>',
  undo:     '<path d="M9 14 4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
  // the check glyph drawn inside done rings / habit days
  check:    '<path d="m5 12 4.5 4.5L19 7"/>',
};

/**
 * Return a new <svg> element for an icon.
 *   icon("calendar")                    → standard 24px icon
 *   icon("thermo", "sd-ico sd-ico--lg") → 40px hero icon
 *   icon("check", "")                   → bare svg, styled by its parent
 */
export function icon(name, className = "sd-ico") {
  const template = document.createElement("template");
  const classAttr = className ? ` class="${className}"` : "";
  template.innerHTML = `<svg${classAttr} viewBox="0 0 24 24" aria-hidden="true">${PATHS[name]}</svg>`;
  return template.content.firstElementChild;
}

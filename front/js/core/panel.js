// =====================================================================
// panel.js — the glass panel every widget sits in
// =====================================================================

import { h } from "./dom.js";
import { icon } from "./icons.js";

/**
 * <section class="sd-glass"> with the standard header (icon + title).
 * Returns { panel, head, body }: fill `body`, put the right-hand count
 * (or anything else) in `head`.
 */
export function createPanel({ iconName, title, className = "" }) {
  const head = h("header", { class: "sd-head" },
    icon(iconName),
    h("span", { class: "t-title" }, title),
  );
  const body = h("div", { class: "sd-panel-body" });
  const panel = h("section", { class: `sd-glass ${className}`.trim() }, head, body);
  return { panel, head, body };
}

/** The muted count / info on the right of a header ("2 / 4 validées") */
export function createAside() {
  return h("span", { class: "sd-aside t-meta sd-num" });
}

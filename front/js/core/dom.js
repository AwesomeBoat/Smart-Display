// =====================================================================
// dom.js — tiny helpers to build DOM nodes without innerHTML
// User data (task names, event titles...) always goes through text
// nodes, so a title like "<b>" is shown as text, never run as HTML.
// =====================================================================

/**
 * Create an element.
 *   h("span", { class: "t-meta", style: { left: "10px" } }, "Hello", otherNode)
 * - props.class  → className
 * - props.style  → object of CSS properties (kebab-case, custom props allowed)
 * - other props  → attributes (null / false are skipped)
 * - children     → strings become text nodes, null / false are skipped
 */
export function h(tag, props = {}, ...children) {
  const node = document.createElement(tag);

  for (const [key, value] of Object.entries(props)) {
    if (value == null || value === false) continue;
    if (key === "class") {
      node.className = value;
    } else if (key === "style") {
      for (const [property, styleValue] of Object.entries(value)) {
        node.style.setProperty(property, styleValue);
      }
    } else {
      node.setAttribute(key, value === true ? "" : value);
    }
  }

  for (const child of children.flat(Infinity)) {
    if (child == null || child === false) continue;
    node.append(child instanceof Node ? child : String(child));
  }
  return node;
}

/** Join class names, skipping the falsy ones: cx("a", done && "b") */
export function cx(...names) {
  return names.filter(Boolean).join(" ");
}

/** Shorthand for a CSS pixel value */
export function px(value) {
  return `${Math.round(value * 10) / 10}px`;
}

/** Placeholder bars shown before the first data arrives (never an empty box) */
export function skeleton(widths = ["70%", "45%"]) {
  return widths.map(width => h("span", { class: "sd-skel", style: { width } }));
}

/**
 * Replace all children of `node`. Like node.replaceChildren(), but accepts
 * nested arrays and skips null / false, so conditional pieces read simply:
 *   setChildren(list, showBar && bar, rows.map(row))
 */
export function setChildren(node, ...children) {
  node.replaceChildren(...children.flat(Infinity).filter(child => child != null && child !== false));
}

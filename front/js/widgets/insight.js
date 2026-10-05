// =====================================================================
// Insight — the intelligent layer talking to you
// The screen's ONE glowing panel (sd-glass--active).
// Data (future, the Chronicle/ML layer): { eyebrow, statement, ask?, expects_reply? }
// No insight yet → the motto "Petit progrès tous les jours." in the same slot.
// Two variants: "panel" (Jour, bottom right) and "tile" (Semaine, top band).
// =====================================================================

import { h, cx, setChildren } from "../core/dom.js";
import { icon } from "../core/icons.js";
import { frenchSpacing } from "../core/format.js";

export function createInsight(zone, { variant = "panel" } = {}) {
  const content = h("div", { class: cx("sd-insight", variant === "tile" && "sd-insight--tile") });
  zone.append(h("section", { class: "sd-glass sd-glass--active" }, content));

  function render(insight) {
    // the panel shows the statement in t-insight-sm; the tile styles <p> itself (32/38)
    const textClass = variant === "panel" ? "t-insight-sm" : null;

    if (!insight) {
      setChildren(content,
        h("p", { class: textClass }, "Petit progrès ", h("em", {}, "tous les jours.")),
        variant === "panel" && h("div", { class: "sd-rule" }),
      );
      return;
    }

    setChildren(content,
      insight.eyebrow && h("span", { class: "t-eyebrow" }, insight.eyebrow),
      h("p", { class: textClass },
        frenchSpacing(insight.statement),
        insight.ask && " ",
        insight.ask && h("em", {}, frenchSpacing(insight.ask)),
      ),
      variant === "panel" && h("div", { class: "sd-rule" }),
      insight.expects_reply && h("div", { class: "sd-insight-hint t-meta" },
        icon("phone"),
        "Réponds depuis ton téléphone",
      ),
    );
  }

  render(null);
  return { update: render };
}

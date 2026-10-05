// =====================================================================
// Tasks — the active profile's to-do list
// Stream: /todo/get_curr_todo → [{ id, name, done, created_at, profile_id }]
// Two views of the same data:
//   createTaskRing   → "Tâches" KPI tile, progress ring "2/4"
//   createTasksPanel → the list: open tasks first, done ones struck through
// The display is read-only: no add button here, adding is done on the phone.
// =====================================================================

import { h, cx, skeleton, setChildren } from "../core/dom.js";
import { icon } from "../core/icons.js";
import { plural } from "../core/format.js";
import { createPanel, createAside } from "../core/panel.js";

/** { done, total } of a task list */
function countTasks(tasks) {
  return { done: tasks.filter(task => task.done).length, total: tasks.length };
}

// ---------------------------------------------------------------------
// KPI tile: progress ring
// ---------------------------------------------------------------------

const RING_SIZE = 148;
const RING_STROKE = 8;
const RING_RADIUS = (RING_SIZE - RING_STROKE) / 2 - 3; // 67, as in the design
const RING_LENGTH = 2 * Math.PI * RING_RADIUS;

export function createTaskRing(zone) {
  const { panel, body } = createPanel({ iconName: "tasks", title: "Tâches" });
  body.append(...skeleton());
  zone.append(panel);

  return {
    update(tasks) {
      const { done, total } = countTasks(tasks);
      const progress = total ? done / total : 0;
      const remaining = total - done;

      setChildren(body,
        h("div", { class: "sd-ring-row" },
          h("div", { class: "sd-ring", style: { width: `${RING_SIZE}px`, height: `${RING_SIZE}px` } },
            ringSvg(progress),
            h("span", { class: "t-temp sd-num sd-ring-value" }, `${done}/${total}`),
          ),
          total
            ? h("div", { class: "t-meta sd-muted" },
                plural(done, "validée"), h("br"),
                `${remaining} ${plural(remaining, "restante")}`)
            : h("p", { class: "t-meta sd-empty" }, "Rien pour aujourd'hui"),
        ),
      );
    },
  };
}

/** The ring itself: a track circle + an accent arc of `progress` (0 → 1) */
function ringSvg(progress) {
  const centre = RING_SIZE / 2;
  const template = document.createElement("template");
  // numbers only in this string: no user data
  template.innerHTML = `
    <svg width="${RING_SIZE}" height="${RING_SIZE}" aria-hidden="true">
      <circle class="track" cx="${centre}" cy="${centre}" r="${RING_RADIUS}" stroke-width="${RING_STROKE}"/>
      ${progress > 0 ? `<circle class="fill" cx="${centre}" cy="${centre}" r="${RING_RADIUS}"
        stroke-width="${RING_STROKE}" stroke-dasharray="${progress * RING_LENGTH} ${RING_LENGTH}"/>` : ""}
    </svg>`;
  return template.content.firstElementChild;
}

// ---------------------------------------------------------------------
// Panel: the list
// ---------------------------------------------------------------------

/**
 * options.showBar  progress bar under the header (Semaine; in Jour the ring shows it)
 * options.maxRows  rows that fit the panel, then "+N autres"
 */
export function createTasksPanel(zone, { showBar = false, maxRows = 6 } = {}) {
  const { panel, head, body } = createPanel({ iconName: "tasks", title: "Tâches", className: "sd-tasks" });
  const count = createAside();
  head.append(count);
  body.append(...skeleton(["80%", "60%", "70%"]));
  zone.append(panel);

  return {
    update(tasks) {
      const { done, total } = countTasks(tasks);
      count.textContent = total ? `${done} / ${total} validées` : "";

      if (!total) {
        setChildren(body, h("p", { class: "t-meta sd-empty" }, "Rien pour aujourd'hui"));
        return;
      }

      // open tasks first, then done ones (each group keeps the server order)
      const ordered = [...tasks.filter(task => !task.done), ...tasks.filter(task => task.done)];
      // "+1 autre" would take a row anyway: show the task instead
      const visible = ordered.length <= maxRows + 1 ? ordered : ordered.slice(0, maxRows);
      const hidden = ordered.length - visible.length;

      setChildren(body,
        showBar && h("div", { class: "sd-bar" }, h("span", { style: { width: `${(done / total) * 100}%` } })),
        h("ul", { class: "sd-list" },
          visible.map(taskRow),
          hidden > 0 && h("li", { class: "sd-more t-meta" }, `+${hidden} ${plural(hidden, "autre")}`),
        ),
      );
    },
  };
}

function taskRow(task) {
  return h("li", { class: cx("sd-row", task.done && "sd-row--done") },
    h("span", { class: cx("sd-check", task.done && "sd-check--done") }, icon("check", "")),
    h("span", { class: "sd-label t-item" }, task.name),
  );
}

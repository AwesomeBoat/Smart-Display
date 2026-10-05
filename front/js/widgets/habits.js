// =====================================================================
// Habits — each habit with its week (Mon → Sun dots) and its streak
// Stream: /habits/get_curr_habits → [{ id, name, streak, week?, done_today? }]
//   streak      consecutive days ending today or yesterday
//   week        (to add in the backend) one bool per day, Monday → today
//   done_today  (to add in the backend) is today logged?
// Without `week`, past days are drawn as neutral dots instead of guessing.
// Two views of the same data:
//   createHabitsPanel    → the week view
//   createBestStreakTile → "Meilleure série" KPI tile (Jour mode)
// =====================================================================

import { h, cx, skeleton, setChildren } from "../core/dom.js";
import { icon } from "../core/icons.js";
import { plural } from "../core/format.js";
import { createPanel, createAside } from "../core/panel.js";
import { weekdayIndex } from "../core/time.js";

const WEEK_LETTERS = ["L", "M", "M", "J", "V", "S", "D"];
const HOT_STREAK = 3; // from 3 days the flame is lit

/** true / false if we know whether today is logged, null if the stream doesn't say */
function isDoneToday(habit, today = weekdayIndex(new Date())) {
  if (typeof habit.done_today === "boolean") return habit.done_today;
  if (Array.isArray(habit.week) && habit.week.length > today) return Boolean(habit.week[today]);
  return null;
}

/** "3 / 5" habits done today, or null if the stream doesn't say */
function countDoneToday(habits) {
  const states = habits.map(habit => isDoneToday(habit));
  if (states.includes(null)) return null;
  return states.filter(Boolean).length;
}

// ---------------------------------------------------------------------
// Panel: week view
// ---------------------------------------------------------------------

/**
 * options.compact  narrow variant (Semaine): smaller dots, 170px names
 * options.maxRows  rows that fit the panel, then "+N autres"
 */
export function createHabitsPanel(zone, { compact = false, maxRows = 7 } = {}) {
  const { panel, head, body } = createPanel({
    iconName: "habits",
    title: "Habitudes",
    className: cx("sd-habits", compact && "sd-compact"),
  });
  const count = createAside();
  head.append(count);
  body.append(...skeleton(["80%", "65%", "72%"]));
  zone.append(panel);

  return {
    update(habits) {
      const doneCount = countDoneToday(habits);
      count.textContent = habits.length && doneCount !== null
        ? `${doneCount} / ${habits.length} aujourd'hui`
        : "";

      if (!habits.length) {
        setChildren(body, h("p", { class: "t-meta sd-empty" }, "Aucune habitude pour l'instant"));
        return;
      }

      const today = weekdayIndex(new Date());
      const visible = habits.length <= maxRows + 1 ? habits : habits.slice(0, maxRows);
      const hidden = habits.length - visible.length;

      setChildren(body,
        lettersRow(today),
        h("ul", { class: "sd-list" },
          visible.map(habit => habitRow(habit, today)),
          hidden > 0 && h("li", { class: "sd-more t-meta" }, `+${hidden} ${plural(hidden, "autre")}`),
        ),
      );
    },
  };
}

/** "L M M J V S D" above the dots, today's letter in accent */
function lettersRow(today) {
  return h("div", { class: "sd-row sd-letters-row" },
    h("span", { class: "sd-habit-name" }),
    h("span", { class: "sd-week sd-week-letters t-meta" },
      WEEK_LETTERS.map((letter, day) => h("span", { class: cx(day === today && "sd-accent") }, letter)),
    ),
    // invisible flame: same width as the real ones, so the columns line up
    h("span", { class: "sd-flame t-meta" }, icon("flame", ""), h("b", {}, "00"), " j"),
  );
}

function habitRow(habit, today) {
  return h("li", { class: "sd-row" },
    h("span", { class: "sd-label sd-habit-name t-item" }, habit.name),
    h("span", { class: "sd-week" },
      WEEK_LETTERS.map((_, day) => dayDot(habit, day, today)),
    ),
    flame(habit.streak),
  );
}

/**
 * One day of the week:
 *   done   → success fill + check (today done: + accent ring)
 *   today  → empty accent ring, glowing
 *   missed → empty faint ring (past day, not logged)
 *   future → small faint dot (also used when the stream doesn't send `week`)
 */
function dayDot(habit, day, today) {
  const known = Array.isArray(habit.week) && day < habit.week.length;
  const done = day === today ? isDoneToday(habit, today) === true : known && Boolean(habit.week[day]);

  let state;
  if (done) state = cx("sd-day--done", day === today && "sd-day--is-today");
  else if (day === today) state = "sd-day--today";
  else if (day < today && known) state = "sd-day--missed";
  else state = "sd-day--future";

  return h("span", { class: `sd-day ${state}` }, done && icon("check", ""));
}

/** Flame + "12 j"; lit (accent fill + glow) from HOT_STREAK days */
function flame(streak) {
  return h("span", {
      class: cx("sd-flame t-meta", streak >= HOT_STREAK && "sd-flame--hot"),
      title: `Série : ${streak} j`,
    },
    icon("flame"),
    h("b", {}, streak),
    " j",
  );
}

// ---------------------------------------------------------------------
// KPI tile: best current streak (Jour mode)
// ---------------------------------------------------------------------

export function createBestStreakTile(zone) {
  const { panel, body } = createPanel({ iconName: "habits", title: "Meilleure série" });
  body.append(...skeleton());
  zone.append(panel);

  return {
    update(habits) {
      if (!habits.length) {
        setChildren(body, h("p", { class: "t-meta sd-empty" }, "Aucune habitude pour l'instant"));
        return;
      }

      const best = habits.reduce((top, habit) => (habit.streak > top.streak ? habit : top));
      const doneCount = countDoneToday(habits);
      const details = doneCount === null
        ? best.name
        : `${best.name} · ${doneCount} / ${habits.length} habitudes aujourd'hui`;

      setChildren(body,
        h("div", { class: "sd-streak-value" },
          h("span", { class: "t-temp sd-accent sd-num" }, best.streak),
          h("span", { class: "t-item sd-muted" }, plural(best.streak, "jour")),
        ),
        h("div", { class: "t-meta sd-muted sd-kpi-meta" }, details),
      );
    },
  };
}

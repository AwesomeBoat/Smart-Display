// =====================================================================
// AgendaWeek — Monday → Sunday grid, 8h → 22h (Semaine mode)
// Stream: the same /calendar/get_curr_calendar; we keep this week's events.
//
//          Lun 5   Mar 6   Mer 7  (Jeu 8)  Ven 9 ...   ← day labels, today in a pill
//                                 [chip all-day]        ← all-day events
//   8h  ───────────────────────────────────────         ← hour lines every 2 h
//          [Formation]       [Formation]
//   10h ───────────────────────────────────
//                          ●━━━━━━━                     ← "now" line, today only
//
// Past events are dimmed, the current one glows. Overlapping events split
// their column. Re-drawn every minute for the "now" line.
// =====================================================================

import { h, cx, px, skeleton, setChildren } from "../core/dom.js";
import { icon } from "../core/icons.js";
import { formatTime, formatWeekRange, formatWeekday, frenchSpacing } from "../core/format.js";
import { parseEvents, eventsBetween, assignLanes } from "../core/events.js";
import { MINUTE, addDays, startOfDay, startOfWeek, hourOfDay, clamp } from "../core/time.js";

const FIRST_HOUR = 8;
const LAST_HOUR = 22;
const LABEL_EVERY = 2;
const DAY_NAMES = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];

// layout of the grid inside the panel (design pixels)
const GUTTER = 56;        // left column with the hour labels
const GRID_TOP = 138;     // y of the first hour line (below labels and chips)
const BLOCK_INSET = 3;    // space between an event block and its column edges
const SHOW_TIME_FROM = 75; // minutes: shorter blocks only show their title

export function createAgendaWeek(zone) {
  const aside = h("span", { class: "sd-aside t-meta" });
  const grid = h("div", { class: "sd-week-grid" },
    h("header", { class: "sd-head" },
      icon("calendar"),
      h("span", { class: "t-title" }, "Cette semaine"),
      aside,
    ),
  );
  // positioned children land in .sd-week-grid; the skeleton sits below the header
  const content = h("div", {}, h("div", { style: { "padding-top": "60px" } }, ...skeleton(["90%", "70%"])));
  grid.append(content);
  zone.append(h("section", { class: "sd-glass" }, grid));

  let events = null;

  function render() {
    const now = new Date();
    const monday = startOfWeek(now);
    const sunday = addDays(monday, 6);
    const week = eventsBetween(events, monday, addDays(monday, 7));

    // header: "5 – 11 octobre · Prochain : Sport à 18:30"
    const upcoming = week.find(event => !event.allDay && event.start > now);
    aside.textContent = [
      formatWeekRange(monday, sunday),
      upcoming && frenchSpacing(`Prochain : ${upcoming.title} ${whenLabel(upcoming.start, now)}`),
    ].filter(Boolean).join(" · ");

    // geometry, measured from the grid (content box of the panel)
    const columnWidth = (grid.clientWidth - GUTTER) / 7;
    const pxPerHour = (grid.clientHeight - GRID_TOP) / (LAST_HOUR - FIRST_HOUR);
    const columnLeft = day => GUTTER + day * columnWidth;
    const yOf = hour => GRID_TOP + (clamp(hour, FIRST_HOUR, LAST_HOUR) - FIRST_HOUR) * pxPerHour;
    const todayIndex = Math.round((startOfDay(now) - monday) / 86400000);

    const nodes = [
      h("div", { class: "sd-week-today", style: { left: px(columnLeft(todayIndex)), width: px(columnWidth) } }),
      dayLabels(monday, todayIndex, columnLeft, columnWidth),
      hourLines(yOf),
      allDayChips(week, monday, columnLeft, columnWidth),
    ];

    // timed events, cut per day (an event over midnight shows in both columns)
    for (let day = 0; day < 7; day++) {
      const dayStart = addDays(monday, day);
      const dayEnd = addDays(dayStart, 1);
      const segments = eventsBetween(week, dayStart, dayEnd)
        .filter(event => !event.allDay)
        .map(event => ({
          event,
          start: event.start < dayStart ? 0 : hourOfDay(event.start),
          end: event.end >= dayEnd ? 24 : hourOfDay(event.end),
        }));
      for (const item of assignLanes(segments)) {
        nodes.push(eventBlock(item, columnLeft(day), columnWidth, yOf, pxPerHour, now));
      }
    }

    // "now" line across today's column
    const nowHour = hourOfDay(now);
    if (nowHour >= FIRST_HOUR && nowHour <= LAST_HOUR) {
      const y = px(yOf(nowHour));
      nodes.push(
        h("div", { class: "sd-week-now-line", style: { left: px(columnLeft(todayIndex)), width: px(columnWidth), top: y } }),
        h("div", { class: "sd-week-now-dot", style: { left: px(columnLeft(todayIndex)), top: y } }),
      );
    }

    setChildren(content, nodes);
  }

  setInterval(() => events && render(), MINUTE);

  return {
    update(rawEvents) {
      events = parseEvents(rawEvents);
      render();
    },
  };
}

/** "à 18:30" today, "vendredi à 18:30" another day */
function whenLabel(start, now) {
  const sameDay = startOfDay(start).getTime() === startOfDay(now).getTime();
  return sameDay ? `à ${formatTime(start)}` : `${formatWeekday(start)} à ${formatTime(start)}`;
}

/** "Lun 5" … "Dim 11": past days faint, today accent in a pill */
function dayLabels(monday, todayIndex, columnLeft, columnWidth) {
  return DAY_NAMES.map((name, day) => h("div", {
      class: cx(
        "sd-week-label t-meta sd-num",
        day < todayIndex && "sd-week-label--past",
        day === todayIndex && "sd-week-label--today",
      ),
      style: { left: px(columnLeft(day)), width: px(columnWidth) },
    },
    name, " ", h("b", {}, addDays(monday, day).getDate()),
  ));
}

function hourLines(yOf) {
  const nodes = [];
  for (let hour = FIRST_HOUR; hour <= LAST_HOUR; hour += LABEL_EVERY) {
    const top = px(yOf(hour));
    nodes.push(
      h("div", { class: "sd-week-hourline", style: { top } }),
      h("span", { class: "sd-week-hour sd-num", style: { top } }, `${hour}h`),
    );
  }
  return nodes;
}

/**
 * All-day events as chips spanning their days.
 * There is room for one row only: when two all-day events share a day,
 * the first one (by start) is shown.
 */
function allDayChips(week, monday, columnLeft, columnWidth) {
  const taken = new Array(7).fill(false);
  const chips = [];

  for (const event of week.filter(item => item.allDay)) {
    // iCal all-day ends are exclusive: an event on the 8th ends on the 9th 00:00
    const first = Math.max(0, Math.round((startOfDay(event.start) - monday) / 86400000));
    const last = Math.min(6, Math.round((startOfDay(event.end) - monday) / 86400000) - 1);
    if (last < first || taken.slice(first, last + 1).some(Boolean)) continue;
    taken.fill(true, first, last + 1);

    chips.push(h("div", {
        class: "sd-chip sd-week-chip t-meta",
        style: {
          left: px(columnLeft(first) + BLOCK_INSET),
          width: px((last - first + 1) * columnWidth - 2 * BLOCK_INSET),
        },
        title: event.title,
      },
      h("i", { class: `dot-${event.colour}` }),
      h("span", {}, event.title),
    ));
  }
  return chips;
}

/** One timed event block in its day column */
function eventBlock({ event, start, end, lane, lanes }, left, columnWidth, yOf, pxPerHour, now) {
  const laneWidth = (columnWidth - 2 * BLOCK_INSET) / lanes;
  const top = yOf(start) + 1;
  const height = Math.max(yOf(end) - yOf(start) - 3, 20);
  const isNow = event.start <= now && now < event.end;
  const isPast = event.end <= now;
  const longEnough = (yOf(end) - yOf(start)) / pxPerHour * 60 >= SHOW_TIME_FROM;

  return h("div", {
      class: cx("sd-week-event", isPast && "sd-week-event--past", isNow && "sd-week-event--now"),
      style: {
        left: px(left + BLOCK_INSET + lane * laneWidth),
        width: px(laneWidth - (lanes > 1 ? 2 : 0)),
        top: px(top),
        height: px(height),
      },
      title: event.location ? `${event.title} · ${event.location}` : event.title,
    },
    h("div", { class: "sd-week-event-title" },
      h("i", { class: `dot-${event.colour}` }),
      h("span", {}, event.title),
    ),
    longEnough && h("div", { class: "sd-week-event-time sd-num" },
      `${formatTime(event.start)}–${formatTime(event.end)}`),
  );
}

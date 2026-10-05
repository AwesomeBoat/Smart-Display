// =====================================================================
// AgendaDay — today as one horizontal timeline, 7h → 23h (Jour mode)
// Stream: /calendar/get_curr_calendar → [{ title, location, start, end, all_day }]
// (next 30 days; we keep today's events).
//
//   7h        9h        11h   ...   23h        ← hour labels every 2 h
//   ──[Formation]──[Repas]──│──[Sport]──        ← rail, events, "now" line
//
// Events before 7h / after 23h are clamped to the edges; overlapping
// events stack in two thin rows. Re-drawn every minute for the "now" line.
// =====================================================================

import { h, cx, px, skeleton, setChildren } from "../core/dom.js";
import { formatCountdown, formatTime, frenchSpacing } from "../core/format.js";
import { createPanel, createAside } from "../core/panel.js";
import { parseEvents, eventsBetween, assignLanes } from "../core/events.js";
import { MINUTE, addDays, startOfDay, hourOfDay, clamp } from "../core/time.js";

const FIRST_HOUR = 7;
const LAST_HOUR = 23;
const LABEL_EVERY = 2;     // an hour label every 2 h
const RAIL_INSET = 40;     // px between the panel edge and the rail ends
const EVENT_GAP = 6;       // px between two consecutive event blocks
const MIN_EVENT_WIDTH = 28;

export function createAgendaDay(zone) {
  const { panel, head, body } = createPanel({ iconName: "calendar", title: "Aujourd'hui" });
  const chips = h("span", { class: "sd-chips" });
  const next = createAside();
  head.append(chips, next);
  body.append(...skeleton(["90%"]));
  zone.append(panel);

  let events = null;

  function render() {
    const now = new Date();
    const today = startOfDay(now);
    const todays = eventsBetween(events, today, addDays(today, 1));
    const timed = todays.filter(event => !event.allDay);

    // header: all-day chips + "Prochain : Sport dans 2 h 06"
    setChildren(chips, todays.filter(event => event.allDay).map(allDayChip));
    const upcoming = timed.find(event => event.start > now);
    next.textContent = upcoming
      ? frenchSpacing(`Prochain : ${upcoming.title} dans ${formatCountdown((upcoming.start - now) / MINUTE)}`)
      : "";

    if (!todays.length) {
      setChildren(body, h("p", { class: "t-meta sd-empty" }, "Rien pour aujourd'hui"));
      return;
    }

    // geometry: hours → x in px, inside the panel's padding box
    const railWidth = panel.clientWidth - 2 * RAIL_INSET;
    const pxPerHour = railWidth / (LAST_HOUR - FIRST_HOUR);
    const xOf = hour => RAIL_INSET + (clamp(hour, FIRST_HOUR, LAST_HOUR) - FIRST_HOUR) * pxPerHour;

    // an event that started yesterday starts at 0h today, one ending tomorrow ends at 24h
    const placed = assignLanes(timed.map(event => ({
      event,
      start: event.start < today ? 0 : hourOfDay(event.start),
      end: event.end >= addDays(today, 1) ? 24 : hourOfDay(event.end),
    })));

    const nowHour = hourOfDay(now);
    const showNow = nowHour >= FIRST_HOUR && nowHour <= LAST_HOUR;

    setChildren(body,
      h("div", { class: "sd-timeline-rail" }),
      hourLabels(xOf),
      placed.map(item => eventBlock(item, xOf, now)),
      showNow && h("div", { class: "sd-timeline-now", style: { left: px(xOf(nowHour)) } }),
      showNow && h("span", {
        class: "sd-timeline-now-label t-meta sd-accent sd-num",
        style: { left: px(xOf(nowHour)) },
      }, formatTime(now)),
    );
  }

  setInterval(() => events && render(), MINUTE); // move the "now" line

  return {
    update(rawEvents) {
      events = parseEvents(rawEvents);
      render();
    },
  };
}

function hourLabels(xOf) {
  const labels = [];
  for (let hour = FIRST_HOUR; hour <= LAST_HOUR; hour += LABEL_EVERY) {
    labels.push(h("span", { class: "sd-timeline-hour t-meta sd-num", style: { left: px(xOf(hour)) } }, `${hour}h`));
  }
  return labels;
}

/** One event block; stacked in 2 thin rows when it overlaps another event */
function eventBlock({ event, start, end, lane, lanes }, xOf, now) {
  const left = xOf(start);
  const width = Math.max(MIN_EVENT_WIDTH, xOf(end) - left - EVENT_GAP);
  const isNow = event.start <= now && now < event.end;
  const stacked = lanes > 1;

  return h("div", {
      class: cx(
        "sd-timeline-event",
        stacked && "sd-timeline-event--stacked",
        stacked && lane % 2 === 1 && "sd-timeline-event--lane-1",
        isNow && "sd-timeline-event--now",
      ),
      style: { left: px(left), width: px(width) },
      title: event.location ? `${event.title} · ${event.location}` : event.title,
    },
    h("i", { class: `dot-${event.colour}` }),
    h("span", { class: stacked ? null : "t-meta" }, event.title),
  );
}

function allDayChip(event) {
  return h("span", { class: "sd-chip t-meta" }, h("i", { class: `dot-${event.colour}` }), event.title);
}

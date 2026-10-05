// =====================================================================
// events.js — turn the /calendar stream into Date-based events
// Shared by AgendaDay (Jour) and AgendaWeek (Semaine).
// =====================================================================

import { HOUR, addDays } from "./time.js";

const EVENT_COLOURS = ["blue", "amber", "violet", "mint"];

/**
 * Parse a date sent by the server (Python isoformat()).
 * "2026-10-08" (all-day) must be read as LOCAL midnight: new Date("2026-10-08")
 * would read it as UTC midnight and shift it by the timezone.
 */
function parseServerDate(text) {
  if (/^\d{4}-\d{2}-\d{2}$/.test(text)) {
    const [year, month, day] = text.split("-").map(Number);
    return new Date(year, month - 1, day);
  }
  return new Date(text); // with time: local if naive, exact if it has an offset
}

/**
 * Stream payload → [{ title, location, start, end, allDay, colour }]
 * start / end are Date objects; a missing end lasts 1 h (or 1 day if all-day).
 */
export function parseEvents(rawEvents) {
  return rawEvents
    .filter(event => event.start)
    .map(event => {
      const start = parseServerDate(event.start);
      const fallbackEnd = event.all_day ? addDays(start, 1) : new Date(start.getTime() + HOUR);
      return {
        title: event.title || "Sans titre",
        location: event.location || "",
        start,
        end: event.end ? parseServerDate(event.end) : fallbackEnd,
        allDay: Boolean(event.all_day),
        colour: eventColour(event.title || ""),
      };
    });
}

/**
 * Pick one of the 4 event colours from the title (a tiny string hash),
 * so a recurring event always keeps the same colour. Colours carry no meaning.
 */
export function eventColour(title) {
  let hash = 0;
  for (const char of title) {
    hash = (hash * 31 + char.codePointAt(0)) >>> 0; // >>> 0 keeps it a positive int
  }
  return EVENT_COLOURS[hash % EVENT_COLOURS.length];
}

/** Events that overlap the [from, to) period, sorted by start */
export function eventsBetween(events, from, to) {
  return events
    .filter(event => event.start < to && event.end > from)
    .sort((a, b) => a.start - b.start);
}

/**
 * Give overlapping events side-by-side "lanes".
 * Returns each event with { lane, lanes }: lane = its position (0, 1, ...),
 * lanes = how many lanes its group of overlapping events needs.
 * `start` / `end` here are numbers (the widgets pass clamped hours).
 */
export function assignLanes(items) {
  const result = [];
  let group = [];        // the current group of events that overlap each other
  let groupEnd = -Infinity;
  let laneEnds = [];     // end time of the last event placed in each lane

  const closeGroup = () => {
    const lanes = Math.max(...group.map(item => item.lane)) + 1;
    group.forEach(item => { item.lanes = lanes; });
    group = [];
    laneEnds = [];
  };

  for (const item of [...items].sort((a, b) => a.start - b.start)) {
    if (group.length && item.start >= groupEnd) closeGroup();

    let lane = laneEnds.findIndex(end => end <= item.start); // first free lane
    if (lane === -1) lane = laneEnds.length;                 // none free: open a new one
    laneEnds[lane] = item.end;

    const placed = { ...item, lane };
    group.push(placed);
    result.push(placed);
    groupEnd = Math.max(groupEnd, item.end);
  }
  if (group.length) closeGroup();
  return result;
}

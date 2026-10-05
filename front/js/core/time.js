// =====================================================================
// time.js — date maths shared by the calendar and habit widgets
// =====================================================================

export const MINUTE = 60 * 1000;
export const HOUR = 60 * MINUTE;
export const DAY = 24 * HOUR;

/** Midnight (local time) of the given day */
export function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

/** Same day, n days later (safe across daylight-saving changes) */
export function addDays(date, days) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days);
}

/** Position of a day in the week, Monday = 0 … Sunday = 6 */
export function weekdayIndex(date) {
  return (date.getDay() + 6) % 7;
}

/** Monday 00:00 of the week containing `date` */
export function startOfWeek(date) {
  return addDays(startOfDay(date), -weekdayIndex(date));
}

/** Hours since midnight, as a decimal: 16:24 → 16.4 */
export function hourOfDay(date) {
  return date.getHours() + date.getMinutes() / 60;
}

/** Keep a value between min and max */
export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

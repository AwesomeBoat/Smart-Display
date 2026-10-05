// =====================================================================
// format.js — French formatting rules of the design system
// Decimal comma, 24-hour time, "1h30", "12 j", narrow no-break space
// before ? ! : ; so they never wrap alone on the next line.
// =====================================================================

const LOCALE = "fr-BE";

/** Narrow no-break space (U+202F), the French space before ? ! : ; */
export const NNBSP = " ";

/** Put a narrow no-break space before ? ! : ; (not inside "16:24") */
export function frenchSpacing(text) {
  return text.replace(/[   ]?([?!:;])(?=\s|$)/g, `${NNBSP}$1`);
}

/** 14.2 → "14,2" (at most `digits` decimals) */
export function formatNumber(value, digits = 1) {
  return value.toLocaleString(LOCALE, { maximumFractionDigits: digits });
}

/** Date → "jeudi 8 octobre" (the CSS uppercases the first letter) */
export function formatLongDate(date) {
  return date.toLocaleDateString(LOCALE, { weekday: "long", day: "numeric", month: "long" });
}

/** Date → "16:24" */
export function formatTime(date) {
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

/** Date → "16:24:37" (same shape as the /clock stream) */
export function formatClock(date) {
  return `${formatTime(date)}:${String(date.getSeconds()).padStart(2, "0")}`;
}

/** Minutes until something → "2 h 06" or "45 min" */
export function formatCountdown(minutes) {
  const total = Math.max(0, Math.round(minutes));
  if (total < 60) return `${total} min`;
  const hours = Math.floor(total / 60);
  return `${hours} h ${String(total % 60).padStart(2, "0")}`;
}

/** Monday + Sunday → "5 – 11 octobre" or "28 septembre – 4 octobre" */
export function formatWeekRange(monday, sunday) {
  const month = (date) => date.toLocaleDateString(LOCALE, { month: "long" });
  if (monday.getMonth() === sunday.getMonth()) {
    return `${monday.getDate()} – ${sunday.getDate()} ${month(sunday)}`;
  }
  return `${monday.getDate()} ${month(monday)} – ${sunday.getDate()} ${month(sunday)}`;
}

/** Date → "vendredi" */
export function formatWeekday(date) {
  return date.toLocaleDateString(LOCALE, { weekday: "long" });
}

/** "1 restante" / "3 restantes" */
export function plural(count, singular, pluralForm = `${singular}s`) {
  return count === 1 ? singular : pluralForm;
}

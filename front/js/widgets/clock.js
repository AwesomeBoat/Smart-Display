// =====================================================================
// Clock — date and time, the largest thing on the screen
// Stream: /clock/get_time → "HH:MM:SS" every second.
// The date is built here (the stream only sends the time).
// If the stream stops, the browser's own clock takes over:
// a frozen clock is the worst failure on a display.
// =====================================================================

import { h } from "../core/dom.js";
import { formatClock, formatLongDate } from "../core/format.js";

const STREAM_TIMEOUT = 2500; // ms without a tick before we use the local clock

export function createClock(zone) {
  const dateText = h("span", { class: "t-date" });
  const timeText = h("span", { class: "t-clock" });
  const secondsText = h("span", { class: "t-seconds" });

  zone.append(
    h("div", { class: "sd-clock" },
      dateText,
      h("div", { class: "sd-clock-time" }, timeText, secondsText),
    ),
  );

  function render(hhmmss) {
    const [hours, minutes, seconds] = hhmmss.split(":");
    timeText.textContent = `${hours}:${minutes}`;
    secondsText.textContent = seconds;
    dateText.textContent = formatLongDate(new Date());
  }

  // fallback: every second, if the server is silent, show the local time
  let lastTick = 0;
  setInterval(() => {
    if (Date.now() - lastTick > STREAM_TIMEOUT) render(formatClock(new Date()));
  }, 1000);
  render(formatClock(new Date())); // something on screen from the first frame

  return {
    update(hhmmss) {
      lastTick = Date.now();
      render(hhmmss);
    },
  };
}

// =====================================================================
// Weather — "Météo" KPI tile: temperature + wind
// Stream: /weather/get_curr_weather_data → "14.2 | 11.0" (°C | km/h).
// The server sends nothing until its first fetch succeeds: until then the
// tile shows skeleton bars (stale state), never an empty box. If the
// connection drops, the last value stays, dimmed, with its age.
// =====================================================================

import { h, skeleton, setChildren } from "../core/dom.js";
import { icon } from "../core/icons.js";
import { formatNumber } from "../core/format.js";
import { createPanel } from "../core/panel.js";

export function createWeatherTile(zone) {
  const { panel, head, body } = createPanel({ iconName: "thermo", title: "Météo" });
  const staleTag = h("span", { class: "sd-stale-tag t-meta" });
  head.append(staleTag);
  zone.append(panel);

  let receivedAt = null; // when the last value arrived

  function setStale(isStale) {
    panel.classList.toggle("sd-glass--stale", isStale);
    staleTag.textContent = isStale && receivedAt ? ageLabel(receivedAt) : "";
  }

  // first state: nothing received yet
  body.append(...skeleton(["60%", "40%"]));
  setStale(true);

  // refresh the "il y a X min" tag while disconnected
  setInterval(() => {
    if (panel.classList.contains("sd-glass--stale")) setStale(true);
  }, 30 * 1000);

  return {
    update(payload) {
      const [temperature, wind] = payload.split("|").map(part => Number(part.trim()));
      receivedAt = Date.now();
      setChildren(body,
        h("div", { class: "sd-weather" },
          h("span", { class: "sd-weather-icon" }, icon("thermo", "sd-ico sd-ico--lg")),
          h("div", { class: "sd-weather-body" },
            h("span", { class: "t-temp sd-num" }, `${formatNumber(temperature)}°C`),
            h("span", { class: "sd-weather-line t-meta" },
              icon("wind"),
              `Vent ${formatNumber(wind, 0)} km/h`,
            ),
          ),
        ),
      );
      setStale(false);
    },

    /** called by the stream: false = connection lost, true = back */
    setConnected(connected) {
      if (!connected && receivedAt) setStale(true);
    },
  };
}

function ageLabel(since) {
  const minutes = Math.floor((Date.now() - since) / 60000);
  return minutes < 1 ? "à l'instant" : `il y a ${minutes} min`;
}

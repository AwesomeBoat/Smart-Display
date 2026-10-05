// =====================================================================
// display.js — entry point of the display (/display_dashboard)
//
// 1. wait for the active profile's settings: mode (jour / semaine) + theme
// 2. scale the 1920×1080 stage to the real screen
// 3. create each widget in its zone (the zones are placed by display.css)
// 4. route each programme of the display stream to its widgets
// A new theme is applied live; a new mode reloads the page, because the
// two modes don't have the same widgets.
//
// The display is read-only: everything is driven from the phone (/phone).
// =====================================================================

import { openStream } from "./core/sse.js";
import { applyTheme } from "./core/settings.js";
import { createClock } from "./widgets/clock.js";
import { createWeatherTile } from "./widgets/weather.js";
import { createTaskRing, createTasksPanel } from "./widgets/tasks.js";
import { createHabitsPanel, createBestStreakTile } from "./widgets/habits.js";
import { createAgendaDay } from "./widgets/agenda-day.js";
import { createAgendaWeek } from "./widgets/agenda-week.js";
import { createInsight } from "./widgets/insight.js";

const DESIGN_WIDTH = 1920;
const DESIGN_HEIGHT = 1080;

const stage = document.querySelector(".sd-stage");
const zone = name => stage.querySelector(`[data-zone="${name}"]`);

// ONE stream for everything (relative URL: same server as this page).
// The names are the programmes sent by the server (display/stream.py)
const stream = openStream("/display/stream", ["settings", "clock", "weather", "todo", "habits", "calendar"]);

// ---------- 1. Settings (the first message starts the display) ----------
let currentMode = null;

stream.listen("settings", ({ mode, theme }) => {
  applyTheme(theme);
  if (currentMode === null) {
    currentMode = mode;
    startDisplay(mode);
  } else if (mode !== currentMode) {
    window.location.reload(); // other mode = other widgets: start again
  }
});

// ---------- 2. Scale the stage to the screen (keep the ratio, centre it) ----------
function fitStage() {
  const scale = Math.min(window.innerWidth / DESIGN_WIDTH, window.innerHeight / DESIGN_HEIGHT);
  const offsetX = (window.innerWidth - DESIGN_WIDTH * scale) / 2;
  const offsetY = (window.innerHeight - DESIGN_HEIGHT * scale) / 2;
  stage.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
}
fitStage();
window.addEventListener("resize", fitStage);

// ---------- 3 + 4. Widgets and their streams, once the mode is known ----------
function startDisplay(mode) {
  stage.dataset.mode = mode; // display.css places the zones from this
  const isWeek = mode === "semaine";

  // ---------- 3. Widgets ----------
  // Jour:    clock · Météo · Tâches ring · Meilleure série / day timeline / Tasks · Habits · Insight
  // Semaine: clock · Météo · Tâches ring · Insight tile    / week grid    / Habits + Tasks
  const clock = createClock(zone("clock"));
  const weather = createWeatherTile(zone("weather"));
  const taskRing = createTaskRing(zone("task-ring"));
  const tasksPanel = createTasksPanel(zone("tasks"), { showBar: isWeek, maxRows: isWeek ? 3 : 6 });
  const habitsPanel = createHabitsPanel(zone("habits"), { compact: isWeek, maxRows: isWeek ? 4 : 6 });
  const bestStreak = isWeek ? null : createBestStreakTile(zone("best-streak"));
  const agenda = isWeek ? createAgendaWeek(zone("calendar")) : createAgendaDay(zone("calendar"));
  const insight = createInsight(zone("insight"), { variant: isWeek ? "tile" : "panel" });
  insight.update(null); // no insight source yet: shows the motto

  // ---------- 4. Route each programme of the stream to its widget(s) ----------
  stream.listen("clock", clock.update, { json: false });

  stream.listen("weather", weather.update, { json: false });
  stream.watchConnection(weather.setConnected);

  // one programme, two widgets each
  stream.listen("todo", tasks => {
    taskRing.update(tasks);
    tasksPanel.update(tasks);
  });

  stream.listen("habits", habits => {
    habitsPanel.update(habits);
    bestStreak?.update(habits);
  });

  stream.listen("calendar", agenda.update);
}

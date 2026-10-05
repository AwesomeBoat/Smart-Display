// =====================================================================
// phone.js — the remote control (/phone)
// Each phone works on ITS profile (saved in localStorage) and can choose
// which profile the display shows. Every list comes from an SSE stream,
// so a change made on any device shows up here by itself.
// All URLs are relative: the browser adds the address of the server.
// =====================================================================

import { h, cx, setChildren } from "./core/dom.js";
import { icon } from "./core/icons.js";
import { NNBSP } from "./core/format.js";
import { applyTheme } from "./core/settings.js";

const message = document.getElementById("message");

// ---------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------

/** Send a request; on failure show the error in words and return null */
async function callApi(url, options) {
  message.textContent = "";
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      message.textContent = `Erreur ${response.status} : ${error.detail ?? "requête refusée"}`;
      return null;
    }
    // 204 = success with no body (ex: delete_profile), nothing to parse
    if (response.status === 204) return true;
    return await response.json();
  } catch {
    message.textContent = "Serveur injoignable";
    return null;
  }
}

/**
 * Follow one SSE stream at a time: opening a new one closes the previous
 * (else each profile switch would stack one more stream).
 * Only calls `render` when the payload changed.
 */
function createStream(render) {
  let source = null;
  let lastPayload = "";
  return {
    open(url) {
      source?.close();
      lastPayload = "";
      source = new EventSource(url);
      source.onmessage = (event) => {
        if (event.data === lastPayload) return;
        lastPayload = event.data;
        render(JSON.parse(event.data));
      };
    },
  };
}

/** Small ghost icon button (delete...) */
function iconButton(iconName, label, onClick, extraClass = "") {
  const button = h("button", { class: cx("sd-btn sd-btn--ghost sd-btn--icon", extraClass), type: "button", "aria-label": label },
    icon(iconName));
  button.onclick = onClick;
  return button;
}

// ---------------------------------------------------------------------
// Tasks
// ---------------------------------------------------------------------

const taskList = document.getElementById("taskList");
const taskCount = document.getElementById("taskCount");
const taskForm = document.getElementById("taskForm");
const taskInput = document.getElementById("taskInput");
const taskStream = createStream(renderTasks);

taskForm.onsubmit = async (event) => {
  event.preventDefault();
  if (!profileId) return;
  const result = await callApi(`/todo/add_task/${profileId}`, { method: "POST", body: new FormData(taskForm) });
  if (result) taskInput.value = "";
};

function renderTasks(tasks) {
  const done = tasks.filter(task => task.done).length;
  taskCount.textContent = tasks.length ? `${done} / ${tasks.length} validées` : "";
  setChildren(taskList, tasks.map(taskRow));
}

function taskRow(task) {
  // the check ring is the toggle button
  const check = h("button", {
      class: cx("sd-check", task.done && "sd-check--done"),
      type: "button",
      role: "checkbox",
      "aria-checked": task.done ? "true" : "false",
      "aria-label": task.name,
    },
    icon("check", ""),
  );
  check.onclick = () => callApi(`/todo/toggle_task/${task.id}`, { method: "PATCH" });

  return h("li", { class: cx("sd-prow", task.done && "sd-row--done") },
    check,
    h("span", { class: "sd-label t-phone-body" }, task.name),
    iconButton("trash", `Supprimer ${task.name}`, () =>
      callApi(`/todo/delete_task/${task.id}`, { method: "DELETE" })),
  );
}

// ---------------------------------------------------------------------
// Habits
// ---------------------------------------------------------------------

const habitList = document.getElementById("habitList");
const habitForm = document.getElementById("habitForm");
const habitInput = document.getElementById("habitInput");
const habitStream = createStream(renderHabits);

habitForm.onsubmit = async (event) => {
  event.preventDefault();
  if (!profileId) return;
  const result = await callApi(`/habits/add_habit/${profileId}`, { method: "POST", body: new FormData(habitForm) });
  if (result) habitInput.value = "";
};

function renderHabits(habits) {
  setChildren(habitList, habits.map(habitRow));
}

/** true / false when the stream says if today is logged, null otherwise */
function isDoneToday(habit) {
  if (typeof habit.done_today === "boolean") return habit.done_today;
  const today = (new Date().getDay() + 6) % 7; // Monday = 0
  if (Array.isArray(habit.week) && habit.week.length > today) return Boolean(habit.week[today]);
  return null;
}

function habitRow(habit) {
  const doneToday = isDoneToday(habit);

  const markDone = h("button", { class: "sd-btn", type: "button" }, "Fait");
  markDone.onclick = () => callApi(`/habits/add_log/${habit.id}`, { method: "POST" });

  const undo = h("button", { class: "sd-btn sd-btn--ghost", type: "button" }, icon("undo"), "Annuler");
  undo.onclick = () => callApi(`/habits/delete_today_log/${habit.id}`, { method: "DELETE" });

  // deleting a habit loses its whole history: ask first
  const remove = iconButton("trash", `Supprimer ${habit.name}`, () => {
    if (confirm(`Supprimer "${habit.name}" et tout son historique ?`)) {
      callApi(`/habits/delete_habit/${habit.id}`, { method: "DELETE" });
    }
  }, "sd-btn--danger");

  return h("li", { class: "sd-prow" },
    h("span", { class: cx("sd-check", doneToday && "sd-check--done") }, icon("check", "")),
    h("span", { class: "sd-label" },
      h("span", { class: "t-phone-body" }, habit.name), h("br"),
      h("span", { class: "t-phone-small sd-muted" }, `Série : ${habit.streak} j`),
    ),
    // "Fait" when today isn't logged, "Annuler" when it is (both if unknown)
    doneToday !== true && markDone,
    doneToday !== false && undo,
    remove,
  );
}

// ---------------------------------------------------------------------
// Profiles
// ---------------------------------------------------------------------

const profileSelect = document.getElementById("profileSelect");
const profileAvatar = document.getElementById("profileAvatar");
const displayStatus = document.getElementById("displayStatus");
const profileDetails = document.getElementById("profileDetails");
const profileForm = document.getElementById("profileForm");
const modeSelect = document.getElementById("modeSelect");
const themeSelect = document.getElementById("themeSelect");

let profileId = null;   // this phone's profile, always a string (select / localStorage)
let profiles = [];      // last list received from the server

function useProfile(id) {
  profileId = id;
  localStorage.setItem("profileId", id);
  taskStream.open(`/todo/stream_tasks/${id}`);
  habitStream.open(`/habits/stream_habits/${id}`);
  renderProfileCard();
}

/** Profile card: mode/theme selects, avatar letter (glowing if on the display), "Sur l'écran : X" */
function renderProfileCard() {
  const current = profiles.find(profile => String(profile.id) === profileId);
  const active = profiles.find(profile => profile.active);

  // display settings of this phone's profile; the phone takes its theme too
  if (current) {
    modeSelect.value = current.display_mode;
    themeSelect.value = current.theme;
    applyTheme(current.theme);
  }

  profileAvatar.textContent = current ? current.name.charAt(0).toUpperCase() : "";
  profileAvatar.classList.toggle("sd-avatar--active", Boolean(current?.active));

  setChildren(displayStatus,
    active && [icon("screen"), `Sur l'écran${NNBSP}: `, h("span", { class: "sd-accent" }, active.name)],
  );
}

/** (Re)build the select from the server, at start and after each profile change */
async function loadProfiles() {
  const result = await callApi("/profile/get_all_profiles");
  if (!result) return;
  profiles = result;

  if (!profiles.length) {
    setChildren(profileSelect);
    message.textContent = "Aucun profil";
    return;
  }
  setChildren(profileSelect, profiles.map(profile =>
    h("option", { value: profile.id }, profile.active ? `${profile.name} (écran)` : profile.name)));

  // keep the current profile, else the saved one; it may have been deleted → the first one
  const wanted = profileId ?? localStorage.getItem("profileId");
  const exists = profiles.some(profile => String(profile.id) === wanted);
  const id = exists ? wanted : String(profiles[0].id);
  profileSelect.value = id;

  // only restart the streams if the profile really changed
  if (id !== profileId) useProfile(id);
  else renderProfileCard();
}

profileSelect.onchange = () => useProfile(profileSelect.value);

// change how the display looks for this phone's profile
async function saveDisplaySettings() {
  const body = new FormData();
  body.append("display_mode", modeSelect.value);
  body.append("theme", themeSelect.value);
  const result = await callApi(`/profile/set_display/${profileId}`, { method: "PATCH", body });
  if (result) loadProfiles();
}
modeSelect.onchange = saveDisplaySettings;
themeSelect.onchange = saveDisplaySettings;

// show this phone's profile on the display
document.getElementById("showOnDisplayBtn").onclick = async () => {
  const result = await callApi(`/profile/set_active/${profileId}`, { method: "PATCH" });
  if (result) loadProfiles();
};

// the server refuses (409) to delete the profile on the display: callApi shows why
document.getElementById("deleteProfileBtn").onclick = async () => {
  const name = profiles.find(profile => String(profile.id) === profileId)?.name;
  if (!confirm(`Supprimer le profil "${name}" avec toutes ses tâches et habitudes ?`)) return;
  const result = await callApi(`/profile/delete_profile/${profileId}`, { method: "DELETE" });
  if (result) loadProfiles();
};

// create a profile and switch this phone to it
profileForm.onsubmit = async (event) => {
  event.preventDefault();
  const result = await callApi("/profile/create_profile", { method: "POST", body: new FormData(profileForm) });
  if (result) {
    profileForm.reset();
    profileDetails.open = false;
    localStorage.setItem("profileId", String(result.id));
    profileId = null; // force loadProfiles to switch to the saved (new) one
    await loadProfiles();
  }
};

loadProfiles();

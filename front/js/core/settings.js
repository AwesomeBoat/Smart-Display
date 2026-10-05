// =====================================================================
// settings.js — display mode and colour theme
// They are per-profile settings, chosen from the phone and streamed by
// /profile/get_curr_display → {"mode": "jour", "theme": "glacier"}
// The display follows the active profile.
// =====================================================================

/** Themes change colours only: they are applied with data-theme on <html> */
export function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
}

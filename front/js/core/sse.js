// =====================================================================
// sse.js — the display's single Server-Sent Events stream
// The display opens ONE stream (/display/stream) that carries every widget,
// each message tagged with its widget name ("event: clock"). A browser keeps
// at most 6 connections per server, so one stream per widget was too many.
// The browser's EventSource reconnects by itself if the server restarts.
// =====================================================================

/**
 * openStream(url, eventNames) → { listen, watchConnection }
 * The last message of each event is kept, so a widget created a bit later
 * (once the display mode is known) still gets what arrived before it.
 */
export function openStream(url, eventNames) {
  const source = new EventSource(url);
  const latest = new Map();   // event name → last raw payload received
  const handlers = new Map(); // event name → the widget callback

  for (const name of eventNames) {
    source.addEventListener(name, (event) => {
      latest.set(name, event.data);
      handlers.get(name)?.(event.data);
    });
  }

  return {
    /**
     * listen(name, onData, { json })
     * onData gets the parsed payload, only when it changed (the server
     * repeats the same data every second or so). json: false for plain text.
     */
    listen(name, onData, { json = true } = {}) {
      let lastPayload = null;
      const handle = (raw) => {
        if (raw === lastPayload) return; // same data as before: nothing to redraw
        lastPayload = raw;
        onData(json ? JSON.parse(raw) : raw);
      };
      handlers.set(name, handle);
      if (latest.has(name)) handle(latest.get(name)); // replay what arrived before
    },

    /** onConnection(true) when the stream (re)connects, false when it drops */
    watchConnection(onConnection) {
      source.addEventListener("open", () => onConnection(true));
      source.addEventListener("error", () => onConnection(false));
    },
  };
}

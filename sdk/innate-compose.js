// Records the `challenge` field as InputEvent {t, kind, n, cls} for phones (Gboard/iOS use composition, keydown = 229).
// No content is stored: only the length change, event kind, character class. A Telex/VNI transform key = key with n = 0 (length unchanged).
// NOT yet tried on a real device: the behavior below follows the Input Events/IME spec and must be checked with sdk/probe.html (see docs/plan/innate-challenge-vi.md).
(function (root) {
  const cls = (c) => (/\d/.test(c) ? "digit" : /\s/.test(c) ? "space" : /\p{L}/u.test(c) ? "letter" : "symbol");

  function createRecorder(el, now = () => performance.now()) {
    const events = [];
    let len = el.value.length, t0 = null, keyCls = null;
    const push = (kind, n, c) => { t0 ??= now(); events.push({ t: Math.round(now() - t0), kind, n, cls: c ?? null }); };

    const onKeydown = (e) => { keyCls = e.keyCode === 229 || e.key === "Process" || e.key === "Unidentified" ? null : e.key.length === 1 ? cls(e.key) : null; };
    const onInput = (e) => {
      const d = el.value.length - len;
      len = el.value.length;
      const type = e.inputType || "";
      if (/^insertFromPaste|^insertFromDrop|^insertReplacementText|^insertFromYank/.test(type) || d > 1) push("paste", Math.max(d, 0));
      else if (d < 0 || /^delete/.test(type)) push("delete", Math.abs(d));
      else if (d === 1) push("key", 1, el.value.length ? cls(el.value[el.value.length - 1]) : null);
      else push("key", 0, keyCls); // d === 0: the IME changed text already typed (circumflex/horn/tone mark). On a phone the key is unknown -> cls null
      keyCls = null;
    };
    el.addEventListener("keydown", onKeydown);
    el.addEventListener("input", onInput);
    return {
      // called on submit: value changed without an input event (assigned by script / ACTION_SET_TEXT) => set_text
      finish() {
        if (el.value.length !== len) { push("set_text", Math.abs(el.value.length - len)); len = el.value.length; }
        el.removeEventListener("keydown", onKeydown); el.removeEventListener("input", onInput);
        return { name: "challenge", expected_len: undefined, events };
      },
      events,
    };
  }
  const api = { createRecorder };
  if (typeof module !== "undefined") module.exports = api; else root.InnateCompose = api;
})(typeof window !== "undefined" ? window : globalThis);

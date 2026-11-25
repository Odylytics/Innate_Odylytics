const test = require("node:test");
const assert = require("node:assert");
const { createRecorder } = require("./innate-compose.js");

function fakeEl() {
  const h = {};
  return { value: "", addEventListener: (n, f) => (h[n] = f), removeEventListener() {}, fire: (n, e = {}) => h[n](e) };
}
// mô phỏng chuỗi sự kiện Gboard Telex: keydown 229 + input (insertCompositionText); giá trị là TOÀN BỘ chuỗi đang soạn
function gboard(steps) {
  let clock = 0;
  const el = fakeEl(), rec = createRecorder(el, () => (clock += 120));
  for (const v of steps) { el.fire("keydown", { keyCode: 229, key: "Unidentified" }); el.value = v; el.fire("input", { inputType: "insertCompositionText" }); }
  return rec;
}

test("Gboard Telex: 'tr','o','w'->ơ,'f'->ờ,'i' cho ra hai phím biến đổi n=0", () => {
  const rec = gboard(["t", "tr", "tro", "trơ", "trờ", "trời"]);
  assert.deepStrictEqual(rec.events.map((e) => e.n), [1, 1, 1, 0, 0, 1]);
  assert.ok(rec.events.every((e) => e.kind === "key"));
  assert.strictEqual(rec.events[3].cls, null); // điện thoại không thấy phím: không đoán Telex/VNI
});

test("dán và chọn gợi ý thành 'paste', xoá thành 'delete'", () => {
  const el = fakeEl(), rec = createRecorder(el, () => 1);
  el.value = "hom nay"; el.fire("input", { inputType: "insertFromPaste" });
  el.value = "hom na"; el.fire("input", { inputType: "deleteContentBackward" });
  el.value = "hom nay troi"; el.fire("input", { inputType: "insertReplacementText" });
  assert.deepStrictEqual(rec.events.map((e) => [e.kind, e.n]), [["paste", 7], ["delete", 1], ["paste", 6]]);
});

test("gán value bằng script (không có sự kiện input) bị phát hiện là set_text khi gửi", () => {
  const el = fakeEl(), rec = createRecorder(el, () => 1);
  el.value = "hom nay troi dep qua";
  const f = rec.finish();
  assert.deepStrictEqual(f.events.map((e) => [e.kind, e.n]), [["set_text", 20]]);
});

test("bàn phím desktop (keydown có key): phím biến đổi mang lớp ký tự, VNI = digit", () => {
  let c = 0; const el = fakeEl(), rec = createRecorder(el, () => (c += 100));
  el.fire("keydown", { keyCode: 79, key: "o" }); el.value = "o"; el.fire("input", { inputType: "insertText" });
  el.fire("keydown", { keyCode: 54, key: "6" }); el.value = "ô"; el.fire("input", { inputType: "insertText" });
  assert.deepStrictEqual(rec.events.map((e) => [e.n, e.cls]), [[1, "letter"], [0, "digit"]]);
});

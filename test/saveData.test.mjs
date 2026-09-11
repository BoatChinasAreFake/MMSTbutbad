import { test } from "node:test";
import assert from "node:assert/strict";
import {
    normColor, sanitizeProvinceList, sanitizeCountry, sanitizeState, isPlainObject
} from "../lib/saveData.mjs";

test("normColor accepts valid triples and byte-clamps", () => {
    assert.deepEqual(normColor([10, 20, 30]), [10, 20, 30]);
    assert.deepEqual(normColor([300, -1, 256]), [300 & 255, -1 & 255, 256 & 255]);
});

test("normColor rejects malformed colours -> neutral grey", () => {
    assert.deepEqual(normColor("notacolor"), [150, 150, 150]);
    assert.deepEqual(normColor([1, 2]), [150, 150, 150]);
    assert.deepEqual(normColor([1, 2, NaN]), [150, 150, 150]);
    assert.deepEqual(normColor(null), [150, 150, 150]);
    assert.deepEqual(normColor(undefined), [150, 150, 150]);
});

test("sanitizeProvinceList keeps only finite numbers", () => {
    assert.deepEqual(sanitizeProvinceList([1, 2, "3", "x", null]), [1, 2, "3"]);
    assert.deepEqual(sanitizeProvinceList("nope"), []);
    assert.deepEqual(sanitizeProvinceList(undefined), []);
});

test("sanitizeCountry fills safe defaults and never trusts persisted spines", () => {
    const c = sanitizeCountry("ABC", { name: "Abcland", color: [1, 2, 3], spines: [{ spine: [] }] });
    assert.equal(c.tag, "ABC");
    assert.equal(c.name, "Abcland");
    assert.deepEqual(c.color, [1, 2, 3]);
    assert.equal(c.curvatureScale, 1.0);
    assert.equal(c.spines, null); // spine geometry is always recomputed
});

test("sanitizeCountry coerces bad fields", () => {
    const c = sanitizeCountry("BAD", { name: 123, color: "x", labelRotation: "junk" });
    assert.equal(c.name, "BAD");          // non-string name -> tag fallback
    assert.deepEqual(c.color, [150, 150, 150]);
    assert.equal(c.labelRotation, 0);
});

test("sanitizeCountry rejects non-object entries", () => {
    assert.equal(sanitizeCountry("X", null), null);
    assert.equal(sanitizeCountry("X", "string"), null);
});

test("sanitizeState handles bad province lists without throwing", () => {
    const good = sanitizeState("7", { name: "Good", color: [1, 2, 3], provinces: [100, 101] });
    assert.equal(good.id, 7);
    assert.deepEqual(good.record.provinces, [100, 101]);

    const bad = sanitizeState("x", { name: "S", provinces: "nope" });
    assert.equal(bad, null); // non-finite id -> skipped

    const badProv = sanitizeState("9", { provinces: "nope" });
    assert.deepEqual(badProv.record.provinces, []); // non-array -> empty, no throw
    assert.equal(badProv.record.name, "State 9");
});

test("isPlainObject", () => {
    assert.equal(isPlainObject({}), true);
    assert.equal(isPlainObject([]), false);
    assert.equal(isPlainObject(null), false);
    assert.equal(isPlainObject("x"), false);
});

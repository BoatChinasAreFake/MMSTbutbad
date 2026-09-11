import { test } from "node:test";
import assert from "node:assert/strict";
import {
    encodeProvinceId, decodeProvinceId, WHITE_SENTINEL,
    isPointInPolygon, resamplePath,
    splitIntoTwoLines, escapeHoverText, normalizeDisplayName,
    normOwner
} from "../lib/pure.mjs";

test("encode/decode province id round-trips", () => {
    for (const id of [1, 255, 256, 65535, 65536, 21316, 16000000]) {
        const [r, g, b] = encodeProvinceId(id);
        assert.equal(decodeProvinceId(r, g, b), id);
    }
});

test("decodeProvinceId maps the pure-white sentinel to 0", () => {
    assert.equal(decodeProvinceId(255, 255, 255), 0);
    assert.equal(WHITE_SENTINEL, 16777215);
});

test("isPointInPolygon: inside vs outside of a square", () => {
    const square = [{ x: 0, y: 0 }, { x: 10, y: 0 }, { x: 10, y: 10 }, { x: 0, y: 10 }];
    assert.equal(isPointInPolygon({ x: 5, y: 5 }, square), true);
    assert.equal(isPointInPolygon({ x: 15, y: 5 }, square), false);
    assert.equal(isPointInPolygon({ x: -1, y: -1 }, square), false);
});

test("isPointInPolygon: concave (C-shaped) polygon excludes the notch", () => {
    // A C shape opening to the right; the notch center should be OUTSIDE.
    const c = [
        { x: 0, y: 0 }, { x: 10, y: 0 }, { x: 10, y: 3 }, { x: 3, y: 3 },
        { x: 3, y: 7 }, { x: 10, y: 7 }, { x: 10, y: 10 }, { x: 0, y: 10 }
    ];
    assert.equal(isPointInPolygon({ x: 1, y: 5 }, c), true);   // in the spine
    assert.equal(isPointInPolygon({ x: 7, y: 5 }, c), false);  // in the notch
});

test("resamplePath returns exactly `count` points with stable endpoints", () => {
    const path = [[0, 0], [10, 0], [10, 10]];
    const out = resamplePath(path, 5);
    assert.equal(out.length, 5);
    assert.deepEqual(out[0], [0, 0]);
    const last = out[out.length - 1];
    assert.ok(Math.abs(last[0] - 10) < 1e-9 && Math.abs(last[1] - 10) < 1e-9);
});

test("resamplePath spaces points evenly by arc length", () => {
    const path = [[0, 0], [8, 0]]; // straight line, length 8
    const out = resamplePath(path, 5); // steps of 2
    assert.deepEqual(out.map(p => Math.round(p[0])), [0, 2, 4, 6, 8]);
});

test("splitIntoTwoLines balances words", () => {
    assert.deepEqual(splitIntoTwoLines("UNITED STATES"), ["UNITED", "STATES"]);
    assert.deepEqual(splitIntoTwoLines("SOLO"), ["SOLO", ""]);
    const [a, b] = splitIntoTwoLines("PEOPLES REPUBLIC OF CHINA");
    assert.ok(a.length > 0 && b.length > 0);
    assert.equal(a + " " + b, "PEOPLES REPUBLIC OF CHINA");
});

test("escapeHoverText escapes HTML-significant characters", () => {
    assert.equal(escapeHoverText('<b>"A&B"</b>'), "&lt;b&gt;&quot;A&amp;B&quot;&lt;/b&gt;");
    assert.equal(escapeHoverText(42), "42");
});

test("normalizeDisplayName collapses placeholders to the tag and upper-cases", () => {
    assert.equal(normalizeDisplayName("France", "FRA"), "FRANCE");
    assert.equal(normalizeDisplayName("placeholder nation", "XYZ"), "XYZ");
});

test("normOwner normalizes falsy tags to null", () => {
    assert.equal(normOwner("FRA"), "FRA");
    assert.equal(normOwner(""), null);
    assert.equal(normOwner(undefined), null);
});

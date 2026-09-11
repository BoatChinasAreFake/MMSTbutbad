// Pure, dependency-free helpers shared by the app and the test suite.
//
// Everything here is free of DOM, WebGL, and module-global state so it can be
// unit-tested in Node and reasoned about in isolation. The browser app imports
// these; the test harness (test/*.test.mjs) imports the same source.

// --- Province ID <-> RGB encoding -----------------------------------------
// Province ids are packed into an RGB pixel as id = R + G*256 + B*65536.
// Pure white (0xFFFFFF) is the ocean/border sentinel and decodes to 0.

export const WHITE_SENTINEL = 0xffffff; // 16777215

export function encodeProvinceId(id) {
    return [id & 255, (id >> 8) & 255, (id >> 16) & 255];
}

export function decodeProvinceId(r, g, b) {
    const id = r + g * 256 + b * 65536;
    return id === WHITE_SENTINEL ? 0 : id;
}

// --- Geometry --------------------------------------------------------------

// Even-odd ray-casting point-in-polygon test. `poly` is an array of {x, y}.
export function isPointInPolygon(pt, poly) {
    let x = pt.x, y = pt.y;
    let inside = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
        let xi = poly[i].x, yi = poly[i].y;
        let xj = poly[j].x, yj = poly[j].y;
        let intersect = ((yi > y) !== (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi || 1) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

// Resample a polyline (array of [x, y]) to exactly `count` evenly-spaced points
// by arc length. NOTE: this is also serialized into the label Web Worker via
// Function.prototype.toString(), so it must stay self-contained (no closures /
// external references).
export function resamplePath(path, count) {
    const lengths = [0];

    for (let i = 1; i < path.length; i++) {
        const dx = path[i][0] - path[i - 1][0];
        const dy = path[i][1] - path[i - 1][1];
        lengths[i] = lengths[i - 1] + Math.hypot(dx, dy);
    }

    const total = lengths[lengths.length - 1];
    const step = total / (count - 1);

    const result = [];
    let j = 0;

    for (let i = 0; i < count; i++) {
        const target = i * step;

        while (j < lengths.length - 2 && lengths[j + 1] < target) j++;

        const t = (target - lengths[j]) / (lengths[j + 1] - lengths[j] || 1);

        const x = path[j][0] * (1 - t) + path[j + 1][0] * t;
        const y = path[j][1] * (1 - t) + path[j + 1][1] * t;

        result.push([x, y]);
    }

    return result;
}

// --- Label text ------------------------------------------------------------

// Balance a multi-word label into two lines with the most even character split.
export function splitIntoTwoLines(text) {
    const words = text.trim().split(/\s+/);
    if (words.length < 2) return [text, ""];

    let bestSplit = 1;
    let minDiff = Infinity;
    for (let i = 1; i < words.length; i++) {
        const part1 = words.slice(0, i).join(" ");
        const part2 = words.slice(i).join(" ");
        const diff = Math.abs(part1.length - part2.length);
        if (diff < minDiff) {
            minDiff = diff;
            bestSplit = i;
        }
    }
    return [
        words.slice(0, bestSplit).join(" "),
        words.slice(bestSplit).join(" ")
    ];
}

// Escape a string for safe insertion into HTML (used by the hover tooltip).
export function escapeHoverText(s) {
    return String(s).replace(/[&<>"]/g, ch => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"
    }[ch]));
}

// Normalize a country name for on-map display: placeholders collapse to the
// tag, everything else is upper-cased.
export function normalizeDisplayName(name, tag) {
    let textVal = name;
    if (textVal.toLowerCase().includes("placeholder")) {
        textVal = tag;
    }
    return textVal.toUpperCase();
}

// --- Ownership -------------------------------------------------------------

export function normOwner(tag) {
    return tag ? tag : null;
}

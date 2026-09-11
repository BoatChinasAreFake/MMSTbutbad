// Pure validation/sanitisation for loaded save files.
//
// Save files may be hand-edited or produced by older versions, so every value
// is treated as untrusted. These helpers never throw on bad input; they coerce
// to safe defaults. Extracted from applyLoadedSaveData() so the rules can be
// unit-tested in isolation.

const NEUTRAL_GREY = [150, 150, 150];

// Accept only a valid [r, g, b] triple (byte-clamped); otherwise neutral grey,
// so a malformed colour can never corrupt the shader LUT.
export function normColor(col) {
    if (Array.isArray(col) && col.length >= 3 &&
        col.slice(0, 3).every(n => typeof n === "number" && isFinite(n))) {
        return [col[0] & 255, col[1] & 255, col[2] & 255];
    }
    return NEUTRAL_GREY.slice();
}

// Keep only entries that are a finite number or a numeric string. Values like
// null, "", [], false coerce to 0 via Number() and must NOT be treated as a
// province id, so they are filtered out explicitly.
export function sanitizeProvinceList(v) {
    if (!Array.isArray(v)) return [];
    return v.filter(p => {
        if (typeof p === "number") return Number.isFinite(p);
        if (typeof p === "string" && p.trim() !== "") return Number.isFinite(Number(p));
        return false;
    });
}

// Build a normalized country record from an untrusted save entry.
export function sanitizeCountry(tag, c) {
    if (!c || typeof c !== "object") return null;
    const num = (v, d) => (v !== undefined ? (Number(v) || d) : d);
    return {
        tag,
        name: (typeof c.name === "string" && c.name) ? c.name : tag,
        fullName: typeof c.fullName === "string" ? c.fullName : "",
        color: normColor(c.color),
        labelOffset: Number(c.labelOffset) || 0,
        labelXOffset: Number(c.labelXOffset) || 0,
        labelArcShift: Number(c.labelArcShift) || 0,
        curvatureScale: num(c.curvatureScale, 1.0),
        fontSizeScale: num(c.fontSizeScale, 1.0),
        labelRotation: Number(c.labelRotation) || 0,
        labelStretch: num(c.labelStretch, 1.0),
        // Spines are recomputed from scratch by the worker; never trust
        // persisted geometry (it may be stale for the loaded territory).
        spines: null
    };
}

// Build a normalized state record. Returns { id, record } or null if invalid.
export function sanitizeState(stateIdStr, s) {
    if (!s || typeof s !== "object") return null;
    const stateId = parseInt(stateIdStr);
    if (!Number.isFinite(stateId)) return null;
    const provinces = sanitizeProvinceList(s.provinces);
    return {
        id: stateId,
        record: {
            id: stateId,
            name: (typeof s.name === "string" && s.name) ? s.name : ("State " + stateId),
            color: normColor(s.color),
            controlStrength: s.controlStrength !== undefined ? (Number(s.controlStrength) || 100) : 100,
            showGradient: !!s.showGradient,
            provinces
        }
    };
}

export function isPlainObject(v) {
    return !!v && typeof v === "object" && !Array.isArray(v);
}

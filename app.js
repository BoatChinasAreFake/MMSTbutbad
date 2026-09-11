
const canvas = document.getElementById("mapCanvas");
const overlayCanvas = document.getElementById("overlayCanvas");
const overlayCtx = overlayCanvas.getContext("2d");
const debugPanel = document.getElementById("debugPanel");

const baseCanvas = document.createElement("canvas");
const baseCtx = baseCanvas.getContext("2d");

const DEBUG = {
    axis: false,
    bezier: false,
    points: false,
    panel: true
};

const img = new Image();
const indexImg = new Image();
const heightmapImg = new Image();
let meta = null;
let hasHeightmap = false;
let showHeightmap = 1.0;
let presetData = null;
let statesData = null;

let zoom = 1;
let offsetX = 0.0;
let offsetY = 0.0;
let isPanning = false;
let startPanX = 0;
let startPanY = 0;
let startOffsetX = 0;
let startOffsetY = 0;

let ownership = {};
let interests = {}; // countryTag -> { provinceId: level (1-10) }
let activeMapmode = "political"; // "political" or "interest"
let straits = [];
let straitAdj = {};
let showStraits = false;
let provinceKeys = [];
const labelCache = {};
const labelGenerationQueue = new Set();
const provinceCenters = {};
const provinceNeighbors = {};
const dirtyCountries = new Set();

let selectionLevel = "province";
let hoi4Data = null;
let states = {};
let provinceToState = {};
let eraserMode = false;
let definitions = {};
const colorToId = {};
let basePixels = null;
let profileData = { frameCount: 0, webglSum: 0, overlaySum: 0, labelSum: 0, totalSum: 0, lastTime: performance.now() };
let lastSpikeData = null;
let deferredWorkerResponses = [];
let currentMouseX = 0, currentMouseY = 0;

// ---------------------------------------------------------------------------
// Unsaved-changes protection: dirty tracking, autosave, and a save-status badge.
// Editing a map represents real user effort, so guard against accidental loss.
// ---------------------------------------------------------------------------
let appReady = false;          // becomes true once the initial load finishes
let documentDirty = false;     // true when there are edits not yet persisted
let lastAutosaveAt = 0;
const AUTOSAVE_INTERVAL_MS = 30000;   // periodic autosave cadence
const AUTOSAVE_DEBOUNCE_MS = 4000;    // quiet period after an edit before autosaving
const AUTOSAVE_KEY = "mappa_mundi_autosave";
let autosaveDebounceTimer = null;

function markDirty() {
    // Ignore mutations that happen during initial load / data restore.
    if (!appReady) return;
    if (!documentDirty) {
        documentDirty = true;
        updateSaveStatusBadge();
    }
    // Debounced autosave so a burst of edits only writes once when it settles.
    if (autosaveDebounceTimer) clearTimeout(autosaveDebounceTimer);
    autosaveDebounceTimer = setTimeout(runAutosave, AUTOSAVE_DEBOUNCE_MS);
}

function markSaved() {
    documentDirty = false;
    updateSaveStatusBadge();
}

function runAutosave() {
    if (!appReady || !documentDirty) return;
    try {
        const data = getWorldPresetData();
        data.saveDate = new Date().toISOString();
        data.autosave = true;
        localStorage.setItem(AUTOSAVE_KEY, JSON.stringify(data));
        lastAutosaveAt = Date.now();
        updateSaveStatusBadge();
    } catch (e) {
        // Storage may be full or blocked; fail quietly, the badge still warns.
        console.warn("Autosave failed:", e);
    }
}

function updateSaveStatusBadge() {
    const badge = document.getElementById("saveStatusBadge");
    if (!badge) return;
    if (documentDirty) {
        let txt = "\u25CF Unsaved changes";
        if (lastAutosaveAt) {
            const t = new Date(lastAutosaveAt);
            const hh = String(t.getHours()).padStart(2, "0");
            const mm = String(t.getMinutes()).padStart(2, "0");
            txt += ` \u00B7 autosaved ${hh}:${mm}`;
        }
        badge.textContent = txt;
        badge.className = "save-badge dirty";
        badge.title = "You have changes that are not saved to preset_ownership.json. Use Save Presets (Ctrl+S) to persist them.";
    } else {
        badge.textContent = "\u2713 All changes saved";
        badge.className = "save-badge clean";
        badge.title = "All changes are saved.";
    }
}

// Offer to recover a newer browser autosave than the file preset on load.
function maybeOfferAutosaveRecovery() {
    let raw;
    try { raw = localStorage.getItem(AUTOSAVE_KEY); } catch (e) { return; }
    if (!raw) return;
    let data;
    try { data = JSON.parse(raw); } catch (e) { return; }
    if (!data || !data.saveDate) return;

    const when = new Date(data.saveDate);
    if (isNaN(when.getTime())) return;

    const ownedCount = data.ownership ? Object.keys(data.ownership).length : 0;
    const ok = confirm(
        `A browser autosave from ${when.toLocaleString()} was found ` +
        `(${ownedCount} owned provinces).\n\n` +
        `Restore it? Choose Cancel to keep the currently loaded map.`
    );
    if (ok) {
        applyLoadedSaveData(data);
        markSaved();
        showToast("Recovered autosave from " + when.toLocaleTimeString());
    }
}

window.addEventListener("beforeunload", (e) => {
    if (documentDirty) {
        e.preventDefault();
        e.returnValue = "";   // triggers the browser's native "leave site?" prompt
        return "";
    }
});

setInterval(runAutosave, AUTOSAVE_INTERVAL_MS);

let COLORS = {
    yellow: [255,255,0],
    red: [255,0,0],
    blue: [0,120,255],
    green: [0,200,0]
};

const BASE_COUNTRY_PRESETS = {};

let countries = {
    yellow: {
        tag: "YLW",
        name: "Yellow",
        color: [255,255,0],
        provinces: new Set()
    },
    red: {
        tag: "RED",
        name: "Red",
        color: [255,0,0],
        provinces: new Set()
    },
    blue: {
        tag: "BLU",
        name: "Blue",
        color: [0,120,255],
        provinces: new Set()
    },
    green: {
        tag: "GRN",
        name: "Green",
        color: [0,200,0],
        provinces: new Set()
    }
};

let selectedColor = "yellow";
let useOfficialNames = false;
let alwaysShowSmallCountryLabels = false;

function selectCountry(tag) {
    selectedColor = tag;
    eraserMode = false;
    
    const eraserBtn = document.getElementById("btnEraser");
    if (eraserBtn) {
        eraserBtn.style.background = "#333";
    }
    
    // Highlight the selected country in the list
    const items = document.querySelectorAll(".country-item");
    items.forEach(item => {
        if (item.dataset.tag === tag) {
            item.style.border = "2px solid white";
            item.style.background = "#333";
            item.scrollIntoView({ behavior: "smooth", block: "nearest" });
        } else {
            item.style.border = "1px solid #333";
            item.style.background = "#222";
        }
    });

    // Update Country Options panel
    const activeTagLabel = document.getElementById("activeCountryTag");
    if (activeTagLabel) {
        activeTagLabel.textContent = tag;
    }
    const editNameInput = document.getElementById("editCountryName");
    if (editNameInput) {
        editNameInput.value = countries[tag] ? countries[tag].name : "";
    }
    const editFullNameInput = document.getElementById("editCountryFullName");
    if (editFullNameInput) {
        editFullNameInput.value = (countries[tag] && countries[tag].fullName) ? countries[tag].fullName : "";
    }
    const editOffsetSlider = document.getElementById("labelOffsetSlider");
    const editOffsetDisp = document.getElementById("labelOffsetDisp");
    if (editOffsetSlider && editOffsetDisp) {
        const offset = (countries[tag] && countries[tag].labelOffset) || 0;
        editOffsetSlider.value = offset;
        editOffsetDisp.textContent = offset;
    }
    const editXOffsetSlider = document.getElementById("labelXOffsetSlider");
    const editXOffsetDisp = document.getElementById("labelXOffsetDisp");
    if (editXOffsetSlider && editXOffsetDisp) {
        const offset = (countries[tag] && countries[tag].labelXOffset) || 0;
        editXOffsetSlider.value = offset;
        editXOffsetDisp.textContent = offset;
    }
    const editArcShiftSlider = document.getElementById("labelArcShiftSlider");
    const editArcShiftDisp = document.getElementById("labelArcShiftDisp");
    if (editArcShiftSlider && editArcShiftDisp) {
        const offset = (countries[tag] && countries[tag].labelArcShift) || 0;
        editArcShiftSlider.value = offset;
        editArcShiftDisp.textContent = offset;
    }
    const editCurveSlider = document.getElementById("curvatureScaleSlider");
    const editCurveDisp = document.getElementById("curvatureScaleDisp");
    if (editCurveSlider && editCurveDisp) {
        const val = (countries[tag] && countries[tag].curvatureScale !== undefined) ? countries[tag].curvatureScale : 1.0;
        editCurveSlider.value = val;
        editCurveDisp.textContent = val.toFixed(1);
    }
    const editRotSlider = document.getElementById("labelRotationSlider");
    const editRotDisp = document.getElementById("labelRotationDisp");
    if (editRotSlider && editRotDisp) {
        const val = (countries[tag] && countries[tag].labelRotation !== undefined) ? countries[tag].labelRotation : 0;
        editRotSlider.value = val;
        editRotDisp.textContent = val;
    }
    const editSizeSlider = document.getElementById("fontSizeScaleSlider");
    const editSizeDisp = document.getElementById("fontSizeScaleDisp");
    if (editSizeSlider && editSizeDisp) {
        const val = (countries[tag] && countries[tag].fontSizeScale !== undefined) ? countries[tag].fontSizeScale : 1.0;
        editSizeSlider.value = val;
        editSizeDisp.textContent = val.toFixed(2);
    }
    const editStretchSlider = document.getElementById("labelStretchSlider");
    const editStretchDisp = document.getElementById("labelStretchDisp");
    if (editStretchSlider && editStretchDisp) {
        const val = (countries[tag] && countries[tag].labelStretch !== undefined) ? countries[tag].labelStretch : 1.0;
        editStretchSlider.value = val;
        editStretchDisp.textContent = val.toFixed(1);
    }
    const editColorInput = document.getElementById("editCountryColor");
    if (editColorInput && countries[tag]) {
        const rgb = countries[tag].color;
        const hex = "#" + ((1 << 24) + (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]).toString(16).slice(1);
        editColorInput.value = hex;
    }

    // Selecting a brush country is not an edit: refresh visuals without
    // flagging the document as having unsaved changes.
    suppressDirtyOnLut = true;
    updateLutData();
    suppressDirtyOnLut = false;
    requestDraw();
}

function updateCountryList() {
    const list = document.getElementById("countryList");
    if (!list) return;
    list.innerHTML = "";
    
    // Sort countries alphabetically by tag
    const sortedTags = Object.keys(countries).sort();
    
    sortedTags.forEach(tag => {
        const c = countries[tag];
        const item = document.createElement("div");
        item.className = "country-item";
        item.dataset.tag = tag;
        
        const colStr = `rgb(${c.color[0]}, ${c.color[1]}, ${c.color[2]})`;
        
        item.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 6px;
            background: #222;
            border: 1px solid #333;
            border-radius: 4px;
            cursor: pointer;
            color: white;
            font-family: sans-serif;
            font-size: 12px;
            margin-bottom: 2px;
        `;
        
        item.onclick = () => selectCountry(tag);
        
        const colorBox = document.createElement("div");
        colorBox.style.cssText = `
            width: 12px;
            height: 12px;
            background: ${colStr};
            border-radius: 2px;
            border: 1px solid #555;
            flex-shrink: 0;
        `;
        
        const tagLabel = document.createElement("span");
        tagLabel.textContent = tag;
        tagLabel.style.fontWeight = "bold";
        tagLabel.style.width = "40px";
        tagLabel.style.flexShrink = "0";
        
        const nameLabel = document.createElement("span");
        nameLabel.textContent = c.name;
        nameLabel.style.color = "#888";
        nameLabel.style.fontSize = "11px";
        nameLabel.style.whiteSpace = "nowrap";
        nameLabel.style.overflow = "hidden";
        nameLabel.style.textOverflow = "ellipsis";
        
        item.appendChild(colorBox);
        item.appendChild(tagLabel);
        item.appendChild(nameLabel);
        list.appendChild(item);
    });
    
    // Preserve the active selection if it still exists, otherwise default to the first tag
    if (selectedColor && sortedTags.includes(selectedColor)) {
        selectCountry(selectedColor);
    } else if (sortedTags.length > 0) {
        selectCountry(sortedTags[0]);
    }
}

function filterCountries() {
    const query = document.getElementById("countrySearch").value.toUpperCase();
    const items = document.querySelectorAll(".country-item");
    items.forEach(item => {
        const tag = item.dataset.tag;
        const name = countries[tag].name.toUpperCase();
        if (tag.includes(query) || name.includes(query)) {
            item.style.display = "flex";
        } else {
            item.style.display = "none";
        }
    });
}

function setColor(c){ selectedColor=c; eraserMode=false; }
function setEraser() {
	eraserMode = true;
	selectedColor = null;
	const eraserBtn = document.getElementById("btnEraser");
	if (eraserBtn) {
		eraserBtn.style.background = "#007bff";
	}
	const items = document.querySelectorAll(".country-item");
	items.forEach(item => {
		item.style.border = "1px solid #333";
		item.style.background = "#222";
	});
}
function clearLabelCache() {
	for (const k in labelCache) {
		delete labelCache[k];
	}
	labelGenerationQueue.clear();
}
function resetMap(){

    clearHistory();
    ownership = {};
    interests = {};

    // Reset country colors back to original preset or base values
    if (presetData && presetData.countries) {
        for (const tag in countries) {
            if (presetData.countries[tag] && presetData.countries[tag].color) {
                countries[tag].color = [...presetData.countries[tag].color];
                COLORS[tag] = [...presetData.countries[tag].color];
            } else if (BASE_COUNTRY_PRESETS[tag] && BASE_COUNTRY_PRESETS[tag].color) {
                countries[tag].color = [...BASE_COUNTRY_PRESETS[tag].color];
                COLORS[tag] = [...BASE_COUNTRY_PRESETS[tag].color];
            }
            countries[tag].provinces.clear();
            interests[tag] = {};
        }
    } else {
        for (const c in countries) {
            if (BASE_COUNTRY_PRESETS[c] && BASE_COUNTRY_PRESETS[c].color) {
                countries[c].color = [...BASE_COUNTRY_PRESETS[c].color];
                COLORS[c] = [...BASE_COUNTRY_PRESETS[c].color];
            }
            countries[c].provinces.clear();
            interests[c] = {};
        }
    }

    dirtyCountries.clear();
	clearLabelCache();

    // Reload preset ownership and interests if available
    if (presetData) {
        for (const provIdStr in presetData.ownership) {
            const provId = parseInt(provIdStr);
            const tag = presetData.ownership[provIdStr];
            if (countries[tag] && provinceCenters[provId]) {
                ownership[provId] = tag;
                countries[tag].provinces.add(provId);
            }
        }
        if (presetData.interests) {
            for (const tag in presetData.interests) {
                if (!interests[tag]) interests[tag] = {};
                for (const provIdStr in presetData.interests[tag]) {
                    interests[tag][parseInt(provIdStr)] = parseInt(presetData.interests[tag][provIdStr]);
                }
            }
        }
    }

    for (const tag in countries) {
        dirtyCountries.add(tag);
    }

    updateCountryList();
    updateLutData();
    draw();
}
function renameCountry(color, newName) {
    if (!countries[color]) return;
    countries[color].name = newName;
    dirtyCountries.add(color);
    clearLabelCache();
    markDirty();
    requestDraw();
    
    // Refresh diplomacy panel if open
    const diploTagSpan = document.getElementById("diploCountryTag");
    if (diploTagSpan && diploTagSpan.innerText === color) {
        openDiplomacyPanel(color);
    }
}

function toggleAccordion(header) {
    header.classList.toggle("active");
    const content = header.nextElementSibling;
    if (content.classList.contains("show")) {
        content.classList.remove("show");
    } else {
        content.classList.add("show");
    }
}

function getNextCountryTag() {
    let maxId = 0;
    for (const tag in countries) {
        const id = parseInt(tag);
        if (!isNaN(id) && id > maxId) {
            maxId = id;
        }
    }
    return String(maxId + 1).padStart(3, '0');
}

function createNewCountryFromUI() {
    const tagInput = document.getElementById("newCountryTag");
    const nameInput = document.getElementById("newCountryName");
    if (!tagInput || !nameInput) return;
    
    const tag = tagInput.value.trim().toUpperCase();
    const name = nameInput.value.trim();
    
    if (!tag || tag.length !== 3) {
        alert("Country Tag must be exactly 3 characters!");
        return;
    }
    if (!name) {
        alert("Please enter a Country Name!");
        return;
    }
    
    if (countries[tag]) {
        alert(`Country tag '${tag}' already exists (${countries[tag].name})!`);
        return;
    }
    
    // Generate distinct random color
    const r = Math.floor(Math.random() * 200) + 40;
    const g = Math.floor(Math.random() * 200) + 40;
    const b = Math.floor(Math.random() * 200) + 40;
    const color = [r, g, b];
    
    countries[tag] = {
        tag: tag,
        name: name,
        color: color,
        labelOffset: 0,
        labelXOffset: 0,
        labelArcShift: 0,
        curvatureScale: 1.0,
        fontSizeScale: 1.0,
        labelRotation: 0,
        labelStretch: 1.0,
        provinces: new Set(),
        spines: null
    };
    
    COLORS[tag] = color;
    dirtyCountries.add(tag);
    
    updateLutData();
    updateCountryList();
    selectCountry(tag);
    
    // Auto-update to the next available numerical tag
    tagInput.value = getNextCountryTag();
    nameInput.value = "";
    
    alert(`Successfully created country ${name} [${tag}]!`);
}
function setCountryTag(color, tag) {
    if (!countries[color]) return;
    countries[color].tag = tag;
}

function createStateFromSelection() {
    if (selectedProvinces.size === 0) {
        alert("Please select one or more provinces to form a state!");
        return;
    }
    
    let stateIdVal = document.getElementById("stateIdInput").value.trim();
    if (!stateIdVal) {
        let maxId = 0;
        for (const idStr in states) {
            const id = parseInt(idStr);
            if (id > maxId) maxId = id;
        }
        stateIdVal = (maxId + 1).toString();
    }
    const stateId = parseInt(stateIdVal);
    if (isNaN(stateId) || stateId <= 0) {
        alert("State ID must be a positive integer!");
        return;
    }
    
    let stateName = document.getElementById("stateNameInput").value.trim();
    if (!stateName) {
        stateName = "State " + stateId;
    }
    
    // Dissolve old state associations for these provinces
    for (const provId of selectedProvinces) {
        const oldStateId = provinceToState[provId];
        if (oldStateId !== undefined && states[oldStateId]) {
            states[oldStateId].provinces.delete(provId);
            if (states[oldStateId].provinces.size === 0) {
                delete states[oldStateId];
            }
        }
    }
    
    // Create new state or update name
    if (!states[stateId]) {
        const r = Math.floor(Math.random() * 200) + 40;
        const g = Math.floor(Math.random() * 200) + 40;
        const b = Math.floor(Math.random() * 200) + 40;
        states[stateId] = {
            id: stateId,
            name: stateName,
            color: [r, g, b],
            provinces: new Set()
        };
    } else {
        states[stateId].name = stateName;
    }
    
    // Assign provinces to the new state
    for (const provId of selectedProvinces) {
        states[stateId].provinces.add(provId);
        provinceToState[provId] = stateId;
    }
    
    // Auto-increment state ID for convenience
    let maxId = 0;
    for (const idStr in states) {
        const id = parseInt(idStr);
        if (id > maxId) maxId = id;
    }
    document.getElementById("stateIdInput").value = maxId + 1;
    document.getElementById("stateNameInput").value = "";
    
    selectedProvinces.clear();
    updateSelectionStatus();
    updateLutData();
    draw();
}

function clearStateFromSelection() {
    if (selectedProvinces.size === 0) return;
    
    for (const provId of selectedProvinces) {
        const oldStateId = provinceToState[provId];
        if (oldStateId !== undefined && states[oldStateId]) {
            states[oldStateId].provinces.delete(provId);
            if (states[oldStateId].provinces.size === 0) {
                delete states[oldStateId];
            }
        }
        delete provinceToState[provId];
    }
    
    selectedProvinces.clear();
    updateSelectionStatus();
    updateLutData();
    draw();
}

function selectStateProvinces() {
    if (selectedProvinces.size === 0) return;
    
    const provs = Array.from(selectedProvinces);
    const firstProv = provs[0];
    const stateId = provinceToState[firstProv];
    
    if (stateId === undefined) {
        alert("The selected province does not belong to any state!");
        return;
    }
    
    // Automatically promote/import preloaded state into editable custom states database
    if (!states[stateId] && hoi4Data && hoi4Data.states[stateId]) {
        const hState = hoi4Data.states[stateId];
        const r = (stateId * 57) % 200 + 40;
        const g = (stateId * 113) % 200 + 40;
        const b = (stateId * 179) % 200 + 40;
        states[stateId] = {
            id: parseInt(stateId),
            name: hState.name || ("State " + stateId),
            color: [r, g, b],
            provinces: new Set(hState.provinces)
        };
    }
    
    if (!states[stateId]) {
        alert("The selected province does not belong to any state!");
        return;
    }
    
    selectedProvinces.clear();
    for (const p of states[stateId].provinces) {
        selectedProvinces.add(p);
    }
    
    updateStateUIControls(stateId);
    
    updateSelectionStatus();
    draw();
}

function exportStatesJSON() {
    const serializableStates = {};
    for (const stateId in states) {
        const s = states[stateId];
        serializableStates[stateId] = {
            id: s.id,
            name: s.name,
            color: s.color,
            controlStrength: s.controlStrength !== undefined ? s.controlStrength : 100,
            showGradient: s.showGradient || false,
            provinces: Array.from(s.provinces)
        };
    }
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(serializableStates, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "states_config.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
}

function importStatesJSONFile(input) {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            states = {};
            provinceToState = {};
            for (const stateIdStr in data) {
                const s = data[stateIdStr];
                const stateId = parseInt(stateIdStr);
                states[stateId] = {
                    id: stateId,
                    name: s.name,
                    color: s.color || [Math.floor(Math.random()*200)+40, Math.floor(Math.random()*200)+40, Math.floor(Math.random()*200)+40],
                    provinces: new Set(s.provinces)
                };
                for (const provId of s.provinces) {
                    provinceToState[provId] = stateId;
                }
            }
            updateLutData();
            draw();
            alert(`Successfully imported ${Object.keys(states).length} states!`);
        } catch (err) {
            alert("Error parsing states JSON: " + err.message);
        }
    };
    reader.readAsText(file);
    input.value = "";
}

function reorderStateIDs() {
    const oldStates = { ...states };
    const sortedIds = Object.keys(oldStates).map(id => parseInt(id)).sort((a, b) => a - b);
    
    if (sortedIds.length === 0) {
        alert("No states currently exist to reorder!");
        return;
    }
    
    states = {};
    provinceToState = {};
    
    let newId = 1;
    for (const oldId of sortedIds) {
        const oldState = oldStates[oldId];
        states[newId] = {
            id: newId,
            name: oldState.name,
            color: oldState.color,
            provinces: oldState.provinces
        };
        for (const provId of oldState.provinces) {
            provinceToState[provId] = newId;
        }
        newId++;
    }
    
    // Set next available state ID input to the next number
    document.getElementById("stateIdInput").value = newId;
    
    updateLutData();
    draw();
    alert(`Successfully reordered ${sortedIds.length} states sequentially from 1 to ${newId - 1}!`);
}

function handleStateRename(name) {
    const idVal = document.getElementById("stateIdInput").value.trim();
    if (!idVal) return;
    const stateId = parseInt(idVal);
    if (states[stateId]) {
        states[stateId].name = name;
    }
}

function addSelectedToState() {
    const idVal = document.getElementById("stateIdInput").value.trim();
    if (!idVal) {
        alert("Please enter or select a State ID first!");
        return;
    }
    const stateId = parseInt(idVal);
    if (!states[stateId]) {
        alert(`State ID ${stateId} does not exist. Use "Create State" first.`);
        return;
    }
    if (selectedProvinces.size === 0) {
        alert("No provinces selected to add!");
        return;
    }
    
    for (const provId of selectedProvinces) {
        const oldStateId = provinceToState[provId];
        if (oldStateId !== undefined && states[oldStateId]) {
            states[oldStateId].provinces.delete(provId);
        }
        states[stateId].provinces.add(provId);
        provinceToState[provId] = stateId;
    }
    
    updateLutData();
    clearSelection();
    alert(`Added ${selectedProvinces.size} provinces to state '${states[stateId].name}' [${stateId}]`);
}

function removeSelectedFromState() {
    if (selectedProvinces.size === 0) {
        alert("No provinces selected to remove!");
        return;
    }
    
    let count = 0;
    for (const provId of selectedProvinces) {
        const stateId = provinceToState[provId];
        if (stateId !== undefined && states[stateId]) {
            states[stateId].provinces.delete(provId);
            delete provinceToState[provId];
            count++;
        }
    }
    
    updateLutData();
    clearSelection();
    alert(`Removed ${count} provinces from their states.`);
}

function deleteState() {
    const idVal = document.getElementById("stateIdInput").value.trim();
    if (!idVal) {
        alert("Please enter or select a State ID first!");
        return;
    }
    const stateId = parseInt(idVal);
    if (!states[stateId]) {
        alert(`State ID ${stateId} does not exist.`);
        return;
    }
    
    if (confirm(`Are you sure you want to delete state '${states[stateId].name}' [${stateId}]?`)) {
        for (const provId of states[stateId].provinces) {
            delete provinceToState[provId];
        }
        delete states[stateId];
        
        document.getElementById("stateNameInput").value = "";
        
        updateLutData();
        clearSelection();
        alert(`State ${stateId} deleted.`);
    }
}

function filterStatesList(query) {
    const resultsContainer = document.getElementById("statesSearchResults");
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = "";
    const cleanQuery = query.toLowerCase().trim();
    
    const matched = [];
    for (const stateId in states) {
        const s = states[stateId];
        if (!cleanQuery || s.name.toLowerCase().includes(cleanQuery) || stateId.includes(cleanQuery)) {
            matched.push(s);
        }
    }
    
    if (matched.length === 0) {
        resultsContainer.style.display = "none";
        return;
    }
    
    resultsContainer.style.display = "block";
    for (const s of matched) {
        const div = document.createElement("div");
        div.style.padding = "4px";
        div.style.cursor = "pointer";
        div.style.borderBottom = "1px solid #222";
        div.style.fontSize = "11px";
        div.style.color = "#eee";
        div.innerText = `[${s.id}] ${s.name} (${s.provinces.size} provs)`;
        
        div.onmouseover = () => div.style.background = "#333";
        div.onmouseout = () => div.style.background = "none";
        div.onclick = () => selectStateFromSearch(s.id);
        
        resultsContainer.appendChild(div);
    }
}

function selectStateFromSearch(stateId) {
    const resultsContainer = document.getElementById("statesSearchResults");
    const searchInput = document.getElementById("stateSearchInput");
    
    if (resultsContainer) resultsContainer.style.display = "none";
    if (searchInput) searchInput.value = "";
    
    updateStateUIControls(stateId);
    
    // Clear selection and select this state's provinces
    selectedProvinces.clear();
    for (const p of states[stateId].provinces) {
        selectedProvinces.add(p);
    }
    updateSelectionStatus();
    draw();
}

// Hide state search results when clicking elsewhere
document.addEventListener("click", (e) => {
    const container = document.getElementById("statesSearchResults");
    const input = document.getElementById("stateSearchInput");
    if (container && input && e.target !== input && !container.contains(e.target)) {
        container.style.display = "none";
    }
});

function openDiplomacyPanel(tag) {
    const country = countries[tag];
    if (!country) return;
    
    const panel = document.getElementById("diplomacyPanel");
    if (panel) panel.style.display = "block";
    
    document.getElementById("diploCountryName").innerText = country.fullName || country.name;
    document.getElementById("diploCountryTag").innerText = tag;
    document.getElementById("diploFlagTag").innerText = tag.substring(0, 3).toUpperCase();
    
    const rgbStr = `rgb(${country.color[0]}, ${country.color[1]}, ${country.color[2]})`;
    const flagColorDiv = document.getElementById("diploFlagColor");
    if (flagColorDiv) {
        flagColorDiv.style.background = `linear-gradient(135deg, ${rgbStr} 20%, rgba(0,0,0,0.5) 100%)`;
    }
    
    // Check and load country flag image from flags/ directory
    const flagImg = document.getElementById("diploFlagImage");
    const flagFallback = document.getElementById("diploFlagFallback");
    if (flagImg && flagFallback) {
        flagImg.style.display = "none";
        flagFallback.style.display = "flex"; // Default to fallback card
        
        flagImg.src = `flags/${tag}.png?t=${Date.now()}`; // Bypass cache
        flagImg.onload = () => {
            flagImg.style.display = "block";
            flagFallback.style.display = "none"; // Hide fallback
        };
        flagImg.onerror = () => {
            flagImg.style.display = "none";
            flagFallback.style.display = "flex"; // Show fallback card
        };
    }
    
    const colorInd = document.getElementById("diploColorIndicator");
    if (colorInd) colorInd.style.background = rgbStr;
    document.getElementById("diploColorText").innerText = `RGB(${country.color.join(", ")})`;
    
    let provCount = country.provinces ? country.provinces.size : 0;
    document.getElementById("diploProvincesCount").innerText = provCount;
    
    let totalPixels = 0;
    if (country.provinces) {
        for (const provId of country.provinces) {
            const center = provinceCenters[provId];
            if (center && center.count) {
                totalPixels += center.count;
            }
        }
    }
    document.getElementById("diploLandArea").innerText = `${totalPixels.toLocaleString('en-US')} pixels`;
    
    let claimsCount = 0;
    for (const otherTag in interests) {
        if (otherTag !== tag) {
            for (const provId in interests[otherTag]) {
                if (country.provinces && country.provinces.has(parseInt(provId))) {
                    claimsCount++;
                }
            }
        }
    }
    document.getElementById("diploClaimsOnUs").innerText = claimsCount;
}

function diploRemoveCountryProvinces() {
    const tag = document.getElementById("diploCountryTag").innerText;
    const country = countries[tag];
    if (country) {
        if (confirm(`Are you sure you want to remove ownership from all provinces owned by ${country.fullName || country.name}?`)) {
            removeOwnershipForCountry(tag);
            closeDiplomacyPanel();
        }
    }
}

function clearActiveCountryTerritory() {
    if (!selectedColor) return;
    const country = countries[selectedColor];
    if (country) {
        if (confirm(`Are you sure you want to clear all territory owned by ${country.fullName || country.name}?`)) {
            removeOwnershipForCountry(selectedColor);
        }
    }
}

function removeOwnershipForCountry(tag) {
    const country = countries[tag];
    if (!country) return;
    
    const provs = Array.from(country.provinces);
    beginEdit("Clear territory of " + tag);
    for (const provId of provs) {
        // Set ownership back to unowned
        delete ownership[provId];
        
        // Update WebGL LUT data to base grey color. The LUT is indexed by the
        // province's palette index, not by its ID.
        const center = provinceCenters[provId];
        if (center && lutData) {
            updateLutForProvince(center.index, [180, 180, 180], provId);
        }
    }
    
    country.provinces.clear();
    commitEdit();
    dirtyCountries.add(tag);
    lutNeedsUpdate = true;
    clearLabelCache();
    updateCountryList();
    requestDraw();
}

function closeDiplomacyPanel() {
    const panel = document.getElementById("diplomacyPanel");
    if (panel) panel.style.display = "none";
}

function diploSelectCountryProvinces() {
    const tag = document.getElementById("diploCountryTag").innerText;
    const country = countries[tag];
    if (country) {
        selectedProvinces.clear();
        for (const p of country.provinces) {
            selectedProvinces.add(p);
        }
        updateSelectionStatus();
        draw();
    }
}

function diploRenameCountry() {
    const tag = document.getElementById("diploCountryTag").innerText;
    const country = countries[tag];
    if (country) {
        const newShortName = prompt("Enter Short Name (for map labels):", country.name);
        if (newShortName !== null && newShortName.trim()) {
            const newFullName = prompt("Enter Full Name (for diplomacy tab):", country.fullName || country.name);
            if (newFullName !== null) {
                renameCountryDetails(tag, newShortName.trim(), newFullName.trim());
            }
        }
    }
}

function renameCountryDetails(tag, shortName, fullName) {
    if (!countries[tag]) return;
    countries[tag].name = shortName;
    countries[tag].fullName = fullName;
    dirtyCountries.add(tag);
    clearLabelCache();
    updateCountryList();
    markDirty();
    requestDraw();
    openDiplomacyPanel(tag);
}

function handleFullNameRenameFromInput(val) {
    if (!selectedColor) return;
    countries[selectedColor].fullName = val.trim();
    dirtyCountries.add(selectedColor);
    markDirty();
    
    // Refresh diplomacy panel if open
    const diploTagSpan = document.getElementById("diploCountryTag");
    if (diploTagSpan && diploTagSpan.innerText === selectedColor) {
        openDiplomacyPanel(selectedColor);
    }
}

function diploRecolorCountry() {
    const tag = document.getElementById("diploCountryTag").innerText;
    const country = countries[tag];
    if (country) {
        const picker = document.getElementById("editCountryColor");
        if (picker) {
            picker.click();
        }
    }
}

function addSelectedToHoveredState() {
    const [mapX, mapY] = screenToMap(currentMouseX, currentMouseY);
    const provId = getProvinceIdAt(mapX, mapY);
    if (!provId || provId === 0) return;
    
    const stateId = provinceToState[provId];
    if (stateId === undefined || !states[stateId]) {
        alert("Hovered province does not belong to any state!");
        return;
    }
    
    if (selectedProvinces.size === 0) {
        // If nothing is selected, select the hovered state (like middle-click)
        selectedProvinces.clear();
        for (const p of states[stateId].provinces) {
            selectedProvinces.add(p);
        }
        updateStateUIControls(stateId);
        updateSelectionStatus();
        draw();
    } else {
        // Add selected provinces to the hovered state
        for (const p of selectedProvinces) {
            const oldStateId = provinceToState[p];
            if (oldStateId !== undefined && states[oldStateId]) {
                states[oldStateId].provinces.delete(p);
            }
            states[stateId].provinces.add(p);
            provinceToState[p] = stateId;
        }
        updateLutData();
        clearSelection();
        alert(`Added provinces to state '${states[stateId].name}' [${stateId}]`);
    }
}

function compileShader(gl, source, type) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error("Shader compile error: " + gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
    }
    return shader;
}

function linkProgram(gl, vs, fs) {
    const program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error("Program link error: " + gl.getProgramInfoLog(program));
        return null;
    }
    return program;
}

let gl;
let program;
let uniformLocations = {};
let indexTexture;
let lutTexture;
let heightmapTexture;
let riversTexture;
let showRivers = 1.0;
let lutData;
let lutWidth = 2048;
let lutHeight = 16;
let lutNeedsUpdate = true;
let showBorders = 1.0;
let showLabels = 1.0;
let waterIdx = -1;

const vsSource = `
    attribute vec2 a_position;
    varying vec2 v_texCoord;
    uniform vec2 u_offset;
    uniform float u_zoom;
    uniform vec2 u_resolution;
    uniform vec2 u_mapSize;

    void main() {
        vec2 worldPos = a_position * u_mapSize;
        vec2 screenPos = (worldPos - u_offset) * u_zoom;
        vec2 clipSpace = (screenPos / u_resolution) * 2.0 - 1.0;
        gl_Position = vec4(clipSpace.x, -clipSpace.y, 0.0, 1.0);
        v_texCoord = a_position;
    }
`;

const fsSource = `
    precision highp float;
    varying vec2 v_texCoord;
    uniform sampler2D u_indexTexture;
    uniform sampler2D u_lutTexture;
    uniform sampler2D u_heightmapTexture;
    uniform sampler2D u_riversTexture;
    uniform float u_showRivers;
    uniform vec2 u_texelSize;
    uniform float u_lutWidth;
    uniform float u_lutHeight;
    uniform float u_showBorders;
    uniform float u_showHeightmap;
    uniform vec2 u_mapSize;
    uniform float u_zoom;
    uniform float u_activeMapmode;
    
    #define DECODE_IDX(col) (floor(col.r * 255.0 + 0.5) + floor(col.g * 255.0 + 0.5) * 256.0 + floor(col.b * 255.0 + 0.5) * 65536.0)
    #define GET_COUNTRY(nIdx) texture2D(u_lutTexture, vec2((mod(nIdx, u_lutWidth) + 0.5) / u_lutWidth, (floor(nIdx / u_lutWidth) + 0.5) / u_lutHeight)).rgb
    #define GET_ALPHA_VAL(nIdx) floor(texture2D(u_lutTexture, vec2((mod(nIdx, u_lutWidth) + 0.5) / u_lutWidth, (floor(nIdx / u_lutWidth) + 0.5) / u_lutHeight)).a * 255.0 + 0.5)

    void main() {
        vec4 indexColor = texture2D(u_indexTexture, v_texCoord);
        
        float r = floor(indexColor.r * 255.0 + 0.5);
        float g = floor(indexColor.g * 255.0 + 0.5);
        float b = floor(indexColor.b * 255.0 + 0.5);
        float idx = r + g * 256.0 + b * 65536.0;

        vec2 sStep = 1.0 / (u_mapSize * u_zoom);
        vec4 nL = texture2D(u_indexTexture, v_texCoord + vec2(-sStep.x, 0.0));
        vec4 nR = texture2D(u_indexTexture, v_texCoord + vec2(sStep.x, 0.0));
        vec4 nD = texture2D(u_indexTexture, v_texCoord + vec2(0.0, -sStep.y));
        vec4 nU = texture2D(u_indexTexture, v_texCoord + vec2(0.0, sStep.y));
        
        float idxL = DECODE_IDX(nL);
        float idxR = DECODE_IDX(nR);
        float idxD = DECODE_IDX(nD);
        float idxU = DECODE_IDX(nU);
        
        float u = (mod(idx, u_lutWidth) + 0.5) / u_lutWidth;
        float v = (floor(idx / u_lutWidth) + 0.5) / u_lutHeight;
        vec4 lutColor = texture2D(u_lutTexture, vec2(u, v));
        vec4 color = vec4(lutColor.rgb, 1.0);
        vec3 baseCountryColor = color.rgb;
        

        
        // Detect water provinces by their fixed sentinel LUT colour (150,180,210).
        // Rivers must not be drawn on top of ocean/lake provinces.
        vec3 waterSentinel = vec3(150.0, 180.0, 210.0) / 255.0;
        bool isWaterProvince = all(lessThan(abs(baseCountryColor - waterSentinel), vec3(0.51 / 255.0)));

        if (u_showRivers > 0.5 && !isWaterProvince) {
            vec4 riverCol = texture2D(u_riversTexture, v_texCoord);
            if (riverCol.a > 0.5) {
                float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));
                vec3 riverWater = riverCol.rgb * (0.7 + 0.3 * clamp(lum / 0.70588, 0.0, 1.5));
                color.rgb = mix(color.rgb, riverWater, 0.95);
            }
        }

        if (u_showHeightmap > 0.5) {
            float h = texture2D(u_heightmapTexture, v_texCoord).r;
            float hR = texture2D(u_heightmapTexture, v_texCoord + vec2(u_texelSize.x, 0.0)).r;
            float hD = texture2D(u_heightmapTexture, v_texCoord + vec2(0.0, u_texelSize.y)).r;
            
            float scale = 30.0;
            float dx = (hR - h) * scale;
            float dy = (hD - h) * scale;
            
            vec3 normal = normalize(vec3(-dx, -dy, 1.0));
            vec3 lightDir = normalize(vec3(-1.0, -1.0, 1.5));
            float light = dot(normal, lightDir);
            
            float shadow = 0.5 + 0.5 * light;
            shadow = clamp(shadow, 0.6, 1.4);
            color = vec4(color.rgb * shadow, 1.0);
        }

        // Apply National Interest Overlay
        if (u_activeMapmode > 0.5) {
            float interestLevel = floor(lutColor.a * 255.0 + 0.5);
            if (interestLevel > 0.5) {
                vec2 mapCoord = v_texCoord * u_mapSize;
                float baseOpacity = 0.05 + (interestLevel / 10.0) * 0.20;
                float stripe = sin((mapCoord.x + mapCoord.y) * 0.4);
                float threshold = 1.0 - (interestLevel / 10.0) * 0.6; 
                float stripeActive = step(threshold, stripe);
                vec3 interestColor = vec3(0.95, 0.25, 0.1); 
                float overlayAlpha = baseOpacity + stripeActive * 0.25 * (interestLevel / 10.0);
                overlayAlpha = clamp(overlayAlpha, 0.0, 0.7);
                color.rgb = mix(color.rgb, interestColor, overlayAlpha);
            } else {
                color.rgb = mix(color.rgb, vec3(dot(color.rgb, vec3(0.299, 0.587, 0.114))), 0.4);
            }
        }
        
        if (u_showBorders > 0.5) {
            
            vec3 countryL = GET_COUNTRY(idxL);
            vec3 countryR = GET_COUNTRY(idxR);
            vec3 countryD = GET_COUNTRY(idxD);
            vec3 countryU = GET_COUNTRY(idxU);
            

            
            float pDiffL = step(0.5, abs(idx - idxL));
            float pDiffR = step(0.5, abs(idx - idxR));
            float pDiffD = step(0.5, abs(idx - idxD));
            float pDiffU = step(0.5, abs(idx - idxU));
            
            float provBorder = (pDiffL + pDiffR + pDiffD + pDiffU) * 0.25;
            float provOpacity = clamp((u_zoom - 3.0) * 0.35, 0.0, 0.25);
            provBorder = clamp(provBorder * provOpacity, 0.0, 1.0);
            
            float alphaVal = floor(lutColor.a * 255.0 + 0.5);
            
            #define GET_ALPHA_VAL(nIdx) floor(texture2D(u_lutTexture, vec2((mod(nIdx, u_lutWidth) + 0.5) / u_lutWidth, (floor(nIdx / u_lutWidth) + 0.5) / u_lutHeight)).a * 255.0 + 0.5)
            
            float alphaL = GET_ALPHA_VAL(idxL);
            float alphaR = GET_ALPHA_VAL(idxR);
            float alphaD = GET_ALPHA_VAL(idxD);
            float alphaU = GET_ALPHA_VAL(idxU);
            
            float cHash = floor(alphaVal / 16.0);
            float sHash = mod(alphaVal, 16.0);

            float cHashL = floor(alphaL / 16.0);
            float cHashR = floor(alphaR / 16.0);
            float cHashD = floor(alphaD / 16.0);
            float cHashU = floor(alphaU / 16.0);

            float sHashL = mod(alphaL, 16.0);
            float sHashR = mod(alphaR, 16.0);
            float sHashD = mod(alphaD, 16.0);
            float sHashU = mod(alphaU, 16.0);

            float dHashL = (u_activeMapmode < 0.5) ? step(0.5, abs(cHash - cHashL)) : 0.0;
            float dHashR = (u_activeMapmode < 0.5) ? step(0.5, abs(cHash - cHashR)) : 0.0;
            float dHashD = (u_activeMapmode < 0.5) ? step(0.5, abs(cHash - cHashD)) : 0.0;
            float dHashU = (u_activeMapmode < 0.5) ? step(0.5, abs(cHash - cHashU)) : 0.0;

            float diffL = clamp(step(0.002, distance(baseCountryColor, countryL)) + dHashL, 0.0, 1.0);
            float diffR = clamp(step(0.002, distance(baseCountryColor, countryR)) + dHashR, 0.0, 1.0);
            float diffD = clamp(step(0.002, distance(baseCountryColor, countryD)) + dHashD, 0.0, 1.0);
            float diffU = clamp(step(0.002, distance(baseCountryColor, countryU)) + dHashU, 0.0, 1.0);
            
            float countryBorder = (diffL + diffR + diffD + diffU) * 0.45;
            countryBorder = clamp(countryBorder, 0.0, 1.0);
            
            float sDiffL = step(0.5, abs(sHash - sHashL));
            float sDiffR = step(0.5, abs(sHash - sHashR));
            float sDiffD = step(0.5, abs(sHash - sHashD));
            float sDiffU = step(0.5, abs(sHash - sHashU));
            
            float stateBorder = (sDiffL + sDiffR + sDiffD + sDiffU) * 0.25;
            stateBorder = clamp(stateBorder, 0.0, 1.0);
            
            // Subtle, delicate state border opacity when zoomed in (starts at 1.35x zoom)
            float stateOpacity = clamp((u_zoom - 1.35) * 0.7, 0.0, 1.0);

            if (countryBorder > 0.0) {
                color.rgb = mix(color.rgb, vec3(0.0), countryBorder * 0.9);
            } else if (stateBorder > 0.0 && stateOpacity > 0.01 && u_activeMapmode < 0.5) {
                // Soft, refined, subtle state border line
                color.rgb = mix(color.rgb, vec3(0.0), stateBorder * 0.45 * stateOpacity);
            } else if (provBorder > 0.0) {
                color.rgb = mix(color.rgb, vec3(0.0), provBorder);
            }
        }
        
        gl_FragColor = color;
    }
`;

function initWebGL() {
    gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (!gl) {
        alert("WebGL not supported!");
        return;
    }
    gl.getExtension('OES_standard_derivatives');

    const vs = compileShader(gl, vsSource, gl.VERTEX_SHADER);
    const fs = compileShader(gl, fsSource, gl.FRAGMENT_SHADER);
    program = linkProgram(gl, vs, fs);
    gl.useProgram(program);

    // Cache uniform locations once. getUniformLocation is a relatively expensive
    // GL query; calling it ~15x per frame in performDraw was pure overhead.
    uniformLocations = {};
    for (const name of [
        "u_indexTexture", "u_lutTexture", "u_heightmapTexture", "u_riversTexture",
        "u_showRivers", "u_offset", "u_zoom", "u_resolution", "u_mapSize",
        "u_texelSize", "u_lutWidth", "u_lutHeight", "u_showHeightmap",
        "u_showBorders", "u_activeMapmode"
    ]) {
        uniformLocations[name] = gl.getUniformLocation(program, name);
    }

    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    const quadVertices = new Float32Array([
        0, 0,
        1, 0,
        0, 1,
        0, 1,
        1, 0,
        1, 1
    ]);
    gl.bufferData(gl.ARRAY_BUFFER, quadVertices, gl.STATIC_DRAW);

    const positionLocation = gl.getAttribLocation(program, "a_position");
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    indexTexture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, indexTexture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, indexImg);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

    // Calculate LUT texture height dynamically based on the loaded province count
    lutWidth = 2048;
    lutHeight = Math.ceil(meta.province_count / lutWidth);
    if (lutHeight < 1) lutHeight = 1;

    lutTexture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, lutTexture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

    lutData = new Uint8Array(lutWidth * lutHeight * 4);
    for (let i = 0; i < lutWidth * lutHeight; i++) {
        const o = i * 4;
        lutData[o] = 180;
        lutData[o+1] = 180;
        lutData[o+2] = 180;
        lutData[o+3] = 255;
    }
    for (const keyStr in meta.centers) {
        const centerData = meta.centers[keyStr];
        if (centerData.is_water) {
            const o = centerData.index * 4;
            lutData[o] = 150;
            lutData[o+1] = 180;
            lutData[o+2] = 210;
        }
    }
    lutNeedsUpdate = true;

    heightmapTexture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, heightmapTexture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0, 255]));
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

    riversTexture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, riversTexture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0, 0]));
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

    const riversImg = new Image();
    riversImg.onload = () => {
        gl.bindTexture(gl.TEXTURE_2D, riversTexture);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, riversImg);
        draw();
    };
    riversImg.src = "rivers_index.png?v=" + Date.now();
}

let labelWorker = null;

function processWorkerResponse(data) {
	const { tag, results } = data;
	const country = countries[tag];
	if (!country) return;
	country.labelGenerating = false;
	country.spines = results;
	generateLabelsForCountry(tag, true);
	draw();
}

function initLabelWorker() {
	const workerCode = `
		let provinceCenters = {};
		let provinceNeighbors = {};
		let straitAdj = {};
		let ownership = {};
		let img = { width: 0, height: 0 };
		let provinceIdMap = null;
		let colorToId = {};
		let provincesSet = new Set();

		function getProvinceIdAt(x, y) {
			const pxX = Math.floor(x);
			const pxY = Math.floor(y);
			if (pxX < 0 || pxX >= img.width || pxY < 0 || pxY >= img.height) return 0;
			return provinceIdMap[pxY * img.width + pxX];
		}

		// Inject global Dijkstra classes/functions
		${MinHeap.toString()}
		${resamplePath.toString()}
		${computeSpineForComponent.toString()}

		self.onmessage = function(e) {
			if (e.data.action === "init") {
				provinceCenters = e.data.provinceCenters;
				img = e.data.img;
				colorToId = e.data.colorToId;
				
				const tempPixels = new Uint8ClampedArray(e.data.basePixelsBuffer);
				provinceIdMap = new Uint16Array(img.width * img.height);
				for (let i = 0; i < provinceIdMap.length; i++) {
					const idx = i * 4;
					const r = tempPixels[idx];
					const g = tempPixels[idx + 1];
					const b = tempPixels[idx + 2];
					let id = r + g * 256 + b * 65536;
					if (id === 16777215) id = 0;
					provinceIdMap[i] = id;
				}
				
				// Reconstruct Set objects
				for (const k in e.data.provinceNeighbors) {
					provinceNeighbors[k] = new Set(e.data.provinceNeighbors[k]);
				}
				for (const k in e.data.straitAdj) {
					straitAdj[k] = new Set(e.data.straitAdj[k]);
				}
				return;
			}
			if (e.data.action === "updateOwnership") {
				ownership = e.data.ownership;
				return;
			}
			if (e.data.action === "compute") {
				const { tag, provinces, text, curvatureScale, ownership: currentOwnership } = e.data;
				ownership = currentOwnership;
				provincesSet = new Set(provinces);
				
				// BFS to find components (same logic as main thread)
				const visited = new Set();
				const components = [];
				for (const provId of provinces) {
					if (visited.has(provId)) continue;
					const component = [];
					const queue = [provId];
					let queueHead = 0;
					visited.add(provId);
					while (queueHead < queue.length) {
						const curr = queue[queueHead++];
						component.push(curr);
						for (const n of provinceNeighbors[curr] || []) {
							if (provincesSet.has(n) && !visited.has(n)) {
								visited.add(n);
								queue.push(n);
							}
						}
						for (const n of straitAdj[curr] || []) {
							if (provincesSet.has(n) && !visited.has(n)) {
								visited.add(n);
								queue.push(n);
							}
						}
					}
					components.push(component);
				}

				const results = [];
				for (const comp of components) {
					if (comp.length < 4) {
						results.push({ spine: [], path: [], controlPoints: [], tension: 0 });
						continue;
					}
					const res = computeSpineForComponent(comp, tag, text, curvatureScale);
					results.push(res);
				}

				self.postMessage({
					tag: tag,
					results: results
				});
			}
		};
	`;

	const blob = new Blob([workerCode], { type: "application/javascript" });
	labelWorker = new Worker(URL.createObjectURL(blob));

	labelWorker.onmessage = function(e) {
		if (isPanning || isDragging) {
			deferredWorkerResponses.push(e.data);
			return;
		}
		processWorkerResponse(e.data);
	};

	// Re-serialize Set structures to Arrays for clone-safety
	const provinceNeighborsCopy = {};
	for (const k in provinceNeighbors) {
		provinceNeighborsCopy[k] = Array.from(provinceNeighbors[k]);
	}
	const straitAdjCopy = {};
	for (const k in straitAdj) {
		straitAdjCopy[k] = Array.from(straitAdj[k]);
	}

	const basePixelsCopy = new Uint8ClampedArray(basePixels);
	labelWorker.postMessage({
		action: "init",
		provinceCenters,
		provinceNeighbors: provinceNeighborsCopy,
		straitAdj: straitAdjCopy,
		colorToId,
		img: { width: baseCanvas.width, height: baseCanvas.height },
		basePixelsBuffer: basePixelsCopy.buffer
	}, [basePixelsCopy.buffer]);
}

function buildStraitAdjacency() {
	straitAdj = {};
	for (const s of straits) {
		if (!straitAdj[s.from]) straitAdj[s.from] = new Set();
		if (!straitAdj[s.to]) straitAdj[s.to] = new Set();
		straitAdj[s.from].add(s.to);
		straitAdj[s.to].add(s.from);
	}
}

function updateStateUIControls(stateId) {
    if (!states[stateId]) return;
    const st = states[stateId];
    const idInput = document.getElementById("stateIdInput");
    const nameInput = document.getElementById("stateNameInput");
    if (idInput) idInput.value = stateId;
    if (nameInput) nameInput.value = st.name;
}

function initApp() {
    buildStraitAdjacency();
    definitions = meta.definitions || {};
    for (const idStr in definitions) {
        const d = definitions[idStr];
        const r = d.color[0];
        const g = d.color[1];
        const b = d.color[2];
        const key = (((r << 24) >>> 0) | (g << 16) | (b << 8) | 255) >>> 0;
        colorToId[key] = parseInt(idStr);
    }

    initWebGL();
    
    if (hasHeightmap) {
        gl.bindTexture(gl.TEXTURE_2D, heightmapTexture);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, heightmapImg);
        showHeightmap = 1.0;
    }
    const heightmapToggle = document.getElementById("graphicsHeightmapToggle");
    if (heightmapToggle) {
        heightmapToggle.checked = showHeightmap > 0.5;
        heightmapToggle.disabled = !hasHeightmap;
        heightmapToggle.style.cursor = hasHeightmap ? "pointer" : "not-allowed";
    }

    overlayCanvas.width = canvas.width = window.innerWidth;
    overlayCanvas.height = canvas.height = window.innerHeight;

    baseCanvas.width = img.width;
    baseCanvas.height = img.height;
    baseCtx.drawImage(indexImg, 0, 0);
	
	basePixels =
		baseCtx.getImageData(
			0,
			0,
			img.width,
			img.height
		).data;

    for (const keyStr in meta.centers) {
        const key = parseInt(keyStr);
        const centerData = meta.centers[keyStr];
        provinceCenters[key] = {
            x: centerData.x,
            y: centerData.y,
            count: centerData.count,
            index: centerData.index,
            isWater: centerData.is_water || false
        };
    }
    console.log("Water province keys loaded:", Object.keys(provinceCenters).filter(k => provinceCenters[k].isWater));

    for (const keyStr in meta.neighbors) {
        const key = parseInt(keyStr);
        const neighborKeys = meta.neighbors[keyStr];
        provinceNeighbors[key] = new Set(neighborKeys.map(k => parseInt(k)));
    }

    if (presetData) {
        for (const k in countries) delete countries[k];
        for (const k in COLORS) delete COLORS[k];
        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                for (const tag in presetData.countries) {
            const c = presetData.countries[tag];
            const base = BASE_COUNTRY_PRESETS[tag] || {};
            countries[tag] = {
                tag: tag,
                name: c.name,
                fullName: c.fullName || "",
                color: c.color,
                labelOffset: c.labelOffset !== undefined ? c.labelOffset : (base.labelOffset || 0),
                labelXOffset: c.labelXOffset !== undefined ? c.labelXOffset : (base.labelXOffset || 0),
                labelArcShift: c.labelArcShift !== undefined ? c.labelArcShift : (base.labelArcShift || 0),
                curvatureScale: c.curvatureScale !== undefined ? c.curvatureScale : (base.curvatureScale !== undefined ? base.curvatureScale : 1.0),
                fontSizeScale: c.fontSizeScale !== undefined ? c.fontSizeScale : (base.fontSizeScale !== undefined ? base.fontSizeScale : 1.0),
                labelRotation: c.labelRotation !== undefined ? c.labelRotation : (base.labelRotation !== undefined ? base.labelRotation : 0),
                labelStretch: c.labelStretch !== undefined ? c.labelStretch : (base.labelStretch !== undefined ? base.labelStretch : 1.0),
                provinces: new Set(),
                // null = "spine not yet computed"; the label worker will build it.
                // An empty array would read as truthy and suppress that computation.
                spines: null
            };
            COLORS[tag] = c.color;
        }
        
        resetMap();
        updateCountryList();
        const tagInput = document.getElementById("newCountryTag");
        if (tagInput) {
            tagInput.value = getNextCountryTag();
        }
        
        // Load state configurations from either states_config.json or presetData
        states = {};
        provinceToState = {};
        const sourceStates = statesData || (presetData && presetData.states);
        if (sourceStates) {
            let maxId = 0;
            for (const stateIdStr in sourceStates) {
                const s = sourceStates[stateIdStr];
                const stateId = parseInt(stateIdStr);
                if (stateId > maxId) maxId = stateId;
                states[stateId] = {
                    id: stateId,
                    name: s.name,
                    color: s.color,
                    controlStrength: s.controlStrength !== undefined ? s.controlStrength : 100,
                    showGradient: s.showGradient !== undefined ? s.showGradient : false,
                    provinces: new Set(s.provinces)
                };
                for (const provId of s.provinces) {
                    provinceToState[provId] = stateId;
                }
            }
            const idInput = document.getElementById("stateIdInput");
            if (idInput) {
                idInput.value = maxId + 1;
            }
            updateLutData();
        }
    } else {
        updateCountryList();
    }

    for (const o in countries) {
        dirtyCountries.add(o);
    }

	document.getElementById("dbgAxis").addEventListener("change", e=>{
		DEBUG.axis = e.target.checked;
		draw();
	});

	document.getElementById("dbgBezier").addEventListener("change", e=>{
		DEBUG.bezier = e.target.checked;
		draw();
	});

	document.getElementById("dbgPoints").addEventListener("change", e=>{
		DEBUG.points = e.target.checked;
		draw();
	});

	document.getElementById("dbgPanelToggle").addEventListener("change", e=>{
		DEBUG.panel = e.target.checked;
		debugPanel.style.display = DEBUG.panel ? "block" : "none";
		draw();
	});

	document.getElementById("dbgHeightmap").addEventListener("change", e=>{
		toggleHeightmapShading(e.target.checked);
	});

    // Fetch HOI4 state mappings database
	fetch("hoi4_data.json?v=" + Date.now())
		.then(r => r.ok ? r.json() : null)
		.then(data => {
			if (data) {
				hoi4Data = data;

				console.log("HOI4 state mappings loaded successfully.");
				document.getElementById("hoi4Panel").style.display = "block";
			}
		})
		.catch(err => console.log("HOI4 state data not available or not parsed."));

	initLabelWorker();
    fitToScreen();
    draw();

    // Initial load is complete: enable dirty tracking, show the save badge,
    // and offer to recover a browser autosave if one is present.
    appReady = true;
    updateSaveStatusBadge();
    maybeOfferAutosaveRecovery();
}

Promise.all([
    new Promise(resolve => {
        img.onload = resolve;
        img.src = "provinces.png?v=" + Date.now();
    }),
    new Promise(resolve => {
        indexImg.onload = resolve;
        indexImg.src = "provinces_index.png?v=" + Date.now();
    }),
    new Promise(resolve => {
        heightmapImg.onload = () => {
            hasHeightmap = true;
            resolve();
        };
        heightmapImg.onerror = () => {
            resolve();
        };
        heightmapImg.src = "heightmap.png?v=" + Date.now();
    }),
    fetch("provinces_meta.json?v=" + Date.now())
        .then(r => r.json())
        .then(data => {
            meta = data;
        }),
    fetch("preset_ownership.json?v=" + Date.now())
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            presetData = data;
        })
        .catch(() => {
            presetData = null;
        }),
    fetch("states_config.json?v=" + Date.now())
        .then(r => r.ok ? r.json() : fetch("states.json?v=" + Date.now()).then(r => r.ok ? r.json() : null))
        .then(data => {
            statesData = data;
        })
        .catch(() => {
            statesData = null;
        }),
    fetch("straits.json?v=" + Date.now())
        .then(r => r.ok ? r.json() : [])
        .then(data => {
            straits = data;
        })
        .catch(() => {
            straits = [];
        })
    ]).then(() => {
    initApp();
});

function fitToScreen(){
    overlayCanvas.width = canvas.width = window.innerWidth;
    overlayCanvas.height = canvas.height = window.innerHeight;
    
    const fitZoom = Math.min(canvas.width / img.width, canvas.height / img.height);
    zoom = fitZoom;
    
    offsetX = -(canvas.width / zoom - img.width) / 2;
    offsetY = -(canvas.height / zoom - img.height) / 2;
    
    if (gl) {
        gl.viewport(0, 0, canvas.width, canvas.height);
    }
}

window.addEventListener("resize", ()=>{fitToScreen(); draw();});

let selectedProvinces = new Set();
// Cached geometry for the selected-province highlight overlay. Rebuilding a
// single Path2D of all arcs and re-filling/stroking it once per frame is far
// cheaper than issuing fill()/stroke() per province every frame — especially
// while panning a large (whole-country) selection, when the geometry is static.
let selectionVersion = 0;
const selectionHighlightCache = { version: -1, zoom: -1, size: -1, path: null };
function markSelectionDirty() { selectionVersion++; }
let activeTool = "box"; // "box", "lasso", "pan"
let lassoPoints = [];

function setTool(toolName) {
    activeTool = toolName;
    document.getElementById("btnToolBox").style.background = toolName === "box" ? "#007bff" : "rgba(255,255,255,0.05)";
    document.getElementById("btnToolBox").style.border = toolName === "box" ? "none" : "1px solid rgba(255,255,255,0.1)";
    document.getElementById("btnToolLasso").style.background = toolName === "lasso" ? "#007bff" : "rgba(255,255,255,0.05)";
    document.getElementById("btnToolLasso").style.border = toolName === "lasso" ? "none" : "1px solid rgba(255,255,255,0.1)";
    document.getElementById("btnToolPan").style.background = toolName === "pan" ? "#007bff" : "rgba(255,255,255,0.05)";
    document.getElementById("btnToolPan").style.border = toolName === "pan" ? "none" : "1px solid rgba(255,255,255,0.1)";
}

function clearSelection() {
    selectedProvinces.clear();
    updateSelectionStatus();
    draw();
}

function updateSelectionStatus() {
    markSelectionDirty();
    document.getElementById("selectionStatus").textContent = `Selected: ${selectedProvinces.size} provinces`;
    updateAdjacencyPanel();
    const stateCountEl = document.getElementById("selectedProvincesCount");
    if (stateCountEl) stateCountEl.innerText = `${selectedProvinces.size} selected`;
}

function updateAdjacencyPanel() {
    const countEl = document.getElementById("selectedStraitsCount");
    if (countEl) countEl.innerText = `${straits.length} total`;
    
    const createCtrl = document.getElementById("straitCreateControls");
    const listEl = document.getElementById("straitList");
    if (!createCtrl || !listEl) return;
    
    if (selectedProvinces.size === 2) {
        createCtrl.style.display = "flex";
    } else {
        createCtrl.style.display = "none";
    }
    
    listEl.innerHTML = "";
    if (selectedProvinces.size === 1) {
        const selectedId = Array.from(selectedProvinces)[0];
        const matches = straits.map((s, idx) => ({ ...s, idx })).filter(s => s.from === selectedId || s.to === selectedId);
        
        if (matches.length > 0) {
            for (const m of matches) {
                const other = m.from === selectedId ? m.to : m.from;
                const item = document.createElement("div");
                item.style.display = "flex";
                item.style.alignItems = "center";
                item.style.justifyContent = "space-between";
                item.style.background = "rgba(255,255,255,0.05)";
                item.style.padding = "4px 6px";
                item.style.borderRadius = "3px";
                item.innerHTML = `
                    <span>To ${other} (${m.type})</span>
                    <button onclick="deleteStrait(${m.idx})" style="background:#dc3545; color:white; border:none; padding:2px 6px; border-radius:3px; cursor:pointer; font-size:10px;">Del</button>
                `;
                listEl.appendChild(item);
            }
        } else {
            listEl.innerHTML = `<div style="font-style:italic; color:#aaa;">No adjacencies for this province.</div>`;
        }
    } else if (selectedProvinces.size !== 2) {
        listEl.innerHTML = `<div style="font-style:italic; color:#666;">Select 1 province to view, or 2 to create.</div>`;
    }
}

function saveStraits(showNotification = false) {
    fetch("/saveStraits", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(straits)
    })
    .then(r => r.json())
    .then(d => {
        if (d.status === "success") {
            console.log("Straits saved successfully.");
            if (showNotification) {
                alert("Straits saved successfully to straits.json!");
            }
        } else {
            alert("Error saving straits: " + d.error);
        }
    })
    .catch(e => console.error("Error saving straits:", e));
}

function toggleStraits() {
    showStraits = !showStraits;
    const btn = document.getElementById("btnToggleStraits");
    if (btn) {
        btn.innerText = showStraits ? "Hide Straits" : "Show Straits";
        btn.style.background = showStraits ? "rgba(255,255,255,0.05)" : "#007bff";
        btn.style.color = showStraits ? "#ccc" : "white";
    }
    draw();
}

function addStrait() {
    if (selectedProvinces.size !== 2) return;
    const arr = Array.from(selectedProvinces);
    const from = arr[0];
    const to = arr[1];
    const type = document.getElementById("straitType").value;
    
    const exists = straits.some(s => (s.from === from && s.to === to) || (s.from === to && s.to === from));
    if (exists) {
        alert("An adjacency already exists between these provinces.");
        return;
    }
    
    straits.push({ from, to, type, through: 0, name: "" });
    buildStraitAdjacency();
    saveStraits();
    updateAdjacencyPanel();
    draw();
}

function deleteStrait(idx) {
    straits.splice(idx, 1);
    buildStraitAdjacency();
    saveStraits();
    updateAdjacencyPanel();
    draw();
}

function exportAdjacenciesCSV() {
    let csv = "From;To;Type;Through;start_x;start_y;stop_x;stop_y;Comment\n";
    for (const s of straits) {
        const p1 = provinceCenters[s.from];
        const p2 = provinceCenters[s.to];
        const x1 = p1 ? Math.round(p1.x) : -1;
        const y1 = p1 ? Math.round(p1.y) : -1;
        const x2 = p2 ? Math.round(p2.x) : -1;
        const y2 = p2 ? Math.round(p2.y) : -1;
        csv += `${s.from};${s.to};${s.type};${s.through};${x1};${y1};${x2};${y2};${s.name || ""}\n`;
    }
    const blob = new Blob([csv], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "adjacencies.csv";
    link.click();
}

function drawStraits() {
    if (!showStraits) return;
    if (!straits || straits.length === 0) return;
    overlayCtx.save();
    const viewW = canvas.width / zoom;
    const viewH = canvas.height / zoom;
    
    for (const strait of straits) {
        const p1 = provinceCenters[strait.from];
        const p2 = provinceCenters[strait.to];
        if (!p1 || !p2) continue;
        
        const p1Visible = p1.x >= offsetX && p1.x <= offsetX + viewW && p1.y >= offsetY && p1.y <= offsetY + viewH;
        const p2Visible = p2.x >= offsetX && p2.x <= offsetX + viewW && p2.y >= offsetY && p2.y <= offsetY + viewH;
        if (!p1Visible && !p2Visible) continue;
        
        if (strait.type === "sea") {
            overlayCtx.strokeStyle = "rgba(0, 191, 255, 0.85)";
            overlayCtx.lineWidth = 2.0 / zoom;
            overlayCtx.setLineDash([4 / zoom, 3 / zoom]);
        } else if (strait.type === "canal") {
            overlayCtx.strokeStyle = "rgba(255, 215, 0, 0.85)";
            overlayCtx.lineWidth = 2.5 / zoom;
            overlayCtx.setLineDash([6 / zoom, 2 / zoom]);
        } else {
            overlayCtx.strokeStyle = "rgba(255, 99, 71, 0.85)";
            overlayCtx.lineWidth = 2.0 / zoom;
            overlayCtx.setLineDash([]);
        }
        
        overlayCtx.beginPath();
        overlayCtx.moveTo(p1.x, p1.y);
        overlayCtx.lineTo(p2.x, p2.y);
        overlayCtx.stroke();
        
        overlayCtx.fillStyle = overlayCtx.strokeStyle;
        overlayCtx.beginPath();
        overlayCtx.arc(p1.x, p1.y, 3 / zoom, 0, 2 * Math.PI);
        overlayCtx.arc(p2.x, p2.y, 3 / zoom, 0, 2 * Math.PI);
        overlayCtx.fill();
    }
    overlayCtx.restore();
}

function applySelectionLogic(newSelection, overrideMode) {
    markSelectionDirty();
    const mode = overrideMode || document.getElementById("selLogicMode").value;
    if (mode === "replace") {
        selectedProvinces = new Set(newSelection);
    } else if (mode === "add") {
        for (const key of newSelection) {
            selectedProvinces.add(key);
        }
    } else if (mode === "subtract") {
        for (const key of newSelection) {
            selectedProvinces.delete(key);
        }
    } else if (mode === "intersect") {
        selectedProvinces = new Set([...selectedProvinces].filter(key => newSelection.has(key)));
    } else if (mode === "xor") {
        for (const key of newSelection) {
            if (selectedProvinces.has(key)) {
                selectedProvinces.delete(key);
            } else {
                selectedProvinces.add(key);
            }
        }
    }
}

function selectAllProvincesOfSelectedCountry() {
    let targetProvinces = new Set();
    if (eraserMode || !selectedColor) {
        // Select all ownerless/unowned land provinces
        for (const keyStr in provinceCenters) {
            const key = parseInt(keyStr);
            const p = provinceCenters[keyStr];
            if (p && !p.isWater && !ownership[key]) {
                targetProvinces.add(key);
            }
        }
    } else {
        const countryObj = countries[selectedColor];
        if (countryObj) {
            targetProvinces = countryObj.provinces;
        }
    }
    
    applySelectionLogic(targetProvinces);
    updateSelectionStatus();
    requestDraw();
}

function toggleSelectedWater() {
    if (selectedProvinces.size === 0) return;
    beginEdit("Toggle land/water");
    
    for (const pid of selectedProvinces) {
        const center = provinceCenters[pid];
        if (center) {
            const wasWater = center.isWater;
            center.isWater = !wasWater;
            
            // Also update definitions
            const d = definitions[pid];
            if (d) {
                d.type = center.isWater ? "water" : "land";
            }
            
            if (center.isWater) {
                // If it became water, remove ownership
                const oldOwner = ownership[pid];
                if (oldOwner && countries[oldOwner]) {
                    countries[oldOwner].provinces.delete(pid);
                }
                delete ownership[pid];
            }
            
            // Update LUT color in real-time
            if (lutData) {
                const index = center.index;
                if (center.isWater) {
                    updateLutForProvince(index, [150, 180, 210], pid);
                } else {
                    const owner = ownership[pid];
                    if (owner && COLORS[owner]) {
                        updateLutForProvince(index, COLORS[owner], pid);
                    } else {
                        updateLutForProvince(index, [180, 180, 180], pid);
                    }
                }
            }
        }
    }
    
    commitEdit();
    // Clear cache to recalculate labels
    clearLabelCache();
    
    requestDraw();
}

/* ============================================================
   EDIT HISTORY (Undo / Redo)
   Diff-based: an edit records only the province entries whose
   ownership (or land/water flag) actually changed, so a 100-step
   history costs a few KB instead of full map snapshots.
   ============================================================ */
const HISTORY_LIMIT = 100;
let undoStack = [];
let redoStack = [];
let pendingEdit = null;

function normOwner(tag) { return tag ? tag : null; }

function snapshotOwnershipState() {
    const own = {};
    for (const pid in ownership) {
        const t = normOwner(ownership[pid]);
        if (t) own[pid] = t;
    }
    const water = {};
    for (const pid in provinceCenters) {
        if (provinceCenters[pid]) water[pid] = !!provinceCenters[pid].isWater;
    }
    return { own, water };
}

// Opens an edit transaction. Re-entrant: nested calls keep the outermost
// snapshot so a compound operation lands as a single undo step.
function beginEdit(label) {
    if (pendingEdit) { pendingEdit.depth++; return; }
    pendingEdit = { label: label || "Edit", depth: 1, base: snapshotOwnershipState() };
}

function cancelEdit() {
    if (!pendingEdit) return;
    if (--pendingEdit.depth > 0) return;
    pendingEdit = null;
}

// Closes the transaction and pushes an undo entry if anything changed.
function commitEdit() {
    if (!pendingEdit) return false;
    if (--pendingEdit.depth > 0) return false;

    const base = pendingEdit.base;
    const label = pendingEdit.label;
    pendingEdit = null;

    const now = snapshotOwnershipState();
    const ownDiff = {};
    const waterDiff = {};
    let changed = 0;

    const ownKeys = new Set(Object.keys(base.own).concat(Object.keys(now.own)));
    for (const pid of ownKeys) {
        const b = base.own[pid] || null;
        const a = now.own[pid] || null;
        if (b !== a) { ownDiff[pid] = [b, a]; changed++; }
    }
    for (const pid in now.water) {
        if (base.water[pid] !== undefined && base.water[pid] !== now.water[pid]) {
            waterDiff[pid] = [base.water[pid], now.water[pid]];
            changed++;
        }
    }

    if (changed === 0) return false;

    undoStack.push({ label, own: ownDiff, water: waterDiff, count: changed });
    if (undoStack.length > HISTORY_LIMIT) undoStack.shift();
    redoStack.length = 0;
    updateHistoryUI();
    markDirty();
    return true;
}

function setProvinceOwner(pid, tag) {
    const old = normOwner(ownership[pid]);
    if (old && countries[old]) {
        countries[old].provinces.delete(Number(pid));
        countries[old].provinces.delete(pid);
        dirtyCountries.add(old);
        // The country's shape changed, so its cached label spine is now stale.
        // Clearing it routes recomputation through the async worker (off the
        // render thread) instead of a stale synchronous main-thread relayout.
        countries[old].spines = null;
    }
    if (tag) {
        ownership[pid] = tag;
        if (countries[tag]) {
            countries[tag].provinces.add(Number(pid));
            dirtyCountries.add(tag);
            countries[tag].spines = null;
        }
    } else {
        delete ownership[pid];
    }
}

function applyHistoryEntry(entry, direction) {
    const idx = direction === "undo" ? 0 : 1;

    for (const pid in entry.water) {
        const center = provinceCenters[pid];
        if (!center) continue;
        center.isWater = entry.water[pid][idx];
        if (definitions[pid]) definitions[pid].type = center.isWater ? "water" : "land";
    }
    for (const pid in entry.own) {
        setProvinceOwner(pid, entry.own[pid][idx]);
    }

    updateLutData();
    clearLabelCache();
    updateCountryList();
    updateSelectionStatus();
    markDirty();
    draw();
}

function undoEdit() {
    if (pendingEdit) cancelEdit();
    const entry = undoStack.pop();
    if (!entry) { showToast("Nothing to undo"); return; }
    applyHistoryEntry(entry, "undo");
    redoStack.push(entry);
    updateHistoryUI();
    showToast("Undo: " + entry.label + " (" + entry.count + " provinces)");
}

function redoEdit() {
    const entry = redoStack.pop();
    if (!entry) { showToast("Nothing to redo"); return; }
    applyHistoryEntry(entry, "redo");
    undoStack.push(entry);
    updateHistoryUI();
    showToast("Redo: " + entry.label + " (" + entry.count + " provinces)");
}

function clearHistory() {
    undoStack = [];
    redoStack = [];
    pendingEdit = null;
    updateHistoryUI();
}

function updateHistoryUI() {
    const u = document.getElementById("btnUndo");
    const r = document.getElementById("btnRedo");
    if (u) {
        u.disabled = undoStack.length === 0;
        u.style.opacity = undoStack.length ? "1" : "0.4";
        u.title = undoStack.length ? "Undo " + undoStack[undoStack.length - 1].label + " (Ctrl+Z)" : "Nothing to undo";
    }
    if (r) {
        r.disabled = redoStack.length === 0;
        r.style.opacity = redoStack.length ? "1" : "0.4";
        r.title = redoStack.length ? "Redo " + redoStack[redoStack.length - 1].label + " (Ctrl+Shift+Z)" : "Nothing to redo";
    }
}

let toastTimer = null;
function showToast(message) {
    let el = document.getElementById("appToast");
    if (!el) {
        el = document.createElement("div");
        el.id = "appToast";
        el.className = "glass-panel";
        el.style.cssText = "position: fixed; bottom: 70px; left: 50%; transform: translateX(-50%) translateY(10px);" +
            "padding: 8px 16px; font-size: 12px; color: #fff; z-index: 3000; pointer-events: none;" +
            "opacity: 0; transition: opacity 0.18s ease, transform 0.18s ease; white-space: nowrap;";
        document.body.appendChild(el);
    }
    el.textContent = message;
    requestAnimationFrame(() => {
        el.style.opacity = "1";
        el.style.transform = "translateX(-50%) translateY(0)";
    });
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        el.style.opacity = "0";
        el.style.transform = "translateX(-50%) translateY(10px)";
    }, 2200);
}

function paintSelection() {
    if (selectedProvinces.size === 0) return;
    
    const targetTag = eraserMode ? null : selectedColor;
    beginEdit(targetTag ? ("Paint " + targetTag) : "Erase ownership");
    
    for (const key of selectedProvinces) {
        const old = ownership[key];
        if (old && countries[old]) {
            countries[old].provinces.delete(key);
            dirtyCountries.add(old);
        }
        
        if (targetTag) {
            ownership[key] = targetTag;
            countries[targetTag].provinces.add(key);
            dirtyCountries.add(targetTag);
        } else {
            delete ownership[key];
        }
    }
    
    selectedProvinces.clear();
    commitEdit();
    updateSelectionStatus();
    updateLutData();
    clearLabelCache();
    draw();
}

function isPointInPolygon(pt, poly) {
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

let selectionBox = null;
let isDragging = false;

function selectProvince(key, isShift) {
	if (key === undefined || key === 0) return;
	console.log("selectProvince key:", key, "metadata:", provinceCenters[key]);

	if (!eraserMode && isShift) {
		const clickedCountry = ownership[key];
		if (!clickedCountry) return;

		const name = prompt("Rename country:", countries[clickedCountry].name);
		if (name) {
			renameCountry(clickedCountry, name);
		}
		return;
	}

	if (eraserMode) {
		beginEdit("Erase province");
		const old = ownership[key];
		if (old && countries[old]) {
			countries[old].provinces.delete(key);	
			dirtyCountries.add(old);
		}
		delete ownership[key];
        if (provinceCenters[key]) {
            updateLutForProvince(provinceCenters[key].index, [180, 180, 180], key);
        }
        commitEdit();
        clearLabelCache();
        draw();
	}
	else {
		beginEdit("Paint province");
		const old = ownership[key];

		if (old && countries[old]) {
			countries[old].provinces.delete(key);
			dirtyCountries.add(old);
		}

		ownership[key] = selectedColor;
		countries[selectedColor].provinces.add(key);
		dirtyCountries.add(selectedColor);
        if (provinceCenters[key]) {
            updateLutForProvince(provinceCenters[key].index, COLORS[selectedColor], key);
        }
        commitEdit();
	}

	// Show the province panel with details
	const d = definitions[key];
	if (d) {
		document.getElementById("pnlId").textContent = key;
		document.getElementById("pnlColor").textContent = `[${d.color.join(", ")}]`;
		document.getElementById("pnlName").value = d.name;
		document.getElementById("pnlType").value = d.type;
		document.getElementById("pnlTerrain").value = d.terrain || "plains";
		document.getElementById("pnlDetailedTerrain").textContent = d.detailed_terrain || "None";
		document.getElementById("provincePanel").style.display = "block";
	}
}

function saveProvinceDetails() {
    const id = document.getElementById("pnlId").textContent;
    if (!definitions[id]) return;

    const newName = document.getElementById("pnlName").value;
    const newType = document.getElementById("pnlType").value;
    const newTerrain = document.getElementById("pnlTerrain").value;

    definitions[id].name = newName;
    definitions[id].type = newType;
    definitions[id].terrain = newTerrain;

    // Update water flag in centers metadata
    const parsedId = parseInt(id);
    if (provinceCenters[parsedId]) {
        provinceCenters[parsedId].isWater = (newType === "water");
        
        // Update LUT color in real-time
        if (lutData) {
            const index = provinceCenters[parsedId].index;
            if (newType === "water") {
                updateLutForProvince(index, [150, 180, 210], parsedId);
            } else {
                // Check if owned by a country
                const owner = ownership[parsedId];
                if (owner && COLORS[owner]) {
                    updateLutForProvince(index, COLORS[owner], parsedId);
                } else {
                    updateLutForProvince(index, [180, 180, 180], parsedId);
                }
            }
        }
    }
    
    // Clear cache to recalculate labels (as straight/curvy might change if type changes water status)
    clearLabelCache();
    
    draw();
}

function exportDefinitions() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(definitions, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "definitions.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
}

function getWorldPresetData() {
    const data = {
        countries: {},
        ownership: {},
        interests: {}
    };
    for (const tag in countries) {
        data.countries[tag] = {
            name: countries[tag].name,
            fullName: countries[tag].fullName || "",
            color: countries[tag].color,
            labelOffset: countries[tag].labelOffset || 0,
            labelXOffset: countries[tag].labelXOffset || 0,
            labelArcShift: countries[tag].labelArcShift || 0,
            curvatureScale: countries[tag].curvatureScale !== undefined ? countries[tag].curvatureScale : 1.0,
            fontSizeScale: countries[tag].fontSizeScale !== undefined ? countries[tag].fontSizeScale : 1.0,
            labelRotation: countries[tag].labelRotation !== undefined ? countries[tag].labelRotation : 0,
            labelStretch: countries[tag].labelStretch !== undefined ? countries[tag].labelStretch : 1.0
        };
    }
    for (const provId in ownership) {
        data.ownership[provId] = ownership[provId];
    }
    for (const tag in interests) {
        if (Object.keys(interests[tag]).length > 0) {
            data.interests[tag] = {};
            for (const provId in interests[tag]) {
                data.interests[tag][provId] = interests[tag][provId];
            }
        }
    }
    // Save state configuration along with presets
    const serializableStates = {};
    for (const stateId in states) {
        const s = states[stateId];
        serializableStates[stateId] = {
            id: s.id,
            name: s.name,
            color: s.color,
            controlStrength: s.controlStrength !== undefined ? s.controlStrength : 100,
            showGradient: s.showGradient || false,
            provinces: Array.from(s.provinces)
        };
    }
    data.states = serializableStates;
    return data;
}


// --- Save & Load Progress System ---

function exportSaveFile() {
    const data = getWorldPresetData();
    data.saveDate = new Date().toISOString();
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const dateStr = new Date().toISOString().slice(0, 10);
    
    const a = document.createElement("a");
    a.href = url;
    a.download = `mappa_mundi_save_${dateStr}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    markSaved();
}

function importSaveFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            applyLoadedSaveData(data);
            markSaved();
            alert("Save file loaded successfully!");
        } catch (err) {
            console.error("Failed to parse save file:", err);
            alert("Error loading save file. Invalid JSON format.");
        }
    };
    reader.readAsText(file);
    event.target.value = "";
}

function quickSaveLocalStorage() {
    try {
        const data = getWorldPresetData();
        data.saveDate = new Date().toISOString();
        localStorage.setItem("mappa_mundi_quicksave", JSON.stringify(data));
        markSaved();
        alert("Quick Save successful! Progress saved to browser storage.");
    } catch (e) {
        console.error("Quick save failed:", e);
        alert("Quick Save failed. Storage limit exceeded or storage blocked.");
    }
}

function quickLoadLocalStorage() {
    try {
        const jsonStr = localStorage.getItem("mappa_mundi_quicksave");
        if (!jsonStr) {
            alert("No Quick Save found in browser storage.");
            return;
        }
        const data = JSON.parse(jsonStr);
        applyLoadedSaveData(data);
        markSaved();
        alert("Quick Load successful! Restored session from browser storage.");
    } catch (e) {
        console.error("Quick load failed:", e);
        alert("Failed to restore Quick Save.");
    }
}

function applyLoadedSaveData(data) {
    if (!data || typeof data !== "object") {
        alert("Could not load save: the file is empty or not a valid save object.");
        return;
    }
    clearHistory();

    // Accept only a valid [r,g,b] triple; fall back to neutral grey otherwise so a
    // malformed colour can never corrupt the LUT / shader.
    const normColor = (col) => {
        if (Array.isArray(col) && col.length >= 3 &&
            col.slice(0, 3).every(n => typeof n === "number" && isFinite(n))) {
            return [col[0] & 255, col[1] & 255, col[2] & 255];
        }
        return [150, 150, 150];
    };
    const asProvinceList = (v) => Array.isArray(v) ? v.filter(p => Number.isFinite(Number(p))) : [];

    // Restore countries
    if (data.countries && typeof data.countries === "object") {
        for (const k in countries) delete countries[k];
        for (const k in COLORS) delete COLORS[k];
        for (const tag in data.countries) {
            const c = data.countries[tag];
            if (!c || typeof c !== "object") continue;
            const color = normColor(c.color);
            countries[tag] = {
                tag: tag,
                name: (typeof c.name === "string" && c.name) ? c.name : tag,
                fullName: typeof c.fullName === "string" ? c.fullName : "",
                color: color,
                labelOffset: Number(c.labelOffset) || 0,
                labelXOffset: Number(c.labelXOffset) || 0,
                labelArcShift: Number(c.labelArcShift) || 0,
                curvatureScale: c.curvatureScale !== undefined ? (Number(c.curvatureScale) || 1.0) : 1.0,
                fontSizeScale: c.fontSizeScale !== undefined ? (Number(c.fontSizeScale) || 1.0) : 1.0,
                labelRotation: Number(c.labelRotation) || 0,
                labelStretch: c.labelStretch !== undefined ? (Number(c.labelStretch) || 1.0) : 1.0,
                provinces: new Set(),
                // Recompute spines from scratch (via the worker) rather than trusting
                // persisted geometry, which may be stale for the loaded territory.
                spines: null
            };
            COLORS[tag] = color;
        }
    }
    
    // Restore ownership
    if (data.ownership && typeof data.ownership === "object") {
        for (const provId in ownership) delete ownership[provId];
        for (const provId in data.ownership) {
            const tag = data.ownership[provId];
            if (!countries[tag]) continue; // ignore ownership referencing unknown countries
            ownership[provId] = tag;
            countries[tag].provinces.add(parseInt(provId));
        }
    }
    
    // Restore states
    if (data.states && typeof data.states === "object") {
        states = {};
        provinceToState = {};
        for (const stateIdStr in data.states) {
            const s = data.states[stateIdStr];
            if (!s || typeof s !== "object") continue;
            const stateId = parseInt(stateIdStr);
            if (!Number.isFinite(stateId)) continue;
            const provList = asProvinceList(s.provinces);
            states[stateId] = {
                id: stateId,
                name: (typeof s.name === "string" && s.name) ? s.name : ("State " + stateId),
                color: normColor(s.color),
                controlStrength: s.controlStrength !== undefined ? (Number(s.controlStrength) || 100) : 100,
                showGradient: !!s.showGradient,
                provinces: new Set(provList)
            };
            for (const provId of provList) {
                provinceToState[provId] = stateId;
            }
        }
    }
    
    // Restore interests
    if (data.interests && typeof data.interests === "object") {
        interests = {};
        for (const tag in data.interests) {
            if (data.interests[tag] && typeof data.interests[tag] === "object") {
                interests[tag] = { ...data.interests[tag] };
            }
        }
    }
    
    updateCountryList();
    updateLutData();
    draw();
}

function saveWorldPreset() {
    const data = getWorldPresetData();
    fetch("/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data, null, 2)
    })
    .then(r => {
        if (r.ok) {
            markSaved();
            alert("Starting preset saved successfully to preset_ownership.json!");
        } else {
            alert("Failed to save starting preset.");
        }
    })
    .catch(e => {
        console.error(e);
        alert("Error saving starting preset. Make sure custom server.py is running: " + e.message);
    });
}

function exportWorldJSON() {
    const data = getWorldPresetData();
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "preset_ownership.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
}

function updateLutForProvince(idx, colorRgb, provId) {
    if (provId !== undefined && provinceToState[provId] !== undefined) {
        const stateId = provinceToState[provId];
        if (states[stateId]) {
            const st = states[stateId];
            if (st.showGradient && (st.controlStrength !== undefined ? st.controlStrength : 100) < 100) {
                colorRgb = [180, 180, 180];
            }
        }
    }
    const offset = idx * 4;
    lutData[offset] = colorRgb[0];
    lutData[offset+1] = colorRgb[1];
    lutData[offset+2] = colorRgb[2];
    
    // Also update packed alpha channel (cHash * 16 + sHash) for border rendering
    if (provId !== undefined) {
        const tag = ownership[provId];
        const stateId = provinceToState[provId];
        const cHash = (tag && countryColoring[tag]) ? countryColoring[tag] : 1;
        const sHash = (stateId !== undefined && stateColoring[stateId]) ? stateColoring[stateId] : 1;
        lutData[offset+3] = (cHash * 16) + sHash;
    }
    
    lutNeedsUpdate = true;
}

let stateColoring = {};
let countryColoring = {};

function buildGraphColoring() {
    stateColoring = {};
    countryColoring = {};

    const stateNeighbors = {};
    for (const sid in states) {
        stateNeighbors[sid] = new Set();
    }
    const countryNeighbors = {};
    for (const tag in countries) {
        countryNeighbors[tag] = new Set();
    }

    if (meta && meta.neighbors) {
        for (const p1Str in meta.neighbors) {
            const p1 = parseInt(p1Str, 10);
            const s1 = provinceToState[p1];
            const t1 = ownership[p1];
            const nbrs = meta.neighbors[p1Str];

            if (nbrs && Array.isArray(nbrs)) {
                for (let i = 0; i < nbrs.length; i++) {
                    const p2 = parseInt(nbrs[i], 10);
                    const s2 = provinceToState[p2];
                    const t2 = ownership[p2];

                    if (s1 !== undefined && s2 !== undefined && s1 !== s2 && states[s1] && states[s2]) {
                        stateNeighbors[s1].add(s2);
                        stateNeighbors[s2].add(s1);
                    }
                    if (t1 && t2 && t1 !== t2 && countries[t1] && countries[t2]) {
                        countryNeighbors[t1].add(t2);
                        countryNeighbors[t2].add(t1);
                    }
                }
            }
        }
    }

    for (const sid in stateNeighbors) {
        const used = new Set();
        for (const nbrSid of stateNeighbors[sid]) {
            if (stateColoring[nbrSid] !== undefined) {
                used.add(stateColoring[nbrSid]);
            }
        }
        let h = 1;
        while (used.has(h) && h < 15) {
            h++;
        }
        stateColoring[sid] = h;
    }

    for (const tag in countryNeighbors) {
        const used = new Set();
        for (const nbrTag of countryNeighbors[tag]) {
            if (countryColoring[nbrTag] !== undefined) {
                used.add(countryColoring[nbrTag]);
            }
        }
        let h = 1;
        while (used.has(h) && h < 15) {
            h++;
        }
        countryColoring[tag] = h;
    }
}

let suppressDirtyOnLut = false; // set while a view-only refresh (e.g. mapmode switch) runs

function updateLutData() {
    if (!lutData) return;
    // Any LUT rebuild after load reflects a state change; treat it as an edit
    // unless it was triggered by a view-only operation such as a mapmode switch.
    if (!suppressDirtyOnLut) markDirty();
    
    // Clear all to default unowned background (color 180, 180, 180)
    for (let i = 0; i < lutWidth * lutHeight; i++) {
        const offset = i * 4;
        lutData[offset] = 180;
        lutData[offset+1] = 180;
        lutData[offset+2] = 180;
    }
    
    if (activeMapmode === "state") {
        // Color by state
        // Draw water first so oceans/lakes are still blue in state mapmode
        for (const keyStr in meta.centers) {
            const centerData = meta.centers[keyStr];
            if (centerData.is_water) {
                const offset = centerData.index * 4;
                lutData[offset] = 150;
                lutData[offset+1] = 180;
                lutData[offset+2] = 210;
            }
        }
        for (const keyStr in provinceCenters) {
            const provId = parseInt(keyStr);
            const center = provinceCenters[keyStr];
            if (center && !center.isWater) {
                const stateId = provinceToState[provId];
                if (stateId !== undefined) {
                    let rgb;
                    if (states[stateId]) {
                        rgb = states[stateId].color;
                    } else {
                        // Generate deterministic distinct color for preloaded states
                        const r = (stateId * 57) % 200 + 40;
                        const g = (stateId * 113) % 200 + 40;
                        const b = (stateId * 179) % 200 + 40;
                        rgb = [r, g, b];
                    }
                    const offset = center.index * 4;
                    lutData[offset] = rgb[0];
                    lutData[offset+1] = rgb[1];
                    lutData[offset+2] = rgb[2];
                    let sHash = ((parseInt(stateId, 10) || 1) * 101 + 17) % 254 + 1;
                    lutData[offset+3] = sHash;
                }
            }
        }
    } else {
        // Color by country (political / interest)
        // Draw water first
        for (const keyStr in meta.centers) {
            const centerData = meta.centers[keyStr];
            if (centerData.is_water) {
                const offset = centerData.index * 4;
                lutData[offset] = 150;
                lutData[offset+1] = 180;
                lutData[offset+2] = 210;
            }
        }
        // Draw country ownership with proper country and state border hash encoding in LUT alpha
        for (const provIdStr in ownership) {
            const provId = parseInt(provIdStr);
            const tag = ownership[provIdStr];
            if (countries[tag] && provinceCenters[provId]) {
                const stateId = provinceToState[provId];
                const idx = provinceCenters[provId].index;
                const colorRgb = COLORS[tag];
                if (!colorRgb) continue;

                const offset = idx * 4;
                lutData[offset] = colorRgb[0];
                lutData[offset+1] = colorRgb[1];
                lutData[offset+2] = colorRgb[2];

                let sHash = 255;
                if (stateId !== undefined) {
                    sHash = ((parseInt(stateId, 10) || 1) * 101 + 17) % 254 + 1;
                }
                lutData[offset+3] = sHash;
            }
        }
    }
    
    // Populate packed country and state hashes in the alpha channel using Greedy Graph Coloring (0 adjacent collisions)
    if (activeMapmode !== "interest") {
        buildGraphColoring();
        for (let i = 0; i < lutWidth * lutHeight; i++) {
            lutData[i * 4 + 3] = 0;
        }
        for (const keyStr in provinceCenters) {
            const provId = parseInt(keyStr);
            const center = provinceCenters[keyStr];
            if (center) {
                const idx = center.index;
                const tag = ownership[provId];
                const stateId = provinceToState[provId];
                
                const cHash = (tag && countryColoring[tag]) ? countryColoring[tag] : 1;
                const sHash = (stateId !== undefined && stateColoring[stateId]) ? stateColoring[stateId] : 1;
                
                lutData[idx * 4 + 3] = cHash * 16 + sHash;
            }
        }
    } else {
        updateAllLutAlphas();
    }
    lutNeedsUpdate = true;
}

function updateAllLutAlphas() {
    if (!lutData) return;
    
    for (let i = 0; i < lutWidth * lutHeight; i++) {
        lutData[i * 4 + 3] = 0;
    }
    
    if (selectedColor && interests[selectedColor]) {
        for (const provIdStr in interests[selectedColor]) {
            const provId = parseInt(provIdStr);
            const level = interests[selectedColor][provId];
            const p = provinceCenters[provId];
            if (p) {
                lutData[p.index * 4 + 3] = level;
            }
        }
    }
    lutNeedsUpdate = true;
}

function setMapmode(mode) {
    activeMapmode = mode;
    suppressDirtyOnLut = true;   // switching mapmode is a view change, not an edit
    updateLutData();
    suppressDirtyOnLut = false;
    requestDraw();
}

function paintInterest() {
    if (!selectedColor) {
        alert("Please select a country first.");
        return;
    }
    if (selectedProvinces.size === 0) {
        alert("Please select one or more provinces to paint interest.");
        return;
    }
    const val = parseInt(document.getElementById("interestSlider").value);
    if (!interests[selectedColor]) {
        interests[selectedColor] = {};
    }
    for (const pid of selectedProvinces) {
        interests[selectedColor][pid] = val;
    }
    updateLutData();
    requestDraw();
}

function clearInterest() {
    if (!selectedColor) return;
    if (selectedProvinces.size === 0) return;
    if (interests[selectedColor]) {
        for (const pid of selectedProvinces) {
            delete interests[selectedColor][pid];
        }
    }
    updateLutData();
    requestDraw();
}

let colorPickerMode = false;

function activateColorPickerTool() {
    if (!selectedColor) {
        alert("Please select a country to recolour first.");
        return;
    }
    colorPickerMode = !colorPickerMode;
    const btn = document.getElementById("btnColorPickerTool");
    if (colorPickerMode) {
        btn.style.background = "#ff9500";
        btn.style.color = "black";
        btn.style.border = "1px solid #ff9500";
        canvas.style.cursor = "crosshair";
    } else {
        btn.style.background = "#333";
        btn.style.color = "white";
        btn.style.border = "1px solid #555";
        canvas.style.cursor = "default";
    }
}

function handleRenameFromInput(val) {
    if (!selectedColor || !val.trim()) return;
    renameCountry(selectedColor, val.trim());
    updateCountryList();
}

function handleLabelOffsetChange(val) {
    if (!selectedColor || !countries[selectedColor]) return;
    const offset = parseFloat(val);
    countries[selectedColor].labelOffset = offset;
    const disp = document.getElementById("labelOffsetDisp");
    if (disp) disp.textContent = val;
    dirtyCountries.add(selectedColor);
    requestDraw();
}

function handleLabelXOffsetChange(val) {
    if (!selectedColor || !countries[selectedColor]) return;
    const offset = parseFloat(val);
    countries[selectedColor].labelXOffset = offset;
    const disp = document.getElementById("labelXOffsetDisp");
    if (disp) disp.textContent = val;
    dirtyCountries.add(selectedColor);
    requestDraw();
}

function handleLabelArcShiftChange(val) {
    if (!selectedColor || !countries[selectedColor]) return;
    const offset = parseFloat(val);
    countries[selectedColor].labelArcShift = offset;
    const disp = document.getElementById("labelArcShiftDisp");
    if (disp) disp.textContent = val;
    dirtyCountries.add(selectedColor);
    requestDraw();
}

function handleCurvatureScaleChange(val) {
    if (!selectedColor || !countries[selectedColor]) return;
    const scale = parseFloat(val);
    countries[selectedColor].curvatureScale = scale;
    const disp = document.getElementById("curvatureScaleDisp");
    if (disp) disp.textContent = scale.toFixed(1);
    dirtyCountries.add(selectedColor);
    requestDraw();
}

function handleFontSizeScaleChange(val) {
    if (!selectedColor || !countries[selectedColor]) return;
    const scale = parseFloat(val);
    countries[selectedColor].fontSizeScale = scale;
    const disp = document.getElementById("fontSizeScaleDisp");
    if (disp) disp.textContent = scale.toFixed(2);
    dirtyCountries.add(selectedColor);
    requestDraw();
}

function handleLabelRotationChange(val) {
    if (!selectedColor || !countries[selectedColor]) return;
    const rot = parseFloat(val);
    countries[selectedColor].labelRotation = rot;
    const disp = document.getElementById("labelRotationDisp");
    if (disp) disp.textContent = val;
    dirtyCountries.add(selectedColor);
    requestDraw();
}

function handleLabelStretchChange(val) {
    if (!selectedColor || !countries[selectedColor]) return;
    const stretch = parseFloat(val);
    countries[selectedColor].labelStretch = stretch;
    const disp = document.getElementById("labelStretchDisp");
    if (disp) disp.textContent = stretch.toFixed(1);
    dirtyCountries.add(selectedColor);
    requestDraw();
}

function handleRecolourFromPicker(hex) {
    if (!selectedColor) return;
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    recolourCountry(selectedColor, [r, g, b]);
}

function recolourCountry(tag, newRgb) {
    if (!countries[tag]) return;
    countries[tag].color = newRgb;
    COLORS[tag] = newRgb;
    
    updateLutData();
    updateCountryList();
    requestDraw();
    
    // Refresh diplomacy panel if open
    const diploTagSpan = document.getElementById("diploCountryTag");
    if (diploTagSpan && diploTagSpan.innerText === tag) {
        openDiplomacyPanel(tag);
    }
}

const provinceIdCache = {};
function getProvinceIdAt(x, y) {
	if (x < 0 || y < 0 || x >= img.width || y >= img.height) return 0;
	const ix = Math.floor(x);
	const iy = Math.floor(y);
	const cacheKey = (iy << 16) | ix;
	if (provinceIdCache[cacheKey] !== undefined) {
		return provinceIdCache[cacheKey];
	}
	
	const idx = (iy * img.width + ix) * 4;
	const r = basePixels[idx];
	const g = basePixels[idx+1];
	const b = basePixels[idx+2];
	
	let result = r + g * 256 + b * 65536;
	if (result === 16777215) { // Pure white is boundary/ocean background
		result = 0;
	}
	provinceIdCache[cacheKey] = result;
	return result;
}

function screenToMap(clientX, clientY) {
	const rect = canvas.getBoundingClientRect();
	const x = clientX - rect.left;
	const y = clientY - rect.top;
	return [
		Math.floor(x / zoom + offsetX),
		Math.floor(y / zoom + offsetY)
	];
}

canvas.addEventListener("mousedown", e => {
	if (e.button === 2 || e.button === 1 || activeTool === "pan") { // Right/Middle click or Pan tool to pan
		isDragging = false;
		isPanning = true;
		currentMouseX = e.clientX;
		currentMouseY = e.clientY;
		startPanX = e.clientX;
		startPanY = e.clientY;
		startOffsetX = offsetX;
		startOffsetY = offsetY;
		e.preventDefault();
		return;
	}

	if (e.button === 0) { // Left click to select
		currentMouseX = e.clientX;
		currentMouseY = e.clientY;
		const [mapX, mapY] = screenToMap(e.clientX, e.clientY);
		isDragging = true;
		if (activeTool === "box") {
			selectionBox = { startX: mapX, startY: mapY, endX: mapX, endY: mapY };
		} else if (activeTool === "lasso") {
			lassoPoints = [{x: mapX, y: mapY}];
		}
	}
});

canvas.addEventListener("mousemove", e => {
	currentMouseX = e.clientX;
	currentMouseY = e.clientY;

	if (isPanning || isDragging) {
		hideHoverTooltip();
		requestDraw();
	} else {
		updateHoverTooltip(e.clientX, e.clientY);
	}
});

canvas.addEventListener("mouseleave", hideHoverTooltip);

// Live hover readout: shows the province under the cursor (id, owner, name)
// without triggering a full redraw. Throttled to only recompute when the
// cursor lands on a different province.
let lastHoverProvId = -1;
function updateHoverTooltip(clientX, clientY) {
	const tooltip = document.getElementById("hoverTooltip");
	if (!tooltip || !window.hoverReadoutEnabled) { if (tooltip) tooltip.style.display = "none"; return; }
	if (typeof img === "undefined" || !img) return;

	const [mapX, mapY] = screenToMap(clientX, clientY);
	const provId = getProvinceIdAt(mapX, mapY);

	if (!provId || provId === 0) {
		lastHoverProvId = -1;
		tooltip.style.display = "none";
		return;
	}

	if (provId !== lastHoverProvId) {
		lastHoverProvId = provId;
		const tag = ownership ? ownership[provId] : null;
		const country = tag && countries ? countries[tag] : null;
		const def = (typeof definitions !== "undefined") ? definitions[provId] : null;
		const provName = def && def.name ? def.name : "";
		const stateId = (typeof provinceToState !== "undefined") ? provinceToState[provId] : undefined;

		let html = `<span style="color:#7fbfff;font-weight:bold;">Province ${provId}</span>`;
		if (provName) html += ` <span style="color:#ccc;">${escapeHoverText(provName)}</span>`;
		if (country) {
			const c = country.color || [150, 150, 150];
			html += `<br><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:rgb(${c[0]},${c[1]},${c[2]});margin-right:4px;vertical-align:middle;"></span>`;
			html += `<span style="color:#ffd479;">${escapeHoverText(country.name || tag)}</span> <span style="color:#888;font-family:monospace;">[${tag}]</span>`;
		} else {
			html += `<br><span style="color:#888;">Unowned</span>`;
		}
		if (stateId !== undefined) html += `<br><span style="color:#9c9;font-size:9px;">State ${stateId}</span>`;
		tooltip.innerHTML = html;
	}

	tooltip.style.display = "block";
	// Offset from cursor, keep on-screen near the right/bottom edges
	const pad = 14;
	let left = clientX + pad;
	let top = clientY + pad;
	const rect = tooltip.getBoundingClientRect();
	if (left + rect.width > window.innerWidth) left = clientX - rect.width - pad;
	if (top + rect.height > window.innerHeight) top = clientY - rect.height - pad;
	tooltip.style.left = left + "px";
	tooltip.style.top = top + "px";
}

function hideHoverTooltip() {
	const tooltip = document.getElementById("hoverTooltip");
	if (tooltip) tooltip.style.display = "none";
	lastHoverProvId = -1;
}

function escapeHoverText(s) {
	return String(s).replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}

window.addEventListener("mouseup", e => {
	if (isPanning) {
		isPanning = false;
		
		// Process deferred worker responses since panning stopped
		if (deferredWorkerResponses.length > 0) {
			for (const data of deferredWorkerResponses) {
				processWorkerResponse(data);
			}
			deferredWorkerResponses = [];
		}

		if (e.button === 2) { // Right click country selection helper
			e.preventDefault();
			const dx = e.clientX - startPanX;
			const dy = e.clientY - startPanY;
			if (Math.hypot(dx, dy) < 5) {
				const [mapX, mapY] = screenToMap(startPanX, startPanY);
				const provId = getProvinceIdAt(mapX, mapY);
				if (provId && provId !== 0) {
					const tag = ownership[provId];
					if (tag) {
						if (e.ctrlKey && e.shiftKey) {
							// Ctrl + Shift + Right-Click: Add all provinces of the country to selection
							const countryObj = countries[tag];
							if (countryObj) {
								for (const p of countryObj.provinces) {
									selectedProvinces.add(p);
								}
								updateSelectionStatus();
								draw();
							}
						} else if (e.shiftKey) {
							// Shift + Right-Click: Select all provinces of the country (replace selection)
							const countryObj = countries[tag];
							if (countryObj) {
								selectedProvinces.clear();
								for (const p of countryObj.provinces) {
									selectedProvinces.add(p);
								}
								updateSelectionStatus();
								draw();
							}
						} else {
							// Plain Right-Click: Select country color brush and open diplomacy panel
							selectCountry(tag);
							openDiplomacyPanel(tag);
						}
					}
				}
			}
		}
		if (e.button === 1) { // Middle click handler (plain or Ctrl + middle click)
			e.preventDefault();
			const dx = e.clientX - startPanX;
			const dy = e.clientY - startPanY;
			if (Math.hypot(dx, dy) < 5) {
				const [mapX, mapY] = screenToMap(startPanX, startPanY);
				const provId = getProvinceIdAt(mapX, mapY);
				if (provId && provId !== 0) {
					const stateId = provinceToState[provId];
					if (stateId !== undefined) {
						// Auto-promote/import preloaded state if not already in states
						if (!states[stateId] && hoi4Data && hoi4Data.states[stateId]) {
							const hState = hoi4Data.states[stateId];
							const r = (stateId * 57) % 200 + 40;
							const g = (stateId * 113) % 200 + 40;
							const b = (stateId * 179) % 200 + 40;
							states[stateId] = {
								id: parseInt(stateId),
								name: hState.name || ("State " + stateId),
								color: [r, g, b],
								provinces: new Set(hState.provinces)
							};
						}

						if (states[stateId]) {
							const stateProvs = states[stateId].provinces;
							if (e.ctrlKey) {
								// Ctrl + Middle-Click toggle logic
								let isFullySelected = true;
								for (const p of stateProvs) {
									if (!selectedProvinces.has(p)) {
										isFullySelected = false;
										break;
									}
								}

								if (isFullySelected) {
									// Remove state from selection
									for (const p of stateProvs) {
										selectedProvinces.delete(p);
									}
								} else {
									// Select the whole state (add state provinces to selection)
									for (const p of stateProvs) {
										selectedProvinces.add(p);
									}
								}
								updateSelectionStatus();
								draw();
							} else if (e.shiftKey) {
								// Shift + Middle-Click: Add all selected provinces to this clicked state!
								if (selectedProvinces.size > 0) {
									const count = selectedProvinces.size;
									for (const p of selectedProvinces) {
										const oldStateId = provinceToState[p];
										if (oldStateId !== undefined && states[oldStateId]) {
											states[oldStateId].provinces.delete(p);
										}
										states[stateId].provinces.add(p);
										provinceToState[p] = stateId;
									}
									updateLutData();
									clearSelection();
									alert(`Successfully added ${count} provinces to state '${states[stateId].name}' [${stateId}]`);
								} else {
									alert("No provinces selected to add to this state!");
								}
							} else {
								// Plain Middle-Click: Select only this state
								selectedProvinces.clear();
								selectedProvinces.add(provId);
								selectStateProvinces();
							}
						}
					}
				}
			}
		}
		return;
	}

	if (!isDragging) return;
	isDragging = false;

	const [mapX, mapY] = screenToMap(e.clientX, e.clientY);
	const newSelection = new Set();

	if (activeTool === "box" && selectionBox) {
		selectionBox.endX = mapX;
		selectionBox.endY = mapY;

		const minX = Math.min(selectionBox.startX, selectionBox.endX);
		const maxX = Math.max(selectionBox.startX, selectionBox.endX);
		const minY = Math.min(selectionBox.startY, selectionBox.endY);
		const maxY = Math.max(selectionBox.startY, selectionBox.endY);

		const dx = maxX - minX;
		const dy = maxY - minY;

		if (dx < 3 && dy < 3) {
			// Single click
			if (selectionBox.startX >= 0 && selectionBox.startY >= 0 && selectionBox.startX < img.width && selectionBox.startY < img.height) {
				const key = getProvinceIdAt(selectionBox.startX, selectionBox.startY);
				if (key && key !== 0 && provinceCenters[key]) {
					if (colorPickerMode) {
						const clickedCountry = ownership[key];
						if (clickedCountry && clickedCountry !== selectedColor) {
							const targetColor = countries[clickedCountry].color;
							recolourCountry(selectedColor, targetColor);
						}
						colorPickerMode = false;
						const btn = document.getElementById("btnColorPickerTool");
						if (btn) {
							btn.style.background = "#333";
							btn.style.color = "white";
							btn.style.border = "1px solid #555";
						}
						canvas.style.cursor = "default";
						selectionBox = null;
						return;
					}
					if (e.shiftKey) {
						const clickedCountry = ownership[key];
						if (clickedCountry && countries[clickedCountry]) {
							const name = prompt("Rename country:", countries[clickedCountry].name);
							if (name) {
								renameCountry(clickedCountry, name);
								updateCountryList();
							}
						}
						selectionBox = null;
						return;
					}
					newSelection.add(key);
					
					// Show details in panel
					const d = definitions[key];
					if (d) {
						document.getElementById("pnlId").textContent = key;
						document.getElementById("pnlColor").textContent = `[${d.color.join(", ")}]`;
						document.getElementById("pnlName").value = d.name;
						document.getElementById("pnlType").value = d.type;
						document.getElementById("pnlTerrain").value = d.terrain || "plains";
						document.getElementById("pnlDetailedTerrain").textContent = d.detailed_terrain || "None";
						document.getElementById("provincePanel").style.display = "block";
					}
				}
			}
		} else {
			// Box selection
			for (const keyStr in provinceCenters) {
				const p = provinceCenters[keyStr];
				const key = parseInt(keyStr);
				if (p && p.x >= minX && p.x <= maxX && p.y >= minY && p.y <= maxY) {
					newSelection.add(key);
				}
			}
		}
		selectionBox = null;
	} else if (activeTool === "lasso" && lassoPoints && lassoPoints.length > 2) {
		// Lasso Selection using point-in-polygon
		for (const keyStr in provinceCenters) {
			const p = provinceCenters[keyStr];
			const key = parseInt(keyStr);
			if (p && isPointInPolygon(p, lassoPoints)) {
				newSelection.add(key);
			}
		}
		lassoPoints = [];
	}

	// If state mode is enabled, expand selection to state/subdivision level (check custom states first, then fallback to HOI4 states)
	if (selectionLevel === "state" && typeof provinceToState !== 'undefined') {
		const expanded = new Set();
		for (const key of newSelection) {
			const stateId = provinceToState[key];
			if (stateId !== undefined && states[stateId]) {
				for (const provId of states[stateId].provinces) {
					expanded.add(provId);
				}
			} else if (stateId !== undefined && hoi4Data && hoi4Data.states && hoi4Data.states[stateId]) {
				for (const provId of hoi4Data.states[stateId].provinces) {
					expanded.add(provId);
				}
			} else {
				expanded.add(key); // Fallback to province if not part of a state
			}
		}
		newSelection.clear();
		for (const key of expanded) {
			newSelection.add(key);
		}
	}

	const logicMode = e.ctrlKey ? "xor" : document.getElementById("selLogicMode").value;
	if (newSelection.size > 0 || logicMode === "replace") {
		applySelectionLogic(newSelection, logicMode);
	}

	// Process deferred worker responses since dragging stopped
	if (deferredWorkerResponses.length > 0) {
		for (const data of deferredWorkerResponses) {
			processWorkerResponse(data);
		}
		deferredWorkerResponses = [];
	}

	updateSelectionStatus();
	draw();
});

canvas.addEventListener("contextmenu", e => e.preventDefault());

// Double-click to select all provinces of a country (bypasses browser shift-right-click context menu override)
canvas.addEventListener("dblclick", e => {
    if (e.button === 0) { // Left double click
        const [mapX, mapY] = screenToMap(e.clientX, e.clientY);
        const provId = getProvinceIdAt(mapX, mapY);
        if (provId && provId !== 0) {
            const tag = ownership[provId];
            if (tag) {
                e.preventDefault();
                if (e.ctrlKey) {
                    // Ctrl + Double-Click: Add all provinces of the country to selection
                    const countryObj = countries[tag];
                    if (countryObj) {
                        for (const p of countryObj.provinces) {
                            selectedProvinces.add(p);
                        }
                        updateSelectionStatus();
                        draw();
                    }
                } else {
                    // Double-Click: Select all provinces of the country (replace selection)
                    const countryObj = countries[tag];
                    if (countryObj) {
                        selectedProvinces.clear();
                        for (const p of countryObj.provinces) {
                            selectedProvinces.add(p);
                        }
                        updateSelectionStatus();
                        draw();
                    }
                }
            }
        }
    }
});

canvas.addEventListener("wheel", e => {
	const rect = canvas.getBoundingClientRect();
	const mouseX = e.clientX - rect.left;
	const mouseY = e.clientY - rect.top;
	
	const worldX = mouseX / zoom + offsetX;
	const worldY = mouseY / zoom + offsetY;
	
	const zoomFactor = 1.1;
	if (e.deltaY < 0) {
		zoom *= zoomFactor;
	} else {
		zoom /= zoomFactor;
	}
	
	zoom = Math.max(0.05, Math.min(zoom, 80.0));
	
	offsetX = worldX - mouseX / zoom;
	offsetY = worldY - mouseY / zoom;
	
	requestDraw();
	e.preventDefault();
});

let drawRequested = false;
function requestDraw() {
    draw();
}

let lastFrameTime = performance.now();
let fpsArray = [];

function draw() {
    if (!drawRequested) {
        drawRequested = true;
        requestAnimationFrame(() => {
            performDraw();
            drawRequested = false;
        });
    }
}

function performDraw() {
    if (!gl) return;
    const start = performance.now();
    
    // Update offsets and selection bounds dynamically during drawing (decoupled from mousemove high-frequency callbacks)
    if (isPanning) {
        const dx = currentMouseX - startPanX;
        const dy = currentMouseY - startPanY;
        offsetX = startOffsetX - dx / zoom;
        offsetY = startOffsetY - dy / zoom;
    }
    if (isDragging) {
        const [mapX, mapY] = screenToMap(currentMouseX, currentMouseY);
        if (activeTool === "box" && selectionBox) {
            selectionBox.endX = mapX;
            selectionBox.endY = mapY;
        } else if (activeTool === "lasso" && lassoPoints) {
            // Only add point if it moved at least 2 pixels to avoid array flooding
            const lastPt = lassoPoints[lassoPoints.length - 1];
            if (!lastPt || Math.hypot(mapX - lastPt.x, mapY - lastPt.y) > 2) {
                lassoPoints.push({x: mapX, y: mapY});
            }
        }
    }
    
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0.13, 0.13, 0.13, 1.0);
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.useProgram(program);

    const U = uniformLocations;

    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, indexTexture);
    gl.uniform1i(U.u_indexTexture, 0);

    if (lutNeedsUpdate) {
        gl.activeTexture(gl.TEXTURE1);
        gl.bindTexture(gl.TEXTURE_2D, lutTexture);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, lutWidth, lutHeight, 0, gl.RGBA, gl.UNSIGNED_BYTE, lutData);
        lutNeedsUpdate = false;
    }
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, lutTexture);
    gl.uniform1i(U.u_lutTexture, 1);

    gl.activeTexture(gl.TEXTURE2);
    gl.bindTexture(gl.TEXTURE_2D, heightmapTexture);
    gl.uniform1i(U.u_heightmapTexture, 2);

    gl.activeTexture(gl.TEXTURE3);
    gl.bindTexture(gl.TEXTURE_2D, riversTexture);
    gl.uniform1i(U.u_riversTexture, 3);
    gl.uniform1f(U.u_showRivers, showRivers);



    gl.uniform2f(U.u_offset, offsetX, offsetY);
    gl.uniform1f(U.u_zoom, zoom);
    gl.uniform2f(U.u_resolution, canvas.width, canvas.height);
    gl.uniform2f(U.u_mapSize, img.width, img.height);
    gl.uniform2f(U.u_texelSize, 1.0 / img.width, 1.0 / img.height);
    gl.uniform1f(U.u_lutWidth, lutWidth);
    gl.uniform1f(U.u_lutHeight, lutHeight);
    gl.uniform1f(U.u_showHeightmap, showHeightmap);
    gl.uniform1f(U.u_showBorders, showBorders);
    gl.uniform1f(U.u_activeMapmode, activeMapmode === "interest" ? 1.0 : 0.0);

    gl.drawArrays(gl.TRIANGLES, 0, 6);
    const afterWebGL = performance.now();

    overlayCtx.setTransform(1, 0, 0, 1, 0, 0);
    overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
 
	if (selectionBox) {
		overlayCtx.save();
		const x1 = (selectionBox.startX - offsetX) * zoom;
		const y1 = (selectionBox.startY - offsetY) * zoom;
		const x2 = (selectionBox.endX - offsetX) * zoom;
		const y2 = (selectionBox.endY - offsetY) * zoom;

		const x = Math.min(x1, x2);
		const y = Math.min(y1, y2);
		const w = Math.abs(x1 - x2);
		const h = Math.abs(y1 - y2);

		overlayCtx.fillStyle = "rgba(0, 120, 255, 0.15)";
		overlayCtx.fillRect(x, y, w, h);
		
		overlayCtx.strokeStyle = "rgba(0, 120, 255, 0.7)";
		overlayCtx.lineWidth = 1;
		overlayCtx.setLineDash([4, 2]);
		overlayCtx.strokeRect(x, y, w, h);
		overlayCtx.restore();
	}

    overlayCtx.setTransform(zoom, 0, 0, zoom, -offsetX * zoom, -offsetY * zoom);

    // Draw lasso path in map coordinates
    if (activeTool === "lasso" && lassoPoints && lassoPoints.length > 1) {
        overlayCtx.save();
        overlayCtx.strokeStyle = "rgba(255, 165, 0, 0.8)";
        overlayCtx.lineWidth = 2 / zoom;
        overlayCtx.fillStyle = "rgba(255, 165, 0, 0.15)";
        overlayCtx.beginPath();
        overlayCtx.moveTo(lassoPoints[0].x, lassoPoints[0].y);
        for (let i = 1; i < lassoPoints.length; i++) {
            overlayCtx.lineTo(lassoPoints[i].x, lassoPoints[i].y);
        }
        overlayCtx.closePath();
        overlayCtx.fill();
        overlayCtx.stroke();
        overlayCtx.restore();
    }

    // Draw highlights for selected provinces in map coordinates
    if (selectedProvinces.size > 0) {
        // Rebuild the batched highlight path only when the selection changed
        // (version bump or size change) or when the zoom level changed (the arc
        // radius is expressed in screen pixels, i.e. 6/zoom world units).
        const cache = selectionHighlightCache;
        if (cache.version !== selectionVersion || cache.size !== selectedProvinces.size || cache.zoom !== zoom || !cache.path) {
            const path = new Path2D();
            const r = 6 / zoom;
            const TWO_PI = 2 * Math.PI;
            for (const pid of selectedProvinces) {
                const center = provinceCenters[pid];
                if (center) {
                    path.moveTo(center.x + r, center.y);
                    path.arc(center.x, center.y, r, 0, TWO_PI);
                }
            }
            cache.path = path;
            cache.version = selectionVersion;
            cache.size = selectedProvinces.size;
            cache.zoom = zoom;
        }
        overlayCtx.save();
        overlayCtx.fillStyle = "rgba(255, 0, 0, 0.4)";
        overlayCtx.strokeStyle = "rgba(255, 0, 0, 0.8)";
        overlayCtx.lineWidth = 1.5 / zoom;
        // Single fill + single stroke for the whole selection.
        overlayCtx.fill(cache.path);
        overlayCtx.stroke(cache.path);
        overlayCtx.restore();
    }

    drawStraits();
    const afterOverlay = performance.now();
    
    if (showLabels > 0.5) {
        drawLabels();
    } else if (DEBUG.panel) {
        debugPanel.innerHTML = window.debugPanelHeader || "";
    }
    const end = performance.now();
    
    dirtyCountries.clear();

    const now = performance.now();
    const frameTime = now - lastFrameTime;
    lastFrameTime = now;
    // Skip idle gaps (> 80ms) when calculating rendering frame rate
    if (frameTime <= 80.0) {
        fpsArray.push(1000 / frameTime);
        if (fpsArray.length > 30) fpsArray.shift();
    }
    const avgFps = fpsArray.reduce((a, b) => a + b, 0) / fpsArray.length;

    // Calculate this frame's profile times
    const totalTimeVal = end - start;
    const webglTime = (afterWebGL - start).toFixed(2);
    const overlayTime = (afterOverlay - afterWebGL).toFixed(2);
    const labelTime = (end - afterOverlay).toFixed(2);
    const totalTime = totalTimeVal.toFixed(2);

    // Lag Spike Analyzer: Capture frames taking longer than 32ms (representing < 30 FPS drops)
    if (totalTimeVal > 32.0) {
        lastSpikeData = {
            total: totalTime,
            webgl: webglTime,
            overlay: overlayTime,
            label: labelTime,
            queue: (typeof labelGenerationQueue !== 'undefined') ? labelGenerationQueue.size : 0,
            timestamp: new Date().toLocaleTimeString()
        };
        console.warn(`[Profiler Spike] Total: ${totalTime}ms | WebGL: ${webglTime}ms | Overlays: ${overlayTime}ms | Labels: ${labelTime}ms`);
    }

    if (DEBUG.panel && debugPanel) {
        let spikeHTML = "";
        if (lastSpikeData) {
            spikeHTML = `
                <div style="border-top: 1px solid rgba(255, 69, 58, 0.3); margin-top: 8px; padding-top: 6px; font-size: 10px; color: #ff6b6b; line-height: 1.4;">
                    <b>Last Spike (${lastSpikeData.timestamp}):</b><br>
                    • Total: <span style="font-family: monospace;">${lastSpikeData.total}ms</span> (Labels: ${lastSpikeData.label}ms)<br>
                    • Background Queue: <span style="font-family: monospace;">${lastSpikeData.queue}</span>
                </div>
            `;
        }

        window.debugPanelHeader = `
            <div style="border-bottom: 1px solid #0f0; margin-bottom: 8px; padding-bottom: 4px;">
                <b>WebGL Engine: ON</b><br>
                FPS: ${avgFps.toFixed(0)}<br>
                Frame Time: ${frameTime.toFixed(2)} ms<br>
                Zoom: ${zoom.toFixed(2)}x<br>
                Offset: (${offsetX.toFixed(0)}, ${offsetY.toFixed(0)})
            </div>
            <div style="font-size: 11px; line-height: 1.5; color: #ccc;">
                <b>Render Timings:</b><br>
                • WebGL Map: <span style="font-family: monospace; color: #0f0;">${webglTime}ms</span><br>
                • Overlays: <span style="font-family: monospace; color: #0f0;">${overlayTime}ms</span><br>
                • Label Layout: <span style="font-family: monospace; color: #0f0;">${labelTime}ms</span><br>
                • CPU Total: <span style="font-family: monospace; color: #0f0;">${totalTime}ms</span>
            </div>
            ${spikeHTML}
        `;
        // Sync visual panel innerHTML immediately
        debugPanel.innerHTML = window.debugPanelHeader;
    }
}

function resamplePath(path, count){

	const lengths = [0];

	for (let i = 1; i < path.length; i++) {
		const dx = path[i][0] - path[i - 1][0];
		const dy = path[i][1] - path[i - 1][1];
		lengths[i] = lengths[i - 1] + Math.hypot(dx, dy);
	}

    const total=lengths[lengths.length-1];
    const step=total/(count-1);

    const result=[];
    let j=0;

    for(let i=0;i<count;i++){
        const target=i*step;

        while(j < lengths.length-2 && lengths[j+1] < target) j++;

        const t=(target-lengths[j])/(lengths[j+1]-lengths[j]||1);

        const x=path[j][0]*(1-t)+path[j+1][0]*t;
        const y=path[j][1]*(1-t)+path[j+1][1]*t;

        result.push([x,y]);
    }

    return result;
}
// Simple and fast Priority Queue implementation for Dijkstra
class MinHeap {
	constructor() {
		this.heap = [];
	}
	push(item) {
		this.heap.push(item);
		let n = this.heap.length - 1;
		while (n > 0) {
			let parentN = Math.floor((n + 1) / 2) - 1;
			if (this.heap[n][1] >= this.heap[parentN][1]) break;
			let temp = this.heap[parentN];
			this.heap[parentN] = this.heap[n];
			this.heap[n] = temp;
			n = parentN;
		}
	}
	pop() {
		if (this.heap.length === 0) return null;
		const min = this.heap[0];
		const end = this.heap.pop();
		if (this.heap.length > 0) {
			this.heap[0] = end;
			let n = 0;
			const len = this.heap.length;
			while (true) {
				let child2N = (n + 1) * 2;
				let child1N = child2N - 1;
				let swap = null;
				if (child1N < len && this.heap[child1N][1] < this.heap[n][1]) {
					swap = child1N;
				}
				if (child2N < len && this.heap[child2N][1] < (swap === null ? this.heap[n][1] : this.heap[child1N][1])) {
					swap = child2N;
				}
				if (swap === null) break;
				let temp = this.heap[n];
				this.heap[n] = this.heap[swap];
				this.heap[swap] = temp;
				n = swap;
			}
		}
		return min;
	}
	isEmpty() {
		return this.heap.length === 0;
	}
}

function computeSpineForComponent(component, countryColor, countryName, curvatureScale = 1.0){
	if (component.length < 2) {
		const p = provinceCenters[component[0]];
		if (!p) return { spine: [], path: [], controlPoints: [], tension: 0 };
		const spine = [[p.x - 30, p.y], [p.x, p.y], [p.x + 30, p.y]];
		return { spine, path: spine, controlPoints: [[p.x, p.y]], tension: 0 };
	}

	let sumX = 0, sumY = 0, totalCount = 0;
	for (const id of component) {
		const p = provinceCenters[id];
		if (p) {
			sumX += p.x * p.count;
			sumY += p.y * p.count;
			totalCount += p.count;
		}
	}
	if (totalCount === 0) return { spine: [], path: [], controlPoints: [], tension: 0 };

	const meanX_raw = sumX / totalCount;
	const meanY_raw = sumY / totalCount;

	// Calculate standard deviation of distances from the raw center to identify appendages
	let sumDistSq = 0;
	for (const id of component) {
		const p = provinceCenters[id];
		if (p) {
			const dx = p.x - meanX_raw;
			const dy = p.y - meanY_raw;
			sumDistSq += (dx * dx + dy * dy) * p.count;
		}
	}
	const stdDev = Math.sqrt(sumDistSq / totalCount);

	// Filter out far-off outlier appendages (e.g. islands, remote corridor wings) beyond 1.6 * stdDev
	const filtered = [];
	let filteredCount = 0;
	for (const id of component) {
		const p = provinceCenters[id];
		if (p) {
			const dx = p.x - meanX_raw;
			const dy = p.y - meanY_raw;
			const dist = Math.hypot(dx, dy);
			if (dist <= 1.6 * stdDev) {
				filtered.push(id);
				filteredCount += p.count;
			}
		}
	}

	// Use filtered subset (main body) if valid, otherwise fallback to the full component
	const activeComp = (filtered.length >= 2 && filtered.length >= component.length * 0.4) ? filtered : component;
	const activeCount = (filtered.length >= 2 && filtered.length >= component.length * 0.4) ? filteredCount : totalCount;

	// Recompute mean for the active main-body component
	let activeSumX = 0, activeSumY = 0;
	for (const id of activeComp) {
		const p = provinceCenters[id];
		if (p) {
			activeSumX += p.x * p.count;
			activeSumY += p.y * p.count;
		}
	}
	const meanX = activeSumX / activeCount;
	const meanY = activeSumY / activeCount;

	// Calculate covariance matrix of active component coordinates (scaling down to prevent float64 overflow)
	let varX = 0, varY = 0, covXY = 0;
	for (const id of activeComp) {
		const p = provinceCenters[id];
		if (p) {
			const dx = (p.x - meanX) / 1000.0;
			const dy = (p.y - meanY) / 1000.0;
			varX += dx * dx * p.count;
			varY += dy * dy * p.count;
			covXY += dx * dy * p.count;
		}
	}

	// Calculate eigenvalues
	const trace = varX + varY;
	const det = varX * varY - covXY * covXY;
	const diff = Math.sqrt(Math.max(0.0, trace * trace - 4.0 * det)) / 2;
	const L1 = trace / 2 + diff; // Primary eigenvalue

	// Solve for primary eigenvector (vx, vy)
	let vx = 1, vy = 0;
	if (Math.abs(covXY) > 1e-4) {
		vx = L1 - varY;
		vy = covXY;
		const len = Math.hypot(vx, vy);
		if (len > 0) {
			vx /= len;
			vy /= len;
		}
	} else {
		if (varX > varY) {
			vx = 1; vy = 0;
		} else {
			vx = 0; vy = 1;
		}
	}

	// Find the projections of the active main body provinces along primary axis
	let minProj = Infinity, maxProj = -Infinity;
	for (const id of activeComp) {
		const p = provinceCenters[id];
		if (p) {
			const dx = p.x - meanX;
			const dy = p.y - meanY;
			const proj = dx * vx + dy * vy;
			if (proj < minProj) minProj = proj;
			if (proj > maxProj) maxProj = proj;
		}
	}

	// Divide the active main body into 3 segments along its axis to capture curvature
	let sumPerpL = 0, countL = 0;
	let sumPerpM = 0, countM = 0;
	let sumPerpR = 0, countR = 0;

	const segmentLimit = (maxProj - minProj) / 3;
	const threshold1 = minProj + segmentLimit;
	const threshold2 = minProj + 2 * segmentLimit;

	for (const id of activeComp) {
		const p = provinceCenters[id];
		if (p) {
			const dx = p.x - meanX;
			const dy = p.y - meanY;
			const proj = dx * vx + dy * vy;
			const perp = -dx * vy + dy * vx;

			if (proj < threshold1) {
				sumPerpL += perp * p.count;
				countL += p.count;
			} else if (proj < threshold2) {
				sumPerpM += perp * p.count;
				countM += p.count;
			} else {
				sumPerpR += perp * p.count;
				countR += p.count;
			}
		}
	}

	const perpL = (sumPerpL / (countL || 1)) * curvatureScale;
	const perpM = (sumPerpM / (countM || 1)) * curvatureScale;
	const perpR = (sumPerpR / (countR || 1)) * curvatureScale;

	const pad = 0.75;
	const midProj = (minProj + maxProj) / 2;

	const P0 = [
		meanX + minProj * pad * vx - perpL * vy,
		meanY + minProj * pad * vy + perpL * vx
	];
	const P3 = [
		meanX + maxProj * pad * vx - perpR * vy,
		meanY + maxProj * pad * vy + perpR * vx
	];
	const M = [
		meanX + midProj * pad * vx - perpM * vy,
		meanY + midProj * pad * vy + perpM * vx
	];

	const P1 = [
		2 * M[0] - (P0[0] + P3[0]) / 2,
		2 * M[1] - (P0[1] + P3[1]) / 2
	];

	const spine = [];
	for (let i = 0; i <= 15; i++) {
		const t = i / 15;
		const mt = 1 - t;
		const x = mt*mt * P0[0] + 2*mt*t * P1[0] + t*t * P3[0];
		const y = mt*mt * P0[1] + 2*mt*t * P1[1] + t*t * P3[1];
		spine.push([x, y]);
	}

	return {
		spine: spine,
		path: spine,
		controlPoints: [P0, M, P3],
		tension: 0.5,
		vx: vx,
		vy: vy,
		meanX: meanX,
		meanY: meanY,
		projStart: minProj * pad,
		projEnd: maxProj * pad
	};
}

function splitIntoTwoLines(text) {
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
function drawLabels(){
	if (zoom >= 1.5) {
		if (DEBUG.panel) {
			debugPanel.innerHTML = window.debugPanelHeader || "";
		}
		return;
	}
	const ctx = overlayCtx;

	ctx.globalAlpha = 1;
	ctx.lineWidth = 1;

	if(DEBUG.panel){
		debugPanel.innerHTML = window.debugPanelHeader || "";
	}

    const w=baseCanvas.width, h=baseCanvas.height;
    const data=basePixels;

	if (typeof labelWorker !== 'undefined' && labelWorker && dirtyCountries.size > 0) {
		labelWorker.postMessage({
			action: "updateOwnership",
			ownership: ownership
		});
	}


window.toggleMapLabelMode = function(enabled) {
    useOfficialNames = enabled;
    clearLabelCache();
    requestDraw();
};

	function generateLabelsForCountry(o, fromWorker = false) {
		try {
		const country = countries[o];
		if (!country || country.provinces.size === 0) return;

		const targetName = useOfficialNames ? (country.fullName || country.name) : country.name;
		if (!targetName || targetName.trim() === "") {
			labelCache[o] = { labels: [] };
			return;
		}
		if (!country.displayName || country._lastCleanName !== targetName) {
			let textVal = targetName;
			if (textVal.toLowerCase().includes("placeholder")) {
				textVal = country.tag;
			}
			country.displayName = textVal.toUpperCase();
			country._lastCleanName = targetName;
		}
		const text = country.displayName;
		const curvatureScale = country.curvatureScale !== undefined ? country.curvatureScale : 1.0;

		// If spines are dirty/empty, offload calculation to Web Worker if available
		if (!country.spines && typeof labelWorker !== 'undefined' && labelWorker && !fromWorker) {
			if (!country.labelGenerating) {
				country.labelGenerating = true;
				labelWorker.postMessage({
					action: "compute",
					tag: o,
					provinces: Array.from(country.provinces),
					text: text,
					curvatureScale: curvatureScale,
					ownership: ownership
				});
			}
			return; // Defer execution; wait for worker callback!
		}
		const labelOffset = country.labelOffset || 0;
		const labelXOffset = country.labelXOffset || 0;
		const labelArcShift = country.labelArcShift || 0;
		const fontSizeScale = country.fontSizeScale !== undefined ? country.fontSizeScale : 1.0;
		const labelRotation = country.labelRotation !== undefined ? country.labelRotation : 0;
		const labelStretch = country.labelStretch !== undefined ? country.labelStretch : 1.0;

		// Find contiguous components using BFS
		const provincesSet = country.provinces;
		const visited = new Set();
		const components = [];

		for (const provId of provincesSet) {
			if (visited.has(provId)) continue;

			const component = [];
			const queue = [provId];
			let queueHead = 0;
			visited.add(provId);

			while (queueHead < queue.length) {
				const curr = queue[queueHead++];
				component.push(curr);

				for (const n of provinceNeighbors[curr] || []) {
					if (provincesSet.has(n) && !visited.has(n)) {
						visited.add(n);
						queue.push(n);
					}
				}
				for (const n of straitAdj[curr] || []) {
					if (provincesSet.has(n) && !visited.has(n)) {
						visited.add(n);
						queue.push(n);
					}
				}
			}
			components.push(component);
		}

		const labels = [];
		for (const comp of components) {
			if (comp.length < 4) continue; // Skip very small components

			const result = computeSpineForComponent(comp, o, text, curvatureScale);
			if (result.spine.length < 2) continue;

			let compArea = 0;
			for (const id of comp) {
				const center = provinceCenters[id];
				if (center) compArea += center.count;
			}
			const thickness = Math.max(30, Math.min(120, Math.sqrt(compArea) * 0.55));
			const spine = result.spine;
			const path = result.path;
			const controlPoints = result.controlPoints;

			const P0 = spine[0];
			const P3 = spine[spine.length - 1];

			const P1 = (controlPoints && controlPoints.length > 0) ? controlPoints[0] : [
				(P0[0] + P3[0]) / 2,
				(P0[1] + P3[1]) / 2
			];

			let fontSize = Math.min(180, thickness * 0.75);

			// Precompute letter layouts to avoid slow operations at draw time
			ctx.save();
			ctx.font = `bold ${fontSize}px Georgia`;
			ctx.textAlign = "center";
			ctx.textBaseline = "middle";

			const cumulative = [0];
			for (let i = 1; i < spine.length; i++) {
				const dx = spine[i][0] - spine[i - 1][0];
				const dy = spine[i][1] - spine[i - 1][1];
				cumulative[i] = cumulative[i - 1] + Math.hypot(dx, dy);
			}
			const totalLen = cumulative[cumulative.length - 1];

			function getPointAndTangentAt(dist) {
				if (dist <= 0) {
					const dx = spine[1][0] - spine[0][0];
					const dy = spine[1][1] - spine[0][1];
					const len = Math.hypot(dx, dy) || 1;
					return [
						spine[0][0] + (dx / len) * dist,
						spine[0][1] + (dy / len) * dist,
						dx,
						dy
					];
				}
				if (dist >= totalLen) {
					const lastIdx = spine.length - 1;
					const dx = spine[lastIdx][0] - spine[lastIdx - 1][0];
					const dy = spine[lastIdx][1] - spine[lastIdx - 1][1];
					const len = Math.hypot(dx, dy) || 1;
					return [
						spine[lastIdx][0] + (dx / len) * (dist - totalLen),
						spine[lastIdx][1] + (dy / len) * (dist - totalLen),
						dx,
						dy
					];
				}
				let x = spine[0][0];
				let y = spine[0][1];
				let dx = spine[1][0] - spine[0][0];
				let dy = spine[1][1] - spine[0][1];
				for (let i = 1; i < cumulative.length; i++) {
					if (cumulative[i] >= dist) {
						const fraction = (dist - cumulative[i - 1]) / (cumulative[i] - cumulative[i - 1] || 1);
						const curr = spine[i];
						const prev = spine[i - 1];
						x = prev[0] * (1 - fraction) + curr[0] * fraction;
						y = prev[1] * (1 - fraction) + curr[1] * fraction;
						dx = curr[0] - prev[0];
						dy = curr[1] - prev[1];
						break;
					}
				}
				return [x, y, dx, dy];
			}


			const margin = Math.min(thickness * 0.15, totalLen * 0.04);
			const startDist = margin;
			const endDist = totalLen - margin;
			const len = endDist - startDist;

			if (len < 20) {
				ctx.restore();
				continue;
			}

			const angle_straight = Math.atan2(P3[1] - P0[1], P3[0] - P0[0]);

			// Determine if we should split the text into two lines (multi-line labels)
			const aspect = totalLen / thickness;
			let lines = [text];
			if (text.includes(" ") && text.length > 12) {
				const baseWidth = ctx.measureText(text).width;
				const scale_single = len / (baseWidth * 1.20);
				console.log(`[SPLIT CHECK] ${o} (${text}) | scale_single: ${scale_single.toFixed(3)} | totalLen: ${totalLen.toFixed(1)} | len: ${len.toFixed(1)} | thickness: ${thickness.toFixed(1)} | aspect: ${aspect.toFixed(2)}`);
				// Split only if single line scales down heavily, and country has enough vertical/horizontal space (and isn't narrow)
				if (scale_single < 1.15 && totalLen >= 30 && thickness >= 20 && aspect < 3.2) {
					const parts = splitIntoTwoLines(text);
					if (parts[1] !== "") {
						lines = parts;
					}
				}
			}

			// Calculate unified scale and effective font size based on the longest line
			let maxBaseTotal = 0;
			for (const line of lines) {
				const letters = line.split('');
				const baseWidths = letters.map(ch => ctx.measureText(ch).width);
				const baseTotal = baseWidths.reduce((a, b) => a + b, 0);
				if (baseTotal > maxBaseTotal) {
					maxBaseTotal = baseTotal;
				}
			}

			let scale = len / (maxBaseTotal * 1.20); 
			scale = Math.min(scale, 1.10);
			scale = Math.max(scale, 0.05);

			let effectiveFont = fontSize * scale * 0.94 * fontSizeScale;
			if (effectiveFont < 4) {
				effectiveFont = 4;
			}

			// Determine automatic stretching based on aspect ratio
			const autoStretch = Math.min(3.0, Math.max(1.0, 1.0 + (aspect - 1.5) * 0.8));

			// Precompute character widths and line layout parameters for clamping and search
			const lineLayouts = [];
			let maxWordLen = 0;
			for (let lIdx = 0; lIdx < lines.length; lIdx++) {
				const lineText = lines[lIdx];
				const letters = lineText.split('');
				ctx.save();
				ctx.font = `bold ${effectiveFont}px Georgia`;
				const letterWidths = letters.map(ch => ctx.measureText(ch).width);
				ctx.restore();
				const lineTotalW = letterWidths.reduce((a, b) => a + b, 0);
				
				let lineGap = 0;
				if (lines.length === 2) {
					lineGap = effectiveFont * 0.06;
				} else {
					lineGap = letters.length > 1 ? (len - lineTotalW) / (letters.length - 1) : 0;
					lineGap = Math.max(0, lineGap);
					const maxGap = effectiveFont * (0.12 + Math.min(0.28, (aspect - 1.5) * 0.1));
					if (lineGap > maxGap) lineGap = maxGap;
				}
				lineGap *= labelStretch * autoStretch;
				const maxFinalGap = effectiveFont * 0.45;
				if (lineGap > maxFinalGap) lineGap = maxFinalGap;
				
				const wordLen = lineTotalW + (letters.length > 1 ? (letters.length - 1) * lineGap : 0);
				if (wordLen > maxWordLen) {
					maxWordLen = wordLen;
				}
				const lineStartDistAdjusted = startDist + (len - wordLen) / 2;
				
				lineLayouts.push({
					letters,
					widths: letterWidths,
					gap: lineGap,
					startDistAdjusted: lineStartDistAdjusted
				});
			}

			const maxShift = Math.max(0, (len - maxWordLen) / 2);

			// Calculate weighted median projection of the provinces to center the text label
			let totalWeight = 0;
			const projWeights = [];
			for (const id of comp) {
				const center = provinceCenters[id];
				if (center) {
					const proj = (center.x - result.meanX) * result.vx + (center.y - result.meanY) * result.vy;
					projWeights.push({ proj, count: center.count });
					totalWeight += center.count;
				}
			}
			projWeights.sort((a, b) => a.proj - b.proj);
			let accumWeights = 0;
			let medianProj = 0;
			for (const item of projWeights) {
				accumWeights += item.count;
				if (accumWeights >= totalWeight * 0.5) {
					medianProj = item.proj;
					break;
				}
			}
			const medianDistFromStart = medianProj - result.projStart;
			const targetCenterDist = Math.max(startDist, Math.min(endDist, medianDistFromStart));
			const defaultCenterDist = startDist + len / 2;
			const targetHShift = Math.max(-maxShift, Math.min(maxShift, targetCenterDist - defaultCenterDist));

			// Compute a unified midpoint normal of the spine to align stacked lines parallelly and prevent shearing
			const midDist = startDist + len / 2;
			const [mx, my, mdx, mdy] = getPointAndTangentAt(midDist);
			const mLen = Math.hypot(mdx, mdy) || 1;
			const mnx = -mdy / mLen;
			const mny = mdx / mLen;

			// Calculate the perpendicular offset from the spine midpoint to the country's centroid
			const centroidDx = result.meanX - mx;
			const centroidDy = result.meanY - my;
			const baseAutoOffset = centroidDx * mnx + centroidDy * mny;

			// Snap directly to the computed mathematical PCA spine (no shifting or pixel checks needed)
			const autoXOffset = 0;
			const autoOffset = 0;
			const computedLetters = [];

			for (let lIdx = 0; lIdx < lines.length; lIdx++) {
				const lineText = lines[lIdx];
				const letters = lineText.split('');

				ctx.save();
				ctx.font = `bold ${effectiveFont}px Georgia`;
				const w = letters.map(ch => ctx.measureText(ch).width);
				const totalW = w.reduce((a, b) => a + b, 0);

				let gap = 0;
				if (lines.length === 2) {
					// For stacked/multi-line text, keep letters tight and cohesive
					gap = effectiveFont * 0.06;
				} else {
					// For single-line text, allow slight spreading but clamp tightly to avoid sparse lettering
					gap = letters.length > 1 ? (len - totalW) / (letters.length - 1) : 0;
					gap = Math.max(0, gap);
					const maxGap = effectiveFont * (0.12 + Math.min(0.28, (aspect - 1.5) * 0.1));
					if (gap > maxGap) gap = maxGap;
				}
				gap *= labelStretch * autoStretch;
				const maxFinalGap = effectiveFont * 0.45;
				if (gap > maxFinalGap) gap = maxFinalGap;

				const wordLen = totalW + (letters.length > 1 ? (letters.length - 1) * gap : 0);
				let startDistAdjusted = startDist + (len - wordLen) / 2;

				const finalHShift = autoXOffset;
				let currentOffset = 0;
				for (let i = 0; i < letters.length; i++) {
					const charW = w[i];
					const dist = startDistAdjusted + currentOffset + charW / 2 + finalHShift + labelArcShift;
					currentOffset += charW + gap;

					const [x, y, dx, dy] = getPointAndTangentAt(dist);

					let lineOffset = 0;
					if (lines.length === 2) {
						// Shift line 1 up and line 2 down perpendicular to the path direction (1.1x line height)
						if (lIdx === 0) {
							lineOffset = -effectiveFont * 0.55;
						} else {
							lineOffset = effectiveFont * 0.55;
						}
					}

					let px = x + mnx * (lineOffset + autoOffset + labelOffset);
					let py = y + mny * (lineOffset + autoOffset + labelOffset);
					px += labelXOffset;

					const angle_local = Math.atan2(dy, dx);
					let diff = angle_local - angle_straight;
					diff = Math.atan2(Math.sin(diff), Math.cos(diff));

					const rotationDamping = 0.95;
					let angle = angle_straight + diff * rotationDamping;

					// Rotate the entire label as a single rigid body around the midpoint of the spine
					if (labelRotation !== 0) {
						const rad = (labelRotation * Math.PI) / 180;
						const cosRot = Math.cos(rad);
						const sinRot = Math.sin(rad);
						const rx = px - mx;
						const ry = py - my;
						px = mx + rx * cosRot - ry * sinRot;
						py = my + ry * cosRot + rx * sinRot;
						angle += rad;
					}

					computedLetters.push({
						char: letters[i],
						x: px,
						y: py,
						angle: angle
					});
				}
				ctx.restore();
			}
			ctx.restore();

			labels.push({
				spine,
				path,
				controlPoints,
				thickness,
				provCount: comp.length,
				tension: result.tension,
				fontSize: fontSize * fontSizeScale,
				effectiveFont,
				letters: computedLetters,
				text: text
			});
		}

		labelCache[o] = { labels };
		} catch (err) {
			console.error("Error generating labels for country " + o + ":", err);
			labelCache[o] = { labels: [] }; // Safe fallback
		}
	}

	for(const o in countries){
		const country = countries[o];
		if (!country || country.provinces.size === 0) continue;

		let cached = labelCache[o];

		if (!cached || dirtyCountries.has(o)) {
			// Synchronous update for manual/dirty triggers (e.g. painting)
			if (dirtyCountries.has(o)) {
				generateLabelsForCountry(o);
				// generateLabelsForCountry may defer to the async worker (when the
				// spine was invalidated by a territory change), leaving the cache
				// unset. In that case fall back to the previous cached labels for
				// this frame; the worker callback will refresh them shortly.
				cached = labelCache[o] || cached;
				labelGenerationQueue.delete(o);
			} else {
				// Queue for asynchronous generation on subsequent frames if not already generating or queued
				if (!country.labelGenerating && !labelGenerationQueue.has(o)) {
					labelGenerationQueue.add(o);
					labelCache[o] = { labels: [] }; // Set placeholder cache to avoid re-queueing next frame
				}
				continue;
			}
		}

		// Nothing to draw yet (e.g. first layout still pending in the worker).
		if (!cached || !cached.labels) continue;

		// Draw curved/rotated labels along spine using cached layout
		for (const label of cached.labels) {
			const thickness = label.thickness;
			const spine = label.spine;
			const path = label.path;
			const controlPoints = label.controlPoints;

			const P0 = spine[0];
			const P3 = spine[spine.length - 1];
			
			// Viewport culling
			const minX = Math.min(P0[0], P3[0]) - thickness;
			const maxX = Math.max(P0[0], P3[0]) + thickness;
			const minY = Math.min(P0[1], P3[1]) - thickness;
			const maxY = Math.max(P0[1], P3[1]) + thickness;
			
			const vpLeft = offsetX;
			const vpRight = offsetX + canvas.width / zoom;
			const vpTop = offsetY;
			const vpBottom = offsetY + canvas.height / zoom;
			if (maxX < vpLeft || minX > vpRight || maxY < vpTop || minY > vpBottom) {
				continue;
			}

			// Size culling: only applied when tiny labels are not forced visible.
			if (!alwaysShowSmallCountryLabels) {
				// Only remove labels for truly small micro-states (e.g., Kosovo, Montenegro)
				// For larger countries with long official names, let the font scale down so they remain visible.
				const isMicroState = label.provCount < 3 || label.thickness < 32;
				if (isMicroState && label.effectiveFont * zoom < 8.0) {
					continue;
				}
				if (label.effectiveFont * zoom < 3.0) { // Ultimate rendering cutoff for performance
					continue;
				}
			}

			ctx.setTransform(zoom, 0, 0, zoom, -offsetX * zoom, -offsetY * zoom);

			if(DEBUG.axis){
				ctx.save();
				ctx.strokeStyle = "rgba(255, 100, 0, 0.6)"; // Dijkstra axis
				ctx.lineWidth = 1.5;
				ctx.beginPath();
				for(let i=0;i<path.length;i++){
					const [x,y] = path[i];
					if(i===0) ctx.moveTo(x, y);
					else ctx.lineTo(x, y);
				}
				ctx.stroke();
				ctx.restore();
			}

			if(DEBUG.bezier){
				ctx.save();
				ctx.strokeStyle = "cyan"; // Bezier curve
				ctx.lineWidth = 2.5;
				ctx.beginPath();
				for(let i=0;i<spine.length;i++){
					const [x,y] = spine[i];
					if(i===0) ctx.moveTo(x, y);
					else ctx.lineTo(x, y);
				}
				ctx.stroke();
				ctx.restore();
			}

			if(DEBUG.points && controlPoints && controlPoints.length > 0){
				ctx.save();
				ctx.fillStyle = "red";
				for(const pt of controlPoints){
					ctx.beginPath();
					ctx.arc(pt[0], pt[1], 4, 0, Math.PI * 2);
					ctx.fill();
				}
				ctx.restore();
			}



			ctx.font = `bold ${label.effectiveFont}px Georgia`;
			ctx.fillStyle = "white";
			ctx.strokeStyle = "black";
			ctx.lineJoin = "round";
			ctx.miterLimit = 2;
			ctx.lineWidth = Math.max(2, label.effectiveFont * 0.22);

			ctx.textAlign = "center";
			ctx.textBaseline = "middle";

			for (let i = 0; i < label.letters.length; i++) {
				const letObj = label.letters[i];
				const cos = Math.cos(letObj.angle);
				const sin = Math.sin(letObj.angle);
				ctx.setTransform(
					cos * zoom,
					sin * zoom,
					-sin * zoom,
					cos * zoom,
					(letObj.x - offsetX) * zoom,
					(letObj.y - offsetY) * zoom
				);
				ctx.strokeText(letObj.char, 0, 0);
				ctx.fillText(letObj.char, 0, 0);
			}
		}
	}
	// Reset transform to default world transform
	ctx.setTransform(zoom, 0, 0, zoom, -offsetX * zoom, -offsetY * zoom);

	// Process queue asynchronously (up to 8ms per frame) to avoid freezing startup
	if (labelGenerationQueue.size > 0 && !isPanning && !isDragging) {
		const maxBatchTime = 8; // ms
		const startTime = performance.now();
		let generatedAny = false;

		for (const o of labelGenerationQueue) {
			labelGenerationQueue.delete(o);
			generateLabelsForCountry(o);
			generatedAny = true;
			if (performance.now() - startTime > maxBatchTime) {
				break;
			}
		}

		if (generatedAny) {
			requestAnimationFrame(draw);
		}
	}
}
// Convenient hotkey listeners
function toggleRivers(enabled) {
	showRivers = enabled ? 1.0 : 0.0;
	requestDraw();
}

function toggleBorders(enabled) {
	showBorders = enabled ? 1.0 : 0.0;
	requestDraw();
}

function toggleHeightmapShading(enabled) {
	showHeightmap = enabled ? 1.0 : 0.0;
	const dbgHeightToggle = document.getElementById("dbgHeightmap");
	if (dbgHeightToggle && dbgHeightToggle.checked !== enabled) {
		dbgHeightToggle.checked = enabled;
	}
	requestDraw();
}

function toggleCountryLabels(enabled) {
	showLabels = enabled ? 1.0 : 0.0;
	requestDraw();
}

function toggleAlwaysShowSmallCountryLabels(enabled) {
	alwaysShowSmallCountryLabels = !!enabled;
	requestDraw();
}

// Hover readout is enabled by default; the toggle lets users disable the tooltip.
window.hoverReadoutEnabled = true;
function toggleHoverReadout(enabled) {
	window.hoverReadoutEnabled = !!enabled;
	if (!enabled) hideHoverTooltip();
}

// Controls & shortcuts help overlay. force: true=open, false=close, undefined=toggle.
function toggleHelpOverlay(force) {
	const overlay = document.getElementById("helpOverlay");
	if (!overlay) return;
	const shouldOpen = (force === undefined) ? !overlay.classList.contains("open") : !!force;
	overlay.classList.toggle("open", shouldOpen);
}

function toggleSidebar() {
	const panel = document.getElementById("sidebarPanel");
	const toggleBtn = document.getElementById("btnSidebarToggle");
	if (panel.style.display === "none") {
		panel.style.display = "block";
		toggleBtn.style.display = "none";
	} else {
		panel.style.display = "none";
		toggleBtn.style.display = "block";
	}
}

function setSelectionLevel(level) {
	selectionLevel = level;
}

function selectHoi4States(type) {
	const tag = document.getElementById("hoi4TagInput").value.toUpperCase().trim();
	if (!tag || !hoi4Data || !hoi4Data.countries[tag]) {
		document.getElementById("hoi4Status").textContent = "Country tag not found.";
		return;
	}
	
	const states = hoi4Data.countries[tag][type] || [];
	const provinces = new Set();
	for (const stateId of states) {
		const state = hoi4Data.states[stateId];
		if (state) {
			for (const p of state.provinces) {
				provinces.add(p);
			}
		}
	}
	
	applySelectionLogic(provinces);
	updateSelectionStatus();
	draw();
	
	document.getElementById("hoi4Status").textContent = `Selected ${provinces.size} provinces across ${states.length} states (${type}).`;
}

function paintHoi4States() {
	if (selectedProvinces.size === 0) {
		alert("No provinces selected to paint!");
		return;
	}
	paintSelection();
}

window.addEventListener("keydown", (e) => {
    // Skip if typing in inputs/selects
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.target.tagName === "TEXTAREA") {
        return;
    }
    
    // Help overlay: "?" toggles it, Escape closes it (handled before modifier guards)
    if (e.key === "?" || (e.shiftKey && e.key === "/")) {
        e.preventDefault();
        toggleHelpOverlay();
        return;
    }
    if (e.key === "Escape") {
        toggleHelpOverlay(false);
        return;
    }

    const key = e.key.toLowerCase();
    if ((e.ctrlKey || e.metaKey) && key === "v") {
        e.preventDefault();
        addStrait();
        return;
    }
    if ((e.ctrlKey || e.metaKey) && key === "s") {
        e.preventDefault();
        saveWorldPreset();
        return;
    }
    if ((e.ctrlKey || e.metaKey) && key === "z") {
        e.preventDefault();
        if (e.shiftKey) redoEdit(); else undoEdit();
        return;
    }
    if ((e.ctrlKey || e.metaKey) && key === "y") {
        e.preventDefault();
        redoEdit();
        return;
    }
    
    // Ignore all other single-key shortcuts if Ctrl, Meta, or Alt keys are held down (avoids browser clashes like Ctrl+F/Ctrl+H)
    if (e.ctrlKey || e.metaKey || e.altKey) {
        return;
    }
    
    if (key === "b") {
        e.preventDefault();
        setTool("box");
    } else if (key === "l") {
        e.preventDefault();
        setTool("lasso");
    } else if (key === "h") {
        e.preventDefault();
        setTool("pan");
    } else if (key === "p") {
        e.preventDefault();
        activateColorPickerTool();
    } else if (key === "e") {
        e.preventDefault();
        setEraser();
    } else if (key === "x") {
        e.preventDefault();
        clearSelection();
    } else if (key === "f" || e.key === "Enter") {
        e.preventDefault();
        paintSelection();
    } else if (key === "c") {
        e.preventDefault();
        selectAllProvincesOfSelectedCountry();
    } else if (key === "i") {
        e.preventDefault();
        paintInterest();
    } else if (["1", "2", "3", "4", "5"].includes(key)) {
        const select = document.getElementById("selLogicMode");
        if (select) {
            const modes = ["replace", "add", "subtract", "intersect", "xor"];
            select.value = modes[parseInt(key) - 1];
        }
    }
});

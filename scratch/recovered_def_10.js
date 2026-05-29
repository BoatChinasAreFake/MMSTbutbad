Created At: 2026-05-29T03:03:09Z
Completed At: 2026-05-29T03:03:09Z
The following changes were made by the replace_file_content tool to: c:\Users\Faaz\Documents\GitHub\Mappa Mundi sine Tempore\index.html. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1718,431 +1718,6 @@
 		debugPanel.innerHTML = window.debugPanelHeader || "";
 	}
 
-    const w=baseCanvas.width, h=baseCanvas.height;
-    const data=basePixels;
-	
-	function computeSpineForComponent(component, countryColor){
-		if (component.length < 2) {
-			return { spine: [], path: [], controlPoints: [] };
-		}
-
-		const compSet = new Set(component);
-
-		// Calculate depth (distance to boundary) for each province in the component
-		const depth = {};
-		const depthQueue = [];
-
-		for (const id of component) {
-			let isBoundary = false;
-			const neighbors = provinceNeighbors[id] || [];
-			if (neighbors.size < 4) {
-				isBoundary = true;
-			}
-			for (const n of neighbors) {
-				if (!compSet.has(n)) {
-					isBoundary = true;
-					break;
-				}
-			}
-			if (isBoundary) {
-				depth[id] = 1;
-				depthQueue.push(id);
-			}
-		}
-
-		// Fallback
-		if (depthQueue.length === 0 && component.length > 0) {
-			depth[component[0]] = 1;
-			depthQueue.push(component[0]);
-		}
-
-		while (depthQueue.length > 0) {
-			const curr = depthQueue.shift();
-			const currDepth = depth[curr];
-
-			for (const n of provinceNeighbors[curr] || []) {
-				if (compSet.has(n) && depth[n] === undefined) {
-					depth[n] = currDepth + 1;
-					depthQueue.push(n);
-				}
-			}
-		}
-
-		// Find max depth
-		let maxD = 1;
-		for (const id of component) {
-			if (depth[id] > maxD) maxD = depth[id];
-		}
-
-		function getFurthestNode(startId) {
-			const dist = {};
-			for (const id of component) dist[id] = Infinity;
-			dist[startId] = 0;
-			const pq = [[startId, 0]];
-
-			while (pq.length > 0) {
-				let minIdx = 0;
-				for (le
<truncated 9003 bytes>
const pull = Math.min(0.5, tension * 1.5);
-					M[0] = (1 - pull) * M_straight[0] + pull * pC.x;
-					M[1] = (1 - pull) * M_straight[1] + pull * pC.y;
-				}
-
-				// Calculate component area and thickness
-				let compArea = 0;
-				for (const id of component) {
-					const center = provinceCenters[id];
-					if (center) compArea += center.count;
-				}
-				const thickness = Math.max(16, Math.min(100, Math.sqrt(compArea) * 0.45));
-
-				// Shift the entire curve in the direction of the bend (eastwards for England)
-				const shiftDist = thickness * 0.10;
-				const shx = ux * shiftDist;
-				const shy = uy * shiftDist;
-
-				P0[0] += shx; P0[1] += shy;
-				P3[0] += shx; P3[1] += shy;
-				M[0] += shx; M[1] += shy;
-			}
-		}
-
-		const P1 = [
-			2 * M[0] - (P0[0] + P3[0]) / 2,
-			2 * M[1] - (P0[1] + P3[1]) / 2
-		];
-
-		// Evaluate Bezier curve at 80 points
-		const spine = [];
-		for (let i = 0; i < 80; i++) {
-			const t = i / 79;
-			const mt = 1 - t;
-			const x = mt*mt * P0[0] + 2*mt*t * P1[0] + t*t * P3[0];
-			const y = mt*mt * P0[1] + 2*mt*t * P1[1] + t*t * P3[1];
-			spine.push([x, y]);
-		}
-
-		if (spine.length >= 2 && spine[spine.length - 1][0] < spine[0][0]) {
-			spine.reverse();
-			path.reverse();
-		}
-
-		return { spine, path, controlPoints: [P1], tension };
-	}
-	
-	function drawLabels(){
-	if (zoom >= 1.5) {
-		if (DEBUG.panel) {
-			debugPanel.innerHTML = window.debugPanelHeader || "";
-		}
-		return;
-	}
-	const ctx = overlayCtx;
-
-	ctx.globalAlpha = 1;
-	ctx.lineWidth = 1;
-
-	if(DEBUG.panel){
-		debugPanel.innerHTML = window.debugPanelHeader || "";
-	}
-
 	for(const o in countries){
 		const country = countries[o];
 		if (!country || country.provinces.size === 0) continue;
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.
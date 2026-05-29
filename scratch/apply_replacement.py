with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Locate drawLabels
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if "function drawLabels(){" in line:
        start_idx = i
        break

if start_idx != -1:
    # Find the matching closing brace for drawLabels
    # Since we replaced it in the last step, it runs from start_idx to the line before "// Convenient hotkey listeners"
    for i in range(start_idx, len(lines)):
        if "// Convenient hotkey listeners" in lines[i]:
            end_idx = i - 1
            break

print("Start line index:", start_idx, lines[start_idx].strip())
print("End line index:", end_idx, lines[end_idx].strip())

replacement_code = """function drawLabels(){
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
	
	function computeSpineForComponent(component, countryColor){
		if (component.length < 2) {
			return { spine: [], path: [], controlPoints: [] };
		}

		const compSet = new Set(component);

		// Calculate depth (distance to boundary) for each province in the component
		const depth = {};
		const depthQueue = [];

		for (const id of component) {
			let isBoundary = false;
			const neighbors = provinceNeighbors[id] || [];
			if (neighbors.size < 4) {
				isBoundary = true;
			}
			for (const n of neighbors) {
				if (!compSet.has(n)) {
					isBoundary = true;
					break;
				}
			}
			if (isBoundary) {
				depth[id] = 1;
				depthQueue.push(id);
			}
		}

		// Fallback
		if (depthQueue.length === 0 && component.length > 0) {
			depth[component[0]] = 1;
			depthQueue.push(component[0]);
		}

		let depthQueueHead = 0;
		while (depthQueueHead < depthQueue.length) {
			const curr = depthQueue[depthQueueHead++];
			const currDepth = depth[curr];

			for (const n of provinceNeighbors[curr] || []) {
				if (compSet.has(n) && depth[n] === undefined) {
					depth[n] = currDepth + 1;
					depthQueue.push(n);
				}
			}
		}

		// Find max depth
		let maxD = 1;
		for (const id of component) {
			if (depth[id] > maxD) maxD = depth[id];
		}

		function getFurthestNode(startId) {
			const dist = {};
			for (const id of component) dist[id] = Infinity;
			dist[startId] = 0;
			
			const pq = new MinHeap();
			pq.push([startId, 0]);

			while (!pq.isEmpty()) {
				const [curr, currCost] = pq.pop();

				if (currCost > dist[curr]) continue;

				const currCenter = provinceCenters[curr];
				if (!currCenter) continue;

				for (const n of provinceNeighbors[curr] || []) {
					if (!compSet.has(n)) continue;

					const nCenter = provinceCenters[n];
					if (!nCenter) continue;

					const stepDist = Math.hypot(currCenter.x - nCenter.x, currCenter.y - nCenter.y);
					const nextCost = currCost + stepDist;

					if (nextCost < dist[n]) {
						dist[n] = nextCost;
						pq.push([n, nextCost]);
					}
				}
			}

			let furthestId = startId;
			let maxDist = -1;
			for (const id of component) {
				if (dist[id] !== Infinity && dist[id] > maxDist) {
					maxDist = dist[id];
					furthestId = id;
				}
			}
			return { id: furthestId, dist: maxDist };
		}

		// 1. Geodesic extremities using 2-pass Dijkstra
		const res1 = getFurthestNode(component[0]);
		const res2 = getFurthestNode(res1.id);
		const A_geo = res1.id;
		const B_geo = res2.id;
		const S_geo = res2.dist;

		// 2. Optimal straight line search
		let A_straight = component[0];
		let B_straight = component[0];
		let bestStraightScore = -Infinity;
		let L_straight = 0;
		let bestOutsideCount = 0;

		function isInside(x, y) {
			const key = getProvinceIdAt(x, y);
			return compSet.has(key);
		}

		// Subsample candidate list when there are many provinces to avoid O(N^2) complexity
		const candidates = [];
		const maxCandidates = 60;
		if (component.length <= maxCandidates) {
			for (let i = 0; i < component.length; i++) candidates.push(component[i]);
		} else {
			const step = Math.ceil(component.length / maxCandidates);
			for (let i = 0; i < component.length; i += step) {
				candidates.push(component[i]);
			}
		}

		for (let i = 0; i < candidates.length; i++) {
			for (let j = i + 1; j < candidates.length; j++) {
				const idA = candidates[i];
				const idB = candidates[j];
				const pA = provinceCenters[idA];
				const pB = provinceCenters[idB];
				if (!pA || !pB) continue;

				const dist = Math.hypot(pB.x - pA.x, pB.y - pA.y);
				// Critical Optimization: Skip candidate check if distance is less than current best score
				if (dist <= bestStraightScore) continue;

				// Sample 20 points along the straight line to accurately detect water crossings
				let outsideCount = 0;
				for (let k = 1; k <= 20; k++) {
					const t = k / 21;
					const sx = pA.x * (1 - t) + pB.x * t;
					const sy = pA.y * (1 - t) + pB.y * t;
					if (!isInside(sx, sy)) {
						outsideCount++;
					}
				}

				const score = dist - 100 * outsideCount;
				if (score > bestStraightScore) {
					bestStraightScore = score;
					A_straight = idA;
					B_straight = idB;
					L_straight = dist;
					bestOutsideCount = outsideCount;
				}
			}
		}

		// 3. Classification using Asymmetry relative to the Optimal Straight Line
		const pA = provinceCenters[A_straight];
		const pB = provinceCenters[B_straight];
		const A_line = pB.y - pA.y;
		const B_line = -(pB.x - pA.x);
		const C_line = pB.x * pA.y - pB.y * pA.x;

		let leftArea = 0;
		let rightArea = 0;
		for (const id of component) {
			const p = provinceCenters[id];
			if (!p) continue;
			const val = A_line * p.x + B_line * p.y + C_line;
			if (val > 0) {
				leftArea += p.count;
			} else {
				rightArea += p.count;
			}
		}
		const totalArea = leftArea + rightArea;
		const asymmetry = totalArea > 0 ? Math.abs(leftArea - rightArea) / totalArea : 0;

		// Dynamically compute tension using asymmetry:
		let tension = 0.0;
		const dy_line = Math.abs(pB.y - pA.y);
		const dx_line = Math.abs(pB.x - pA.x);
		if (bestOutsideCount === 0 && asymmetry >= 0.10 && dy_line <= dx_line) {
			tension = Math.min(0.22, (asymmetry - 0.10) * 2.0);
		}

		let A = A_straight;
		let B = B_straight;

		// Re-order A and B to ensure natural reading: South-to-North / Left-to-Right
		const centerA = provinceCenters[A];
		const centerB = provinceCenters[B];
		if (centerA && centerB) {
			const dx = Math.abs(centerA.x - centerB.x);
			const dy = Math.abs(centerA.y - centerB.y);
			if (dx > dy) {
				if (centerA.x > centerB.x) {
					const temp = A; A = B; B = temp;
				}
			} else {
				if (centerA.y < centerB.y) {
					const temp = A; A = B; B = temp;
				}
			}
		}

		// Dijkstra's algorithm to find the depth-weighted path from A to B
		function dijkstra(start, end) {
			const dist = {};
			const prev = {};
			for (const id of component) {
				dist[id] = Infinity;
			}
			dist[start] = 0;
			
			const pq = new MinHeap();
			pq.push([start, 0]);

			while (!pq.isEmpty()) {
				const [curr, currCost] = pq.pop();

				if (curr === end) break;
				if (currCost > dist[curr]) continue;

				for (const n of provinceNeighbors[curr] || []) {
					if (!compSet.has(n)) continue;

					// Mild depth cost: 1 + (maxD - depth) * 0.25
					const moveCost = 1 + (maxD - (depth[n] || 1)) * 0.25;
					const nextCost = currCost + moveCost;

					if (nextCost < dist[n]) {
						dist[n] = nextCost;
						prev[n] = curr;
						pq.push([n, nextCost]);
					}
				}
			}

			const path = [];
			let cur = end;
			while (cur !== undefined) {
				path.push(cur);
				cur = prev[cur];
			}
			path.reverse();
			return path;
		}

		const pathIds = dijkstra(A, B);
		const path = [];
		for (const id of pathIds) {
			const p = provinceCenters[id];
			if (p) path.push([p.x, p.y]);
		}

		if (path.length < 2) {
			return { spine: path, path: path, controlPoints: [], tension };
		}

		const P0 = [...path[0]];
		const P3 = [...path[path.length - 1]];

		if (path.length < 4) {
			// Linear interpolation (straight line spine)
			const spine = [];
			for (let i = 0; i < 80; i++) {
				const t = i / 79;
				const x = P0[0] * (1 - t) + P3[0] * t;
				const y = P0[1] * (1 - t) + P3[1] * t;
				spine.push([x, y]);
			}
			return { spine, path, controlPoints: [], tension };
		}

		// Calculate cumulative length along the Dijkstra path to find geometric 1/3 and 2/3 points
		const pathLengths = [0];
		for (let i = 1; i < path.length; i++) {
			pathLengths[i] = pathLengths[i - 1] + Math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]);
		}
		const pathTotalLen = pathLengths[pathLengths.length - 1];

		function getPathPointAt(dist) {
			for (let i = 1; i < pathLengths.length; i++) {
				if (pathLengths[i] >= dist) {
					const a = path[i - 1];
					const b = path[i];
					const t = (dist - pathLengths[i - 1]) / (pathLengths[i] - pathLengths[i - 1] || 1);
					return [
						a[0] * (1 - t) + b[0] * t,
						a[1] * (1 - t) + b[1] * t
					];
				}
			}
			return [...path[path.length - 1]];
		}

		const M_dijkstra = getPathPointAt(pathTotalLen * 0.5);
		const M_straight = [
			(P0[0] + P3[0]) / 2,
			(P0[1] + P3[1]) / 2
		];

		const M = [
			(1 - tension) * M_straight[0] + tension * M_dijkstra[0],
			(1 - tension) * M_straight[1] + tension * M_dijkstra[1]
		];

		if (tension > 0.0) {
			// Compute area-weighted centroid of the component to determine the correct bend direction
			let sumX = 0, sumY = 0, totalPCount = 0;
			for (const id of component) {
				const p = provinceCenters[id];
				if (p) {
					sumX += p.x * p.count;
					sumY += p.y * p.count;
					totalPCount += p.count;
				}
			}
			const M_centroid = [sumX / (totalPCount || 1), sumY / (totalPCount || 1)];

			// Find bend direction
			const vx = M_centroid[0] - M_straight[0];
			const vy = M_centroid[1] - M_straight[1];
			const v_len = Math.hypot(vx, vy);

			if (v_len > 0.1) {
				const ux = vx / v_len;
				const uy = vy / v_len;

				let maxProj = -Infinity;
				let bestId = component[0];

				for (const id of component) {
					const p = provinceCenters[id];
					if (!p) continue;
					const proj = (p.x - M_straight[0]) * ux + (p.y - M_straight[1]) * uy;
					if (proj > maxProj) {
						maxProj = proj;
						bestId = id;
					}
				}

				const pC = provinceCenters[bestId];
				if (pC) {
					const pull = Math.min(0.5, tension * 1.5);
					M[0] = (1 - pull) * M_straight[0] + pull * pC.x;
					M[1] = (1 - pull) * M_straight[1] + pull * pC.y;
				}

				// Calculate component area and thickness
				let compArea = 0;
				for (const id of component) {
					const center = provinceCenters[id];
					if (center) compArea += center.count;
				}
				const thickness = Math.max(16, Math.min(100, Math.sqrt(compArea) * 0.45));

				// Shift the entire curve in the direction of the bend
				const shiftDist = thickness * 0.10;
				const shx = ux * shiftDist;
				const shy = uy * shiftDist;

				P0[0] += shx; P0[1] += shy;
				P3[0] += shx; P3[1] += shy;
				M[0] += shx; M[1] += shy;
			}
		}

		const P1 = [
			2 * M[0] - (P0[0] + P3[0]) / 2,
			2 * M[1] - (P0[1] + P3[1]) / 2
		];

		// Evaluate Bezier curve at 80 points
		const spine = [];
		for (let i = 0; i < 80; i++) {
			const t = i / 79;
			const mt = 1 - t;
			const x = mt*mt * P0[0] + 2*mt*t * P1[0] + t*t * P3[0];
			const y = mt*mt * P0[1] + 2*mt*t * P1[1] + t*t * P3[1];
			spine.push([x, y]);
		}

		if (spine.length >= 2 && spine[spine.length - 1][0] < spine[0][0]) {
			spine.reverse();
			path.reverse();
		}

		return { spine, path, controlPoints: [P1], tension };
	}

	for(const o in countries){
		const country = countries[o];
		if (!country || country.provinces.size === 0) continue;

		let text = country.name;
		if (text.toLowerCase().includes("placeholder")) {
			text = country.tag;
		}
		text = text.toUpperCase();
		
		let cached = labelCache[o];

		if (!cached || dirtyCountries.has(o)) {
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
				}
				components.push(component);
			}

			const labels = [];
			for (const comp of components) {
				if (comp.length < 4) continue; // Skip very small components

				const result = computeSpineForComponent(comp, o);
				if (result.spine.length < 2) continue;

				let compArea = 0;
				for (const id of comp) {
					const center = provinceCenters[id];
					if (center) compArea += center.count;
				}
				const thickness = Math.max(16, Math.min(100, Math.sqrt(compArea) * 0.45));
				const spine = result.spine;
				const path = result.path;
				const controlPoints = result.controlPoints;

				const P0 = spine[0];
				const P3 = spine[spine.length - 1];

				const P1 = (controlPoints && controlPoints.length > 0) ? controlPoints[0] : [
					(P0[0] + P3[0]) / 2,
					(P0[1] + P3[1]) / 2
				];

				let fontSize = Math.min(70, thickness * 0.75);

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
					let t = 1;
					for (let i = 1; i < cumulative.length; i++) {
						if (cumulative[i] >= dist) {
							const t0 = (i - 1) / (spine.length - 1);
							const t1 = i / (spine.length - 1);
							const fraction = (dist - cumulative[i - 1]) / (cumulative[i] - cumulative[i - 1] || 1);
							t = t0 * (1 - fraction) + t1 * fraction;
							break;
						}
					}
					const mt = 1 - t;
					const x = mt*mt * P0[0] + 2*mt*t * P1[0] + t*t * P3[0];
					const y = mt*mt * P0[1] + 2*mt*t * P1[1] + t*t * P3[1];
					const dx = 2 * mt * (P1[0] - P0[0]) + 2 * t * (P3[0] - P1[0]);
					const dy = 2 * mt * (P1[1] - P0[1]) + 2 * t * (P3[1] - P1[1]);
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

				const letters = text.split('');
				const baseWidths = letters.map(ch => ctx.measureText(ch).width);
				const baseTotal = baseWidths.reduce((a, b) => a + b, 0);

				const usableLen = len;
				let scale = usableLen / (baseTotal * 1.35); 
				scale = Math.min(scale, 1);
				scale = Math.max(scale, 0.12);

				const effectiveFont = fontSize * scale * 0.85;
				ctx.font = `bold ${effectiveFont}px Georgia`;

				const w = letters.map(ch => ctx.measureText(ch).width);
				const totalW = w.reduce((a, b) => a + b, 0);
				
				let gap = letters.length > 1 ? (len - totalW) / (letters.length - 1) : 0;
				const maxGap = effectiveFont * 1.2;
				if (letters.length > 1 && gap > maxGap) {
					gap = maxGap;
				}
				
				const wordLen = totalW + (letters.length > 1 ? (letters.length - 1) * gap : 0);
				const startDistAdjusted = startDist + (len - wordLen) / 2;
				const angle_straight = Math.atan2(P3[1] - P0[1], P3[0] - P0[0]);

				const computedLetters = [];
				let currentOffset = 0;
				for (let i = 0; i < letters.length; i++) {
					const charW = w[i];
					const dist = startDistAdjusted + currentOffset + charW / 2;
					currentOffset += charW + gap;

					const [x, y, dx, dy] = getPointAndTangentAt(dist);
					const lenDir = Math.hypot(dx, dy) || 1;
					const nx = -dy / lenDir;
					const ny = dx / lenDir;

					const inward = Math.min(thickness * 0.12, effectiveFont * 0.4);
					const px = x + nx * inward;
					const py = y + ny * inward;

					const angle_local = Math.atan2(dy, dx);
					let diff = angle_local - angle_straight;
					diff = Math.atan2(Math.sin(diff), Math.cos(diff));
					
					const rotationDamping = 0.95;
					const angle = angle_straight + diff * rotationDamping;

					computedLetters.push({
						char: letters[i],
						x: px,
						y: py,
						angle: angle
					});
				}
				ctx.restore();

				labels.push({
					spine,
					path,
					controlPoints,
					thickness,
					provCount: comp.length,
					tension: result.tension,
					fontSize,
					effectiveFont,
					letters: computedLetters
				});
			}

			cached = { labels };
			labelCache[o] = cached;
		}

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

			if (label.fontSize * zoom < 7.5) {
				continue;
			}

			ctx.font = `bold ${label.effectiveFont}px Georgia`;
			ctx.fillStyle = "white";
			ctx.strokeStyle = "black";
			ctx.lineJoin = "round";
			ctx.miterLimit = 2;
			ctx.lineWidth = Math.max(0.1, label.effectiveFont * 0.05);

			ctx.textAlign = "center";
			ctx.textBaseline = "middle";

			for (let i = 0; i < label.letters.length; i++) {
				const letObj = label.letters[i];
				ctx.save();
				ctx.translate(letObj.x, letObj.y);
				ctx.rotate(letObj.angle);
				ctx.fillText(letObj.char, 0, 0);
				ctx.strokeText(letObj.char, 0, 0);
				ctx.restore();
			}
		}
	}
}"""

lines[start_idx:end_idx+1] = [replacement_code + "\n"]

with open("index.html", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Replacement complete successfully!")

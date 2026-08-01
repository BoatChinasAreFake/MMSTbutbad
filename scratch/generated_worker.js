
let provinceCenters = {};
let provinceNeighbors = {};
let straitAdj = {};
let ownership = {};
let img = { width: 0, height: 0 };
let basePixels = null;
let colorToId = {};
function getProvinceIdAt(x, y) {
    const pxX = Math.floor(x);
    const pxY = Math.floor(y);
    if (pxX < 0 || pxX >= img.width || pxY < 0 || pxY >= img.height) return 0;
    const idx = (pxY * img.width + pxX) * 4;
    const r = basePixels[idx];
    const g = basePixels[idx + 1];
    const b = basePixels[idx + 2];
    const key = (((r << 24) >>> 0) | (g << 16) | (b << 8) | 255) >>> 0;
    return colorToId[key] || 0;
}

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

function computeSpineForComponent(component, countryColor, countryName, curvatureScale = 1.0){
	if (component.length < 2) {
		return { spine: [], path: [], controlPoints: [], tension: 0 };
	}

	let sumX = 0, sumY = 0, totalArea = 0;
	for (const id of component) {
		const p = provinceCenters[id];
		if (p) {
			sumX += p.x * p.count;
			sumY += p.y * p.count;
			totalArea += p.count;
		}
	}
	const meanX = sumX / (totalArea || 1);
	const meanY = sumY / (totalArea || 1);
	const labelHeightOffset = Math.max(30, Math.min(120, Math.sqrt(totalArea) * 0.55)) * 0.18;

	function distToSegment(px, py, ax, ay, bx, by) {
		const dx = bx - ax;
		const dy = by - ay;
		const l2 = dx * dx + dy * dy;
		if (l2 === 0) return Math.hypot(px - ax, py - ay);
		let t = ((px - ax) * dx + (py - ay) * dy) / l2;
		t = Math.max(0, Math.min(1, t));
		return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
	}

	const waterCache = {};
	function isWaterSurroundedByOwnLand(waterId) {
		if (waterCache[waterId] !== undefined) return waterCache[waterId];
		
		const visitedWater = new Set([waterId]);
		const queue = [[waterId, 0]];
		let queueHead = 0;
		let foundOwnLand = false;
		let foundForeignLand = false;
		
		while (queueHead < queue.length) {
			const [curr, dist] = queue[queueHead++];
			
			const neighbors = provinceNeighbors[curr] || [];
			for (const n of neighbors) {
				const np = provinceCenters[n];
				if (!np) continue;
				if (np.isWater) {
					if (dist < 4 && !visitedWater.has(n)) {
						visitedWater.add(n);
						queue.push([n, dist + 1]);
					}
				} else {
					const owner = ownership[n];
					if (owner === countryColor) {
						foundOwnLand = true;
					} else {
						foundForeignLand = true;
					}
				}
			}
		}
		
		const result = foundOwnLand && !foundForeignLand;
		waterCache[waterId] = result;
		return result;
	}

	function evaluateBezierPenalty(P0, P3, vx, vy, bend) {
		const M = [
			(P0[0] + P3[0]) / 2,
			(P0[1] + P3[1]) / 2
		];
		const ux = -vy;
		const uy = vx;
		const pull = 0.30;
		M[0] += bend * pull * ux;
		M[1] += bend * pull * uy;

		const P1 = [
			2 * M[0] - (P0[0] + P3[0]) / 2,
			2 * M[1] - (P0[1] + P3[1]) / 2
		];

		let penalty = 0;
		for (let k = 1; k <= 20; k++) {
			const t = k / 21;
			const mt = 1 - t;
			const sx = mt*mt * P0[0] + 2*mt*t * P1[0] + t*t * P3[0];
			const sy = mt*mt * P0[1] + 2*mt*t * P1[1] + t*t * P3[1];

			const next_t = (k + 0.1) / 21;
			const next_mt = 1 - next_t;
			const nsx = next_mt*next_mt * P0[0] + 2*next_mt*next_t * P1[0] + next_t*next_t * P3[0];
			const nsy = next_mt*next_mt * P0[1] + 2*next_mt*next_t * P1[1] + next_t*next_t * P3[1];
			const dx = nsx - sx;
			const dy = nsy - sy;
			const lenDir = Math.hypot(dx, dy) || 1;
			const nx = -dy / lenDir;
			const ny = dx / lenDir;

			const samples = [
				[sx, sy, true],
				[sx + nx * labelHeightOffset, sy + ny * labelHeightOffset, false],
				[sx - nx * labelHeightOffset, sy - ny * labelHeightOffset, false]
			];

			for (const [x, y, isSpine] of samples) {
				const key = getProvinceIdAt(x, y);
				if (ownership[key] === countryColor) {
					continue;
				}

				const p = provinceCenters[key];
				if (p) {
					if (p.isWater) {
						if (isWaterSurroundedByOwnLand(key)) {
							penalty += 8; 
						} else {
							penalty += 30; 
						}
					} else {
						penalty += isSpine ? 80 : 15; 
					}
				} else {
					penalty += isSpine ? 80 : 15;
				}
			}
		}
		return penalty;
	}

	const projDirs = [];
	for (let i = 0; i < 16; i++) {
		const angle = (i * Math.PI) / 8;
		projDirs.push([Math.cos(angle), Math.sin(angle)]);
	}

	const candidates = [];
	const bestDists = new Array(16).fill(-Infinity);
	const bestProvIds = new Array(16).fill(null);

	for (const id of component) {
		const c = provinceCenters[id];
		if (!c || c.isWater) continue;

		const dx = c.x - meanX;
		const dy = c.y - meanY;

		for (let i = 0; i < 16; i++) {
			const dot = dx * projDirs[i][0] + dy * projDirs[i][1];
			if (dot > bestDists[i]) {
				bestDists[i] = dot;
				bestProvIds[i] = id;
			}
		}
	}

	for (let i = 0; i < 16; i++) {
		if (bestProvIds[i] !== null && !candidates.includes(bestProvIds[i])) {
			candidates.push(bestProvIds[i]);
		}
	}

	if (candidates.length < 2) {
		const first = component[0];
		const last = component[component.length - 1];
		return { spine: [], path: [provinceCenters[first], provinceCenters[last]], controlPoints: [], tension: 0, bendAmount: 0, vx: 0, vy: 0, meanX, meanY, projStart: 0, projEnd: 100 };
	}

	let bestPath = [];
	let maxScore = -Infinity;
	let bestPair = [null, null];

	for (let i = 0; i < candidates.length; i++) {
		for (let j = i + 1; j < candidates.length; j++) {
			const startId = candidates[i];
			const endId = candidates[j];

			const distMap = {};
			const parentMap = {};
			const heap = new MinHeap();

			distMap[startId] = 0;
			heap.push([startId, 0]);

			while (!heap.isEmpty()) {
				const top = heap.pop();
				if (!top) break;
				const curr = top[0];
				const d = top[1];

				if (d > distMap[curr]) continue;
				if (curr === endId) break;

				const neighbors = provinceNeighbors[curr] || [];
				for (const n of neighbors) {
					if (!provincesSet.has(n)) continue;
					const weight = provinceCenters[n]?.isWater ? 2.5 : 1.0;
					const alt = d + weight;
					if (distMap[n] === undefined || alt < distMap[n]) {
						distMap[n] = alt;
						parentMap[n] = curr;
						heap.push([n, alt]);
					}
				}

				const straits = straitAdj[curr] || [];
				for (const n of straits) {
					if (!provincesSet.has(n)) continue;
					const alt = d + 1.8;
					if (distMap[n] === undefined || alt < distMap[n]) {
						distMap[n] = alt;
						parentMap[n] = curr;
						heap.push([n, alt]);
					}
				}
			}

			if (distMap[endId] !== undefined) {
				const path = [];
				let curr = endId;
				while (curr !== undefined) {
					path.push(curr);
					curr = parentMap[curr];
				}
				path.reverse();

				let pathLen = 0;
				for (let k = 1; k < path.length; k++) {
					const p1 = provinceCenters[path[k - 1]];
					const p2 = provinceCenters[path[k]];
					if (p1 && p2) {
						pathLen += Math.hypot(p2.x - p1.x, p2.y - p1.y);
					}
				}

				const startPt = provinceCenters[startId];
				const endPt = provinceCenters[endId];
				const directDist = Math.hypot(endPt.x - startPt.x, endPt.y - startPt.y);
				const straightness = directDist / (pathLen || 1);

				let borderPenalty = 0;
				for (const node of path) {
					const nodeNeighbors = provinceNeighbors[node] || [];
					for (const n of nodeNeighbors) {
						if (!provincesSet.has(n)) {
							const np = provinceCenters[n];
							if (np && !np.isWater) {
								borderPenalty += (provinceCenters[node]?.isWater) ? 15 : 80;
							}
						}
					}
				}

				const score = pathLen * 0.95 + straightness * 120 - borderPenalty;
				if (score > maxScore) {
					maxScore = score;
					bestPath = path;
					bestPair = [startPt, endPt];
				}
			}
		}
	}

	if (bestPath.length < 2 || !bestPair[0] || !bestPair[1]) {
		const first = component[0];
		const last = component[component.length - 1];
		return { spine: [], path: [provinceCenters[first], provinceCenters[last]], controlPoints: [], tension: 0, bendAmount: 0, vx: 0, vy: 0, meanX, meanY, projStart: 0, projEnd: 100 };
	}

	const pathCoords = bestPath.map(id => [provinceCenters[id].x, provinceCenters[id].y]);
	const resampled = resamplePath(pathCoords, 10);

	const P0 = resampled[0];
	const P3 = resampled[resampled.length - 1];

	const dx = P3[0] - P0[0];
	const dy = P3[1] - P0[1];
	const lenLine = Math.hypot(dx, dy) || 1;
	const vx = dx / lenLine;
	const vy = dy / lenLine;

	let projStart = Infinity;
	let projEnd = -Infinity;
	for (const pt of resampled) {
		const proj = (pt[0] - P0[0]) * vx + (pt[1] - P0[1]) * vy;
		if (proj < projStart) projStart = proj;
		if (proj > projEnd) projEnd = proj;
	}

	const maxBend = lenLine * 0.65;
	let bestBendAmount = 0;

	let maxPositivePerp = maxBend * curvatureScale;
	let maxNegativePerp = -maxBend * curvatureScale;

	const finalPenaltyPos = evaluateBezierPenalty(P0, P3, vx, vy, maxPositivePerp);
	const finalPenaltyNeg = evaluateBezierPenalty(P0, P3, vx, vy, maxNegativePerp);

	if (finalPenaltyPos < finalPenaltyNeg) {
		bestBendAmount = maxPositivePerp;
	} else if (finalPenaltyNeg < finalPenaltyPos) {
		bestBendAmount = maxNegativePerp;
	} else {
		bestBendAmount = 0;
	}

	const bendAmount = bestBendAmount;
	const M = [
		(P0[0] + P3[0]) / 2,
		(P0[1] + P3[1]) / 2
	];
	const ux = -vy;
	const uy = vx;
	const pull = 0.30;
	M[0] += bendAmount * pull * ux;
	M[1] += bendAmount * pull * uy;

	const P1 = [
		2 * M[0] - (P0[0] + P3[0]) / 2,
		2 * M[1] - (P0[1] + P3[1]) / 2
	];

	const spine = [];
	for (let i = 0; i < 80; i++) {
		const t = i / 79;
		const mt = 1 - t;
		const x = mt*mt * P0[0] + 2*mt*t * P1[0] + t*t * P3[0];
		const y = mt*mt * P0[1] + 2*mt*t * P1[1] + t*t * P3[1];
		spine.push([x, y]);
	}

	for (let i = 0; i < spine.length; i++) {
		const p = spine[i];
		const key = getProvinceIdAt(p[0], p[1]);
		
		if (key !== 0 && ownership[key] !== countryColor) {
			const pc = provinceCenters[key];
			if (pc && !pc.isWater) {
				let closestCenter = null;
				let minDist = Infinity;
				for (const id of component) {
					const c = provinceCenters[id];
					if (c) {
						const d2 = (p[0] - c.x) * (p[0] - c.x) + (p[1] - c.y) * (p[1] - c.y);
						if (d2 < minDist) {
							minDist = d2;
							closestCenter = c;
						}
					}
				}
				if (closestCenter) {
					p[0] = p[0] * 0.15 + closestCenter.x * 0.85;
					p[1] = p[1] * 0.15 + closestCenter.y * 0.85;
				}
			}
		}
	}

	const smoothedSpine = [];
	const windowSize = 5; 
	for (let i = 0; i < spine.length; i++) {
		let sumX = 0;
		let sumY = 0;
		let count = 0;
		for (let w = -windowSize; w <= windowSize; w++) {
			const idx = i + w;
			if (idx >= 0 && idx < spine.length) {
				sumX += spine[idx][0];
				sumY += spine[idx][1];
				count++;
			}
		}
		smoothedSpine.push([sumX / count, sumY / count]);
	}
	for (let i = 0; i < spine.length; i++) {
		spine[i][0] = smoothedSpine[i][0];
		spine[i][1] = smoothedSpine[i][1];
	}

	return { spine, path: [P0, P3], controlPoints: [P1], tension: 0.5, bendAmount, vx, vy, meanX, meanY, projStart, projEnd };
}

self.onmessage = function(e) {
    // ...
}

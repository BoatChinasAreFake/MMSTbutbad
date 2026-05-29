Created At: 2026-05-27T13:42:08Z
Completed At: 2026-05-27T13:42:08Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 1886
Total Bytes: 61353
Showing lines 1190 to 1290
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1190: function drawLabels(){
1191: 	const ctx = overlayCtx;
1192: 
1193: 	ctx.globalAlpha = 1;
1194: 	ctx.lineWidth = 1;
1195: 
1196: 	if(DEBUG.panel){
1197: 		debugPanel.innerHTML = window.debugPanelHeader || "";
1198: 	}
1199: 
1200:     const w=baseCanvas.width, h=baseCanvas.height;
1201:     const data=basePixels;
1202: 	
1203: 	function computeSpineForComponent(component, countryColor){
1204: 		if (component.length < 2) {
1205: 			return { spine: [], path: [], controlPoints: [] };
1206: 		}
1207: 
1208: 		const compSet = new Set(component);
1209: 
1210: 		// Calculate depth (distance to boundary) for each province in the component
1211: 		const depth = {};
1212: 		const depthQueue = [];
1213: 
1214: 		for (const id of component) {
1215: 			let isBoundary = false;
1216: 			const neighbors = provinceNeighbors[id] || [];
1217: 			if (neighbors.size < 4) {
1218: 				isBoundary = true;
1219: 			}
1220: 			for (const n of neighbors) {
1221: 				if (!compSet.has(n)) {
1222: 					isBoundary = true;
1223: 					break;
1224: 				}
1225: 			}
1226: 			if (isBoundary) {
1227: 				depth[id] = 1;
1228: 				depthQueue.push(id);
1229: 			}
1230: 		}
1231: 
1232: 		// Fallback
1233: 		if (depthQueue.length === 0 && component.length > 0) {
1234: 			depth[component[0]] = 1;
1235: 			depthQueue.push(component[0]);
1236: 		}
1237: 
1238: 		while (depthQueue.length > 0) {
1239: 			const curr = depthQueue.shift();
1240: 			const currDepth = depth[curr];
1241: 
1242: 			for (const n of provinceNeighbors[curr] || []) {
1243: 				if (compSet.has(n) && depth[n] === undefined) {
1244: 					depth[n] = currDepth + 1;
1245: 					depthQueue.push(n);
1246: 				}
1247: 			}
1248: 		}
1249: 
1250: 		// Find max depth
1251: 		let maxD = 1;
1252: 		for (const id of component) {
1253: 			if (depth[id] > maxD) maxD = depth[id];
1254: 		}
1255: 
1256: 		function getFurthestNode(startId) {
1257: 			const dist = {};
1258: 			for (const id of component) dist[id] = Infinity;
1259: 			dist[startId] = 0;
1260: 			const pq = [[startId, 0]];
1261: 
1262: 			while (pq.length > 0) {
1263: 				let minIdx = 0;
1264: 				for (let i = 1; i < pq.length; i++) {
1265: 					if (pq[i][1] < pq[minIdx][1]) minIdx = i;
1266: 				}
1267: 				const [curr, currCost] = pq.splice(minIdx, 1)[0];
1268: 
1269: 				if (currCost > dist[curr]) continue;
1270: 
1271: 				const currCenter = provinceCenters[curr];
1272: 				if (!currCenter) continue;
1273: 
1274: 				for (const n of provinceNeighbors[curr] || []) {
1275: 					if (!compSet.has(n)) continue;
1276: 
1277: 					const nCenter = provinceCenters[n];
1278: 					if (!nCenter) continue;
1279: 
1280: 					const stepDist = Math.hypot(currCenter.x - nCenter.x, currCenter.y - nCenter.y);
1281: 					const nextCost = currCost + stepDist;
1282: 
1283: 					if (nextCost < dist[n]) {
1284: 						dist[n] = nextCost;
1285: 						pq.push([n, nextCost]);
1286: 					}
1287: 				}
1288: 			}
1289: 
1290: 			let furthestId = startId;
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

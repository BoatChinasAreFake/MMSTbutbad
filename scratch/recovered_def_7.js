Created At: 2026-05-29T03:01:21Z
Completed At: 2026-05-29T03:01:21Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 2458
Total Bytes: 79878
Showing lines 1700 to 1800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1700:         result.push([x,y]);
1701:     }
1702: 
1703:     return result;
1704: }
1705: function drawLabels(){
1706: 	if (zoom >= 1.5) {
1707: 		if (DEBUG.panel) {
1708: 			debugPanel.innerHTML = window.debugPanelHeader || "";
1709: 		}
1710: 		return;
1711: 	}
1712: 	const ctx = overlayCtx;
1713: 
1714: 	ctx.globalAlpha = 1;
1715: 	ctx.lineWidth = 1;
1716: 
1717: 	if(DEBUG.panel){
1718: 		debugPanel.innerHTML = window.debugPanelHeader || "";
1719: 	}
1720: 
1721:     const w=baseCanvas.width, h=baseCanvas.height;
1722:     const data=basePixels;
1723: 	
1724: 	function computeSpineForComponent(component, countryColor){
1725: 		if (component.length < 2) {
1726: 			return { spine: [], path: [], controlPoints: [] };
1727: 		}
1728: 
1729: 		const compSet = new Set(component);
1730: 
1731: 		// Calculate depth (distance to boundary) for each province in the component
1732: 		const depth = {};
1733: 		const depthQueue = [];
1734: 
1735: 		for (const id of component) {
1736: 			let isBoundary = false;
1737: 			const neighbors = provinceNeighbors[id] || [];
1738: 			if (neighbors.size < 4) {
1739: 				isBoundary = true;
1740: 			}
1741: 			for (const n of neighbors) {
1742: 				if (!compSet.has(n)) {
1743: 					isBoundary = true;
1744: 					break;
1745: 				}
1746: 			}
1747: 			if (isBoundary) {
1748: 				depth[id] = 1;
1749: 				depthQueue.push(id);
1750: 			}
1751: 		}
1752: 
1753: 		// Fallback
1754: 		if (depthQueue.length === 0 && component.length > 0) {
1755: 			depth[component[0]] = 1;
1756: 			depthQueue.push(component[0]);
1757: 		}
1758: 
1759: 		while (depthQueue.length > 0) {
1760: 			const curr = depthQueue.shift();
1761: 			const currDepth = depth[curr];
1762: 
1763: 			for (const n of provinceNeighbors[curr] || []) {
1764: 				if (compSet.has(n) && depth[n] === undefined) {
1765: 					depth[n] = currDepth + 1;
1766: 					depthQueue.push(n);
1767: 				}
1768: 			}
1769: 		}
1770: 
1771: 		// Find max depth
1772: 		let maxD = 1;
1773: 		for (const id of component) {
1774: 			if (depth[id] > maxD) maxD = depth[id];
1775: 		}
1776: 
1777: 		function getFurthestNode(startId) {
1778: 			const dist = {};
1779: 			for (const id of component) dist[id] = Infinity;
1780: 			dist[startId] = 0;
1781: 			const pq = [[startId, 0]];
1782: 
1783: 			while (pq.length > 0) {
1784: 				let minIdx = 0;
1785: 				for (let i = 1; i < pq.length; i++) {
1786: 					if (pq[i][1] < pq[minIdx][1]) minIdx = i;
1787: 				}
1788: 				const [curr, currCost] = pq.splice(minIdx, 1)[0];
1789: 
1790: 				if (currCost > dist[curr]) continue;
1791: 
1792: 				const currCenter = provinceCenters[curr];
1793: 				if (!currCenter) continue;
1794: 
1795: 				for (const n of provinceNeighbors[curr] || []) {
1796: 					if (!compSet.has(n)) continue;
1797: 
1798: 					const nCenter = provinceCenters[n];
1799: 					if (!nCenter) continue;
1800: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-05-29T03:02:10Z
Completed At: 2026-05-29T03:02:10Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 2277
Total Bytes: 74272
Showing lines 1700 to 2140
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
1756: 	
<truncated 11366 bytes>
ath.min(0.5, tension * 1.5);
2084: 					M[0] = (1 - pull) * M_straight[0] + pull * pC.x;
2085: 					M[1] = (1 - pull) * M_straight[1] + pull * pC.y;
2086: 				}
2087: 
2088: 				// Calculate component area and thickness
2089: 				let compArea = 0;
2090: 				for (const id of component) {
2091: 					const center = provinceCenters[id];
2092: 					if (center) compArea += center.count;
2093: 				}
2094: 				const thickness = Math.max(16, Math.min(100, Math.sqrt(compArea) * 0.45));
2095: 
2096: 				// Shift the entire curve in the direction of the bend (eastwards for England)
2097: 				const shiftDist = thickness * 0.10;
2098: 				const shx = ux * shiftDist;
2099: 				const shy = uy * shiftDist;
2100: 
2101: 				P0[0] += shx; P0[1] += shy;
2102: 				P3[0] += shx; P3[1] += shy;
2103: 				M[0] += shx; M[1] += shy;
2104: 			}
2105: 		}
2106: 
2107: 		const P1 = [
2108: 			2 * M[0] - (P0[0] + P3[0]) / 2,
2109: 			2 * M[1] - (P0[1] + P3[1]) / 2
2110: 		];
2111: 
2112: 		// Evaluate Bezier curve at 80 points
2113: 		const spine = [];
2114: 		for (let i = 0; i < 80; i++) {
2115: 			const t = i / 79;
2116: 			const mt = 1 - t;
2117: 			const x = mt*mt * P0[0] + 2*mt*t * P1[0] + t*t * P3[0];
2118: 			const y = mt*mt * P0[1] + 2*mt*t * P1[1] + t*t * P3[1];
2119: 			spine.push([x, y]);
2120: 		}
2121: 
2122: 		if (spine.length >= 2 && spine[spine.length - 1][0] < spine[0][0]) {
2123: 			spine.reverse();
2124: 			path.reverse();
2125: 		}
2126: 
2127: 		return { spine, path, controlPoints: [P1], tension };
2128: 	}
2129: 	
2130: 	function drawLabels(){
2131: 	if (zoom >= 1.5) {
2132: 		if (DEBUG.panel) {
2133: 			debugPanel.innerHTML = window.debugPanelHeader || "";
2134: 		}
2135: 		return;
2136: 	}
2137: 	const ctx = overlayCtx;
2138: 
2139: 	ctx.globalAlpha = 1;
2140: 	ctx.lineWidth = 1;
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

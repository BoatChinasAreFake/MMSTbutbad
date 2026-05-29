Created At: 2026-05-29T03:05:15Z
Completed At: 2026-05-29T03:05:15Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 1853
Total Bytes: 62425
Showing lines 1705 to 1820
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
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
1721: 	for(const o in countries){
1722: 		const country = countries[o];
1723: 		if (!country || country.provinces.size === 0) continue;
1724: 
1725: 		let text = country.name.toUpperCase();
1726: 		let cached = labelCache[o];
1727: 
1728: 		if (!cached || dirtyCountries.has(o)) {
1729: 			// Find contiguous components using BFS
1730: 			const provincesSet = country.provinces;
1731: 			const visited = new Set();
1732: 			const components = [];
1733: 
1734: 			for (const provId of provincesSet) {
1735: 				if (visited.has(provId)) continue;
1736: 
1737: 				const component = [];
1738: 				const queue = [provId];
1739: 				let queueHead = 0;
1740: 				visited.add(provId);
1741: 
1742: 				while (queueHead < queue.length) {
1743: 					const curr = queue[queueHead++];
1744: 					component.push(curr);
1745: 
1746: 					for (const n of provinceNeighbors[curr] || []) {
1747: 						if (provincesSet.has(n) && !visited.has(n)) {
1748: 							visited.add(n);
1749: 							queue.push(n);
1750: 						}
1751: 					}
1752: 				}
1753: 				components.push(component);
1754: 			}
1755: 
1756: 			// For each reasonably sized component, calculate a cen
<truncated 187 bytes>
alArea = 0;
1762: 				for (const id of comp) {
1763: 					const center = provinceCenters[id];
1764: 					if (center) {
1765: 						sumX += center.x * center.count;
1766: 						sumY += center.y * center.count;
1767: 						totalArea += center.count;
1768: 					}
1769: 				}
1770: 
1771: 				if (totalArea > 0) {
1772: 					const cx = sumX / totalArea;
1773: 					const cy = sumY / totalArea;
1774: 					const fontSize = Math.max(10, Math.min(32, Math.sqrt(totalArea) * 0.35));
1775: 					
1776: 					labels.push({
1777: 						x: cx,
1778: 						y: cy,
1779: 						fontSize,
1780: 						area: totalArea
1781: 					});
1782: 				}
1783: 			}
1784: 
1785: 			cached = { labels };
1786: 			labelCache[o] = cached;
1787: 		}
1788: 
1789: 		// Draw the calculated labels
1790: 		ctx.save();
1791: 		ctx.textAlign = "center";
1792: 		ctx.textBaseline = "middle";
1793: 		ctx.strokeStyle = "black";
1794: 
1795: 		for (const label of cached.labels) {
1796: 			// Culling: check if label is within screen bounds
1797: 			const margin = label.fontSize * 5;
1798: 			const vpLeft = offsetX;
1799: 			const vpRight = offsetX + canvas.width / zoom;
1800: 			const vpTop = offsetY;
1801: 			const vpBottom = offsetY + canvas.height / zoom;
1802: 
1803: 			if (label.x + margin < vpLeft || label.x - margin > vpRight || 
1804: 				label.y + margin < vpTop || label.y - margin > vpBottom) {
1805: 				continue;
1806: 			}
1807: 
1808: 			// Scale font dynamically based on zoom
1809: 			const fontSize = label.fontSize;
1810: 			ctx.font = `bold ${fontSize}px Georgia`;
1811: 			ctx.lineWidth = Math.max(1, fontSize * 0.15);
1812: 			ctx.fillStyle = "white";
1813: 
1814: 			ctx.fillText(text, label.x, label.y);
1815: 			ctx.strokeText(text, label.x, label.y);
1816: 		}
1817: 		ctx.restore();
1818: 	}
1819: }
1820: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

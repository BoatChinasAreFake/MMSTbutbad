Created At: 2026-05-26T14:13:26Z
Completed At: 2026-05-26T14:13:26Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 1498
Total Bytes: 44973
Showing lines 801 to 1498
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
801:     const step=total/(count-1);
802: 
803:     const result=[];
804:     let j=0;
805: 
806:     for(let i=0;i<count;i++){
807:         const target=i*step;
808: 
809:         while(j < lengths.length-2 && lengths[j+1] < target) j++;
810: 
811:         const t=(target-lengths[j])/(lengths[j+1]-lengths[j]||1);
812: 
813:         const x=path[j][0]*(1-t)+path[j+1][0]*t;
814:         const y=path[j][1]*(1-t)+path[j+1][1]*t;
815: 
816:         result.push([x,y]);
817:     }
818: 
819:     return result;
820: }
821: function drawLabels(){
822: 	const ctx = overlayCtx;
823: 
824: 	ctx.globalAlpha = 1;
825: 	ctx.lineWidth = 1;
826: 
827: 	if(DEBUG.panel){
828: 		debugPanel.innerHTML = window.debugPanelHeader || "";
829: 	}
830: 
831:     const w=baseCanvas.width, h=baseCanvas.height;
832:     const data=basePixels;
833: 	
834: 	function computeSpineForComponent(component, countryColor){
835: 		if (component.length < 2) {
836: 			return { spine: [], path: [], controlPoints: [] };
837: 		}
838: 
839: 		const compSet = new Set(component);
840: 
841: 		// Calculate depth (distance to boundary) for each province in the component
842: 		const depth = {};
843: 		const depthQueue = [];
844: 
845: 		for (const id of component) {
846: 			let isBoundary = false;
847: 			const neighbors = provinceNeighbors[id] || [];
848: 			if (neighbors.size < 4) {
849: 				isBoundary = true;
850: 			}
851: 			for (const n of neighbors) {
852: 				if (!compSet.has(n)) {
853: 					isBoundary = true;
854: 					break;
855: 				}
856
<truncated 19937 bytes>
intAndTangentAt(dist);
1447: 
1448: 				const lenDir = Math.hypot(dx, dy) || 1;
1449: 				const nx = -dy / lenDir;
1450: 				const ny = dx / lenDir;
1451: 
1452: 				const inward = Math.min(thickness * 0.12, effectiveFont * 0.4);
1453: 
1454: 				const px = x + nx * inward;
1455: 				const py = y + ny * inward;
1456: 
1457: 				const angle_local = Math.atan2(dy, dx);
1458: 				
1459: 				// Damped rotation: blend local angle with overall straight-line angle
1460: 				let diff = angle_local - angle_straight;
1461: 				diff = Math.atan2(Math.sin(diff), Math.cos(diff)); // normalize to [-PI, PI]
1462: 				
1463: 				const rotationDamping = 0.95; // 0.95 = follow curve almost exactly to prevent misalignment on deep bends
1464: 				const angle = angle_straight + diff * rotationDamping;
1465: 
1466: 				ctx.save();
1467: 
1468: 				ctx.translate(px, py);
1469: 				ctx.rotate(angle);
1470: 
1471: 				// Draw centered at (0,0) since ctx.textAlign is "center"
1472: 				ctx.fillText(letters[i], 0, 0);
1473: 				ctx.strokeText(letters[i], 0, 0);
1474: 
1475: 				ctx.restore();
1476: 			}
1477: 			if(DEBUG.panel){
1478: 				debugPanel.innerHTML += `
1479: 					<b>${text}</b><br>
1480: 					pts: ${label.provCount}<br>
1481: 					tension: ${label.tension !== undefined ? label.tension.toFixed(2) : "N/A"}<br>
1482: 					thickness: ${thickness.toFixed(2)}<br>
1483: 					fontSize: ${fontSize.toFixed(2)}<br>
1484: 					widthLine: ${ctx.lineWidth}<br>
1485: 					scale: ${scale.toFixed(3)}<br>
1486: 					effectiveFont: ${(fontSize * scale).toFixed(2)}<br>
1487: 					len: ${len.toFixed(2)}<br>
1488: 					usableLen: ${usableLen.toFixed(2)}<br>
1489: 					textWidth: ${baseTotal.toFixed(2)}<br>
1490: 					<br>
1491: 				`;
1492: 			}
1493: 		}
1494: 	}
1495: }
1496: </script>
1497: </body>
1498: </html>
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

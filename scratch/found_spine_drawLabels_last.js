Created At: 2026-05-29T03:01:48Z
Completed At: 2026-05-29T03:01:59Z
The following changes were made by the replace_file_content tool to: c:\Users\Faaz\Documents\GitHub\Mappa Mundi sine Tempore\index.html. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -2127,10 +2127,25 @@
 		return { spine, path, controlPoints: [P1], tension };
 	}
 	
+	function drawLabels(){
+	if (zoom >= 1.5) {
+		if (DEBUG.panel) {
+			debugPanel.innerHTML = window.debugPanelHeader || "";
+		}
+		return;
+	}
+	const ctx = overlayCtx;
+
+	ctx.globalAlpha = 1;
+	ctx.lineWidth = 1;
+
+	if(DEBUG.panel){
+		debugPanel.innerHTML = window.debugPanelHeader || "";
+	}
+
 	for(const o in countries){
-
 		const country = countries[o];
-		if (!country) continue;
+		if (!country || country.provinces.size === 0) continue;
 
 		let text = country.name.toUpperCase();
 		let cached = labelCache[o];
@@ -2137,4 +2137,5 @@
 		if (!cached || dirtyCountries.has(o)) {
+			// Find contiguous components using BFS
 			const provincesSet = country.provinces;
 			const visited = new Set();
 			const components = [];
@@ -2159,53 +2159,48 @@
 				components.push(component);
 			}
 
+			// For each reasonably sized component, calculate a centroid
 			const labels = [];
-
 			for (const comp of components) {
-				if (comp.length < 4) continue; // Skip very small components
-
-				const result = computeSpineForComponent(comp, o);
-				if (result.spine.length < 2) continue;
-
-				// Calculate thickness based on this component's area
-				let compArea = 0;
+				if (comp.length < 3) continue; // Skip tiny islands
+
+				let sumX = 0, sumY = 0, totalArea = 0;
 				for (const id of comp) {
 					const center = provinceCenters[id];
-					if (center) compArea += center.count;
-				}
-				const thickness = Math.max(16, Math.min(100, Math.sqrt(compArea) * 0.45));
-
-				labels.push({
-					spine: result.spine,
-					path: result.path,
-					cont
<truncated 6812 bytes>
 nx = -dy / lenDir;
-				const ny = dx / lenDir;
-
-				const inward = Math.min(thickness * 0.12, effectiveFont * 0.4);
-
-				const px = x + nx * inward;
-				const py = y + ny * inward;
-
-				const angle_local = Math.atan2(dy, dx);
-				
-				// Damped rotation: blend local angle with overall straight-line angle
-				let diff = angle_local - angle_straight;
-				diff = Math.atan2(Math.sin(diff), Math.cos(diff)); // normalize to [-PI, PI]
-				
-				const rotationDamping = 0.95; // 0.95 = follow curve almost exactly to prevent misalignment on deep bends
-				const angle = angle_straight + diff * rotationDamping;
-
-				ctx.save();
-
-				ctx.translate(px, py);
-				ctx.rotate(angle);
-
-				// Draw centered at (0,0) since ctx.textAlign is "center"
-				ctx.fillText(letters[i], 0, 0);
-				ctx.strokeText(letters[i], 0, 0);
-
-				ctx.restore();
-			}
-			if(DEBUG.panel){
-				debugPanel.innerHTML += `
-					<b>${text}</b><br>
-					pts: ${label.provCount}<br>
-					tension: ${label.tension !== undefined ? label.tension.toFixed(2) : "N/A"}<br>
-					thickness: ${thickness.toFixed(2)}<br>
-					fontSize: ${fontSize.toFixed(2)}<br>
-					widthLine: ${ctx.lineWidth}<br>
-					scale: ${scale.toFixed(3)}<br>
-					effectiveFont: ${(fontSize * scale).toFixed(2)}<br>
-					len: ${len.toFixed(2)}<br>
-					usableLen: ${usableLen.toFixed(2)}<br>
-					textWidth: ${baseTotal.toFixed(2)}<br>
-					<br>
-				`;
-			}
-		}
+			ctx.lineWidth = Math.max(1, fontSize * 0.15);
+			ctx.fillStyle = "white";
+
+			ctx.fillText(text, label.x, label.y);
+			ctx.strokeText(text, label.x, label.y);
+		}
+		ctx.restore();
 	}
 }
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.
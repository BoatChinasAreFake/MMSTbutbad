Created At: 2026-05-27T21:07:47Z
Completed At: 2026-05-27T21:07:47Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 2182
Total Bytes: 72434
Showing lines 1331 to 1500
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1331: function draw() {
1332:     if (!gl) return;
1333:     
1334:     gl.viewport(0, 0, canvas.width, canvas.height);
1335:     gl.clearColor(0.13, 0.13, 0.13, 1.0);
1336:     gl.clear(gl.COLOR_BUFFER_BIT);
1337: 
1338:     gl.useProgram(program);
1339: 
1340:     gl.activeTexture(gl.TEXTURE0);
1341:     gl.bindTexture(gl.TEXTURE_2D, indexTexture);
1342:     gl.uniform1i(gl.getUniformLocation(program, "u_indexTexture"), 0);
1343: 
1344:     if (lutNeedsUpdate) {
1345:         gl.activeTexture(gl.TEXTURE1);
1346:         gl.bindTexture(gl.TEXTURE_2D, lutTexture);
1347:         gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, lutWidth, lutHeight, 0, gl.RGBA, gl.UNSIGNED_BYTE, lutData);
1348:         lutNeedsUpdate = false;
1349:     }
1350:     gl.activeTexture(gl.TEXTURE1);
1351:     gl.bindTexture(gl.TEXTURE_2D, lutTexture);
1352:     gl.uniform1i(gl.getUniformLocation(program, "u_lutTexture"), 1);
1353: 
1354:     gl.activeTexture(gl.TEXTURE2);
1355:     gl.bindTexture(gl.TEXTURE_2D, heightmapTexture);
1356:     gl.uniform1i(gl.getUniformLocation(program, "u_heightmapTexture"), 2);
1357: 
1358:     gl.uniform2f(gl.getUniformLocation(program, "u_offset"), offsetX, offsetY);
1359:     gl.uniform1f(gl.getUniformLocation(program, "u_zoom"), zoom);
1360:     gl.uniform2f(gl.getUniformLocation(program, "u_resolution"), canvas.width, canvas.height);
1361:     gl.uniform2f(gl.getUniformLocation(program, "u_mapSize"), img.width, img.height);
1362:     gl.uniform2f(gl.getUniformLocation(program, "u_texelSize"), 1.0 / img.width, 1.0 / img.
<truncated 3466 bytes>
gPanelHeader = `
1444:             <div style="border-bottom: 1px solid #0f0; margin-bottom: 8px; padding-bottom: 4px;">
1445:                 <b>WebGL Engine: ON</b><br>
1446:                 FPS: ${avgFps.toFixed(0)}<br>
1447:                 Frame Time: ${frameTime.toFixed(2)} ms<br>
1448:                 Zoom: ${zoom.toFixed(2)}x<br>
1449:                 Offset: (${offsetX.toFixed(0)}, ${offsetY.toFixed(0)})
1450:             </div>
1451:         `;
1452:     }
1453: }
1454: 
1455: function resamplePath(path, count){
1456: 
1457: 	const lengths = [0];
1458: 
1459: 	for (let i = 1; i < path.length; i++) {
1460: 		const dx = path[i][0] - path[i - 1][0];
1461: 		const dy = path[i][1] - path[i - 1][1];
1462: 		lengths[i] = lengths[i - 1] + Math.hypot(dx, dy);
1463: 	}
1464: 
1465:     const total=lengths[lengths.length-1];
1466:     const step=total/(count-1);
1467: 
1468:     const result=[];
1469:     let j=0;
1470: 
1471:     for(let i=0;i<count;i++){
1472:         const target=i*step;
1473: 
1474:         while(j < lengths.length-2 && lengths[j+1] < target) j++;
1475: 
1476:         const t=(target-lengths[j])/(lengths[j+1]-lengths[j]||1);
1477: 
1478:         const x=path[j][0]*(1-t)+path[j+1][0]*t;
1479:         const y=path[j][1]*(1-t)+path[j+1][1]*t;
1480: 
1481:         result.push([x,y]);
1482:     }
1483: 
1484:     return result;
1485: }
1486: function drawLabels(){
1487: 	const ctx = overlayCtx;
1488: 
1489: 	ctx.globalAlpha = 1;
1490: 	ctx.lineWidth = 1;
1491: 
1492: 	if(DEBUG.panel){
1493: 		debugPanel.innerHTML = window.debugPanelHeader || "";
1494: 	}
1495: 
1496:     const w=baseCanvas.width, h=baseCanvas.height;
1497:     const data=basePixels;
1498: 	
1499: 	function computeSpineForComponent(component, countryColor){
1500: 		if (component.length < 2) {
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

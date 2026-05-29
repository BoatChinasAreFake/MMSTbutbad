Created At: 2026-05-26T07:03:50Z
Completed At: 2026-05-26T07:03:50Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 1424
Total Bytes: 41408
Showing lines 700 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
700:     const now = performance.now();
701:     const frameTime = now - lastFrameTime;
702:     lastFrameTime = now;
703:     fpsArray.push(1000 / (frameTime || 1));
704:     if (fpsArray.length > 30) fpsArray.shift();
705:     const avgFps = fpsArray.reduce((a, b) => a + b, 0) / fpsArray.length;
706: 
707:     if (DEBUG.panel && debugPanel) {
708:         window.debugPanelHeader = `
709:             <div style="border-bottom: 1px solid #0f0; margin-bottom: 8px; padding-bottom: 4px;">
710:                 <b>WebGL Engine: ON</b><br>
711:                 FPS: ${avgFps.toFixed(0)}<br>
712:                 Frame Time: ${frameTime.toFixed(2)} ms<br>
713:                 Zoom: ${zoom.toFixed(2)}x<br>
714:                 Offset: (${offsetX.toFixed(0)}, ${offsetY.toFixed(0)})
715:             </div>
716:         `;
717:     }
718: }
719: 
720: function resamplePath(path, count){
721: 
722: 	const lengths = [0];
723: 
724: 	for (let i = 1; i < path.length; i++) {
725: 		const dx = path[i][0] - path[i - 1][0];
726: 		const dy = path[i][1] - path[i - 1][1];
727: 		lengths[i] = lengths[i - 1] + Math.hypot(dx, dy);
728: 	}
729: 
730:     const total=lengths[lengths.length-1];
731:     const step=total/(count-1);
732: 
733:     const result=[];
734:     let j=0;
735: 
736:     for(let i=0;i<count;i++){
737:         const target=i*step;
738: 
739:         while(j < lengths.length-2 && lengths[j+1] < target) j++;
740: 
741:         const t=(target-lengths[j])/(lengths[j+1]-lengths[j]||1);
742: 
743:         const x=path[j][0]*(1-t)+path[j+1][0]*t;
744:         const y=path[j][1]*(1-t)+path[j+1][1]*t;
745: 
746:         result.push([x,y]);
747:     }
748: 
749:     return result;
750: }
751: function drawLabels(){
752: 
753: 	ctx.setTransform(1,0,0,1,0,0);
754: 	ctx.globalAlpha = 1;
755: 	ctx.lineWidth = 1;
756: 
757: 	if(DEBUG.panel){
758: 		debugPanel.innerHTML = "";
759: 	}
760: 
761:     const w=baseCanvas.width, h=baseCanvas.height;
762:     const data=basePixels;
763: 
764:     function owner(x,y){
765:         if(x<0||y<0||x>=w||y>=h) return "__neutral__";
766: 		const key = provinceMap[y*w + x];
767: 		return ownership[key] || "__neutral__";
768:     }
769: 	
770: 	function computeSpineForComponent(component, countryColor){
771: 		if (component.length < 2) {
772: 			return { spine: [], path: [], controlPoints: [] };
773: 		}
774: 
775: 		const compSet = new Set(component);
776: 
777: 		// Calculate depth (distance to boundary) for each province in the component
778: 		const depth = {};
779: 		const depthQueue = [];
780: 
781: 		for (const id of component) {
782: 			let isBoundary = false;
783: 			const neighbors = provinceNeighbors[id] || [];
784: 			if (neighbors.size < 4) {
785: 				isBoundary = true;
786: 			}
787: 			for (const n of neighbors) {
788: 				if (!compSet.has(n)) {
789: 					isBoundary = true;
790: 					break;
791: 				}
792: 			}
793: 			if (isBoundary) {
794: 				depth[id] = 1;
795: 				depthQueue.push(id);
796: 			}
797: 		}
798: 
799: 		// Fallback
800: 		if (depthQueue.length === 0 && component.length > 0) {
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-05-26T07:04:59Z
Completed At: 2026-05-26T07:04:59Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 1418
Total Bytes: 41255
Showing lines 1 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: <!DOCTYPE html>
2: <html>
3: <head>
4:     <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
5:     <meta http-equiv="Pragma" content="no-cache">
6:     <meta http-equiv="Expires" content="0">
7:     <title>Map Sandbox</title>
8:     <style>
9:         body { margin: 0; overflow: hidden; background: #222; }
10: 
11:         .ui {
12:             position: fixed;
13:             top: 10px; left: 10px;
14:             z-index: 10;
15:             background: #111;
16:             padding: 10px;
17:             border-radius: 8px;
18:         }
19: 
20:         button { margin: 2px; }
21: 
22:         #debugPanel{
23:             position:fixed;
24:             top:10px;
25:             right:10px;
26:             background:#000;
27:             color:#0f0;
28:             font-family:monospace;
29:             font-size:12px;
30:             padding:10px;
31:             border-radius:8px;
32:             z-index:20;
33:             max-width:240px;
34:         }
35:     </style>
36: </head>
37: <body>
38: 
39: <div class="ui">
40:     <button onclick="setColor('yellow')">Yellow</button>
41:     <button onclick="setColor('red')">Red</button>
42:     <button onclick="setColor('blue')">Blue</button>
43:     <button onclick="setColor('green')">Green</button>
44:     <button onclick="setEraser()">Eraser</button>
45:     <button onclick="resetMap()">Reset</button>
46: 
47:     <div id="debugControls" style="
48:         margin-top:8px;
49:         color:white;
50:         font-family
<truncated 24328 bytes>
: 
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
752: 	const ctx = overlayCtx;
753: 
754: 	ctx.globalAlpha = 1;
755: 	ctx.lineWidth = 1;
756: 
757: 	if(DEBUG.panel){
758: 		debugPanel.innerHTML = window.debugPanelHeader || "";
759: 	}
760: 
761:     const w=baseCanvas.width, h=baseCanvas.height;
762:     const data=basePixels;
763: 	
764: 	function computeSpineForComponent(component, countryColor){
765: 		if (component.length < 2) {
766: 			return { spine: [], path: [], controlPoints: [] };
767: 		}
768: 
769: 		const compSet = new Set(component);
770: 
771: 		// Calculate depth (distance to boundary) for each province in the component
772: 		const depth = {};
773: 		const depthQueue = [];
774: 
775: 		for (const id of component) {
776: 			let isBoundary = false;
777: 			const neighbors = provinceNeighbors[id] || [];
778: 			if (neighbors.size < 4) {
779: 				isBoundary = true;
780: 			}
781: 			for (const n of neighbors) {
782: 				if (!compSet.has(n)) {
783: 					isBoundary = true;
784: 					break;
785: 				}
786: 			}
787: 			if (isBoundary) {
788: 				depth[id] = 1;
789: 				depthQueue.push(id);
790: 			}
791: 		}
792: 
793: 		// Fallback
794: 		if (depthQueue.length === 0 && component.length > 0) {
795: 			depth[component[0]] = 1;
796: 			depthQueue.push(component[0]);
797: 		}
798: 
799: 		while (depthQueue.length > 0) {
800: 			const curr = depthQueue.shift();
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

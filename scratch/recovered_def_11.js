Created At: 2026-05-29T03:06:35Z
Completed At: 2026-05-29T03:06:35Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/scratch/found_spine_drawLabels.js`
Total Lines: 66
Total Bytes: 2227
Showing lines 1 to 66
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: Created At: 2026-05-26T07:04:05Z
2: Completed At: 2026-05-26T07:04:05Z
3: The following changes were made by the multi_replace_file_content tool to: c:\Users\Faaz\Documents\GitHub\Mappa Mundi sine Tempore\index.html. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
4: [diff_block_start]
5: @@ -749,8 +749,8 @@
6:      return result;
7:  }
8:  function drawLabels(){
9: -
10: -	ctx.setTransform(1,0,0,1,0,0);
11: +	const ctx = overlayCtx;
12: +
13:  	ctx.globalAlpha = 1;
14:  	ctx.lineWidth = 1;
15:  
16: @@ -757,4 +757,4 @@
17: -		debugPanel.innerHTML = "";
18: +		debugPanel.innerHTML = window.debugPanelHeader || "";
19:  	}
20:  
21:      const w=baseCanvas.width, h=baseCanvas.height;
22: @@ -761,9 +761,3 @@
23: -
24: -    function owner(x,y){
25: -        if(x<0||y<0||x>=w||y>=h) return "__neutral__";
26: -		const key = provinceMap[y*w + x];
27: -		return ownership[key] || "__neutral__";
28: -    }
29:  	
30:  	function computeSpineForComponent(component, countryColor){
31:  		if (component.length < 2) {
32: @@ -1220,7 +1220,6 @@
33:  			
34:  			if(DEBUG.axis){
35:  				ctx.save();
36: -				ctx.setTransform(zoom,0,0,zoom,0,0);
37:  
38:  				ctx.strokeStyle = "rgba(255, 100, 0, 0.6)"; // Semi-transparent orange for raw Dijkstra axis
39:  				ctx.lineWidth = 1.5;
40: @@ -1236,7 +1236,6 @@
41:  
42:  			if(DEBUG.bezier){
43:  				ctx.save();
44: -				ctx.setTransform(zoom,0,0,zoom,0,0);
45:  
46:  				ctx.strokeStyle = "cyan"; // Cyan for the Bezier curve spine
47:  				ctx.lineWidth = 2.5;
48: @@ -1252,7 +1252,6 @@
49:  
50:  			if(DEBUG.points && controlPoints && controlPoints.length > 0){
51:  				ctx.save();
52: -				ctx.setTransform(zoom,0,0,zoom,0,0);
53:  				ctx.fillStyle = "red"; // Red circles for control points
54:  				for(const pt of controlPoints){
55:  					ctx.beginPath();
56: @@ -1383,7 +1383,6 @@
57:  				const angle = angle_straight + diff * rotationDamping;
58:  
59:  				ctx.save();
60: -				ctx.setTransform(zoom,0,0,zoom,0,0);
61:  
62:  				ctx.translate(px, py);
63:  				ctx.rotate(angle);
64: [diff_block_end]
65: 
66: Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.
The above content shows the entire, complete file contents of the requested file.

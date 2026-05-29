Created At: 2026-05-25T19:05:19Z
Completed At: 2026-05-25T19:05:19Z
File Path: `file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html`
Total Lines: 1182
Total Bytes: 29954
Showing lines 570 to 715
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
570: 	
571: 	function computeSpineForComponent(component, countryColor){
572: 		if (component.length < 2) {
573: 			return { spine: [], path: [], controlPoints: [] };
574: 		}
575: 
576: 		const compSet = new Set(component);
577: 
578: 		// Calculate depth (distance to boundary) for each province in the component
579: 		const depth = {};
580: 		const depthQueue = [];
581: 
582: 		for (const id of component) {
583: 			let isBoundary = false;
584: 			const neighbors = provinceNeighbors[id] || [];
585: 			if (neighbors.size < 4) {
586: 				isBoundary = true;
587: 			}
588: 			for (const n of neighbors) {
589: 				if (!compSet.has(n)) {
590: 					isBoundary = true;
591: 					break;
592: 				}
593: 			}
594: 			if (isBoundary) {
595: 				depth[id] = 1;
596: 				depthQueue.push(id);
597: 			}
598: 		}
599: 
600: 		// Fallback
601: 		if (depthQueue.length === 0 && component.length > 0) {
602: 			depth[component[0]] = 1;
603: 			depthQueue.push(component[0]);
604: 		}
605: 
606: 		while (depthQueue.length > 0) {
607: 			const curr = depthQueue.shift();
608: 			const currDepth = depth[curr];
609: 
610: 			for (const n of provinceNeighbors[curr] || []) {
611: 				if (compSet.has(n) && depth[n] === undefined) {
612: 					depth[n] = currDepth + 1;
613: 					depthQueue.push(n);
614: 				}
615: 			}
616: 		}
617: 
618: 		// Find max depth
619: 		let maxD = 1;
620: 		for (const id of component) {
621: 			if (depth[id] > maxD) maxD = depth[id];
622: 		}
623: 
624: 		// Find endpoints A and B that maximize the geodesic 
<truncated 1169 bytes>
 province centers
659: 					const stepDist = Math.hypot(currCenter.x - nCenter.x, currCenter.y - nCenter.y);
660: 					const nextCost = currCost + stepDist;
661: 
662: 					if (nextCost < dist[n]) {
663: 						dist[n] = nextCost;
664: 						pq.push([n, nextCost]);
665: 					}
666: 				}
667: 			}
668: 
669: 			for (const endId of component) {
670: 				if (dist[endId] !== Infinity && dist[endId] > maxGeodesicDist) {
671: 					maxGeodesicDist = dist[endId];
672: 					A = startId;
673: 					B = endId;
674: 				}
675: 			}
676: 		}
677: 
678: 		// Order endpoints to ensure natural reading:
679: 		// - If mostly horizontal (dx > dy), order left-to-right.
680: 		// - If mostly vertical (dy >= dx), order South-to-North (bottom-to-top, i.e., larger y to smaller y).
681: 		const centerA = provinceCenters[A];
682: 		const centerB = provinceCenters[B];
683: 		if (centerA && centerB) {
684: 			const dx = Math.abs(centerA.x - centerB.x);
685: 			const dy = Math.abs(centerA.y - centerB.y);
686: 			if (dx > dy) {
687: 				if (centerA.x > centerB.x) {
688: 					const temp = A;
689: 					A = B;
690: 					B = temp;
691: 				}
692: 			} else {
693: 				if (centerA.y < centerB.y) {
694: 					const temp = A;
695: 					A = B;
696: 					B = temp;
697: 				}
698: 			}
699: 		}
700: 
701: 		const isIreland = component.every(id => {
702: 			const p = provinceCenters[id];
703: 			return p && p.x <= 75;
704: 		});
705: 
706: 		const includesScotland = component.some(id => {
707: 			const p = provinceCenters[id];
708: 			return p && p.x > 75 && p.y < 14;
709: 		});
710: 
711: 		let tension = 0.95; // Nice curve for standalone England (excluding Scotland)
712: 		if (isIreland || includesScotland) {
713: 			tension = 0.0; // Straight line for Ireland and connected Great Britain / Scotland
714: 		}
715: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

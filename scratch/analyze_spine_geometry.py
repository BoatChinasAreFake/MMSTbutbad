import json
import math
from collections import deque

def analyze():
    # Load provinces metadata
    with open('provinces_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    # Load presets and ownership
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        preset_data = json.load(f)
        
    countries = preset_data['countries']
    ownership = preset_data['ownership']
    
    # Build reverse ownership map
    country_provinces = {}
    for prov_id, tag in ownership.items():
        if tag not in country_provinces:
            country_provinces[tag] = []
        country_provinces[tag].append(int(prov_id))
        
    province_centers = {}
    for k, v in meta['centers'].items():
        province_centers[int(k)] = v
        
    province_neighbors = {}
    for k, neighbors_list in meta['neighbors'].items():
        province_neighbors[int(k)] = [int(n) for n in neighbors_list]

    # Find neighbors from straits too
    straits_adj = {}
    if 'straits' in meta:
        for s in meta['straits']:
            a, b = int(s[0]), int(s[1])
            if a not in straits_adj: straits_adj[a] = []
            if b not in straits_adj: straits_adj[b] = []
            straits_adj[a].append(b)
            straits_adj[b].append(a)

    print("Analyzing 54 presets and their geometric characteristics...")
    
    results = []
    
    # Only analyze countries with non-default presets
    for tag, cinfo in countries.items():
        has_changed = (
            cinfo.get('labelOffset', 0) != 0 or
            cinfo.get('labelXOffset', 0) != 0 or
            cinfo.get('curvatureScale', 1) != 1 or
            cinfo.get('fontSizeScale', 1) != 1 or
            cinfo.get('labelRotation', 0) != 0 or
            cinfo.get('labelStretch', 1) != 1
        )
        if not has_changed:
            continue
            
        provs = country_provinces.get(tag, [])
        if len(provs) == 0:
            continue
            
        # Group into components using BFS
        provs_set = set(provs)
        visited = set()
        components = []
        
        for p in provs:
            if p in visited:
                continue
            comp = []
            queue = deque([p])
            visited.add(p)
            while queue:
                curr = queue.popleft()
                comp.append(curr)
                # neighbors
                for n in province_neighbors.get(curr, []):
                    if n in provs_set and n not in visited:
                        visited.add(n)
                        queue.append(n)
                # straits
                for n in straits_adj.get(curr, []):
                    if n in provs_set and n not in visited:
                        visited.add(n)
                        queue.append(n)
            components.append(comp)
            
        # Find the largest component by area/count
        if not components:
            continue
            
        def comp_area(comp):
            return sum(province_centers[pid]['count'] for pid in comp if pid in province_centers)
            
        main_comp = max(components, key=comp_area)
        if len(main_comp) < 4:
            continue
            
        # Calculate centroid of main component
        sumX = 0
        sumY = 0
        totalArea = 0
        for pid in main_comp:
            p = province_centers.get(pid)
            if p:
                sumX += p['x'] * p['count']
                sumY += p['y'] * p['count']
                totalArea += p['count']
        
        if totalArea == 0:
            continue
            
        meanX = sumX / totalArea
        meanY = sumY / totalArea
        
        # Estimate thickness
        thickness = max(30, min(120, math.sqrt(totalArea) * 0.55))
        
        # Find optimal straight path between candidate points (simplified pairing)
        # We can sort component by coordinate spread to find extreme ends
        # or do a heuristic search of candidates
        candidates = []
        maxCandidates = 35
        if len(main_comp) <= maxCandidates:
            candidates = list(main_comp)
        else:
            step = math.ceil(len(main_comp) / maxCandidates)
            candidates = [main_comp[i] for i in range(0, len(main_comp), step)]
            
        bestA, bestB = candidates[0], candidates[0]
        best_dist = -1
        # Simple longest distance pairing for skeleton approximation in python
        for i in range(len(candidates)):
            for j in range(i+1, len(candidates)):
                pA = province_centers.get(candidates[i])
                pB = province_centers.get(candidates[j])
                if pA and pB:
                    d = math.hypot(pB['x'] - pA['x'], pB['y'] - pA['y'])
                    if d > best_dist:
                        best_dist = d
                        bestA, bestB = candidates[i], candidates[j]
                        
        pA = province_centers[bestA]
        pB = province_centers[bestB]
        len_dir = math.hypot(pB['x'] - pA['x'], pB['y'] - pA['y']) or 1
        vx = (pB['x'] - pA['x']) / len_dir
        vy = (pB['y'] - pA['y']) / len_dir
        
        # Project all main component provinces
        sorted_projs = []
        for pid in main_comp:
            p = province_centers.get(pid)
            if p:
                proj = (p['x'] - meanX) * vx + (p['y'] - meanY) * vy
                perp = -(p['x'] - meanX) * vy + (p['y'] - meanY) * vx
                sorted_projs.append({'proj': proj, 'perp': perp, 'count': p['count']})
                
        sorted_projs.sort(key=lambda x: x['proj'])
        
        # Percentile trimming (12% to 88%)
        accum = 0
        projStart = sorted_projs[0]['proj']
        projEnd = sorted_projs[-1]['proj']
        startThreshold = totalArea * 0.12
        endThreshold = totalArea * 0.88
        for item in sorted_projs:
            accum += item['count']
            if accum >= startThreshold and projStart == sorted_projs[0]['proj']:
                projStart = item['proj']
            if accum >= endThreshold:
                projEnd = item['proj']
                break
                
        P0 = [meanX + projStart * vx, meanY + projStart * vy]
        P3 = [meanX + projEnd * vx, meanY + projEnd * vy]
        
        # Orient left to right
        if P3[0] < P0[0]:
            P0, P3 = P3, P0
            vx, vy = -vx, -vy
            projStart, projEnd = -projEnd, -projStart
            
        spine_len = math.hypot(P3[0] - P0[0], P3[1] - P0[1]) or 1
        
        # Midpoint of spine line
        spine_mid = [(P0[0] + P3[0]) / 2, (P0[1] + P3[1]) / 2]
        
        # Centroid offset from straight spine midpoint (in direction of normal [-vy, vx])
        # perp vector is [-vy, vx]
        centroid_dx = meanX - spine_mid[0]
        centroid_dy = meanY - spine_mid[1]
        centroid_perp = -centroid_dy * vy + centroid_dx * vx # projection along normal
        centroid_proj = centroid_dx * vx + centroid_dy * vy  # projection along spine direction
        
        results.append({
            'tag': tag,
            'name': cinfo['name'],
            'labelOffset': cinfo.get('labelOffset', 0),
            'labelXOffset': cinfo.get('labelXOffset', 0),
            'labelRotation': cinfo.get('labelRotation', 0),
            'labelStretch': cinfo.get('labelStretch', 1),
            'curvatureScale': cinfo.get('curvatureScale', 1),
            'centroid_perp': centroid_perp,
            'centroid_proj': centroid_proj,
            'thickness': thickness,
            'spine_len': spine_len,
            'aspect_ratio': spine_len / thickness
        })
        
    # Print out results
    print(f"{'Country Name':<35} | {'V-Shift':<7} | {'CentroidPerp':<12} | {'H-Shift':<7} | {'CentroidProj':<12} | {'Aspect':<6} | {'Stretch':<7} | {'Curve':<5}")
    print("-" * 115)
    for r in sorted(results, key=lambda x: x['name']):
        print(f"{r['name'][:35]:<35} | {r['labelOffset']:<7} | {r['centroid_perp']:+12.1f} | {r['labelXOffset']:<7} | {r['centroid_proj']:+12.1f} | {r['aspect_ratio']:5.2f} | {r['labelStretch']:<7} | {r['curvatureScale']:<5}")

if __name__ == '__main__':
    analyze()

import json
import math
from collections import deque

def analyze():
    with open('provinces_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        preset_data = json.load(f)
        
    countries = preset_data['countries']
    ownership = preset_data['ownership']
    
    country_provinces = {}
    for prov_id, tag in ownership.items():
        if tag not in country_provinces:
            country_provinces[tag] = []
        country_provinces[tag].append(int(prov_id))
        
    province_centers = {int(k): v for k, v in meta['centers'].items()}
    province_neighbors = {int(k): [int(n) for n in v] for k, v in meta['neighbors'].items()}
    
    straits_adj = {}
    if 'straits' in meta:
        for s in meta['straits']:
            a, b = int(s[0]), int(s[1])
            if a not in straits_adj: straits_adj[a] = []
            if b not in straits_adj: straits_adj[b] = []
            straits_adj[a].append(b)
            straits_adj[b].append(a)

    results = []
    
    for tag, cinfo in countries.items():
        has_changed = (
            cinfo.get('labelOffset', 0) != 0 or
            cinfo.get('labelXOffset', 0) != 0 or
            cinfo.get('curvatureScale', 1) != 1 or
            cinfo.get('labelRotation', 0) != 0 or
            cinfo.get('labelStretch', 1) != 1
        )
        if not has_changed:
            continue
            
        provs = country_provinces.get(tag, [])
        if len(provs) == 0:
            continue
            
        # Get components
        provs_set = set(provs)
        visited = set()
        components = []
        for p in provs:
            if p in visited: continue
            comp = []
            queue = deque([p])
            visited.add(p)
            while queue:
                curr = queue.popleft()
                comp.append(curr)
                for n in province_neighbors.get(curr, []):
                    if n in provs_set and n not in visited:
                        visited.add(n)
                        queue.append(n)
                for n in straits_adj.get(curr, []):
                    if n in provs_set and n not in visited:
                        visited.add(n)
                        queue.append(n)
            components.append(comp)
            
        if not components: continue
        main_comp = max(components, key=lambda c: sum(province_centers[pid]['count'] for pid in c if pid in province_centers))
        
        sumX, sumY, totalArea = 0, 0, 0
        for pid in main_comp:
            p = province_centers.get(pid)
            if p:
                sumX += p['x'] * p['count']
                sumY += p['y'] * p['count']
                totalArea += p['count']
                
        meanX = sumX / totalArea
        meanY = sumY / totalArea
        
        # Candidate selection
        candidates = []
        maxCandidates = 35
        if len(main_comp) <= maxCandidates:
            candidates = list(main_comp)
        else:
            step = math.ceil(len(main_comp) / maxCandidates)
            candidates = [main_comp[i] for i in range(0, len(main_comp), step)]
            
        bestA, bestB = candidates[0], candidates[0]
        best_dist = -1
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
        
        # Project all
        projs = []
        for pid in main_comp:
            p = province_centers.get(pid)
            if p:
                proj = (p['x'] - meanX) * vx + (p['y'] - meanY) * vy
                projs.append((proj, p['count']))
        projs.sort(key=lambda x: x[0])
        
        # Percentile limits
        accum = 0
        projStart = projs[0][0]
        projEnd = projs[-1][0]
        startThreshold = totalArea * 0.12
        endThreshold = totalArea * 0.88
        for p_val, count in projs:
            accum += count
            if accum >= startThreshold and projStart == projs[0][0]:
                projStart = p_val
            if accum >= endThreshold:
                projEnd = p_val
                break
                
        P0 = [meanX + projStart * vx, meanY + projStart * vy]
        P3 = [meanX + projEnd * vx, meanY + projEnd * vy]
        if P3[0] < P0[0]:
            P0, P3 = P3, P0
            vx, vy = -vx, -vy
            projStart, projEnd = -projEnd, -projStart
            
        spine_len = math.hypot(P3[0] - P0[0], P3[1] - P0[1]) or 1
        
        # Calculate weighted median projection
        accum = 0
        median_proj = projStart
        medianThreshold = totalArea * 0.50
        for p_val, count in projs:
            accum += count
            if accum >= medianThreshold:
                median_proj = p_val
                break
                
        # Find where median_proj lies relative to the spine center (projStart + projEnd) / 2
        spine_center_proj = (projStart + projEnd) / 2
        predicted_h_shift = median_proj - spine_center_proj
        
        results.append({
            'name': cinfo['name'],
            'labelXOffset': cinfo.get('labelXOffset', 0),
            'predicted_h_shift': predicted_h_shift,
            'spine_len': spine_len
        })
        
    print(f"{'Country Name':<35} | {'H-Shift (Manual)':<18} | {'Predicted (Weighted Median)':<28} | {'Spine Len':<10}")
    print("-" * 98)
    for r in sorted(results, key=lambda x: x['name']):
        print(f"{r['name'][:35]:<35} | {r['labelXOffset']:<18} | {r['predicted_h_shift']:+28.1f} | {r['spine_len']:<10.1f}")

if __name__ == '__main__':
    analyze()

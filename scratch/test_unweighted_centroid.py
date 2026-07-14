import json
import math
from collections import deque

def analyze():
    with open('provinces_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
    with open('preset_ownership_backup.json', 'r', encoding='utf-8') as f:
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
    
    for tag in ['000', '001', '004', '002', '003']: # Russia, USA, Australia, China, India
        cinfo = countries[tag]
        provs = country_provinces.get(tag, [])
        if len(provs) == 0: continue
            
        # Get main component
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
        
        # Weighted centroid
        sumX_w, sumY_w, totalArea_w = 0, 0, 0
        # Unweighted centroid
        sumX_uw, sumY_uw, totalArea_uw = 0, 0, 0
        
        for pid in main_comp:
            p = province_centers.get(pid)
            if p:
                sumX_w += p['x'] * p['count']
                sumY_w += p['y'] * p['count']
                totalArea_w += p['count']
                
                sumX_uw += p['x']
                sumY_uw += p['y']
                totalArea_uw += 1
                
        meanX_w = sumX_w / totalArea_w
        meanY_w = sumY_w / totalArea_w
        
        meanX_uw = sumX_uw / totalArea_uw
        meanY_uw = sumY_uw / totalArea_uw
        
        # Longest spine search
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
                proj = (p['x'] - meanX_w) * vx + (p['y'] - meanY_w) * vy
                projs.append((proj, p['count']))
        projs.sort(key=lambda x: x[0])
        
        accum = 0
        projStart = projs[0][0]
        projEnd = projs[-1][0]
        startThreshold = totalArea_w * 0.12
        endThreshold = totalArea_w * 0.88
        for p_val, count in projs:
            accum += count
            if accum >= startThreshold and projStart == projs[0][0]:
                projStart = p_val
            if accum >= endThreshold:
                projEnd = p_val
                break
                
        # Center of spine
        spine_center_proj = (projStart + projEnd) / 2
        
        # Project unweighted centroid relative to weighted mean
        uw_proj = (meanX_uw - meanX_w) * vx + (meanY_uw - meanY_w) * vy
        
        # Let's print out the differences
        print(f"Country: {cinfo['name']}")
        print(f"  Weighted Centroid Proj   = {0:.1f}")
        print(f"  Unweighted Centroid Proj = {uw_proj:.1f}")
        print(f"  Spine Center Proj        = {spine_center_proj:.1f}")
        print(f"  Distance from Spine Center to Unweighted = {uw_proj - spine_center_proj:.1f}")
        print()

if __name__ == '__main__':
    analyze()

import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime

#Suppress SSL warnings from MPC website#
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#CONFIGURATION#

#Maximum magnitude for LCO 2m telescope with ~60s exposure#
MAX_MAG = 22.0

LCO_SITES = {
    'ogg (Maui)':         {'lat': 20.7},
    'elp (Texas)':        {'lat': 30.7},
    'lsc (Chile)':        {'lat': -30.2},
    'cpt (South Africa)': {'lat': -32.4},
    'coj (Australia)':    {'lat': -31.3},
    'tfn (Tenerife)':     {'lat': 28.3},
}


#FETCH NEOCP#

def fetch_neocp():

    url = "https://www.minorplanetcenter.net/iau/NEO/toconfirm_tabular.html"
    
    try:
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            print("Could not find data table on NEOCP page")
            return []
        
        rows = table.find_all('tr')
        
        #All data is in one row so get all columns#
        all_cols = []
        for row in rows[1:]:  
            cols = row.find_all('td')
            all_cols.extend([col.text.strip() for col in cols])
        
        COLS_PER_OBJECT = 12
        objects = []
        seen = set()
        
        i = 0
        while i + COLS_PER_OBJECT <= len(all_cols):
            raw = all_cols[i:i + COLS_PER_OBJECT]
            
            if not raw[0] or 'Moved' in raw[6] or raw[2] == '':
                i += COLS_PER_OBJECT
                continue
            
            #Fixing parse issuses such as doubling and merging#
            desig_raw = raw[0]
            desig = desig_raw.split()[0] if desig_raw else ''
            
            if not desig or desig in seen:
                i += COLS_PER_OBJECT
                continue
            seen.add(desig)
            
            score_raw = raw[1]
            try:
                score_parts = score_raw.strip().split()
                if len(score_parts) == 2:
                    score = score_parts[1]
                else:
                    score = str(int(score_raw) // 1001) if len(score_raw) == 6 else score_raw
            except (ValueError, IndexError):
                score = score_raw
            
            ra_raw = raw[3]
            try:
                ra_parts = ra_raw.split()
                ra_deg = float(ra_parts[0])
                ra_hms = f"{ra_parts[1]} {ra_parts[2]}"
            except (ValueError, IndexError):
                ra_deg = None
                ra_hms = ra_raw
            
            dec_raw = raw[4]
            try:
                dec_parts = dec_raw.split()
                dec_deg = float(dec_parts[0])
                dec_dms = f"{dec_parts[1]} {dec_parts[2]}"
            except (ValueError, IndexError):
                dec_deg = None
                dec_dms = dec_raw
            
            v_raw = raw[5]
            try:
                v_parts = v_raw.split()
                mag = float(v_parts[-1])  
            except (ValueError, IndexError):
                mag = None
            
            obj = {
                'Temp_Desig': desig,
                'Score':      score,
                'Discovery':  raw[2],
                'RA_str':     ra_hms,
                'Dec_str':    dec_dms,
                'RA_deg':     ra_deg,
                'Dec_deg':    dec_deg,
                'V':          mag,
                'Updated':    raw[6],
                'Note':       raw[7],
                'NObs':       raw[8],
                'Arc':        raw[9],
                'H':          raw[10],
                'Not_Seen':   raw[11],
            }
            objects.append(obj)
            
            i += COLS_PER_OBJECT
        
        print(f"Fetched {len(objects)} objects from NEOCP")
        return objects
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NEOCP: {e}")
        return []

#CHECK OBSERVABILITY#

def check_observability(dec_deg):

    visible_from = []
    for site_name, site_info in LCO_SITES.items():
        if abs(dec_deg - site_info['lat']) < 60:
            visible_from.append(site_name)
    return visible_from


#ANALYSE OBJECTS#

def analyse_all(objects):
    results = []
    
    for obj in objects:
        ra = obj.get('RA_deg')
        dec = obj.get('Dec_deg')
        if ra is None or dec is None:
            continue
        
        mag = obj.get('V')
        if mag is not None and mag > MAX_MAG:
            continue
        
        dec_for_obs = parse_dec(obj['Dec_str'])
        if dec_for_obs is None:
            continue
            
        visible_from = check_observability(dec_for_obs)
        if not visible_from:
            continue
        
        note = obj.get('Note', '')
        
        results.append({
            'desig':        obj['Temp_Desig'],
            'ra_str':       obj['RA_str'],
            'dec_str':      obj['Dec_str'],
            'ra_deg':       ra,
            'dec_deg':      dec_for_obs,
            'mag':          mag,
            'discovery':    obj['Discovery'],
            'nobs':         obj['NObs'],
            'arc':          obj['Arc'],
            'H':            obj['H'],
            'not_seen':     obj['Not_Seen'],
            'note':         note,
            'score':        obj['Score'],
            'visible_from': visible_from,
            'num_sites':    len(visible_from),
        })
    
    results.sort(key=lambda x: x['num_sites'], reverse=True)
    return results


def parse_dec(dec_str):

    try:
        parts = dec_str.strip().split()
        sign = -1 if '-' in parts[0] else 1
        degrees = abs(float(parts[0]))
        minutes = float(parts[1])
        return sign * (degrees + minutes / 60.0)
    except (ValueError, IndexError):
        return None


#PRINT RESULTS#

def print_results(results):
    print(".")
    print("OBSERVABLE NEOCP OBJECTS FROM LCO")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")

    
    print(f"\n  {'Desig':<12} {'RA':>8} {'Dec':>8} {'V':>5} "
          f"{'NObs':>5} {'Arc':>6} {'H':>5} {'Sites':>5} {'Note':>5}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*5} "
          f"{'-'*5} {'-'*6} {'-'*5} {'-'*5} {'-'*5}")
    
    for r in results:
        note_flag = f"  {r['note']}" if r['note'] else ""
        mag_str = f"{r['mag']:>5.1f}" if r['mag'] is not None else "  N/A"
        print(f"  {r['desig']:<12} {r['ra_str']:>8} {r['dec_str']:>8} "
              f"{mag_str} {r['nobs']:>5} {r['arc']:>6} "
              f"{r['H']:>5} {r['num_sites']:>5}{note_flag}")
    
    print(".")
    print("TOP CANDIDATES - SITE DETAILS")

    
    for r in results[:10]:
        print(f"\n  {r['desig']}")
        print(f"    Discovery:    {r['discovery']}")
        print(f"    RA/Dec:       {r['ra_str']} / {r['dec_str']}")
        print(f"    Magnitude:    {r['mag']:.1f}")
        print(f"    Observations: {r['nobs']}  Arc: {r['arc']} days")
        print(f"    Last seen:    {r['not_seen']} days ago")
        print(f"    Visible from: {', '.join(r['visible_from'])}")
        if r['note']:
            print(f"   Note:       {r['note']}")
    
    print(".")
    print("SUMMARY")
    print(f"Total NEOCP objects:     {len(results)} observable from LCO")
    print(f"Bright enough (V<{MAX_MAG}):  {len([r for r in results if r['mag'] and r['mag'] < MAX_MAG])}")



#RUN#

if __name__ == '__main__':
    objects = fetch_neocp()
    if objects:
        results = analyse_all(objects)
        print_results(results)

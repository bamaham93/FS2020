import requests
import xml.etree.ElementTree as ET
from datetime import datetime



def fetch_metar(icao: str):
    """Fetch latest METAR for an ICAO airport code using AviationWeather.gov ADDS.
    Returns a dict with keys: raw_text, observation_time, temp_c, wind, flight_category or None on failure.
    Prints debug info to console for diagnosis.
    """
    if not icao:
        print("fetch_metar: ICAO missing")
        return None
    icao = icao.strip().upper()
    # NOAA Aviation Weather plain text METAR endpoint
    url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao.upper()}.TXT"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; FS2020App/1.0)"}
        resp = requests.get(url, timeout=6, headers=headers)
        print(f"fetch_metar: {icao} HTTP {resp.status_code}")
        print("URL:", resp.url)
        print("Response (first 1000 chars):\n", resp.text[:1000])
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        if len(lines) < 2:
            print(f"fetch_metar: {icao} - No METAR found in response.")
            return None
        # First line is timestamp, second is raw METAR
        obs_time = lines[0].strip()
        raw = lines[1].strip()
        # Parse temp and wind from METAR string (simple regex)
        import re
        # Initialize all fields
        wind = None
        wind_gust = None
        vis = None
        sky = []
        temp_c = None
        dew_c = None
        altim = None
        remarks = None

        # Wind: e.g. 06003KT or VRB03KT or 06003G15KT
        m = re.search(r" (\d{3}|VRB)(\d{2,3})(G(\d{2,3}))?KT", raw)
        if m:
            dir, spd, _, gust = m.group(1), m.group(2), m.group(3), m.group(4)
            wind = f"{dir}° @ {spd} kt" if dir != 'VRB' else f"VRB @ {spd} kt"
            if gust:
                wind_gust = f"Gust {gust} kt"

        # Visibility: e.g. 10SM, 6SM
        m = re.search(r" (\d{1,2})SM", raw)
        if m:
            vis = f"{m.group(1)} SM"

        # Sky condition: OVC009 SCT020 BKN100 etc.
        sky = re.findall(r" (FEW|SCT|BKN|OVC|CLR|SKC)(\d{3})", raw)
        sky_str = ", ".join([f"{cover} {int(height)*100} ft" for cover, height in sky]) if sky else None

        # Temp/dewpoint: 12/11 or M01/M03
        m = re.search(r" (M?\d{2})/(M?\d{2}) ", raw+" ")
        if m:
            t, d = m.group(1), m.group(2)
            temp_c = -int(t[1:]) if t.startswith('M') else int(t)
            dew_c = -int(d[1:]) if d.startswith('M') else int(d)

        # Altimeter: e.g. A2992
        m = re.search(r" A(\d{4})", raw)
        if m:
            altim = f"{m.group(1)[:2]}.{m.group(1)[2:]} inHg"

        # Remarks: RMK ...
        m = re.search(r" RMK (.+)$", raw)
        remarks = None
        remarks_translated = None
        if m:
            remarks = m.group(1)
            # Simple translation for common codes
            translations = []
            # AO2: Automated station with precipitation sensor
            if 'AO2' in remarks:
                translations.append('Automated station with precipitation sensor')
            if 'AO1' in remarks:
                translations.append('Automated station without precipitation sensor')
            # SLPxxx: Sea-level pressure
            m_slp = re.search(r"SLP(\d{3})", remarks)
            if m_slp:
                val = m_slp.group(1)
                slp = float(val) / 10.0
                translations.append(f"Sea-level pressure: {slp:.1f} hPa")
            # 600xx: Precipitation in last hour (in hundredths of an inch)
            m_600 = re.search(r"600(\d{3})", remarks)
            if m_600:
                val = int(m_600.group(1))
                if val > 0:
                    translations.append(f"Precipitation last hour: {val/100.0:.2f} in")
            # Txxxx: Precise temp/dewpoint (in tenths of C)
            m_t = re.search(r"T(\d{4})(\d{4})", remarks)
            if m_t:
                t_raw, d_raw = m_t.group(1), m_t.group(2)
                def parse_t(val):
                    sign = -1 if val[0]=='1' else 1
                    return sign * int(val[1:])/10.0
                t = parse_t(t_raw)
                d = parse_t(d_raw)
                translations.append(f"Precise temp: {t:.1f}°C, dewpoint: {d:.1f}°C")
            # $: Maintenance needed
            if '$' in remarks:
                translations.append('Maintenance needed at station')
            # 550xx: Pressure tendency
            m_550 = re.search(r"550(\d{2})", remarks)
            if m_550:
                translations.append('Pressure tendency code: ' + m_550.group(1))
            if translations:
                remarks_translated = "; ".join(translations)

        return {
            "raw_text": raw,
            "observation_time": obs_time,
            "temp_c": temp_c,
            "dew_c": dew_c,
            "wind": wind,
            "wind_gust": wind_gust,
            "visibility": vis,
            "sky": sky_str,
            "altimeter": altim,
            "remarks": remarks,
            "remarks_translated": remarks_translated,
            "flight_category": None,
        }
    except Exception as exc:
        print(f"fetch_metar: {icao} - Exception: {exc}")
        return None

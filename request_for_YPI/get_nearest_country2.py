import math
from typing import Dict, Optional


# Base de données locale avec les coordonnées de tous les pays
COUNTRIES_DATABASE = {
    "AD": {"name": "Andorra", "lat": 42.5462, "lon": 1.6004},
    "AE": {"name": "United Arab Emirates", "lat": 23.4241, "lon": 53.8478},
    "AF": {"name": "Afghanistan", "lat": 33.9391, "lon": 67.709},
    "AG": {"name": "Antigua and Barbuda", "lat": 17.0578, "lon": -61.7964},
    "AI": {"name": "Anguilla", "lat": 18.2206, "lon": -63.0686},
    "AL": {"name": "Albania", "lat": 41.1533, "lon": 20.1683},
    "AM": {"name": "Armenia", "lat": 40.0691, "lon": 45.0382},
    "AO": {"name": "Angola", "lat": -11.2027, "lon": 17.8739},
    "AR": {"name": "Argentina", "lat": -38.4161, "lon": -63.6167},
    "AT": {"name": "Austria", "lat": 47.5162, "lon": 14.5501},
    "AU": {"name": "Australia", "lat": -25.2744, "lon": 133.7751},
    "AZ": {"name": "Azerbaijan", "lat": 40.1431, "lon": 47.5769},
    "BA": {"name": "Bosnia and Herzegovina", "lat": 43.9159, "lon": 17.6791},
    "BB": {"name": "Barbados", "lat": 13.1939, "lon": -59.5432},
    "BD": {"name": "Bangladesh", "lat": 23.6850, "lon": 90.3563},
    "BE": {"name": "Belgium", "lat": 50.5039, "lon": 4.4699},
    "BF": {"name": "Burkina Faso", "lat": 12.2383, "lon": -1.5616},
    "BG": {"name": "Bulgaria", "lat": 42.7339, "lon": 25.4858},
    "BH": {"name": "Bahrain", "lat": 26.0667, "lon": 50.5577},
    "BI": {"name": "Burundi", "lat": -3.3731, "lon": 29.9189},
    "BJ": {"name": "Benin", "lat": 9.3077, "lon": 2.3158},
    "BN": {"name": "Brunei", "lat": 4.5353, "lon": 114.7277},
    "BO": {"name": "Bolivia", "lat": -16.2902, "lon": -63.5887},
    "BR": {"name": "Brazil", "lat": -14.2350, "lon": -51.9253},
    "BS": {"name": "Bahamas", "lat": 25.0343, "lon": -77.3963},
    "BT": {"name": "Bhutan", "lat": 27.5142, "lon": 90.4336},
    "BW": {"name": "Botswana", "lat": -22.3285, "lon": 24.6849},
    "BY": {"name": "Belarus", "lat": 53.7098, "lon": 27.9534},
    "BZ": {"name": "Belize", "lat": 17.1899, "lon": -88.7979},
    "CA": {"name": "Canada", "lat": 56.1304, "lon": -106.3468},
    "CD": {"name": "Democratic Republic of the Congo", "lat": -4.0383, "lon": 21.7587},
    "CF": {"name": "Central African Republic", "lat": 6.6111, "lon": 20.9394},
    "CG": {"name": "Republic of the Congo", "lat": -4.0383, "lon": 21.7587},
    "CH": {"name": "Switzerland", "lat": 46.8182, "lon": 8.2275},
    "CI": {"name": "Côte d'Ivoire", "lat": 7.5400, "lon": -5.5471},
    "CL": {"name": "Chile", "lat": -35.6751, "lon": -71.5430},
    "CM": {"name": "Cameroon", "lat": 3.8480, "lon": 11.5021},
    "CN": {"name": "China", "lat": 35.8617, "lon": 104.1954},
    "CO": {"name": "Colombia", "lat": 4.5709, "lon": -74.2973},
    "CR": {"name": "Costa Rica", "lat": 9.7489, "lon": -83.7534},
    "CU": {"name": "Cuba", "lat": 21.5218, "lon": -77.7812},
    "CV": {"name": "Cape Verde", "lat": 16.5388, "lon": -23.0418},
    "CY": {"name": "Cyprus", "lat": 34.9249, "lon": 33.4299},
    "CZ": {"name": "Czechia", "lat": 49.8175, "lon": 15.4730},
    "DE": {"name": "Germany", "lat": 51.1657, "lon": 10.4515},
    "DJ": {"name": "Djibouti", "lat": 11.8254, "lon": 42.5905},
    "DK": {"name": "Denmark", "lat": 56.2639, "lon": 9.5018},
    "DM": {"name": "Dominica", "lat": 15.4150, "lon": -61.3710},
    "DO": {"name": "Dominican Republic", "lat": 18.7357, "lon": -70.1627},
    "DZ": {"name": "Algeria", "lat": 28.0339, "lon": 1.6596},
    "EC": {"name": "Ecuador", "lat": -1.8312, "lon": -78.1834},
    "EE": {"name": "Estonia", "lat": 58.5953, "lon": 25.0136},
    "EG": {"name": "Egypt", "lat": 26.8206, "lon": 30.8025},
    "ER": {"name": "Eritrea", "lat": 15.1794, "lon": 39.7823},
    "ES": {"name": "Spain", "lat": 40.4637, "lon": -3.7492},
    "ET": {"name": "Ethiopia", "lat": 9.1450, "lon": 40.4897},
    "FI": {"name": "Finland", "lat": 61.9241, "lon": 25.7482},
    "FJ": {"name": "Fiji", "lat": -17.7134, "lon": 178.0650},
    "FK": {"name": "Falkland Islands", "lat": -51.7934, "lon": -59.5432},
    "FR": {"name": "France", "lat": 46.2276, "lon": 2.2137},
    "GA": {"name": "Gabon", "lat": -0.8037, "lon": 11.6045},
    "GB": {"name": "United Kingdom", "lat": 55.3781, "lon": -3.4360},
    "GD": {"name": "Grenada", "lat": 12.1696, "lon": -61.6742},
    "GE": {"name": "Georgia", "lat": 42.3154, "lon": 43.3569},
    "GH": {"name": "Ghana", "lat": 7.3697, "lon": -5.8789},
    "GI": {"name": "Gibraltar", "lat": 36.1408, "lon": -5.3536},
    "GL": {"name": "Greenland", "lat": 71.7069, "lon": -42.6043},
    "GM": {"name": "Gambia", "lat": 13.4549, "lon": -15.3105},
    "GN": {"name": "Guinea", "lat": 9.9456, "lon": -9.6966},
    "GQ": {"name": "Equatorial Guinea", "lat": 1.6508, "lon": 10.2679},
    "GR": {"name": "Greece", "lat": 39.0742, "lon": 21.8243},
    "GT": {"name": "Guatemala", "lat": 15.7835, "lon": -90.2308},
    "GW": {"name": "Guinea-Bissau", "lat": 11.8037, "lon": -15.1804},
    "GY": {"name": "Guyana", "lat": 4.8604, "lon": -58.9302},
    "HK": {"name": "Hong Kong", "lat": 22.3193, "lon": 114.1694},
    "HN": {"name": "Honduras", "lat": 15.2000, "lon": -86.2419},
    "HR": {"name": "Croatia", "lat": 45.1000, "lon": 15.2000},
    "HT": {"name": "Haiti", "lat": 18.9712, "lon": -72.2852},
    "HU": {"name": "Hungary", "lat": 47.1625, "lon": 19.5033},
    "ID": {"name": "Indonesia", "lat": -0.7893, "lon": 113.9213},
    "IE": {"name": "Ireland", "lat": 53.4129, "lon": -8.2439},
    "IL": {"name": "Israel", "lat": 31.0461, "lon": 34.8516},
    "IN": {"name": "India", "lat": 20.5937, "lon": 78.9629},
    "IQ": {"name": "Iraq", "lat": 33.2232, "lon": 43.6793},
    "IR": {"name": "Iran", "lat": 32.4279, "lon": 53.6880},
    "IS": {"name": "Iceland", "lat": 64.9631, "lon": -19.0208},
    "IT": {"name": "Italy", "lat": 41.8719, "lon": 12.5674},
    "JM": {"name": "Jamaica", "lat": 18.1096, "lon": -77.2975},
    "JO": {"name": "Jordan", "lat": 30.5852, "lon": 36.2384},
    "JP": {"name": "Japan", "lat": 36.2048, "lon": 138.2529},
    "KE": {"name": "Kenya", "lat": -0.0236, "lon": 37.9062},
    "KG": {"name": "Kyrgyzstan", "lat": 41.2044, "lon": 74.7661},
    "KH": {"name": "Cambodia", "lat": 12.5657, "lon": 104.9910},
    "KI": {"name": "Kiribati", "lat": -3.3704, "lon": -168.7340},
    "KM": {"name": "Comoros", "lat": -11.6455, "lon": 43.3333},
    "KN": {"name": "Saint Kitts and Nevis", "lat": 17.2978, "lon": -62.7830},
    "KP": {"name": "North Korea", "lat": 40.3399, "lon": 127.5101},
    "KR": {"name": "South Korea", "lat": 35.9078, "lon": 127.7669},
    "KW": {"name": "Kuwait", "lat": 29.3117, "lon": 47.4818},
    "KZ": {"name": "Kazakhstan", "lat": 48.0196, "lon": 66.9237},
    "LA": {"name": "Laos", "lat": 19.8523, "lon": 102.4955},
    "LB": {"name": "Lebanon", "lat": 33.8547, "lon": 35.8623},
    "LC": {"name": "Saint Lucia", "lat": 13.9094, "lon": -60.9789},
    "LI": {"name": "Liechtenstein", "lat": 47.2661, "lon": 9.5585},
    "LK": {"name": "Sri Lanka", "lat": 7.8731, "lon": 80.7718},
    "LR": {"name": "Liberia", "lat": 6.4281, "lon": -9.4295},
    "LS": {"name": "Lesotho", "lat": -29.6100, "lon": 28.2336},
    "LT": {"name": "Lithuania", "lat": 55.1694, "lon": 23.8813},
    "LU": {"name": "Luxembourg", "lat": 49.8153, "lon": 6.1296},
    "LV": {"name": "Latvia", "lat": 56.8796, "lon": 24.6032},
    "LY": {"name": "Libya", "lat": 26.3351, "lon": 17.2283},
    "MA": {"name": "Morocco", "lat": 31.7917, "lon": -7.0926},
    "MC": {"name": "Monaco", "lat": 43.7384, "lon": 7.4246},
    "MD": {"name": "Moldova", "lat": 47.4116, "lon": 28.3699},
    "ME": {"name": "Montenegro", "lat": 42.7087, "lon": 19.3744},
    "MG": {"name": "Madagascar", "lat": -18.7669, "lon": 46.8691},
    "MH": {"name": "Marshall Islands", "lat": 7.1315, "lon": 171.1845},
    "MK": {"name": "North Macedonia", "lat": 41.6086, "lon": 21.7453},
    "ML": {"name": "Mali", "lat": 17.5707, "lon": -3.9962},
    "MM": {"name": "Myanmar", "lat": 21.9162, "lon": 95.9560},
    "MN": {"name": "Mongolia", "lat": 46.8625, "lon": 103.8467},
    "MO": {"name": "Macao", "lat": 22.1987, "lon": 113.5439},
    "MR": {"name": "Mauritania", "lat": 21.0079, "lon": -10.9408},
    "MS": {"name": "Montserrat", "lat": 16.7425, "lon": -62.1898},
    "MT": {"name": "Malta", "lat": 35.9375, "lon": 14.3754},
    "MU": {"name": "Mauritius", "lat": -20.3484, "lon": 57.5522},
    "MV": {"name": "Maldives", "lat": 3.2028, "lon": 73.2207},
    "MW": {"name": "Malawi", "lat": -13.2543, "lon": 34.3015},
    "MX": {"name": "Mexico", "lat": 23.6345, "lon": -102.5528},
    "MY": {"name": "Malaysia", "lat": 4.2105, "lon": 101.6964},
    "MZ": {"name": "Mozambique", "lat": -18.6657, "lon": 35.5296},
    "NA": {"name": "Namibia", "lat": -22.9375, "lon": 18.6947},
    "NE": {"name": "Niger", "lat": 17.6078, "lon": 8.6753},
    "NG": {"name": "Nigeria", "lat": 9.0820, "lon": 8.6753},
    "NI": {"name": "Nicaragua", "lat": 12.8654, "lon": -85.2072},
    "NL": {"name": "Netherlands", "lat": 52.1326, "lon": 5.2913},
    "NO": {"name": "Norway", "lat": 60.4720, "lon": 8.4689},
    "NP": {"name": "Nepal", "lat": 28.3949, "lon": 84.1240},
    "NR": {"name": "Nauru", "lat": -0.5228, "lon": 166.9315},
    "NZ": {"name": "New Zealand", "lat": -40.9006, "lon": 174.8860},
    "OM": {"name": "Oman", "lat": 21.4735, "lon": 55.9754},
    "PA": {"name": "Panama", "lat": 8.7832, "lon": -80.7744},
    "PE": {"name": "Peru", "lat": -9.1900, "lon": -75.0152},
    "PG": {"name": "Papua New Guinea", "lat": -6.3150, "lon": 143.9555},
    "PH": {"name": "Philippines", "lat": 12.8797, "lon": 121.7740},
    "PK": {"name": "Pakistan", "lat": 30.3753, "lon": 69.3451},
    "PL": {"name": "Poland", "lat": 51.9194, "lon": 19.1451},
    "PT": {"name": "Portugal", "lat": 39.3999, "lon": -8.2245},
    "PW": {"name": "Palau", "lat": 7.3150, "lon": 134.4807},
    "PY": {"name": "Paraguay", "lat": -23.4425, "lon": -58.4438},
    "QA": {"name": "Qatar", "lat": 25.3548, "lon": 51.1839},
    "RO": {"name": "Romania", "lat": 45.9432, "lon": 24.9668},
    "RS": {"name": "Serbia", "lat": 44.0165, "lon": 21.0059},
    "RU": {"name": "Russia", "lat": 61.5240, "lon": 105.3188},
    "RW": {"name": "Rwanda", "lat": -1.9403, "lon": 29.8739},
    "SA": {"name": "Saudi Arabia", "lat": 23.8859, "lon": 45.0792},
    "SB": {"name": "Solomon Islands", "lat": -9.6457, "lon": 160.1562},
    "SC": {"name": "Seychelles", "lat": -4.6796, "lon": 55.4920},
    "SD": {"name": "Sudan", "lat": 12.8628, "lon": 30.8065},
    "SE": {"name": "Sweden", "lat": 60.1282, "lon": 18.6435},
    "SG": {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
    "SI": {"name": "Slovenia", "lat": 46.1512, "lon": 14.9955},
    "SK": {"name": "Slovakia", "lat": 48.6690, "lon": 19.6990},
    "SL": {"name": "Sierra Leone", "lat": 8.4606, "lon": -11.7799},
    "SM": {"name": "San Marino", "lat": 43.9424, "lon": 12.4578},
    "SN": {"name": "Senegal", "lat": 14.4974, "lon": -14.4524},
    "SO": {"name": "Somalia", "lat": 5.1521, "lon": 46.1996},
    "SR": {"name": "Suriname", "lat": 3.9193, "lon": -56.0278},
    "SS": {"name": "South Sudan", "lat": 6.8770, "lon": 31.3070},
    "ST": {"name": "São Tomé and Príncipe", "lat": 0.6295, "lon": 6.5296},
    "SV": {"name": "El Salvador", "lat": 13.7942, "lon": -88.8965},
    "SY": {"name": "Syria", "lat": 34.8021, "lon": 38.9968},
    "SZ": {"name": "Eswatini", "lat": -26.5225, "lon": 31.4659},
    "TC": {"name": "Turks and Caicos Islands", "lat": 21.9945, "lon": -71.9541},
    "TD": {"name": "Chad", "lat": 15.4730, "lon": 18.7322},
    "TG": {"name": "Togo", "lat": 6.1256, "lon": 1.2317},
    "TH": {"name": "Thailand", "lat": 15.8700, "lon": 100.9925},
    "TJ": {"name": "Tajikistan", "lat": 38.8610, "lon": 71.2761},
    "TL": {"name": "Timor-Leste", "lat": -8.8383, "lon": 125.9181},
    "TM": {"name": "Turkmenistan", "lat": 38.9697, "lon": 59.5563},
    "TN": {"name": "Tunisia", "lat": 33.8869, "lon": 9.5375},
    "TO": {"name": "Tonga", "lat": -21.1789, "lon": -175.1982},
    "TR": {"name": "Turkey", "lat": 38.9637, "lon": 35.2433},
    "TT": {"name": "Trinidad and Tobago", "lat": 10.6918, "lon": -61.2225},
    "TV": {"name": "Tuvalu", "lat": -7.1095, "lon": 177.6493},
    "TW": {"name": "Taiwan", "lat": 23.6978, "lon": 120.9605},
    "TZ": {"name": "Tanzania", "lat": -6.3690, "lon": 34.8888},
    "UA": {"name": "Ukraine", "lat": 48.3794, "lon": 31.1656},
    "UG": {"name": "Uganda", "lat": 1.3733, "lon": 32.2903},
    "US": {"name": "United States", "lat": 37.0902, "lon": -95.7129},
    "UY": {"name": "Uruguay", "lat": -32.5228, "lon": -55.7658},
    "UZ": {"name": "Uzbekistan", "lat": 41.3775, "lon": 64.5853},
    "VA": {"name": "Vatican City", "lat": 41.9029, "lon": 12.4534},
    "VC": {"name": "Saint Vincent and the Grenadines", "lat": 12.9843, "lon": -61.2872},
    "VE": {"name": "Venezuela", "lat": 6.4238, "lon": -66.5897},
    "VN": {"name": "Vietnam", "lat": 14.0583, "lon": 108.2772},
    "VU": {"name": "Vanuatu", "lat": -17.7404, "lon": 168.3045},
    "WS": {"name": "Samoa", "lat": -13.7590, "lon": -172.1046},
    "YE": {"name": "Yemen", "lat": 15.5527, "lon": 48.5164},
    "ZA": {"name": "South Africa", "lat": -30.5595, "lon": 22.9375},
    "ZM": {"name": "Zambia", "lat": -13.1339, "lon": 27.8493},
    "ZW": {"name": "Zimbabwe", "lat": -19.0154, "lon": 29.1549},
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en kilomètres entre deux points (latitude, longitude).
    Utilise la formule Haversine.
    
    Args:
        lat1, lon1: Coordonnées du point 1
        lat2, lon2: Coordonnées du point 2
    
    Returns:
        float: Distance en kilomètres
    """
    R = 6371  # Rayon de la Terre en km
    
    # Convertir les degrés en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formule Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return distance


def find_nearest_countries_by_iso(iso_code: str, num_countries: int = 5) -> Optional[Dict]:
    """
    Trouve les N pays les plus proches d'un pays donné en utilisant son code ISO 3166-1 alpha-2.
    Utilise une base de données locale.
    
    Args:
        iso_code: Code ISO 3166-1 alpha-2 du pays (ex: "FR", "DE", "KE")
        num_countries: Nombre de pays à retourner (par défaut 5)
    
    Returns:
        dict avec le pays de référence et ses pays les plus proches
    """
    
    # Valider et normaliser le code ISO
    iso_code = iso_code.upper()
    
    if iso_code not in COUNTRIES_DATABASE:
        print(f"❌ ISO code '{iso_code}' not found")
        available_codes = sorted(COUNTRIES_DATABASE.keys())
        print(f"Available ISO codes ({len(available_codes)} total):")
        # Afficher les codes par groupes de 20
        for i in range(0, len(available_codes), 20):
            print(f"   {' '.join(available_codes[i:i+20])}")
        return None
    
    # Récupérer la référence
    reference = COUNTRIES_DATABASE[iso_code]
    ref_lat = reference["lat"]
    ref_lon = reference["lon"]
    
    # Calculer les distances
    distances = []
    
    for code, country_data in COUNTRIES_DATABASE.items():
        if code == iso_code:
            continue  # Exclure le pays de référence
        
        distance = haversine_distance(
            ref_lat, 
            ref_lon,
            country_data["lat"],
            country_data["lon"]
        )
        
        distances.append({
            "iso_code": code,
            "country_name": country_data["name"],
            "distance_km": round(distance, 2),
        })
    
    # Trier par distance et récupérer les N plus proches
    distances.sort(key=lambda x: x["distance_km"])
    
    result = {
        "reference_iso_code": iso_code,
        "reference_country_name": reference["name"],
        "nearest_countries": distances[:num_countries]
    }
    
    return result


def get_5_nearest_countries_by_coordinates(country_code: str, num_countries: int = 5) -> Optional[Dict]:
    """
    Trouve les N pays les plus proches d'un pays donné en utilisant les coordonnées.
    (Fonction legacy - utilise find_nearest_countries_by_iso())
    
    Args:
        country_code: Code du pays (ex: "FR")
        num_countries: Nombre de pays à retourner (par défaut 5)
    
    Returns:
        dict avec le pays de référence et ses pays les plus proches
    """
    return find_nearest_countries_by_iso(country_code, num_countries)


def display_nearest_countries(result: Optional[Dict]) -> None:
    """Affiche les résultats de manière lisible."""
    
    if not result:
        print("❌ No results to display")
        return
    
    ref_code = result["reference_iso_code"]
    ref_name = result["reference_country_name"]
    
    print("\n" + "="*80)
    print(f"🌍 5 NEAREST COUNTRIES TO {ref_code} ({ref_name})")
    print("="*80 + "\n")
    
    print(f"{'Rank':<6} {'ISO':<8} {'Country Name':<35} {'Distance (km)':>15}")
    print("-"*80)
    
    for i, country in enumerate(result["nearest_countries"], 1):
        code = country["iso_code"]
        name = country["country_name"]
        distance = country["distance_km"]
        
        print(f"{i:<6} {code:<8} {name:<35} {distance:>15,.2f}")
    
    print("\n")


def export_to_json(result: Optional[Dict], filename: str = "nearest_countries.json") -> None:
    """Exporte les résultats en JSON."""
    
    if not result:
        return
    
    import json
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results exported to {filename}")


if __name__ == "__main__":
    # Test 1: France (ISO 3166-1 alpha-2: FR)
    print("\n" + "="*80)
    print("TEST 1: NEAREST COUNTRIES TO FRANCE (FR)")
    print("="*80)
    
    result_fr = find_nearest_countries_by_iso("FR", num_countries=5)
    print(result_fr)
    display_nearest_countries(result_fr)
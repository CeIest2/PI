import requests
import math
from typing import List, Dict, Optional
import time


def get_all_countries_coordinates() -> Dict[str, Dict]:
    """
    Récupère les coordonnées de tous les pays via l'API RestCountries.
    
    Returns:
        dict: Dictionnaire avec code pays comme clé et coordonnées comme valeur
    """
    print("📍 Fetching coordinates for all countries from RestCountries API...")
    
    # URL alternatives en cas d'erreur
    urls = [
        "https://restcountries.com/v3.1/all",
        "https://restcountries.com/v2/all",
        "https://restcountries.eu/rest/v2/all"
    ]
    
    for url in urls:
        try:
            print(f"   Trying: {url}")
            
            # Ajouter un User-Agent et des headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                url, 
                timeout=15,  # Augmenter le timeout
                headers=headers,
                verify=True
            )
            response.raise_for_status()
            
            countries_data = response.json()
            coordinates_db = {}
            
            for country in countries_data:
                # Support de v3.1 et v2
                codes = country.get("cca2") or country.get("alpha2Code")
                latlng = country.get("latlng")
                
                if codes and latlng and len(latlng) == 2:
                    country_name = country.get("name", {})
                    if isinstance(country_name, dict):
                        country_name = country_name.get("common", "Unknown")
                    
                    capital = country.get("capital")
                    if isinstance(capital, list):
                        capital = capital[0] if capital else "Unknown"
                    
                    coordinates_db[codes] = {
                        "name": country_name,
                        "lat": latlng[0],
                        "lon": latlng[1],
                        "region": country.get("region", "Unknown"),
                        "capital": capital
                    }
            
            if coordinates_db:
                print(f"✅ Successfully loaded {len(coordinates_db)} countries")
                return coordinates_db
        
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Timeout on {url}, trying next...")
            time.sleep(2)
            continue
        
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection error on {url}, trying next...")
            time.sleep(2)
            continue
        
        except requests.exceptions.HTTPError as e:
            print(f"   ⚠️ HTTP Error {e.response.status_code} on {url}, trying next...")
            time.sleep(2)
            continue
        
        except Exception as e:
            print(f"   ⚠️ Error on {url}: {e}, trying next...")
            time.sleep(2)
            continue
    
    print(f"❌ All API endpoints failed")
    return {}


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
    
    Args:
        iso_code: Code ISO 3166-1 alpha-2 du pays (ex: "FR", "DE", "KE")
        num_countries: Nombre de pays à retourner (par défaut 5)
    
    Returns:
        dict avec le pays de référence et ses pays les plus proches
    """
    
    # Récupérer toutes les coordonnées
    all_countries = get_all_countries_coordinates()
    
    if not all_countries:
        print("❌ Unable to fetch country coordinates")
        return None
    
    # Valider et normaliser le code ISO
    iso_code = iso_code.upper()
    if iso_code not in all_countries:
        print(f"❌ ISO code '{iso_code}' not found")
        available_codes = sorted(all_countries.keys())
        print(f"Available ISO codes ({len(available_codes)} total):")
        # Afficher les codes par groupes de 20
        for i in range(0, len(available_codes), 20):
            print(f"   {' '.join(available_codes[i:i+20])}")
        return None
    
    # Récupérer la référence
    reference = all_countries[iso_code]
    ref_lat = reference["lat"]
    ref_lon = reference["lon"]
    
    print(f"\n📍 Reference Country: {iso_code} ({reference['name']})")
    print(f"   Region: {reference['region']}")
    print(f"   Capital: {reference['capital']}")
    print(f"   Coordinates: ({ref_lat}, {ref_lon})\n")
    
    # Calculer les distances
    distances = []
    
    for code, country_data in all_countries.items():
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
            "latitude": country_data["lat"],
            "longitude": country_data["lon"],
            "region": country_data["region"],
            "capital": country_data["capital"]
        })
    
    # Trier par distance et récupérer les N plus proches
    distances.sort(key=lambda x: x["distance_km"])
    
    result = {
        "reference_iso_code": iso_code,
        "reference_country_name": reference["name"],
        "reference_region": reference["region"],
        "reference_capital": reference["capital"],
        "reference_coordinates": {
            "latitude": ref_lat,
            "longitude": ref_lon
        },
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
    ref_region = result["reference_region"]
    
    print("\n" + "="*100)
    print(f"🌍 5 NEAREST COUNTRIES TO {ref_code} ({ref_name})")
    print(f"   Region: {ref_region}")
    print("="*100 + "\n")
    
    print(f"{'Rank':<6} {'ISO':<8} {'Country Name':<25} {'Region':<20} {'Distance (km)':>15} {'Capital':<20}")
    print("-"*100)
    
    for i, country in enumerate(result["nearest_countries"], 1):
        code = country["iso_code"]
        name = country["country_name"]
        region = country["region"]
        distance = country["distance_km"]
        capital = country["capital"]
        
        print(f"{i:<6} {code:<8} {name:<25} {region:<20} {distance:>15,.2f} {capital:<20}")
    
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
    print("\n" + "="*100)
    print("TEST 1: NEAREST COUNTRIES TO FRANCE (FR)")
    print("="*100)
    
    result_fr = find_nearest_countries_by_iso("FR", num_countries=5)
    display_nearest_countries(result_fr)
    
    # Test 2: Kenya (ISO 3166-1 alpha-2: KE)
    print("\n" + "="*100)
    print("TEST 2: NEAREST COUNTRIES TO KENYA (KE)")
    print("="*100)
    
    result_ke = find_nearest_countries_by_iso("KE", num_countries=5)
    display_nearest_countries(result_ke)
    
    # Test 3: Japon (ISO 3166-1 alpha-2: JP)
    print("\n" + "="*100)
    print("TEST 3: NEAREST COUNTRIES TO JAPAN (JP)")
    print("="*100)
    
    result_jp = find_nearest_countries_by_iso("JP", num_countries=5)
    display_nearest_countries(result_jp)
    
    # Test 4: Exporter en JSON
    if result_fr:
        export_to_json(result_fr, "nearest_to_france.json")
        export_to_json(result_ke, "nearest_to_kenya.json")
    
    # Test 5: Tous les pays les plus proches
    print("\n" + "="*100)
    print("TEST 5: ALL NEARBY COUNTRIES FOR MULTIPLE COUNTRIES")
    print("="*100)
    
    for iso_code in ["US", "JP", "BR", "ZA", "GB", "DE"]:
        result = find_nearest_countries_by_iso(iso_code, num_countries=3)
        display_nearest_countries(result)
    
    # Test 6: Code ISO invalide
    print("\n" + "="*100)
    print("TEST 6: TEST WITH INVALID ISO CODE")
    print("="*100)
    
    result_invalid = find_nearest_countries_by_iso("XX", num_countries=5)
import requests
from typing import Dict, Optional
import time

GDP_INDICATOR = "NY.GDP.MKTP.CD"

def get_country_gdp_2024(country_code: str) -> Optional[Dict]:
    """Retrieve ISO code and 2024 GDP for a single country."""
    country_code = country_code.upper()
    
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{GDP_INDICATOR}"
    params = {
        "format": "json",
        "date": "2024",
        "per_page": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if len(data) > 1 and data[1]:
            record = data[1][0]
            value = record.get('value')
            
            if value is None:
                print(f"❌ No data for {country_code} in 2024")
                return None
                
            result = {
                "country_code": country_code,
                "gdp_2024": float(value)
            }
            print(f"  ✓ GDP found: {result['gdp_2024']}")
            return result
            
        print(f"❌ No data found.")
        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_all_countries_gdp_2024() -> Optional[Dict[str, Dict]]:
    """Retrieve ISO code and 2024 GDP for ALL countries."""
    all_countries_data = {}
    
    try:
        # Fetch list of sovereign countries
        countries_resp = requests.get(
            "http://api.worldbank.org/v2/country", 
            params={"format": "json", "per_page": 400},
            timeout=10
        )
        valid_countries = {}
        if len(countries_resp.json()) > 1:
            for c in countries_resp.json()[1]:
                if c['capitalCity']: 
                    valid_countries[c['id']] = c['name']
        
        print(f"   ✓ {len(valid_countries)} sovereign countries identified.")

        # Fetch GDP for all countries
        url = f"http://api.worldbank.org/v2/country/all/indicator/{GDP_INDICATOR}"
        params = {
            "format": "json",
            "date": "2024",
            "per_page": 10000
        }
        
        start_time = time.time()
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        duration = time.time() - start_time
        
        count = 0
        if len(data) > 1 and data[1]:
            for record in data[1]:
                iso_code = record['countryiso3code']
                value = record['value']
                
                if iso_code in valid_countries and value is not None:
                    all_countries_data[iso_code] = {
                        "country_code": iso_code,
                        "gdp_2024": float(value)
                    }
                    count += 1
        
        print(f"\n✅ COMPLETED: {count} countries processed successfully.")
        return all_countries_data

    except Exception as e:
        print(f"❌ Critical error: {e}")
        return None


def find_similar_gdp_countries(country_code: str, num_countries: int = 5) -> Optional[Dict]:
    """Find N countries with GDP closest to the reference country."""
    country_code = country_code.upper()
    
    # Get reference country GDP
    reference_country = get_country_gdp_2024(country_code)
    
    if not reference_country:
        print(f"❌ Unable to find GDP for {country_code}")
        return None
    
    reference_gdp = reference_country["gdp_2024"]
    
    # Get all countries GDP
    all_countries = get_all_countries_gdp_2024()
    
    if not all_countries:
        print("❌ Unable to retrieve GDP data for all countries")
        return None
    
    # Calculate GDP difference for each country
    countries_with_diff = []
    
    for iso_code, country_data in all_countries.items():
        if iso_code == country_code:
            continue
        
        gdp_diff = abs(country_data["gdp_2024"] - reference_gdp)
        
        countries_with_diff.append({
            "country_code": iso_code,
            "gdp_2024": country_data["gdp_2024"],
            "gdp_difference": gdp_diff
        })
    
    # Sort by GDP difference (ascending) and take top N
    countries_with_diff.sort(key=lambda x: x["gdp_difference"])
    similar_countries = countries_with_diff[:num_countries]
    
    result = {
        "reference": {
            "country_code": reference_country["country_code"],
            "gdp_2024": reference_country["gdp_2024"]
        },
        "similar_countries": [
            {
                "country_code": c["country_code"],
                "gdp_2024": c["gdp_2024"]
            }
            for c in similar_countries
        ]
    }
    
    return result


if __name__ == "__main__":

    print("="*80)
    print("TEST 1: GDP OF A SINGLE COUNTRY (FRANCE)")
    print("="*80)
    fr_data = get_country_gdp_2024("FR")
    print(f"France data: {fr_data}\n")
    
    print("="*80)
    print("TEST 2: ALL COUNTRIES")
    print("="*80)
    all_gdp = get_all_countries_gdp_2024()
    print(all_gdp)
    
    print("\n" + "="*80)
    print("TEST 3: COUNTRIES WITH GDP SIMILAR TO FRANCE")
    print("="*80)
    similar_fr = find_similar_gdp_countries("FR", num_countries=5)
    print(similar_fr)


import requests
import os
import json


def get_data_from_country(country_code, year=2024):
    """Use of internet society API to get data for a specific country."""

    api_key = os.getenv("INTERNET_SOCIETY_API_KEY")
    if not api_key:
        raise ValueError("INTERNET_SOCIETY_API_KEY not found in environment variables")
    
    base_url = "https://pulse-api.internetsociety.org/resilience"
    endpoint = f"{base_url}?country={country_code}&year={year}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"     
    }

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Data received for {country_code}")
        return data
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error {e.response.status_code}")
        print(f"   Message: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None


def get_data_from_year(year):
    """Use of internet society API to get data for a specific year."""

    api_key = os.getenv("INTERNET_SOCIETY_API_KEY")
    if not api_key:
        raise ValueError("INTERNET_SOCIETY_API_KEY not found in environment variables")
    
    base_url = "https://pulse-api.internetsociety.org/resilience"
    endpoint = f"{base_url}?year={year}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"     
    }

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Data received for year {year}")
        return data
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error {e.response.status_code}")
        print(f"   Message: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None


# Mapping of paths to actual structures in the API
INDICATOR_MAPPING = {
    "./security/enabling_technologies/ipv6_adoption": {
        "pillar": "security",
        "dimension": "enabling_technologies",
        "indicator": "ipv6"
    },
    "./security/enabling_technologies/https_adoption": {
        "pillar": "security",
        "dimension": "enabling_technologies",
        "indicator": "https"
    },
    "./security/dns_security/dnssec_adoption": {
        "pillar": "security",
        "dimension": "dns_ecosystem",
        "indicator": "dnssec"
    },
    "./security/dns_security/dnssec_validation": {
        "pillar": "security",
        "dimension": "dns_ecosystem",
        "indicator": "dnssec_validation"
    },
    "./security/routing_hygiene": {
        "pillar": "security",
        "dimension": "routing_hygiene",
        "indicator": None  # Entire dimension
    },
    "./security/routing_hygiene/upstream_connections": {
        "pillar": "security",
        "dimension": "routing_hygiene",
        "indicator": "upstream_redundancy"
    },
    "./security/security_threat/secure_internet_servers": {
        "pillar": "security",
        "dimension": "security_threat",
        "indicator": "secure_internet_servers"
    },
    "./security/security_threat/ddos_protection": {
        "pillar": "security",
        "dimension": "security_threat",
        "indicator": "ddos_potential"
    },
    "./security/security_threat/cybersecurity_index_score": {
        "pillar": "security",
        "dimension": "security_threat",
        "indicator": "global_cybersecurity_index"
    },
    "./performance/fixed_networks/vitesse_upload": {
        "pillar": "performance",
        "dimension": "fixed_networks",
        "indicator": "upload"
    },
    "./performance/fixed_networks/responsiveness": {
        "pillar": "performance",
        "dimension": "fixed_networks",
        "indicator": "latency"
    },
    "./performance/fixed_networks/vitesses_download": {
        "pillar": "performance",
        "dimension": "fixed_networks",
        "indicator": "download"
    },
    "./performance/fixed_networks/consistency": {
        "pillar": "performance",
        "dimension": "fixed_networks",
        "indicator": "jitter"
    },
    "./performance/mobile_networks/upload_download_speeds": {
        "pillar": "performance",
        "dimension": "mobile_networks",
        "indicator": None  # Entire dimension
    },
    "./performance/mobile_networks/responsiveness": {
        "pillar": "performance",
        "dimension": "mobile_networks",
        "indicator": "latency"
    },
    "./performance/mobile_networks/consistency": {
        "pillar": "performance",
        "dimension": "mobile_networks",
        "indicator": "jitter"
    },
    "./market_readiness/traffic_localization/egov_index_score": {
        "pillar": "market_readiness",
        "dimension": "traffic_localization",
        "indicator": "egdi"
    },
    "./market_readiness/traffic_localization/domain_count": {
        "pillar": "market_readiness",
        "dimension": "traffic_localization",
        "indicator": "domain_count"
    },
    "./market_readiness/traffic_localization/peering_efficiency": {
        "pillar": "market_readiness",
        "dimension": "traffic_localization",
        "indicator": "peering_efficiency"
    },
    "./market_readiness/market_structure/market_competition": {
        "pillar": "market_readiness",
        "dimension": "market_structure",
        "indicator": "as_hegemony"
    },
    "./market_readiness/market_structure/affordability": {
        "pillar": "market_readiness",
        "dimension": "market_structure",
        "indicator": "affordability"
    },
    "./market_readiness/market_structure/upstream_provider_diversity": {
        "pillar": "market_readiness",
        "dimension": "market_structure",
        "indicator": "market_concentration"
    },
    "./infrastructure/mobile_connectivity/network_coverage": {
        "pillar": "infrastructure",
        "dimension": "mobile_connectivity",
        "indicator": "network_coverage"
    },
    "./infrastructure/mobile_connectivity/spectrum_allocation": {
        "pillar": "infrastructure",
        "dimension": "mobile_connectivity",
        "indicator": "spectrum_allocation"
    },
    "./infrastructure/enabling_infrastructure/data_center_coverage": {
        "pillar": "infrastructure",
        "dimension": "enabling_infrastructure",
        "indicator": "datacenters"
    },
    "./infrastructure/enabling_infrastructure/ixp_coverage": {
        "pillar": "infrastructure",
        "dimension": "enabling_infrastructure",
        "indicator": "number_of_ixps"
    },
}


def extract_indicator_by_path(data, indicator_path):
    """
    Extract data from a specific indicator based on its path.
    Returns the country and the average of the quarters.
    
    Args:
        data: JSON data from the API
        indicator_path: The path of the indicator (ex: "./security/enabling_technologies/ipv6_adoption")
    
    Returns:
        dict with the country and the annual average of the indicator
    """
    
    if indicator_path not in INDICATOR_MAPPING:
        print(f"❌ Path not recognized: {indicator_path}")
        print(f"Available paths:")
        for path in sorted(INDICATOR_MAPPING.keys()):
            print(f"  - {path}")
        return None
    
    mapping = INDICATOR_MAPPING[indicator_path]
    pillar = mapping["pillar"]
    dimension = mapping["dimension"]
    indicator = mapping["indicator"]
    
    values = []
    country = None
    year = None
    
    for quarter_data in data.get("data", []):
        country = quarter_data.get("country")
        year = quarter_data.get("year")
        
        try:
            if indicator is None:
                # If no specific indicator, return the entire dimension
                dimension_data = quarter_data["pillars"][pillar]["dimensions"][dimension]
                value = dimension_data.get("value")
            else:
                # Retrieve the specific indicator
                value = quarter_data["pillars"][pillar]["dimensions"][dimension]["indicators"][indicator]["value"]
            
            if value is not None:
                values.append(value)
        
        except KeyError as e:
            print(f"❌ Invalid path for {indicator_path}")
            print(f"   Error: {e}")
            return None
    
    # Calculate the average
    if values:
        average = sum(values) / len(values)
    else:
        average = None
    
    result = {
        "country": country,
        "year": year,
        "indicator": indicator_path,
        "average": average
    }
    
    return result


def extract_all_countries_by_indicator(year, indicator_path):
    """
    Extract data from a specific indicator for ALL countries in a year.
    Returns a list of all countries with the average of the quarters.
    
    Args:
        year: The year (ex: 2024)
        indicator_path: The path of the indicator (ex: "./security/enabling_technologies/ipv6_adoption")
    
    Returns:
        list with all countries and their annual average for the indicator
    """
    
    # Validate the indicator path
    if indicator_path not in INDICATOR_MAPPING:
        print(f"❌ Path not recognized: {indicator_path}")
        print(f"Available paths:")
        for path in sorted(INDICATOR_MAPPING.keys()):
            print(f"  - {path}")
        return None
    
    # Retrieve data for the year
    data = get_data_from_year(year)
    
    if not data or not data.get("data"):
        print(f"❌ No data available for year {year}")
        return None
    
    mapping = INDICATOR_MAPPING[indicator_path]
    pillar = mapping["pillar"]
    dimension = mapping["dimension"]
    indicator = mapping["indicator"]
    
    # Dictionary to group countries and their values
    countries_data = {}
    
    for quarter_data in data.get("data", []):
        country = quarter_data.get("country")
        
        # Initialize the country if it doesn't exist
        if country not in countries_data:
            countries_data[country] = {
                "country": country,
                "year": quarter_data.get("year"),
                "values": []
            }
        
        try:
            if indicator is None:
                # If no specific indicator, return the entire dimension
                dimension_data = quarter_data["pillars"][pillar]["dimensions"][dimension]
                value = dimension_data.get("value")
            else:
                # Retrieve the specific indicator
                value = quarter_data["pillars"][pillar]["dimensions"][dimension]["indicators"][indicator]["value"]
            
            if value is not None:
                countries_data[country]["values"].append(value)
        
        except KeyError as e:
            print(f"❌ Invalid path for {indicator_path}")
            print(f"   Error: {e}")
            return None
    
    # Build the result with averages
    results = []
    
    for country, data_country in countries_data.items():
        if data_country["values"]:
            average = sum(data_country["values"]) / len(data_country["values"])
        else:
            average = None
        
        results.append({
            "country": country,
            "average": average
        })
    
    # Sort by country
    results.sort(key=lambda x: x["country"])
    
    return results


def display_countries_indicator_results(results):
    """Display the results of an indicator for all countries in a readable manner."""
    
    if not results:
        print("❌ No results to display")
        return
    
    print(f"{'Country':<10} {'Average (%)':>15} {'Normalized Score':>20}")
    print("-" * 80)
    
    for result in results:
        country = result["country"]
        average = result["average"]
        
        if average is not None:
            avg_percent = average * 100
            print(f"{country:<10} {avg_percent:>14.2f}% {average:>20.4f}")
        else:
            print(f"{country:<10} {'N/A':>15} {'N/A':>20}")
    
    print()
    
    # Global statistics
    averages = [r["average"] for r in results if r["average"] is not None]
    if averages:
        global_avg = sum(averages) / len(averages)
        max_country = max(results, key=lambda x: x["average"] if x["average"] else 0)
        min_country = min(results, key=lambda x: x["average"] if x["average"] else float('inf'))
        
        print(f"📈 GLOBAL STATISTICS:")
        print(f"   Global average: {global_avg*100:.2f}%")
        print(f"   Best country: {max_country['country']} ({max_country['average']*100:.2f}%)")
        print(f"   Worst country: {min_country['country']} ({min_country['average']*100:.2f}%)")
        print(f"   Number of countries: {len(results)}")


def find_similar_countries(country_code, indicator_path, year=2024):
    """
    Find 5 countries with a score similar to the given country for a specific indicator.
    
    Args:
        country_code: Country code (ex: "FR")
        indicator_path: The path of the indicator (ex: "./security/enabling_technologies/ipv6_adoption")
        year: The year (default 2024)
    
    Returns:
        dict with the reference country and its 5 similar countries
    """
    
    # Validate the indicator path
    if indicator_path not in INDICATOR_MAPPING:
        print(f"❌ Path not recognized: {indicator_path}")
        return None
    
    # 1. Retrieve the index of the reference country
    print(f"📍 Retrieving data for {country_code}...")
    data_country = get_data_from_country(country_code, year)
    
    if not data_country:
        print(f"❌ Unable to retrieve data for {country_code}")
        return None
    
    reference_result = extract_indicator_by_path(data_country, indicator_path)
    
    if not reference_result or reference_result["average"] is None:
        print(f"❌ Unable to extract indicator for {country_code}")
        return None
    
    reference_score = reference_result["average"]
    
    print(f"✅ Reference score for {country_code}: {reference_score:.4f} ({reference_score*100:.2f}%)")
    
    # 2. Retrieve all countries for this indicator
    print(f"📍 Retrieving data for ALL countries...")
    all_countries = extract_all_countries_by_indicator(year, indicator_path)
    
    if not all_countries:
        print(f"❌ Unable to retrieve data for all countries")
        return None
    
    # 3. Calculate the distance of each country from the reference
    countries_with_distance = []
    
    for country_data in all_countries:
        country = country_data["country"]
        average = country_data["average"]
        
        # Exclude the reference country itself
        if country == country_code or average is None:
            continue
        
        # Absolute distance
        distance = abs(average - reference_score)
        
        countries_with_distance.append({
            "country": country,
            "average": average,
            "distance": distance,
            "difference": average - reference_score  # Positive if better, negative if worse
        })
    
    # 4. Sort by distance (the 5 closest)
    countries_with_distance.sort(key=lambda x: x["distance"])
    similar_countries = countries_with_distance[:5]
    
    # 5. Build the result
    result = {
        "reference_country": country_code,
        "reference_score": reference_score,
        "indicator": indicator_path,
        "year": year,
        "similar_countries": similar_countries
    }
    
    return result


def display_similar_countries(result):
    """Display similar countries in a readable manner."""
    
    if not result:
        print("❌ No results to display")
        return
    
    ref_country = result["reference_country"]
    ref_score = result["reference_score"]
    indicator = result["indicator"]
    year = result["year"]
    
    print(f"\n{'='*80}")
    print(f"🔍 COUNTRIES SIMILAR TO {ref_country}")
    print(f"{'='*80}")
    print(f"Indicator: {indicator}")
    print(f"Year: {year}")
    print(f"Reference score ({ref_country}): {ref_score:.4f} ({ref_score*100:.2f}%)")
    print(f"{'='*80}\n")
    
    print(f"{'Rank':<6} {'Country':<10} {'Score':>15} {'Difference':>15} {'Gap':>15}")
    print("-" * 80)
    
    for i, country_data in enumerate(result["similar_countries"], 1):
        country = country_data["country"]
        average = country_data["average"]
        difference = country_data["difference"]
        distance = country_data["distance"]
        
        # Symbol to indicate if better or worse
        symbol = "🔼" if difference > 0 else "🔽"
        
        avg_percent = average * 100
        diff_percent = difference * 100
        dist_percent = distance * 100
        
        print(f"{i:<6} {country:<10} {avg_percent:>14.2f}% {symbol} {diff_percent:>13.2f}% {dist_percent:>14.2f}%")
    
    print()
    print(f"📊 SUMMARY:")
    print(f"   Country with best score: {result['similar_countries'][0]['country']} "
          f"({result['similar_countries'][0]['average']*100:.2f}%)")
    print(f"   Country with closest score: {result['similar_countries'][0]['country']} "
          f"(gap of {result['similar_countries'][0]['distance']*100:.2f}%)")


if __name__ == "__main__":
    # Find similar countries
    print("\n" + "="*80)
    print("3️⃣ FIND SIMILAR COUNTRIES")
    print("="*80)
    
    similar = find_similar_countries("FR", "./security/enabling_technologies/ipv6_adoption", 2024)
    
    if similar:
        display_similar_countries(similar)
        
        # Also display in JSON format
        print("\n" + "="*80)
        print("JSON FORMAT")
        print("="*80)
        print(json.dumps(similar, indent=2))
import time
from pathlib import Path
from typing import Dict, List

import pandas as pd
import plotly.express as px
import requests

# Data configuration
WORLD_BANK_INDICATOR = "SP.POP.TOTL"  # Population, total (UN/World Bank)
WORLD_BANK_API = "https://api.worldbank.org/v2/country/{code}/indicator/{indicator}"
MADDISON_DATASET_URL = "https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx"

# List of countries to query (you can expand this list)
# Using a mix of full names and ISO codes
COUNTRIES = [
    "United States",
    "China",
    "India",
    "Indonesia",
    "Pakistan",
    "Brazil",
    "Nigeria",
    "Bangladesh",
    "Russia",
    "Mexico",
    "Japan",
    "Ethiopia",
    "Philippines",
    "Egypt",
    "Vietnam",
    "DR Congo",
    "Turkey",
    "Iran",
    "Germany",
    "Thailand",
    "United Kingdom",
    "France",
    "Italy",
    "Tanzania",
    "South Africa",
    "Myanmar",
    "Kenya",
    "South Korea",
    "Colombia",
    "Spain",
    "Argentina",
    "Algeria",
    "Sudan",
    "Uganda",
    "Ukraine",
    "Iraq",
    "Afghanistan",
    "Poland",
    "Canada",
    "Morocco",
    "Saudi Arabia",
    "Uzbekistan",
    "Peru",
    "Angola",
    "Malaysia",
    "Mozambique",
    "Ghana",
    "Yemen",
    "Nepal",
    "Venezuela",
    "Madagascar",
    "Australia",
    "North Korea",
    "Cameroon",
    "Niger",
    "Taiwan",
    "Mali",
    "Burkina Faso",
    "Syria",
    "Sri Lanka",
    "Malawi",
    "Zambia",
    "Romania",
    "Chile",
    "Kazakhstan",
    "Netherlands",
    "Guatemala",
    "Ecuador",
    "Cambodia",
    "Senegal",
    "Chad",
    "Somalia",
    "Zimbabwe",
    "Guinea",
    "Rwanda",
    "Benin",
    "Tunisia",
    "Bolivia",
    "Belgium",
    "Haiti",
    "Cuba",
    "South Sudan",
    "Dominican Republic",
    "Czech Republic",
    "Greece",
    "Jordan",
    "Portugal",
    "Azerbaijan",
    "Sweden",
    "Honduras",
    "United Arab Emirates",
    "Hungary",
    "Tajikistan",
    "Belarus",
    "Austria",
    "Papua New Guinea",
    "Serbia",
    "Israel",
    "Switzerland",
    "Togo",
    "Sierra Leone",
    "Hong Kong",
    "Laos",
    "Paraguay",
    "Bulgaria",
    "Libya",
    "Lebanon",
    "Nicaragua",
    "Kyrgyzstan",
    "El Salvador",
    "Turkmenistan",
    "Singapore",
    "Denmark",
    "Finland",
    "Congo",
    "Slovakia",
    "Norway",
    "Oman",
    "Palestine",
    "Costa Rica",
    "Liberia",
    "Ireland",
    "Central African Republic",
    "New Zealand",
    "Mauritania",
    "Panama",
    "Kuwait",
    "Croatia",
    "Moldova",
    "Georgia",
    "Eritrea",
    "Uruguay",
    "Bosnia and Herzegovina",
    "Mongolia",
    "Armenia",
    "Jamaica",
    "Qatar",
    "Albania",
    "Puerto Rico",
    "Lithuania",
    "Namibia",
    "Gambia",
    "Botswana",
    "Gabon",
    "Lesotho",
    "North Macedonia",
    "Slovenia",
    "Guinea-Bissau",
    "Latvia",
    "Bahrain",
    "Equatorial Guinea",
    "Trinidad and Tobago",
    "Estonia",
    "Timor-Leste",
    "Mauritius",
    "Cyprus",
    "Eswatini",
    "Djibouti",
    "Fiji",
    "Reunion",
    "Comoros",
    "Guyana",
    "Bhutan",
    "Solomon Islands",
    "Macao",
    "Montenegro",
    "Luxembourg",
    "Suriname",
    "Cabo Verde",
    "Maldives",
    "Malta",
    "Brunei",
    "Belize",
    "Bahamas",
    "Iceland",
    "Vanuatu",
    "Barbados",
    "Sao Tome & Principe",
    "Samoa",
    "Saint Lucia",
    "Kiribati",
    "Micronesia",
    "Grenada",
    "Saint Vincent & the Grenadines",
    "Tonga",
    "Seychelles",
    "Antigua and Barbuda",
    "Andorra",
    "Dominica",
    "Saint Kitts & Nevis",
    "Liechtenstein",
    "Monaco",
    "San Marino",
    "Palau",
    "Nauru",
    "Tuvalu",
    "Vatican City",
]


def get_country_iso3_mapping() -> Dict[str, str]:
    """
    Create a mapping of country names to ISO3 codes.
    This is a simplified version - you may need to expand this.
    """
    mapping = {
        "United States": "USA",
        "China": "CHN",
        "India": "IND",
        "Indonesia": "IDN",
        "Pakistan": "PAK",
        "Brazil": "BRA",
        "Nigeria": "NGA",
        "Bangladesh": "BGD",
        "Russia": "RUS",
        "Mexico": "MEX",
        "Japan": "JPN",
        "Ethiopia": "ETH",
        "Philippines": "PHL",
        "Egypt": "EGY",
        "Vietnam": "VNM",
        "DR Congo": "COD",
        "Turkey": "TUR",
        "Iran": "IRN",
        "Germany": "DEU",
        "Thailand": "THA",
        "United Kingdom": "GBR",
        "France": "FRA",
        "Italy": "ITA",
        "South Africa": "ZAF",
        "South Korea": "KOR",
        "Spain": "ESP",
        "Argentina": "ARG",
        "Ukraine": "UKR",
        "Poland": "POL",
        "Canada": "CAN",
        "Australia": "AUS",
        "Romania": "ROU",
        "Chile": "CHL",
        "Netherlands": "NLD",
        "Ecuador": "ECU",
        "Guatemala": "GTM",
        "Belgium": "BEL",
        "Czech Republic": "CZE",
        "Greece": "GRC",
        "Portugal": "PRT",
        "Sweden": "SWE",
        "Hungary": "HUN",
        "Belarus": "BLR",
        "Austria": "AUT",
        "Serbia": "SRB",
        "Switzerland": "CHE",
        "Bulgaria": "BGR",
        "Denmark": "DNK",
        "Finland": "FIN",
        "Slovakia": "SVK",
        "Norway": "NOR",
        "Ireland": "IRL",
        "Croatia": "HRV",
        "Moldova": "MDA",
        "Georgia": "GEO",
        "Uruguay": "URY",
        "Bosnia and Herzegovina": "BIH",
        "Albania": "ALB",
        "Lithuania": "LTU",
        "Slovenia": "SVN",
        "Latvia": "LVA",
        "Estonia": "EST",
        "North Macedonia": "MKD",
        "Luxembourg": "LUX",
        "Montenegro": "MNE",
        "Malta": "MLT",
        "Iceland": "ISL",
        "Andorra": "AND",
        "Liechtenstein": "LIE",
        "Monaco": "MCO",
        "San Marino": "SMR",
        "Vatican City": "VAT",
        "Puerto Rico": "PRI",
        "Hong Kong": "HKG",
        "Singapore": "SGP",
    }
    return mapping


def fetch_world_bank_population(country_code: str) -> List[Dict]:
    """Fetch World Bank population series for a country.

    Uses the standard population indicator (UN/World Bank) and requests all
    available years in one go.
    """

    url = WORLD_BANK_API.format(code=country_code.lower(), indicator=WORLD_BANK_INDICATOR)
    params = {"format": "json", "per_page": 20000, "date": "1800:2050"}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"  ❌ World Bank error {response.status_code} for {country_code}")
        return []

    payload = response.json()
    if len(payload) < 2 or not isinstance(payload[1], list):
        print(f"  ⚠️  No World Bank data for {country_code}")
        return []

    wb_records = []
    for entry in payload[1]:
        if entry.get("value") is None:
            continue
        wb_records.append({"year": int(entry["date"]), "population": int(entry["value"])})

    return wb_records


def load_maddison_dataset() -> pd.DataFrame:
    """Download the Maddison Project population dataset (2020 release)."""

    df = pd.read_excel(MADDISON_DATASET_URL, sheet_name="Full data")
    df = df.rename(columns={"countrycode": "country_code", "year": "year", "pop": "population"})
    return df[["country_code", "year", "population", "country"]]


def fetch_maddison_population(country_code: str, maddison_df: pd.DataFrame) -> List[Dict]:
    """Return Maddison Project records for a single ISO3 code."""

    country_data = maddison_df[maddison_df["country_code"] == country_code]
    if country_data.empty:
        return []

    return country_data[["year", "population"]].to_dict(orient="records")


def merge_population_series(wb_records: List[Dict], maddison_records: List[Dict]) -> pd.DataFrame:
    """Combine World Bank and Maddison series, favoring World Bank where overlapping."""

    wb_df = pd.DataFrame(wb_records)
    maddison_df = pd.DataFrame(maddison_records)

    if wb_df.empty and maddison_df.empty:
        return pd.DataFrame(columns=["year", "population"])

    if wb_df.empty:
        return maddison_df

    if maddison_df.empty:
        return wb_df

    wb_df = wb_df.set_index("year")
    maddison_df = maddison_df.set_index("year")

    merged = maddison_df.combine_first(wb_df)
    merged.update(wb_df)
    return merged.reset_index()


def fetch_all_country_data(countries: list[str]) -> pd.DataFrame:
    """Fetch population data for all countries and compile into a dataframe."""

    all_data = []
    iso3_mapping = get_country_iso3_mapping()
    maddison_df = load_maddison_dataset()

    print(f"Fetching data for {len(countries)} countries...")
    print("Using World Bank (UN) for modern data and Maddison Project for long-run history.\n")

    for i, country in enumerate(countries, 1):
        print(f"[{i}/{len(countries)}] Fetching {country}...", end=" ")

        iso3 = iso3_mapping.get(country, country[:3].upper())
        wb_records = fetch_world_bank_population(iso3)
        maddison_records = fetch_maddison_population(iso3, maddison_df)
        merged = merge_population_series(wb_records, maddison_records)

        if not merged.empty:
            for _, row in merged.iterrows():
                all_data.append(
                    {
                        "country": country,
                        "country_code": iso3,
                        "year": int(row["year"]),
                        "population": float(row["population"]),
                    }
                )
            print("✓")
        else:
            print("⚠️  no data")

        time.sleep(0.05)

    df = pd.DataFrame(all_data)
    print(f"\n✅ Successfully fetched data for {df['country'].nunique()} countries")
    return df


def calculate_population_fractions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate each country's current population as a fraction of its historical peak.

    Args:
        df: DataFrame with historical population data

    Returns:
        DataFrame with population fractions calculated
    """
    # Get the most recent year's data for current population
    latest_year = df['year'].max()
    current_pop = df[df['year'] == latest_year][['country', 'country_code', 'population']].copy()
    current_pop.columns = ['country', 'country_code', 'current_population']

    # Get historical peak for each country
    peak_pop = df.groupby('country_code').agg({'population': 'max', 'country': 'first'}).reset_index()
    peak_pop.columns = ['country_code', 'peak_population', 'country']

    # Merge current and peak populations
    result = current_pop.merge(peak_pop, on=['country', 'country_code'])

    # Calculate fraction
    result['population_fraction'] = result['current_population'] / result['peak_population']

    # Round for display
    result['fraction_display'] = result['population_fraction'].round(3)

    return result


def create_map(df_fractions: pd.DataFrame) -> object:
    """
    Create an interactive choropleth map using Plotly.

    Args:
        df_fractions: DataFrame with population fractions

    Returns:
        Plotly figure object
    """
    fig = px.choropleth(
        df_fractions,
        locations='country_code',
        color='population_fraction',
        hover_name='country',
        hover_data={
            'country_code': False,
            'population_fraction': ':.3f',
            'current_population': ':,.0f',
            'peak_population': ':,.0f',
        },
        color_continuous_scale='RdYlGn',
        range_color=[0.5, 1.0],
        labels={
            'population_fraction': 'Population Fraction',
            'current_population': 'Current Population',
            'peak_population': 'Peak Population',
        },
        title="Countries' Current Population as Fraction of Historical Peak (World Bank + Maddison)",
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'), height=600, width=1200
    )

    return fig


def main():
    """Main execution function."""

    # Fetch data from World Bank and Maddison Project
    print("=" * 70)
    print("FETCHING POPULATION DATA FROM WORLD BANK + MADDISON")
    print("=" * 70)
    df = fetch_all_country_data(COUNTRIES)

    if df.empty:
        print("\n❌ No data was fetched. Please check your internet connection.")
        return

    # Calculate fractions
    print("\n" + "=" * 70)
    print("CALCULATING POPULATION FRACTIONS")
    print("=" * 70)
    df_fractions = calculate_population_fractions(df)

    # Display interesting results
    print("\n=== COUNTRIES AT PEAK POPULATION (fraction ≥ 0.99) ===")
    at_peak = df_fractions[df_fractions['population_fraction'] >= 0.99].sort_values(
        'current_population', ascending=False
    )
    if not at_peak.empty:
        print(at_peak[['country', 'fraction_display', 'current_population']].head(15).to_string(index=False))

    print("\n=== COUNTRIES BELOW PEAK POPULATION (fraction < 0.90) ===")
    below_peak = df_fractions[df_fractions['population_fraction'] < 0.90].sort_values('population_fraction')
    if not below_peak.empty:
        print(
            below_peak[['country', 'fraction_display', 'current_population', 'peak_population']]
            .head(15)
            .to_string(index=False)
        )

    # Create and save the map
    print("\n" + "=" * 70)
    print("CREATING MAP VISUALIZATION")
    print("=" * 70)
    fig = create_map(df_fractions)

    # Save outputs to the script's directory
    script_dir = Path(__file__).parent
    output_html = script_dir / 'population_fraction_map.html'
    output_csv = script_dir / 'population_fractions.csv'

    fig.write_html(output_html)
    print(f"✅ Map saved to: {output_html}")

    df_fractions.sort_values('population_fraction').to_csv(output_csv, index=False)
    print(f"✅ Data saved to: {output_csv}")

    print("\n" + "=" * 70)
    print("✨ COMPLETE! Open the HTML file in your browser to view the map.")
    print("=" * 70)

    return fig


if __name__ == "__main__":
    main()

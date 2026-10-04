"""Check the public population data sources used by the map (no API key needed)."""
from population_fraction_map_api import fetch_world_bank_population, load_maddison_dataset


def main():
    world_bank = fetch_world_bank_population("USA")
    maddison = load_maddison_dataset()
    if not world_bank or maddison.empty:
        raise SystemExit("Population source check failed")
    print(f"World Bank: {len(world_bank)} USA records; Maddison: {len(maddison)} records")


if __name__ == "__main__":
    main()

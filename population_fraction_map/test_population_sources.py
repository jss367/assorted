import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location("population_sources", Path(__file__).with_name("population_fraction_map_api.py"))
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


def test_all_configured_countries_have_explicit_iso3_codes():
    mapping = source.get_country_iso3_mapping()
    assert set(source.COUNTRIES) <= mapping.keys()
    assert mapping["United Arab Emirates"] == "ARE"
    assert mapping["Taiwan"] == "TWN"
    assert mapping["DR Congo"] == "COD"
    assert mapping["Congo"] == "COG"


def test_unknown_country_fails_before_fetching_data(monkeypatch):
    download = Mock()
    monkeypatch.setattr(source, "load_maddison_dataset", download)
    with pytest.raises(ValueError, match="No ISO3 mapping for: Unknown"):
        source.fetch_all_country_data(["Unknown"])
    download.assert_not_called()


def test_fetch_uses_explicit_codes_and_retains_maddison_only_country(monkeypatch):
    monkeypatch.setattr(source, "load_maddison_dataset", lambda: pd.DataFrame([
        {"country_code": "TWN", "year": 1950, "population": 100}]))
    wb = Mock(side_effect=lambda code: [{"year": 2020, "population": 200}] if code == "ARE" else [])
    monkeypatch.setattr(source, "fetch_world_bank_population", wb)
    monkeypatch.setattr(source.time, "sleep", lambda _: None)
    result = source.fetch_all_country_data(["United Arab Emirates", "Taiwan"])
    assert [call.args[0] for call in wb.call_args_list] == ["ARE", "TWN"]
    assert set(result["country"]) == {"United Arab Emirates", "Taiwan"}


def test_no_source_records_returns_empty_dataframe_with_schema(monkeypatch):
    monkeypatch.setattr(source, "load_maddison_dataset", lambda: pd.DataFrame(columns=["country_code", "year", "population"]))
    monkeypatch.setattr(source, "fetch_world_bank_population", lambda _: [])
    monkeypatch.setattr(source.time, "sleep", lambda _: None)
    result = source.fetch_all_country_data(["Taiwan"])
    assert result.empty
    assert list(result.columns) == ["country", "country_code", "year", "population"]

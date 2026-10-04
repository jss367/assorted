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


def test_maddison_thousands_are_normalized_before_merging(monkeypatch):
    raw = pd.DataFrame([{"countrycode": "ARE", "year": 1950, "pop": 2500, "country": "United Arab Emirates"}])
    monkeypatch.setattr(source.pd, "read_excel", lambda *a, **k: raw.copy())
    maddison = source.load_maddison_dataset()
    merged = source.merge_population_series([{ "year": 2020, "population": 2000000}],
        source.fetch_maddison_population("ARE", maddison))
    merged["country"], merged["country_code"] = "United Arab Emirates", "ARE"
    result = source.calculate_population_fractions(merged)
    assert result.iloc[0]["peak_population"] == 2500000
    assert result.iloc[0]["population_fraction"] == 0.8


def test_latest_year_is_selected_separately_for_each_country():
    rows = pd.DataFrame([
        {"country": "Taiwan", "country_code": "TWN", "year": 1950, "population": 200},
        {"country": "Taiwan", "country_code": "TWN", "year": 2018, "population": 100},
        {"country": "United Arab Emirates", "country_code": "ARE", "year": 2025, "population": 300},
    ])
    result = source.calculate_population_fractions(rows).set_index("country_code")
    assert set(result.index) == {"TWN", "ARE"}
    assert result.loc["TWN", "population_fraction"] == 0.5


@pytest.mark.parametrize("error", [source.requests.ConnectionError("offline"), ValueError("invalid JSON")])
def test_world_bank_failures_leave_the_fallback_available(monkeypatch, error):
    response = Mock(status_code=200)
    if isinstance(error, source.requests.RequestException):
        get = Mock(side_effect=error)
    else:
        response.json.side_effect = error
        get = Mock(return_value=response)
    monkeypatch.setattr(source.requests, "get", get)
    assert source.fetch_world_bank_population("TWN") == []


def test_missing_maddison_population_does_not_hide_latest_valid_value():
    data = pd.DataFrame([
        {"country_code": "TWN", "year": 2017, "population": 100},
        {"country_code": "TWN", "year": 2018, "population": float("nan")},
    ])
    records = source.fetch_maddison_population("TWN", data)
    assert records == [{"year": 2017, "population": 100.}]
    data["country"] = "Taiwan"
    result = source.calculate_population_fractions(data)
    assert result.iloc[0]["current_population"] == 100


def test_map_export_includes_original_source_bibliography(tmp_path):
    fig = Mock()
    fig.to_html.return_value = '<html><body>map</body></html>'
    path = tmp_path / 'map.html'
    source.write_map_html(fig, path)
    html = path.read_text()
    assert 'Bolt, Jutta and Jan Luiten van Zanden (2020)' in html
    assert 'Prados de la Escosura' in html
    assert 'Original sources' in html


@pytest.mark.parametrize("error", [OSError("unavailable"), ValueError("unreadable workbook"), source.BadZipFile("bad workbook")])
def test_maddison_failure_preserves_world_bank_only_generation(monkeypatch, error):
    monkeypatch.setattr(source.pd, "read_excel", Mock(side_effect=error))
    monkeypatch.setattr(source, "fetch_world_bank_population", lambda _: [{"year": 2025, "population": 100}])
    monkeypatch.setattr(source.time, "sleep", lambda _: None)
    result = source.fetch_all_country_data(["United States"])
    assert list(result["population"]) == [100.]


def test_ireland_excludes_pre_partition_island_population():
    data = pd.DataFrame([
        {"country_code": "IRL", "year": 1920, "population": 4361000},
        {"country_code": "IRL", "year": 1921, "population": 3096000},
    ])
    assert source.fetch_maddison_population("IRL", data) == [{"year": 1921, "population": 3096000}]

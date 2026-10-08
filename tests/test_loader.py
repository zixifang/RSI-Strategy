import pandas as pd

from src.data.loader import REQUIRED_COLUMNS, load_data, load_sample


def test_sample_schema():
    frame = load_sample(n_days=30)
    assert list(frame.columns) == ["date", "ticker", "open", "high", "low", "close", "volume"]
    assert frame["date"].is_monotonic_increasing
    assert frame["ticker"].eq("SAMPLE").all()


def test_load_data_roundtrip(tmp_path):
    sample = load_sample("AAPL", n_days=20)
    csv = sample.drop(columns=["ticker"])
    csv.to_csv(tmp_path / "AAPL.csv", index=False)
    loaded = load_data(["aapl"], data_dir=tmp_path)
    assert set(REQUIRED_COLUMNS).issubset(loaded.columns)
    assert loaded["ticker"].eq("AAPL").all()
    pd.testing.assert_series_equal(
        loaded["close"].reset_index(drop=True),
        sample["close"].reset_index(drop=True),
        check_names=False,
    )

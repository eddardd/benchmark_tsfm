"""Tests for the GIFT-Eval leaderboard-combos loading (offline)."""

import importlib.util
import pathlib

# Load by path: ``import datasets.gifteval`` would clash with the HF lib.
_spec = importlib.util.spec_from_file_location(
    "gifteval_module",
    pathlib.Path(__file__).parents[2] / "datasets" / "gifteval.py",
)
gifteval = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gifteval)


def test_parse_leaderboard_csv(tmp_path):
    csv_path = tmp_path / "leaderboard_combos.csv"
    csv_path.write_text(
        "dataset_name,term\n"
        "m4_weekly/W,short\n"
        "electricity/15T,short\n"
        "electricity/15T,medium\n"
        "electricity/15T,long\n"
    )
    table = gifteval._parse_leaderboard_csv(csv_path)
    assert table == {
        "m4_weekly/W": ("short",),
        "electricity/15T": ("short", "medium", "long"),
    }


def test_non_canonical_combo_skips(monkeypatch):
    monkeypatch.setattr(
        gifteval, "_leaderboard_cache", {"m4_weekly/W": ("short",)}
    )
    ds = gifteval.Dataset.__new__(gifteval.Dataset)
    ds.dataset_name, ds.term = "m4_weekly/W", "long"
    data = ds.get_data()
    assert set(data) == {"_skip_reason"}
    assert "does not define term 'long'" in data["_skip_reason"]


def test_hf_arrow_directory():
    assert gifteval._hf_arrow_directory("m4_weekly/W") == "m4_weekly"
    assert gifteval._hf_arrow_directory("loop_seattle/H") == "LOOP_SEATTLE/H"
    assert (
        gifteval._hf_arrow_directory("car_parts/M") == "car_parts_with_missing"
    )

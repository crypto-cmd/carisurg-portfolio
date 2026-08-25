import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
firmware_dir = repo_root / 'firmware'
sys.path.insert(0, str(firmware_dir))

import predict


def test_goldilocks_zone_accepts_valid_feature_pair():
    assert predict.is_goldilocks_zone(220.0, 0.7) is True
    assert predict.is_goldilocks_zone(240.0, 0.55) is True
    assert predict.is_goldilocks_zone(180.0, 0.7) is False
    assert predict.is_goldilocks_zone(280.0, 0.7) is False


def test_goldilocks_zone_bounds_are_defined_for_plotting():
    bounds = predict.get_goldilocks_zone_bounds()
    assert bounds == {'contrast_min': 0.5, 'contrast_max': 1.0, 'imax_min': 200.0, 'imax_max': 265.0}

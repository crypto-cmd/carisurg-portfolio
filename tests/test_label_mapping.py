import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
firmware_dir = repo_root / 'firmware'
sys.path.insert(0, str(firmware_dir))

import expt7
import expt8
import numpy as np


def test_label_mapping_for_arduino_button_states():
    assert expt7.resolve_label_info(0) == (0, 'No Button')
    assert expt7.resolve_label_info(1) == (1, 'Ecoflex')
    assert expt7.resolve_label_info(2) == (2, 'Cellophane_A')
    assert expt7.resolve_label_info(3) == (3, 'Cellophane_B')
    assert expt7.resolve_label_info(4) == (4, 'Record_Point')


def test_record_point_only_triggers_once_for_repeated_4s():
    assert expt7.should_record_point(4, 0, False) is True
    assert expt7.should_record_point(4, 4, True) is True
    assert expt7.should_record_point(4, 4, False) is False
    assert expt7.should_record_point(0, 4, True) is False


def test_average_multiple_record_point_windows():
    windows = [
        {0: np.array([1.0, 3.0]), 1: np.array([10.0, 12.0]), 2: np.array([20.0, 24.0]), 3: np.array([30.0, 34.0]), 4: np.array([40.0, 44.0]), 5: np.array([50.0, 54.0])},
        {0: np.array([3.0, 5.0]), 1: np.array([14.0, 16.0]), 2: np.array([28.0, 32.0]), 3: np.array([36.0, 38.0]), 4: np.array([48.0, 52.0]), 5: np.array([58.0, 62.0])},
    ]

    avg = expt8.average_trigger_windows(windows)

    np.testing.assert_allclose(avg[0], np.array([2.0, 4.0]))
    np.testing.assert_allclose(avg[1], np.array([12.0, 14.0]))
    np.testing.assert_allclose(avg[2], np.array([24.0, 28.0]))
    np.testing.assert_allclose(avg[3], np.array([33.0, 36.0]))
    np.testing.assert_allclose(avg[4], np.array([44.0, 48.0]))
    np.testing.assert_allclose(avg[5], np.array([54.0, 58.0]))

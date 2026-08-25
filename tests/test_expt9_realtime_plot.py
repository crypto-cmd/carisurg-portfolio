import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
firmware_dir = repo_root / 'firmware'
sys.path.insert(0, str(firmware_dir))

import expt9
import numpy as np


class Expt9RealtimeTests(unittest.TestCase):
    def test_average_trigger_windows(self):
        windows = [
            {0: np.array([1.0, 3.0]), 1: np.array([10.0, 12.0]), 2: np.array([20.0, 24.0]), 3: np.array([30.0, 34.0]), 4: np.array([40.0, 44.0]), 5: np.array([50.0, 54.0])},
            {0: np.array([3.0, 5.0]), 1: np.array([14.0, 16.0]), 2: np.array([28.0, 32.0]), 3: np.array([36.0, 38.0]), 4: np.array([48.0, 52.0]), 5: np.array([58.0, 62.0])},
        ]

        avg = expt9.average_trigger_windows(windows)

        np.testing.assert_allclose(avg[0], np.array([2.0, 4.0]))
        np.testing.assert_allclose(avg[1], np.array([12.0, 14.0]))
        np.testing.assert_allclose(avg[2], np.array([24.0, 28.0]))
        np.testing.assert_allclose(avg[3], np.array([33.0, 36.0]))
        np.testing.assert_allclose(avg[4], np.array([44.0, 48.0]))
        np.testing.assert_allclose(avg[5], np.array([54.0, 58.0]))

    def test_record_trigger_only_emits_on_transition(self):
        self.assertTrue(expt9.should_record_point(4, 0))
        self.assertFalse(expt9.should_record_point(4, 4))
        self.assertFalse(expt9.should_record_point(0, 4))


if __name__ == '__main__':
    unittest.main()
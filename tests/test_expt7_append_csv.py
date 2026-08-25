import csv
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
firmware_dir = repo_root / 'firmware'
sys.path.insert(0, str(firmware_dir))

import expt7


def test_ensure_csv_headers_and_run_id_continue(tmp_path):
    csv_path = tmp_path / 'waveform_row_data.csv'

    expt7.ensure_csv_headers(csv_path)
    assert csv_path.exists()

    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(expt7.CSV_HEADER)
        writer.writerow([1, 1, 'Ecoflex', '[]', '[]', '[]', '[]', '[]', '[]'])

    assert expt7.resolve_next_run_id(csv_path) == 2

    row = [2, 2, 'Cellophane', '[]', '[]', '[]', '[]', '[]', '[]']
    expt7.append_waveform_row(csv_path, row)

    with open(csv_path, newline='') as file:
        rows = list(csv.reader(file))

    assert rows[0] == expt7.CSV_HEADER
    assert rows[1] == [1, 1, 'Ecoflex', '[]', '[]', '[]', '[]', '[]', '[]']
    assert rows[2] == [2, 2, 'Cellophane', '[]', '[]', '[]', '[]', '[]', '[]']

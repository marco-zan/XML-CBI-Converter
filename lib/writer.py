
from classes.Entry import Entry
from pathlib import Path
import csv


def export_csv(output_path: Path, sorted_entries: list[Entry]):
    with open(output_path, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        # Headers
        spamwriter.writerow(Entry.to_print_headers())
        
        # Data
        for el in sorted_entries:
            spamwriter.writerow(el.csv_exported())


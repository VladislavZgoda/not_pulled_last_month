from pathlib import Path
from pprint import pprint

import polars as pl


class RidingsFilter:
    def __init__(self, meter_ridings_path: Path, application_nine_path: Path) -> None:
        self.meter_ridings_path = meter_ridings_path
        self.application_nine_path = application_nine_path

    def filter(self) -> None:
        self._filter_application_nine()

    def _filter_application_nine(self) -> pl.Series:
        df = pl.read_excel(self.application_nine_path, read_options={"header_row": 1})
        pprint(df)

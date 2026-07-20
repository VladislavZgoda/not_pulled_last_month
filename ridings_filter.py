from pathlib import Path
from pprint import pprint

import polars as pl


class RidingsFilter:
    def __init__(self, meter_ridings_path: Path, application_nine_path: Path) -> None:
        self.meter_ridings_path = meter_ridings_path
        self.application_nine_path = application_nine_path

    def filter(self) -> None:
        useless_meters = self._filter_application_nine()
        pprint(useless_meters)

    def _filter_application_nine(self) -> pl.Series:
        return (
            pl.read_excel(
                source=self.application_nine_path,
                sheet_name="Быт",
                read_options={"header_row": 1},
            )
            .with_columns(
                pl.coalesce(
                    pl.col("Дата").str.to_datetime("%d.%m.%Y", strict=False),
                    pl.col("Дата").str.to_datetime("%Y-%m-%d", strict=False),
                ).alias("Дата")
            )
            .filter(
                pl.col("Тип ПУ").str.starts_with("NP"),
                pl.col("Дата").dt.day().is_between(21, 25, closed="both"),
            )
            .select(pl.col("Номер_ПУ").cast(pl.Int32))
            .to_series()
        )

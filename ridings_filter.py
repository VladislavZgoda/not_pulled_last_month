from pathlib import Path

import polars as pl


class RidingsFilter:
    def __init__(self, meter_ridings_path: Path, application_nine_path: Path) -> None:
        self.meter_ridings_path = meter_ridings_path
        self.application_nine_path = application_nine_path

    def filter(self) -> pl.DataFrame:
        useless_meters = self._filter_application_nine()
        df_meter_ridings = self._filter_meter_ridings(useless_meters)
        return df_meter_ridings

    def _filter_application_nine(self) -> pl.Series:
        return (
            pl.read_excel(
                source=self.application_nine_path,
                sheet_name="Быт",
                read_options={"header_row": 1},
            )
            .filter(
                pl.col("Тип ПУ").str.starts_with("NP"),
                pl.col("Дата")
                .str.to_datetime("%d.%m.%Y")
                .dt.day()
                .is_between(21, 25, closed="both"),
            )
            .select(pl.col("Номер_ПУ").cast(pl.Int32))
            .to_series()
        )

    def _filter_meter_ridings(self, useless_meters: pl.Series) -> pl.DataFrame:
        return (
            pl.read_excel(
                source=self.meter_ridings_path,
                read_options={"header_row": 1},
            )
            .head(-1)
            .filter(
                ~pl.col("Серийный №").cast(pl.Int32).is_in(useless_meters),
                pl.col("Тип устройства").str.starts_with("NP"),
                pl.col("Код потребителя").str.strip_chars().str.starts_with("230700"),
                pl.col("Наименование точки учета") != "ОДПУ",
            )
        )

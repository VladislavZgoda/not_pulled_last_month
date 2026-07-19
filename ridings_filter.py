from pathlib import Path


class RidingsFilter:
    def __init__(self, meter_ridings_path: Path, application_nine_path: Path) -> None:
        self.meter_ridings_path = meter_ridings_path
        self.application_nine_path = application_nine_path

    def test(self) -> None:
        print(self.meter_ridings_path)
        print(self.application_nine_path)

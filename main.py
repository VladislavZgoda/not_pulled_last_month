from io import BytesIO
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Button, Footer, Header
from textual_fspicker import FileSave

from file_picker import FilePicker, FilePathSelected, FILE_LOCATION
from create_workbook import create_wb
from readings_filter import ReadingsFilter


def main():
    app = NotPulledLastMonthApp()
    app.run()


class NotPulledLastMonthApp(App):
    meter_readings_path: var[Path | None] = var(None)
    application_nine_path: var[Path | None] = var(None)
    xlsx_buffer: var[BytesIO | None] = var(None)

    CSS_PATH = "styles.tcss"
    TITLE = "Поиск не загруженных показаний"
    SUB_TITLE = "Выбираются данные приборов серии NP на основе сравнения Приложения №9 за прошлый месяц и текущей выгрузки."

    BINDINGS = [
        ("d", "toggle_dark", "Включить/выключить темный режим"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield FilePicker(
            "Выберите файл с показаниями",
            "meter_readings",
        )
        yield FilePicker(
            "Выберите приложение №9",
            "application_nine",
        )
        yield Button("Отфильтровать показания", id="filter_readings", disabled=True)
        yield Button("Сохранить файл", id="save_file", disabled=True)

    def on_mount(self) -> None:
        self.screen.styles.border = ("panel", "snow")

    def on_file_path_selected(self, event: FilePathSelected) -> None:
        match event.picker_id:
            case "meter_readings":
                self.meter_readings_path = event.file_path
            case "application_nine":
                self.application_nine_path = event.file_path
            case _:
                return

        self._reset_filtered_result()
        self._check_and_enable_filter_btn()

    @on(Button.Pressed, "#filter_readings")
    @work(thread=True)
    def handle_filter_btn(self) -> None:
        if self.meter_readings_path is None:
            raise ValueError("Требуется объект Path, получен None.")
        if self.application_nine_path is None:
            raise ValueError("Требуется объект Path, получен None.")

        self.call_from_thread(self._on_filter_start)
        df = ReadingsFilter(
            self.meter_readings_path, self.application_nine_path
        ).filter()
        xlsx_buffer = create_wb(df)
        self.call_from_thread(self._on_filter_done, xlsx_buffer)

    @on(Button.Pressed, "#save_file")
    @work
    async def handle_save_btn(self) -> None:
        if self.xlsx_buffer is None:
            raise ValueError("Требуется объект BytesIO, получен None.")
        if save_path := await self.push_screen_wait(FileSave(FILE_LOCATION)):
            with open(save_path.with_suffix(".xlsx"), "wb") as f:
                f.write(self.xlsx_buffer.getvalue())
            self.notify("Файл сохранён.", timeout=10)
            self._reset_state()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

        self.screen.styles.border = (
            ("panel", "snow")
            if self.theme == "textual-dark"
            else ("panel", "darkslategray")
        )

    def _on_filter_start(self) -> None:
        self.query_one("#filter_readings", Button).loading = True

    def _on_filter_done(self, xlsx_buffer: BytesIO) -> None:
        self.notify("Показания отфильтрованы.")
        self.xlsx_buffer = xlsx_buffer
        self.query_one("#filter_readings", Button).loading = False
        save_file_btn = self.query_one("#save_file", Button)
        save_file_btn.disabled = False
        save_file_btn.variant = "success"

    def _reset_filtered_result(self) -> None:
        self.xlsx_buffer = None

        save_file_btn = self.query_one("#save_file", Button)
        save_file_btn.disabled = True
        save_file_btn.variant = "default"

    def _check_and_enable_filter_btn(self) -> None:
        if self.meter_readings_path is None:
            return
        if self.application_nine_path is None:
            return

        filter_ridings_btn = self.query_one("#filter_readings", Button)
        filter_ridings_btn.disabled = False
        filter_ridings_btn.variant = "warning"

    def _reset_state(self) -> None:
        self.meter_readings_path = None
        self.application_nine_path = None
        self.xlsx_buffer = None

        for picker in self.query(FilePicker):
            picker.reset()

        filter_readings_btn = self.query_one("#filter_readings", Button)
        filter_readings_btn.disabled = True
        filter_readings_btn.variant = "default"

        save_file_btn = self.query_one("#save_file", Button)
        save_file_btn.disabled = True
        save_file_btn.variant = "default"


if __name__ == "__main__":
    main()

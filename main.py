import platform
from io import BytesIO
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult, Widget
from textual.message import Message
from textual.reactive import var
from textual.widgets import Button, Footer, Header, Label
from textual_fspicker import FileOpen, FileSave, Filters

from create_workbook import create_wb
from ridings_filter import RidingsFilter


def main():
    app = NotPulledLastMonthApp()
    app.run()


FILE_LOCATION = (
    Path.home() / "Desktop" if platform.system() == "Windows" else Path.home()
)

FILE_FILTER = Filters(("XLSX", lambda p: p.suffix.lower() == ".xlsx"))


class NotPulledLastMonthApp(App):
    meter_ridings_path: var[Path | None] = var(None)
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
        yield MeterRidings()
        yield ApplicationNine()
        yield Button("Отфильтровать показания", id="filter_ridings", disabled=True)
        yield Button("Сохранить файл", id="save_file", disabled=True)
        yield Label(variant="success", id="save_btn_label")

    def on_mount(self) -> None:
        self.screen.styles.border = ("panel", "snow")

    def on_meter_ridings_path_selected(self, event: MeterRidingsPathSelected) -> None:
        self.meter_ridings_path = event.file_path
        self._check_and_enable_filter_btn()

    def on_application_nine_path_selected(
        self, event: ApplicationNinePathSelected
    ) -> None:
        self.application_nine_path = event.file_path
        self._check_and_enable_filter_btn()

    @on(Button.Pressed, "#filter_ridings")
    def handle_filter_btn(self) -> None:
        if self.meter_ridings_path is None:
            raise ValueError("Требуется объект Path, получен None.")
        if self.application_nine_path is None:
            raise ValueError("Требуется объект Path, получен None.")

        df = RidingsFilter(self.meter_ridings_path, self.application_nine_path).filter()
        self.xlsx_buffer = create_wb(df)
        save_file_btn = self.query_one("#save_file", Button)
        save_file_btn.disabled = False
        save_file_btn.variant = "success"

    @on(Button.Pressed, "#save_file")
    @work
    async def handle_save_btn(self) -> None:
        if self.xlsx_buffer is None:
            raise ValueError("Требуется объект BytesIO, получен None.")
        if save_path := await self.push_screen_wait(FileSave(FILE_LOCATION)):
            with open(save_path.with_suffix(".xlsx"), "wb") as f:
                f.write(self.xlsx_buffer.getvalue())
            self.query_one("#save_btn_label", Label).update("Файл сохранён.")

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

        if self.theme == "textual-dark":
            self.screen.styles.border = ("panel", "snow")
        else:
            self.screen.styles.border = ("panel", "darkslategray")

    def _check_and_enable_filter_btn(self) -> None:
        if self.meter_ridings_path is None:
            return
        if self.application_nine_path is None:
            return

        filter_ridings_btn = self.query_one("#filter_ridings", Button)
        filter_ridings_btn.disabled = False
        filter_ridings_btn.variant = "warning"


class MeterRidingsPathSelected(Message):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        super().__init__()


class ApplicationNinePathSelected(Message):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        super().__init__()


class MeterRidings(Widget):
    def compose(self) -> ComposeResult:
        yield Button(
            "Выберите файл с показаниями", variant="primary", id="meter_ridings"
        )
        yield Label(variant="success", id="meter_ridings_label")

    @on(Button.Pressed, "#meter_ridings")
    @work
    async def open_meter_ridings(self) -> None:
        if file_opened := await self.app.push_screen_wait(
            FileOpen(FILE_LOCATION, filters=FILE_FILTER)
        ):
            self.query_one("#meter_ridings_label", Label).update(str(file_opened))
            self.post_message(MeterRidingsPathSelected(file_opened))


class ApplicationNine(Widget):
    def compose(self) -> ComposeResult:
        yield Button("Выберите приложение №9", variant="primary", id="application_nine")
        yield Label(variant="success", id="application_nine_label")

    @on(Button.Pressed, "#application_nine")
    @work
    async def open_application_nine(self) -> None:
        if file_opened := await self.app.push_screen_wait(
            FileOpen(FILE_LOCATION, filters=FILE_FILTER)
        ):
            self.query_one("#application_nine_label", Label).update(str(file_opened))
            self.post_message(ApplicationNinePathSelected(file_opened))


if __name__ == "__main__":
    main()

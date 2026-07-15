from pathlib import Path
import platform

from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Label

from textual_fspicker import FileOpen


def main():
    app = NotPulledLastMonthApp()
    app.run()


class NotPulledLastMonthApp(App):
    def __init__(self) -> None:
        self._meter_ridings_path: Path | None = None
        self._application_nine_path: Path | None = None
        self._file_location = (
            Path.home() / "Desktop" if platform.system() == "Windows" else Path.home()
        )
        super().__init__()

    CSS_PATH = "styles.tcss"
    TITLE = "Поиск не загруженных показаний"
    SUB_TITLE = "Выбираются данные приборов серии NP на основе сравнения Приложения №9 за прошлый месяц и текущей выгрузки."

    BINDINGS = [
        ("d", "toggle_dark", "Включить/выключить темный режим"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Button(
            "Выберите файл с показаниями", variant="primary", id="meter_ridings"
        )
        yield Label(variant="success", id="meter_ridings_label")
        yield Button("Выберите приложение №9", variant="primary", id="application_nine")
        yield Label(variant="success", id="application_nine_label")

    def on_mount(self) -> None:
        self.screen.styles.border = ("panel", "snow")

    @on(Button.Pressed, "#meter_ridings")
    @work
    async def open_meter_ridings(self) -> None:
        if opened := await self.push_screen_wait(FileOpen(self._file_location)):
            self.query_one("#meter_ridings_label", Label).update(str(opened))
            self._meter_ridings_path = opened

    @on(Button.Pressed, "#application_nine")
    @work
    async def open_application_nine(self) -> None:
        if opened := await self.push_screen_wait(FileOpen(self._user_desktop)):
            self.query_one("#application_nine_label", Label).update(str(opened))
            self._application_nine_path = opened

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

        if self.theme == "textual-dark":
            self.screen.styles.border = ("panel", "snow")
        else:
            self.screen.styles.border = ("panel", "darkslategray")


if __name__ == "__main__":
    main()

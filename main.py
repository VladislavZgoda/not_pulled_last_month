from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


def main():
    app = NotPulledLastMonthApp()
    app.run()


class NotPulledLastMonthApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "Поиск не загруженных показаний"
    SUB_TITLE = "Выбираются данные приборов серии NP на основе сравнения Приложения №9 за прошлый месяц и текущей выгрузки."

    BINDINGS = [
        ("d", "toggle_dark", "Включить/выключить темный режим"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.screen.styles.border = ("panel", "snow")

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

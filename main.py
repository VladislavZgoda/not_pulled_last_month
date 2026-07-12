from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


def main():
    app = NotPulledLastMonthApp()
    app.run()


class NotPulledLastMonthApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    main()

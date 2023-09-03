from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.validation import URL
from textual.widgets import Button, Footer, Header, Static, Input, Log, Label, Select
from textual.worker import Worker

from utils.concurrency import send_batch_requests
from constants import HttpMethod, AuthType


class Request(Static):
    nr_request = reactive(1)
    url = reactive(None)
    future_list = reactive(None)
    worker: Worker | None = None
    authentication = reactive(False)

    def watch_nr_request(self, value):
        self.query_one("#nr_request").value = str(value)

    def watch_future_list(self, futures):
        log = self.query_one("#log", Log)
        if futures:
            for f in futures:
                log.write(f"> {f.result().status_code}\n")

    @staticmethod
    def validate_nr_request(count: int) -> int:
        """Validate value."""
        if count <= 0:
            count = 1
        elif count > 10:
            count = 10
        return count

    @on(Input.Changed, "#url_input")
    def url_input(self, event: Input.Changed) -> None:
        if event.validation_result.is_valid:
            self.url = event.value

    @on(Select.Changed, "#auth_type")
    def auth_type_select(self, event: Select.Changed) -> None:
        pass

    @on(Button.Pressed, "#increment_request")
    def increment_requests(self):
        self.nr_request += 1

    @on(Button.Pressed, "#decrement_request")
    def decrement_requests(self):
        self.nr_request -= 1

    async def make_requests(self):
        log = self.query_one("#log", Log)
        try:
            self.future_list = await send_batch_requests(self.nr_request, self.url)
        except ExceptionGroup as exc_group:
            log.write(f"{exc_group.exceptions}")
            for exc in exc_group.exceptions:
                log.write(f"- {exc}\n")
        finally:
            self.remove_class("started")

    @on(Button.Pressed, "#start")
    async def start_requests(self):
        log = self.query_one("#log", Log)
        log.clear()
        self.add_class("started")
        if self.url and self.nr_request:
            self.worker = self.run_worker(self.make_requests(), exclusive=True)

    @on(Button.Pressed, "#stop")
    async def stop_requests(self):
        self.remove_class("started")
        if self.worker:
            self.worker.cancel()
        self.worker = None

    def compose(self) -> ComposeResult:
        yield Label("URL", id="url_label")
        yield Input(
            placeholder="http://httpbin.org", id="url_input", validators=[URL()]
        )
        yield Label("METHOD", id="method_label")
        yield Select(
            options=[(name, name) for name in HttpMethod.__members__],
            id="method_select",
        )
        yield Label("AUTHENTICATION")
        yield Horizontal(
            Select(
                options=[(name, name) for name in AuthType.__members__], id="auth_type"
            ),
            Input(id="auth_value"),
            id="request_headers",
        )
        yield Label("NR.")
        yield Button("+", id="increment_request", variant="success")
        yield Button("-", id="decrement_request", variant="error")
        yield Input(id="nr_request", disabled=True)
        yield Log(id="log")

        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")


class AppDelivery(App):
    """A Textual app to manage requests."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "static/app_delivery.tcss"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Request()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark  # noqa


if __name__ == "__main__":
    app = AppDelivery()
    app.run()

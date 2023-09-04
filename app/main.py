import asyncio

import httpx
from httpx import Response
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.validation import URL
from textual.widgets import Button, Footer, Header, Static, Input, Log, Label, Select
from textual.worker import Worker, WorkerState

from utils.concurrency import send_request
from constants import HttpMethod, AuthType


class Request(Static):
    url = reactive(None)
    http_method = reactive(HttpMethod.GET)
    nr_request = reactive(1)
    authentication_type = reactive(None)
    authentication_payload = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker: Worker | None = None

    # WATCHERS
    def watch_nr_request(self, value):
        self.query_one("#nr_request").value = str(value)

    def watch_future_list(self, futures):
        log = self.query_one("#log", Log)
        if futures:
            for f in futures:
                log.write(f"> {f.result().status_code}\n")

    # URL
    @on(Input.Changed, "#url_input")
    def url_input(self, event: Input.Changed) -> None:
        if event.validation_result.is_valid:
            self.url = event.value

    # AUTHENTICATION
    @on(Select.Changed, "#auth_type")
    def auth_type_select(self, event: Select.Changed) -> None:
        self.authentication_type = event.value

    @on(Input.Changed, "#auth_value")
    def auth_value_input(self, event: Select.Changed) -> None:
        self.authentication_payload = event.value

    # NR. REQUESTS
    @staticmethod
    def validate_nr_request(count: int) -> int:
        """Validate value."""
        if count <= 0:
            count = 1
        return count

    @on(Button.Pressed, "#increment_request")
    def increment_requests(self):
        self.nr_request += 1

    @on(Button.Pressed, "#increment_request_10")
    def increment_requests_by_10(self):
        self.nr_request += 10

    @on(Button.Pressed, "#decrement_request")
    def decrement_requests(self):
        self.nr_request -= 1

    @on(Button.Pressed, "#decrement_request_10")
    def decrement_requests_by_10(self):
        self.nr_request -= 10

    # WORKERS
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state is WorkerState.SUCCESS:
            self.remove_class("started")

    async def make_requests(self):
        log = self.query_one("#log", Log)
        async with httpx.AsyncClient() as client:
            requests = [
                send_request(client, self.url)
                for _ in range(self.nr_request)
            ]
            responses = await asyncio.gather(*requests)
        for res in responses:
            res: Response
            log.write_line(f"> status_code: {res.status_code}, {res.text}")

    def pre_flight_check_validations(self):
        if not self.url:
            return "Invalid or missing url"

    @on(Button.Pressed, "#start")
    async def start_requests(self):
        log = self.query_one("#log", Log)
        log.clear()
        if msg := self.pre_flight_check_validations():
            self.notify(message=msg, severity="error")
            return
        self.add_class("started")
        self.worker = self.run_worker(self.make_requests())

    @on(Button.Pressed, "#stop")
    async def stop_requests(self):
        self.remove_class("started")
        if self.worker:
            self.worker.cancel()
        self.worker = None

    def compose(self) -> ComposeResult:
        yield Label("URL", id="url_label")
        yield Input(
            placeholder="https://httpbin.org", id="url_input", validators=[URL()]
        )
        yield Label("HTTP METHOD", id="http_method_label")
        yield Select(
            value=HttpMethod.GET,
            options=[(name, name) for name in HttpMethod],
            id="http_method_select",
        )
        yield Label("AUTHENTICATION")
        yield Horizontal(
            Select(options=[(name, name) for name in AuthType], id="auth_type"),
            Input(id="auth_value"),
            id="authentication",
        )
        yield Label("NR. REQUESTS", id="nr_requests_label")
        yield Horizontal(

            Button("+1", id="increment_request", variant="success"),
            Button("-1", id="decrement_request", variant="error"),
            Button("+10", id="increment_request_10", variant="success"),
            Button("-10", id="decrement_request_10", variant="error"),
            Input(id="nr_request", disabled=True),
            id="nr_requests_widget"
        )

        yield Log(id="log")

        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")

    def serialize(self):
        return {
            "url": self.url,
            "method": self.http_method,
            "auth_type": self.authentication_type,
            "auth_payload": self.authentication_payload,
            "nr_requests": self.nr_request,
        }


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

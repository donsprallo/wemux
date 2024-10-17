<div align="center">

# Wemux

A message bus for event driven apps.

[![Tests](https://github.com/donsprallo/wemux/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/donsprallo/wemux/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

**Wemux** is a message bus for event driven apps. It is a simple and lightweight
library that allows you to publish and subscribe to events and handle commands.
It is designed to be used in a single process, but can be extended to work
across multiple processes or even machines.

## Installation

```bash
python -m pip install wemux
```

## Usage

```python
import wemux

# Create the message bus instance.
mbus = wemux.create_in_memory_message_bus()


class ExampleEvent(wemux.Event):

    def __init__(self, message: str):
        super().__init__()
        self.message = message


@mbus.subscribe(ExampleEvent)
class ExampleEventHandler(wemux.EventHandler):

    def handle(self, event: ExampleEvent) -> None:
        # Access the event data.
        print(event.message)


# Emit the example event.
event = ExampleEvent("Hello, world!")
mbus.emit(event)
```

It is also possible to emit new events while handle event handlers.

````python
import wemux

# Create the message bus instance.
mbus = wemux.create_in_memory_message_bus()


class AnotherEvent(wemux.Event):

    def __init__(self, message: str):
        super().__init__()
        self.message = message


@mbus.subscribe(AnotherEvent)
class AnotherEventHandler(wemux.EventHandler):

    def handle(self, event: AnotherEvent) -> None:
        # Access the event data.
        print(event.message)
````

Commands can be handled in a similar way. The only difference is that commands
are not emitted, but sent directly to the message bus. This allows you to send
commands to the message bus from anywhere in your code. Commands are designed
to be used for actions that should return a result.

```python
import wemux

# Create the message bus instance.
mbus = wemux.create_in_memory_message_bus()


class ExampleCommand(wemux.Command):

    def __init__(self, message: str):
        super().__init__()
        self.message = message


@mbus.subscribe(ExampleCommand)
class ExampleCommandHandler(wemux.CommandHandler[str]):
    """A command handler for ExampleCommand. The result type is str."""

    def handle(self, command: ExampleCommand) -> str:
        # Push a new event.
        event = ExampleEvent("Another event.")
        self.push(event)
        # Access the command data.
        return command.message


# Send a command.
command = ExampleCommand("Hello, world!")
message = mbus.handle(command)
assert message == "Hello, world!"
```

Handlers can be chained together to create complex workflows. This allows you
to create a pipeline of middlewares that process events and commands in a
specific order.

```python
import wemux
import logging

# Create the message bus instance.
mbus = wemux.create_in_memory_message_bus()

# Create a handler chain with a logger middleware.
handler = ExampleCommandHandler()
logger = logging.getLogger(__name__)
handler.chain(wemux.LoggerMiddleware(logger))

# Register the handler with the message bus.
mbus.subscribe_command(ExampleCommand, handler)
mbus.handle(ExampleCommand("Hello, world!"))
```

Or with a decorator.

```python
import wemux
import logging

logger = logging.getLogger(__name__)
mbus = wemux.create_in_memory_message_bus()


class AnotherMiddleware(wemux.Handler):

    def handle(self, message: wemux.Message) -> wemux.Message:
        print("Another middleware.")
        return self.next(message)

    def error(self, message: wemux.Message, error: Exception) -> None:
        print("Another middleware error.")
        print(error)
        self.next(message, error)


# Create the middleware by chaining multiple middlewares.
middleware = wemux.LoggerMiddleware(logger)
    .chain(AnotherMiddleware())


@mbus.subscribe(ExampleCommand, middleware=middleware)
class ExampleCommandHandler(wemux.CommandHandler[str]):
    ...
```

## Development

Install all dependencies with [pdm](https://pdm-project.org).

```bash
pdm install
```

Run tests with [pytest](https://docs.pytest.org).

```bash
pdm run pytest
```

Run tests with coverage.

```bash
pdm run pytest --cov=wemux
```

Create coverage report. Replace `TYPE` with `term`, `html`, `xml`, `json`.

```bash
pdm run pytest --cov=wemux --cov-report=TYPE
```

Run linter with [ruff](https://docs.astral.sh/ruff).

```bash
pdm run ruff check
```
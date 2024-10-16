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

# Create a message bus.
message_bus = wemux.create_in_memory_message_bus()


class ExampleEvent(wemux.Event):
    """An example event."""
    
    def __init__(self, message: str):
        self.message = message
        
        
@message_bus.register_handler(ExampleEvent)
class ExampleEventHandler(wemux.EventHandler[ExampleEvent]):
    """An event handler for ExampleEvent."""

    def handle(self, event: ExampleEvent) -> None:
        # Access the event data.
        print(event.message)

        
# Emit an event.
event = ExampleEvent("Hello, world!")
message_bus.emit(event)
```

It is also possible to emit new events while handle event handlers.

````python
import wemux

class AnotherEvent(wemux.Event):
    """Another example event."""
    
    def __init__(self, message: str):
        self.message = message

        
@message_bus.register_handler(AnotherEvent)
class AnotherEventHandler(wemux.EventHandler[AnotherEvent]):
    """An event handler for AnotherEvent."""

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


class ExampleCommand(wemux.Command):
    """An example command."""
    
    def __init__(self, message: str):
        self.message = message

        
@message_bus.register_handler(ExampleCommand)
class ExampleCommandHandler(wemux.CommandHandler[ExampleCommand, str]):
    """A command handler for ExampleCommand. The result type is str."""
    
    def handle(self, command: ExampleCommand) -> str:
        # Push a new event.
        event = ExampleEvent("Another event.")
        self.push(event)
        # Access the command data.
        return command.message


# Send a command.
command = ExampleCommand("Hello, world!")
message = message_bus.handle(command)
assert message == "Hello, world!"
```

Handlers can be chained together to create complex workflows. This allows you
to create a pipeline of middlewares that process events and commands in a
specific order.

```python
import wemux
import logging

# Create a handler chain with a logger middleware.
handler = ExampleCommandHandler()
logger = logging.getLogger(__name__)
handler.chain(wemux.LoggerMiddleware(logger))

# Register the handler with the message bus.
message_bus.register_command_handler(handler)
message_bus.handle(ExampleCommand("Hello, world!"))
```

Or with a decorator.

```python
import wemux
import logging


class AnotherMiddleware(wemux.Middleware):
    """Another middleware that override the handle and the error method."""

    def handle(self, message: wemux.Message) -> wemux.Message:
        print("Another middleware.")
        return self.next(message)
                
    def error(self, message: wemux.Message, error: Exception) -> None:
        print("Another middleware error.")
        print(error)
        self.next(message, error)


# Create the middleware.
logger = logging.getLogger(__name__)
middleware = wemux.LoggerMiddleware(logger) \
    .chain(AnotherMiddleware())


@message_bus.register_handler(ExampleCommand, middleware=middleware)
class ExampleCommandHandler(wemux.CommandHandler[ExampleCommand, str]):
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
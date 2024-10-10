```mermaid
---
title: wemux class diagram
---

classDiagram
    namespace errors {
        class Exception {
            <<class>>
        }

        class MessageBusError {
            <<class>>
        }
        class HandlerNotFoundError {
            <<class>>
        }
    }
    Exception <|-- MessageBusError
    MessageBusError <|-- HandlerNotFoundError
```

```mermaid
classDiagram
    namespace message {
        class Event {
            <<class>>
        }

        class Command {
            <<class>>
        }

        class Message {
            <<type>>
        }

        class Result {
            <<class>>
        }
    }
    Event <-- Message
    Command <-- Message
```

```mermaid
classDiagram
    namespace handler {
        class CommandHandler {
            <<class>>
            +handle(command: Command): Any
        }

        class EventListener {
            <<class>>
            +handle(event: Event): void
        }
    }
```

```mermaid
classDiagram
    namespace middleware {
        class Middleware {
            <<class>>
            +before(message: Message): void
            +after(message: Message): void
            +error(message: Message, error: Exception): void
        }

        class LoggerMiddleware {
            <<class>>
            +LoggerMiddleware(logger: Logger|None)
        }
    }
    Middleware <|-- LoggerMiddleware
```

```mermaid
classDiagram
    namespace dispatcher {
        class CommandDispatcher {
            <<abstract>>
            +dispatch(handlers: CommandHandlerMap, command: Command): void*
        }

        class EventDispatcher {
            <<abstract>>
            +dispatch(listeners: list[EventListener], event: Event): void*
        }

        class EventCollector {
            <<abstract>>
            +collect(): void*
        }

        class LocalEventCollector {
            <<class>>
        }

        class LocalCommandDispatcher {
            <<class>>
            +LocalCommandDispatcher(middlewares: list[Middleware])
            +dispatch(handlers: CommandHandlerMap, command: Command): void
        }

        class LocalEventDispatcher {
            <<class>>
            +LocalEventDispatcher(middlewares: list[Middleware])
            +dispatch(listeners: list[EventListener], event: Event
            ): void
        }
    }
    CommandDispatcher <|-- LocalCommandDispatcher
    EventDispatcher <|-- LocalEventDispatcher
    EventCollector <|-- LocalEventCollector
```

```mermaid
classDiagram
    namespace messagebus {
        class MessageBus {
            <<class>>
            +MessageBus(
            command_dispatcher: CommandDispatcher,
            event_dispatcher: EventDispatcher,
            event_collector: EventCollector
            )
            +add_listener(key: Type[Event], listener: EventListener): void
            +add_handler(key: Type[Command], handler: CommandHandler): void
            +emit(event: Event): void
            +handle(command: Command): Any
            #emit_events(): void
        }
    }
```
# Design by Contract Framework

This project provides a Python framework for **Design by Contract** programming, enabling iterative development with formal specifications and runtime verification.

## Overview

Design by Contract is a software development methodology where you specify the behavior of software components using precise assertions. This framework allows you to write code iteratively while maintaining formal specifications that can be verified at runtime.

This project follows a **systematic development plan** with runtime verification as the foundation, and plans to add **static checking features** at a later stage to provide compile-time contract verification.

## Development Workflow

The framework supports an iterative development style:

1. **Write a function stub** - Start with the basic structure of what you want to implement
2. **Add specifications** - Describe what the function should do using decorators
3. **Add logical conditions** - Define preconditions, postconditions, and invariants
4. **Test and verify** - Run the code with various inputs to verify the contracts

## Decorators

### Specification Decorators

- **`@specification`** - Provides a verbal written specification of what the function is supposed to do
- **`@pre_description`** - Verbal description of the preconditions
- **`@post_description`** - Verbal description of the postconditions
- **`@invariant_description`** - Verbal description of the invariants
- **`@raises`** - Specifies the list of possible exceptions the function can raise

### Logical Condition Decorators

- **`@precondition`** - Defines conditions that must be true when the function is called
- **`@postcondition`** - Defines conditions that must be true when the function returns
- **`@invariant`** - Defines conditions that must remain true throughout execution

The logical decorators use **total Python fragments** (side-effect free expressions) that can be evaluated safely. All logical conditions must be **fully mypy typed** with no untyped variables. This will enable us to use static checking techniques at a later stage.

## Runtime Verification

When enabled with appropriate flags, the framework:

- Executes precondition checks before function calls
- Executes postcondition checks after function returns
- Monitors invariants during execution
- Drives automated testing by running code with various data conditions
- Verifies that all contracts are satisfied

## Features

- **Side-effect free expressions** - Logical conditions use pure Python fragments
- **Runtime contract checking** - Verify contracts during execution
- **Automated testing support** - Generate test cases based on contracts
- **Iterative development** - Start with stubs and gradually add implementation
- **Formal verification** - Mathematical precision in software specifications

## Roadmap

The project is being developed through a systematic plan:

1. **Phase 1 (Current)** - Runtime verification and contract checking
2. **Phase 2 (Planned)** - Static analysis and compile-time contract verification
3. **Phase 3 (Future)** - Advanced formal verification tools and IDE integration

The current implementation focuses on runtime verification to establish the foundation, with static checking features planned for future releases.

## Usage

```python
from contracts import (
    specification, pre_description, post_description, raises,
    precondition, postcondition, enable_contracts, PreconditionViolation
)

def div_precondition(a: int, b: int) -> bool:
    return b != 0

def div_postcondition(result: int, a: int, b: int) -> bool:
    return result == a // b

@specification("Divides two integers and returns the result")
@pre_description("Both arguments must be integers, divisor cannot be zero")
@post_description("Returns the integer division of a by b")
@raises([PreconditionViolation, ZeroDivisionError])
@precondition(div_precondition)
@postcondition(div_postcondition)
def div(a: int, b: int) -> int:
    return a // b

# Enable contract checking
enable_contracts()

# Use the function - contracts will be verified at runtime
result = div(10, 2)  # Works fine
result = div(10, 0)  # Raises PreconditionViolation
```

This framework helps ensure code correctness through formal specifications while maintaining the flexibility of iterative development.

# Design by Contract Framework

This project provides a Python framework for **Design by Contract** programming, enabling iterative development with formal specifications and runtime verification.

## Overview

Design by Contract is a software development methodology where you specify the behavior of software components using precise assertions. This framework allows you to write code iteratively while maintaining formal specifications that can be verified at runtime.

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

### Logical Condition Decorators

- **`@precondition`** - Defines conditions that must be true when the function is called
- **`@postcondition`** - Defines conditions that must be true when the function returns
- **`@invariant`** - Defines conditions that must remain true throughout execution

The logical decorators use **total Python fragments** (side-effect free expressions) that can be evaluated safely.

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

## Usage

```python
@specification("Divides two integers and returns the result")
@pre_description("Both arguments must be integers, divisor cannot be zero")
@post_description("Returns the integer division of a by b")
@precondition(lambda a, b: isinstance(a, int) and isinstance(b, int) and b != 0)
@postcondition(lambda result, a, b: result == a // b)
def div(a: int, b: int) -> int:
    # Implementation here
    pass
```

This framework helps ensure code correctness through formal specifications while maintaining the flexibility of iterative development.

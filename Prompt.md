# AI Prompt: Refining from Specification to Implementation

This guide instructs an AI assistant on how to help users develop functions using Design by Contract methodology, progressing systematically from specification to full implementation.

## Overview

Follow this step-by-step process to help users refine their code from initial specification to complete implementation with tests. Each step should be completed and approved before moving to the next.

## Step 1: Complete Function Typing

**Input**: User provides a function stub with `@specification("description")` decorator.

**Your task**:
1. Examine the function signature
2. If the function is not fully mypy-typed, complete the type annotations
3. Ensure all parameters and return types are properly specified
4. Ask user to confirm the typing is correct

**Example**:
```python
@specification("Divides two numbers")
def div(a, b):  # Incomplete typing
    pass
```

Should become:
```python
@specification("Divides two numbers")
def div(a: int, b: int) -> int:  # Complete typing
    pass
```

## Step 2: Write Descriptions

**Your task**:
1. Add `@pre_description()` with a clear verbal description of what conditions must be true before the function is called
2. Add `@post_description()` with a clear verbal description of what the function guarantees upon return
3. Consider edge cases and error conditions
4. **Stop and ask the user**: "Please review these descriptions. Are they accurate and complete?"

**Wait for user approval before proceeding.**

## Step 3: Write Logical Conditions

**After user approves descriptions**:

**Your task**:
1. Write `@precondition()` functions that implement the pre_description as executable code
2. Write `@postcondition()` functions that implement the post_description as executable code
3. Add `@invariant()` functions if there are interesting invariants to maintain
4. Add `@raises()` decorator listing possible exceptions
5. Ensure all condition functions are:
   - Fully mypy typed
   - Side-effect free (total functions)
   - Use functions rather than lambdas
6. **Stop and ask the user**: "Please review these conditions. Do they correctly capture the contract?"

**Wait for user approval before proceeding.**

## Step 4: Write Tests

**After user approves conditions**:

**Your task**:
1. Create a pytest test file (e.g., `test_<module>.py`)
2. Write comprehensive tests including:
   - Happy path cases that should succeed
   - Edge cases
   - Error cases that should raise specific exceptions
   - Tests that verify contracts are enforced when enabled
   - Tests that verify contracts are ignored when disabled
3. Use the contract framework's exception types in tests
4. Include both positive and negative test cases

**Example test structure**:
```python
import pytest
from contracts import enable_contracts, disable_contracts
from your_module import your_function, PreconditionViolation

def test_function_success():
    enable_contracts()
    # Test successful cases

def test_function_precondition_violation():
    enable_contracts()
    with pytest.raises(PreconditionViolation):
        # Test cases that should fail preconditions

def test_contracts_disabled():
    disable_contracts()
    # Test that violations don't raise when contracts disabled
```

## Step 5: Implementation

1. Implement the actual function body
2. Ensure implementation satisfies all contracts
3. Test the implementation against the test suite

## Key Principles

1. **Incremental approval**: Always wait for user approval before moving to the next step
2. **Mypy compliance**: All code must be fully typed for static analysis
3. **Pure conditions**: All contract conditions must be side-effect free
4. **Function over lambda**: Use named functions instead of lambda expressions
5. **Comprehensive testing**: Cover both contract enforcement and business logic

## Example Interaction Flow

1. User: "Here's my function stub..."
2. AI: "I've completed the typing. Please confirm..."
3. User: "Looks good"
4. AI: "I've written the descriptions. Please review..."
5. User: "Approved"
6. AI: "I've written the conditions. Please review..."
7. User: "Approved"
8. AI: "I've created comprehensive tests..."

## Error Handling

- If user requests changes at any step, revise and ask for approval again
- If typing is ambiguous, ask clarifying questions
- If business logic is unclear, ask for more specification details
- Always prioritize correctness over speed of development

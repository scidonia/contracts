"""
Example usage of the Design by Contract framework.
"""

from contracts import (
    specification,
    pre_description,
    post_description,
    precondition,
    postcondition,
    enable_contracts,
    ImplementThis,
)


def div_precondition(a: int, b: int) -> bool:
    """Precondition: divisor cannot be zero."""
    return b != 0


def div_postcondition(result: int, a: int, b: int) -> bool:
    """Postcondition: result should be the integer division of a by b."""
    return result == a // b


@specification("Divides two integers and returns the result")
@pre_description("Both arguments must be integers, divisor cannot be zero")
@post_description("Returns the integer division of a by b")
@precondition(div_precondition)
@postcondition(div_postcondition)
def div(a: int, b: int) -> int:
    """Divide two integers."""
    return a // b


def sqrt_precondition(x: float) -> bool:
    """Precondition: input must be non-negative."""
    return x >= 0


def sqrt_postcondition(result: float, x: float) -> bool:
    """Postcondition: result squared should equal input (within tolerance)."""
    return abs(result * result - x) < 1e-10


@specification("Computes the square root of a non-negative number")
@pre_description("Input must be non-negative")
@post_description("Result squared equals the input")
@precondition(sqrt_precondition)
@postcondition(sqrt_postcondition)
def sqrt(x: float) -> float:
    """Compute square root - not yet implemented."""
    raise ImplementThis("Square root function not yet implemented")


def main() -> None:
    """Main function to demonstrate the contract system."""
    # Enable contract checking
    enable_contracts()
    
    # Test the div function
    print("Testing div function with contracts enabled...")
    
    try:
        result = div(10, 2)
        print(f"div(10, 2) = {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        result = div(10, 0)  # This should raise a PreconditionViolation
        print(f"div(10, 0) = {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test the unimplemented sqrt function
    print("\nTesting unimplemented sqrt function...")
    try:
        result = sqrt(4.0)
        print(f"sqrt(4.0) = {result}")
    except ImplementThis as e:
        print(f"Implementation needed: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

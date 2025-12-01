"""
Design by Contract framework for Python.

This package provides decorators and utilities for implementing
Design by Contract programming with runtime verification.
"""

import functools
import os
from typing import Any, Callable, TypeVar, List, Type

F = TypeVar('F', bound=Callable[..., Any])

# Global flag to enable/disable contract checking
_CONTRACT_CHECKING_ENABLED = os.environ.get('CONTRACTS_ENABLED', '').lower() in ('1', 'true', 'yes')


class ContractViolation(Exception):
    """Base exception for contract violations."""
    pass


class PreconditionViolation(ContractViolation):
    """Exception raised when a precondition is violated."""
    pass


class PostconditionViolation(ContractViolation):
    """Exception raised when a postcondition is violated."""
    pass


class InvariantViolation(ContractViolation):
    """Exception raised when an invariant is violated."""
    pass


class ImplementThis(Exception):
    """
    Exception that acts as a logical hole for unimplemented functionality.
    
    This exception should be raised in function stubs to indicate that
    the implementation is not yet complete. It serves as a placeholder
    that can be detected by static analysis tools and testing frameworks.
    """
    pass


class DontImplementThis(Exception):
    """
    Exception that indicates code should be ignored during implementation.
    
    This exception should be raised in function stubs to indicate that
    the code is intentionally left unimplemented and should be skipped
    by AI assistants and automated tools.
    """
    pass


def enable_contracts() -> None:
    """Enable contract checking at runtime."""
    global _CONTRACT_CHECKING_ENABLED
    _CONTRACT_CHECKING_ENABLED = True


def disable_contracts() -> None:
    """Disable contract checking at runtime."""
    global _CONTRACT_CHECKING_ENABLED
    _CONTRACT_CHECKING_ENABLED = False


def contracts_enabled() -> bool:
    """Check if contract checking is currently enabled."""
    return _CONTRACT_CHECKING_ENABLED


def specification(description: str) -> Callable[[F], F]:
    """
    Decorator to add a specification description to a function.
    
    Args:
        description: A verbal description of what the function does
        
    Returns:
        The decorated function with specification metadata
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_contract_metadata'):
            func._contract_metadata = {}
        func._contract_metadata['specification'] = description
        return func
    return decorator


def pre_description(description: str) -> Callable[[F], F]:
    """
    Decorator to add a precondition description to a function.
    
    Args:
        description: A verbal description of the preconditions
        
    Returns:
        The decorated function with precondition description metadata
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_contract_metadata'):
            func._contract_metadata = {}
        func._contract_metadata['pre_description'] = description
        return func
    return decorator


def post_description(description: str) -> Callable[[F], F]:
    """
    Decorator to add a postcondition description to a function.
    
    Args:
        description: A verbal description of the postconditions
        
    Returns:
        The decorated function with postcondition description metadata
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_contract_metadata'):
            func._contract_metadata = {}
        func._contract_metadata['post_description'] = description
        return func
    return decorator


def invariant_description(description: str) -> Callable[[F], F]:
    """
    Decorator to add an invariant description to a function.
    
    Args:
        description: A verbal description of the invariants
        
    Returns:
        The decorated function with invariant description metadata
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_contract_metadata'):
            func._contract_metadata = {}
        func._contract_metadata['invariant_description'] = description
        return func
    return decorator


def raises(exceptions: List[Type[Exception]]) -> Callable[[F], F]:
    """
    Decorator to specify the list of possible exceptions a function can raise.
    
    Args:
        exceptions: A list of exception types that the function may raise
        
    Returns:
        The decorated function with exception specification metadata
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_contract_metadata'):
            func._contract_metadata = {}
        func._contract_metadata['raises'] = exceptions
        return func
    return decorator


def precondition(condition: Callable[..., bool]) -> Callable[[F], F]:
    """
    Decorator to add a precondition to a function.
    
    Args:
        condition: A function that takes the same arguments as the decorated
                  function and returns True if the precondition is satisfied
                  
    Returns:
        The decorated function with precondition checking
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_contract_metadata'):
            func._contract_metadata = {}
        
        if 'preconditions' not in func._contract_metadata:
            func._contract_metadata['preconditions'] = []
        func._contract_metadata['preconditions'].append(condition)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if _CONTRACT_CHECKING_ENABLED:
                # Check precondition
                try:
                    if not condition(*args, **kwargs):
                        raise PreconditionViolation(
                            f"Precondition violated for function {func.__name__}"
                        )
                except Exception as e:
                    if isinstance(e, PreconditionViolation):
                        raise
                    raise PreconditionViolation(
                        f"Error evaluating precondition for {func.__name__}: {e}"
                    )
            
            return func(*args, **kwargs)
        
        # Copy contract metadata to wrapper
        wrapper._contract_metadata = func._contract_metadata
        return wrapper
    return decorator


def postcondition(condition: Callable[..., bool]) -> Callable[[F], F]:
    """
    Decorator to add a postcondition to a function.
    
    Args:
        condition: A function that takes the result as first argument,
                  followed by the original function arguments, and returns
                  True if the postcondition is satisfied
                  
    Returns:
        The decorated function with postcondition checking
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_contract_metadata'):
            func._contract_metadata = {}
        
        if 'postconditions' not in func._contract_metadata:
            func._contract_metadata['postconditions'] = []
        func._contract_metadata['postconditions'].append(condition)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if _CONTRACT_CHECKING_ENABLED:
                # Check postcondition
                try:
                    if not condition(result, *args, **kwargs):
                        raise PostconditionViolation(
                            f"Postcondition violated for function {func.__name__}"
                        )
                except Exception as e:
                    if isinstance(e, PostconditionViolation):
                        raise
                    raise PostconditionViolation(
                        f"Error evaluating postcondition for {func.__name__}: {e}"
                    )
            
            return result
        
        # Copy contract metadata to wrapper
        wrapper._contract_metadata = func._contract_metadata
        return wrapper
    return decorator


def invariant(condition: Callable[..., bool]) -> Callable[[F], F]:
    """
    Decorator to add an invariant to a function.
    
    Args:
        condition: A function that takes the same arguments as the decorated
                  function and returns True if the invariant is satisfied
                  
    Returns:
        The decorated function with invariant checking
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_contract_metadata'):
            func._contract_metadata = {}
        
        if 'invariants' not in func._contract_metadata:
            func._contract_metadata['invariants'] = []
        func._contract_metadata['invariants'].append(condition)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if _CONTRACT_CHECKING_ENABLED:
                # Check invariant before execution
                try:
                    if not condition(*args, **kwargs):
                        raise InvariantViolation(
                            f"Invariant violated before execution of {func.__name__}"
                        )
                except Exception as e:
                    if isinstance(e, InvariantViolation):
                        raise
                    raise InvariantViolation(
                        f"Error evaluating invariant for {func.__name__}: {e}"
                    )
            
            result = func(*args, **kwargs)
            
            if _CONTRACT_CHECKING_ENABLED:
                # Check invariant after execution
                try:
                    if not condition(*args, **kwargs):
                        raise InvariantViolation(
                            f"Invariant violated after execution of {func.__name__}"
                        )
                except Exception as e:
                    if isinstance(e, InvariantViolation):
                        raise
                    raise InvariantViolation(
                        f"Error evaluating invariant for {func.__name__}: {e}"
                    )
            
            return result
        
        # Copy contract metadata to wrapper
        wrapper._contract_metadata = func._contract_metadata
        return wrapper
    return decorator


__all__ = [
    'specification',
    'pre_description',
    'post_description',
    'invariant_description',
    'raises',
    'precondition',
    'postcondition',
    'invariant',
    'enable_contracts',
    'disable_contracts',
    'contracts_enabled',
    'ContractViolation',
    'PreconditionViolation',
    'PostconditionViolation',
    'InvariantViolation',
    'ImplementThis',
    'DontImplementThis',
]

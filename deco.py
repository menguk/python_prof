#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable():
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''
    def wrapper(*args, **kwargs):
        pass  # Пустая функция-обертка, чтобы не вызывать исходную функцию
    return wrapper



def decorator():
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''
    return


def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''
    def wrapper(*args, **kwargs):
        wrapper.calls += 1  # добавляем к функции атрибут для отслеживания количества вызовов
        return func(*args, **kwargs)
    wrapper.calls = 0  # при первом вызове иниц-м как 0
    return wrapper


def memo(func):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    cache -словарь, где ключи агрументы функции fib(),
    а значения - результаты выполнения функции для соотв-х аргументов
    '''
    cache = {}

    def wrapper(*args):
        if args in cache:
            return cache[args]
        else:
            result = func(*args)
            cache[args] = result
            return result
    return wrapper


def n_ary(func):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    def wrapper(*args):
        if len(args) == 0:
            raise ValueError("At least one argument is required")
        elif len(args) == 1:
            return args[0]
        else:
            result = args[0]
            for arg in args[1:]:
                result = func(result, arg)
            return result
    return wrapper

def trace(indentation=""):   # indentation  для указания отступа при выводе трассировки вызовов функции.
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"{indentation} --> {func.__name__}({', '.join(map(repr, args))})")
            result = func(*args, **kwargs)
            print(f"{indentation} <-- {func.__name__}({', '.join(map(repr, args))}) == {result}")
            return result
        return wrapper
    return decorator


@countcalls
@memo
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n - 1) + fib(n - 2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()

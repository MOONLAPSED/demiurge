```python
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar('T')
U = TypeVar('U')

@dataclass(frozen=True)
class Functor(Generic[T]):
    value: T

    def map(self, func: Callable[[T], U]) -> 'Functor[U]':
        return Functor(func(self.value))


@dataclass(frozen=True)
class Monad(Functor[T]):
    def flat_map(self, func: Callable[[T], 'Monad[U]']) -> 'Monad[U]':
        return func(self.value)
```

Functions in a first class functions architecture, like Python, are slightly different from 'functors': `Functor ≈ "Something you can apply a function to, while keeping the same type of container."` It is an aspect of [[Category Theory]] and/or Functional Semantics.

See also: [[Model]] (Machine Learning) - a collection of Functions.
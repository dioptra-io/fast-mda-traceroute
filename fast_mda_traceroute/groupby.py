from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Set, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def identity(x: T) -> T:
    return x


def group_by(
    elements: Iterable[T], key: Callable[[T], K], val: Callable[[T], V] = identity
) -> Dict[K, List[V]]:
    groups: Dict[K, List[V]] = defaultdict(list)
    for el in elements:
        groups[key(el)].append(val(el))
    return dict(groups)


def group_by_unique(
    elements: Iterable[T], key: Callable[[T], K], val: Callable[[T], V] = identity
) -> Dict[K, Set[V]]:
    groups: Dict[K, Set[V]] = defaultdict(set)
    for el in elements:
        groups[key(el)].add(val(el))
    return dict(groups)

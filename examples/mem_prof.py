import copy
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import (
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    override,
    Tuple,
    TypeVar,
)

from bytewax import operators as op
from bytewax.connectors.files import CSVSource, FileSource
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow, f_repr
from bytewax.inputs import (
    batch,
    DynamicSource,
    FixedPartitionedSource,
    StatefulSourcePartition,
    StatelessSourcePartition,
)
from bytewax.operators import KeyedStream, StatefulLogic


def _readlines(f) -> Iterator[str | None]:
    """Turn a file into a generator of lines but support `tell`.

    Python files don't support `tell` to learn the offset if you use
    them in iterator mode via `next`, so re-create that iterator using
    `readline`.

    """
    while True:
        line = f.readline().strip()
        # print(f'read: {len(line)=}', file=sys.stderr)
        # if len(line) <= 0:
        #     break
        yield line


def _get_path_dev(path: Path) -> str:
    return hex(path.stat().st_dev)


class _PipeSourcePartition(StatefulSourcePartition[str, None]):
    def __init__(self, path: Path):
        self._f = open(path, "rt")
        self._it = _readlines(self._f)
        self._last_empty = False

    @override
    def next_batch(self) -> List[str]:
        line = next(self._it)
        self._last_empty = not bool(line)
        # if line:
        #     print(f'{key_func(line)=}', file=sys.stderr)
        #     print(f'{len(line)=}', file=sys.stderr)
        if line:
            return [line]
        return []

    @override
    def snapshot(self) -> None:
        return

    @override
    def next_awake(self) -> Optional[datetime]:
        if self._last_empty:
            delta = timedelta(microseconds=10)
            # delta = timedelta(microseconds=100)
            # delta = timedelta(milliseconds=100)
            # print(f'next awake in {delta=}', file=sys.stderr)
            return datetime.now(timezone.utc) + delta

    @override
    def close(self) -> None:
        self._f.close()


class PipeSource(FixedPartitionedSource[str, None]):
    def __init__(
        self,
        paths: List[Path | str],
    ):
        self._paths = [Path(x) for x in paths]

    @override
    def list_parts(self) -> List[str]:
        xs = []
        for path in self._paths:
            if not path.exists():
                print(f"path not found: {path}", file=sys.stderr)
                continue
            fs_id = _get_path_dev(path)
            xs.append(f"{fs_id}::{path}")
        print(f"list_parts: {xs}", file=sys.stderr)
        return xs

    @override
    def build_part(
        self, step_id: str, for_part: str, resume_state: Optional[int]
    ) -> _PipeSourcePartition:
        print(f"build_part: {for_part}", file=sys.stderr)
        _fs_id, path = for_part.split("::", 1)
        # TODO: Warn and return None. Then we could support
        # continuation from a different file.
        # assert path == str(self._path), "Can't resume reading from different file"
        return _PipeSourcePartition(Path(path))


flow = Dataflow("mem_prof")
stream = op.input("some_inp", flow, PipeSource([Path("some_fifo"), Path("other_fifo")]))

stream = op.filter("filter", stream, lambda x: bool(x))


def key_func(x):
    return x[0].upper()


stream = op.key_on("key", stream, key_func)

# stream = op.redistribute("shuffle", stream)


@dataclass
class State:
    key: str
    count: int


def mapper(state: State | None, value: str) -> Tuple[State, List[int]]:
    if not state:
        state = State(key=key_func(value), count=0)
    state.count += len(value)
    return state, [state.count]


V = TypeVar("V")
W = TypeVar("W")
S = TypeVar("S")


@dataclass
class _StatefulFlatMapLogic(StatefulLogic[V, W, S]):
    step_id: str
    mapper: Callable[[Optional[S], V], Tuple[Optional[S], Iterable[W]]]
    state: Optional[S]

    @override
    def on_item(self, value: V) -> Tuple[Iterable[W], bool]:
        res = self.mapper(self.state, value)
        try:
            s, ws = res
        except TypeError as ex:
            msg = (
                f"return value of `mapper` {f_repr(self.mapper)} "
                f"in step {self.step_id!r} "
                "must be a 2-tuple of `(updated_state, emit_values)`; "
                f"got a {type(res)!r} instead"
            )
            raise TypeError(msg) from ex
        if s is None:
            # No need to update state as we're thowing everything
            # away.
            return (ws, StatefulLogic.DISCARD)
        else:
            self.state = s
            return (ws, StatefulLogic.RETAIN)

    @override
    def snapshot(self) -> S:
        assert self.state is not None
        print(f"{self.state=}", file=sys.stderr)
        return copy.deepcopy(self.state)


def stateful_flat_map(
    step_id: str,
    up: KeyedStream[V],
    mapper: Callable[[Optional[S], V], Tuple[Optional[S], Iterable[W]]],
) -> KeyedStream[W]:
    def shim_builder(resume_state: Optional[S]) -> _StatefulFlatMapLogic[V, W, S]:
        return _StatefulFlatMapLogic(step_id, mapper, resume_state)

    return op.stateful("stateful", up, shim_builder)


stream = stateful_flat_map("count", stream, mapper)
op.output("out", stream, StdOutSink())

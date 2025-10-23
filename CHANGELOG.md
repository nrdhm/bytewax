# Bytewax Changelog

All notable changes to this project will be documented in this file.
For help with updating to new Bytewax versions, please see the
[migration guide](https://bytewax.io/docs/reference/migration).

## Latest

__Add any extra change notes here and we'll put them in the release
notes on GitHub when we make a new release.__

## v0.22.0
- Fixes a stall when multiple workers read from partitioned input
  https://github.com/nrdhm/bytewax/pull/3


## v0.21.1

- `join_window` operator now supports using stream-order via the
  `ordered` parameter.

- Windowing operators now correctly respect `now_getter` and
  `to_system_utc` in `EventClock`.

- Fixes an issue where the runtime would not properly report the
  correct exception being raised by dataflow code.

- Fixes a bug where window closing will be delayed if using event time
  and all values for a key fall into a single window and event
  timestamps are within `wait_for_system_duration` of each other.

- Fixes a bug where using `EventClock` on macOS systems would randomly
  assert.

## v0.21.0

- {py:obj}`~bytewax.inputs.SimplePollingSource` now allows you to
  retain state to support at-least-once delivery.

- Fixes a bug when using
  {py:obj}`~bytewax.operators.windowing.SlidingWindower` where values
  would be assigned to an extra window if their timestamps were near
  the end of the correct window.

- Upstream type hints on
  {py:obj}`bytewax.connectors.kafka.operators.serialize_key`,
  {py:obj}`~bytewax.connectors.kafka.operators.serialize_value`, and
  {py:obj}`~bytewax.connectors.kafka.operators.serialize` have been
  made more broad to support all Kafka serializers, like
  {py:obj}`confluent_kafka.serialization.StringSerializer`.

- *Breaking change* - Fixes a bug which caused two of the same types
  of windowing operators in a dataflow to spuriously result in a
  `ValueError`. This fix invalidates any recovery data for all
  windowing operators; it is recommended to delete and re-create
  the recovery store if you are using windowing operators.

- Fixes a performance issue where
  {py:obj}`bytewax.operators.StatefulBatchLogic.notify_at` (and thus
  many of the other stateful operators' `notify_at` derived from it)
  was being called superfluously.

## v0.20.1

- Fixes a bug when using
  {py:obj}`~bytewax.operators.windowing.EventClock` where in-order but
  "slow" data results in watermark assertion errors.

## v0.20.0

- Adds a dataflow structure visualizer. Run `python -m
  bytewax.visualize`.

- *Breaking change* The internal format of recovery databases has been
  changed from using `JsonPickle` to Python's built-in {py:obj}`pickle`.
  Recovery stores that used the old format will not be usable after
  upgrading.

- *Breaking change* The `unary` operator and `UnaryLogic` have been
  renamed to `stateful` and `StatefulLogic` respectively.

- Adds a `stateful_batch` operator to allow for lower-level batch
  control while managing state.

- `StatefulLogic.on_notify`, `StatefulLogic.on_eof`, and
  `StatefulLogic.notify_at` are now optional overrides. The defaults
  retain the state and emit nothing.

- *Breaking change* Windowing operators have been moved from
  `bytewax.operators.window` into `bytewax.operators.windowing`.

- *Breaking change* `ClockConfig`s have had `Config` dropped from
  their name and are just `Clock`s. E.g. If you previously `from
  bytewax.operators.window import SystemClockConfig` now `from
  bytewax.operators.windowing import SystemClock`.

- *Breaking change* `WindowConfig`s have been renamed to `Windower`s.
  E.g. If you previously `from bytewax.operators.window import
  SessionWindow` now `from bytewax.operators.windowing import
  SessionWindower`.

- *Breaking change* All windowing operators now return a set of
  streams {py:obj}`~bytewax.operators.windowing.WindowOut`.
  {py:obj}`~bytewax.operators.windowing.WindowMetadata` now is
  branched into its own stream and is no longer part of the single
  downstream. All window operator emitted items are labeled with the
  unique window ID they came from to facilitate joining the data
  later.

- *Breaking change* {py:obj}`~bytewax.operators.windowing.fold_window`
  now requires a `merge` argument. This handles whenever the session
  windower determines that two windows must be merged because a new
  item bridged a gap.

- *Breaking change* The `join_named` and `join_window_named` operators
  have been removed because they did not support returning proper type
  information. Use {py:obj}`~bytewax.operators.join` or
  {py:obj}`~bytewax.operators.windowing.join_window` instead, which
  have been enhanced to properly type their downstream values.

- *Breaking change* {py:obj}`~bytewax.operators.join` and
  {py:obj}`~bytewax.operators.windowing.join_window` have had their
  `product` argument replaced with `insert_mode`. You now can specify
  more nuanced kinds of join modes.

- Python interfaces are now provided for custom clocks and windowers.
  Subclass {py:obj}`~bytewax.operators.windowing.Clock` (and a
  corresponding {py:obj}`~bytewax.operators.windowing.ClockLogic`) or
  {py:obj}`~bytewax.operators.windowing.Windower` (and a corresponding
  {py:obj}`~bytewax.operators.windowing.WindowerLogic`) to define your
  own senses of time and window definitions.

- Adds a {py:obj}`~bytewax.operators.windowing.window` operator to
  allow you to write more flexible custom windowing operators.

- Session windows now work correctly with out-of-order data and joins.

- {py:obj}`~bytewax.operators.windowing.WindowMetadata` now contains a
  {py:obj}`~bytewax.operators.windowing.WindowMetadata.merged_ids`
  field with any window IDs that were merged into this window.

- All windowing operators now process items in timestamp order. The
  most visible change that this results in is that the
  {py:obj}`~bytewax.operators.windowing.collect_window` operator now
  emits collections with values in timestamp order.

- Adds a {py:obj}`~bytewax.operators.filter_map_value` operator.

- Adds a {py:obj}`~bytewax.operators.enrich_cached` operator for
  easier joining with an external data source.

- Adds a {py:obj}`~bytewax.operators.key_rm` convenience operator to
  remove keys from a {py:obj}`~bytewax.operators.KeyedStream`.

## v0.19.1

- Fixes a bug where using a system clock on certain architectures
  causes items to be dropped from windows.

## v0.19.0

- Multiple operators have been reworked to avoid taking and releasing
  Python's global interpreter lock while iterating over multiple items.
  Windowing operators, stateful operators and operators like `branch`
  will see significant performance improvements.

  Thanks to @damiondoesthings for helping us track this down!

- *Breaking change* `FixedPartitionedSource.build_part`,
  `DynamicSource.build`, `FixedPartitionedSink.build_part` and `DynamicSink.build`
  now take an additional `step_id` argument. This argument can be used when
  labeling custom Python metrics.

- Custom Python metrics can now be collected using the `prometheus-client`
  library.

- *Breaking change* The schema registry interface has been removed.
  You can still use schema registries, but you need to instantiate
  the (de)serializers on your own. This allows for more flexibility.
  See the `confluent_serde` and `redpanda_serde` examples for how
  to use the new interface.

- Fixes bug where items would be incorrectly marked as late in sliding
  and tumbling windows in cases where the timestamps are very far from
  the `align_to` parameter of the windower.
- Adds `stateful_flat_map` operator.

- *Breaking change* Removes `builder` argument from `stateful_map`.
  Instead, the initial state value is always `None` and you can call
  your previous builder by hand in the `mapper`.

- *Breaking change* Improves performance by removing the `now:
  datetime` argument from `FixedPartitionedSource.build_part`,
  `DynamicSource.build`, and `UnaryLogic.on_item`. If you need the
  current time, use:

```python
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
```

- *Breaking change* Improves performance by removing the `sched:
  datetime` argument from `StatefulSourcePartition.next_batch`,
  `StatelessSourcePartition.next_batch`, `UnaryLogic.on_notify`. You
  should already have the scheduled next awake time in whatever
  instance variable you returned in
  `{Stateful,Stateless}SourcePartition.next_awake` or
  `UnaryLogic.notify_at`.

## v0.18.2

- Fixes a bug that prevented the deletion of old state in recovery stores.

- Better error messages on invalid epoch and backup interval
  parameters.

- Fixes bug where dataflow will hang if a source's `next_awake` is set
  far in the future.

## v0.18.1

- Changes the default batch size for `KafkaSource` from 1 to 1000 to match
  the Kafka input operator.

- Fixes an issue with the `count_window` operator:
  https://github.com/bytewax/bytewax/issues/364.

## v0.18.0

- Support for schema registries, through
  `bytewax.connectors.kafka.registry.RedpandaSchemaRegistry` and
  `bytewax.connectors.kafka.registry.ConfluentSchemaRegistry`.

- Custom Kafka operators in `bytewax.connectors.kafka.operators`:
  `input`, `output`, `deserialize_key`, `deserialize_value`,
  `deserialize`, `serialize_key`, `serialize_value` and `serialize`.

- *Breaking change* `KafkaSource` now emits a special
  `KafkaSourceMessage` to allow access to all data on consumed
  messages. `KafkaSink` now consumes `KafkaSinkMessage` to allow
  setting additional fields on produced messages.

- Non-linear dataflows are now possible. Each operator method returns
  a handle to the `Stream`s it produces; add further steps via calling
  operator functions on those returned handles, not the root
  `Dataflow`. See the migration guide for more info.

- Auto-complete and type hinting on operators, inputs, outputs,
  streams, and logic functions now works.

- A ton of new operators: `collect_final`, `count_final`,
  `count_window`, `flatten`, `inspect_debug`, `join`, `join_named`,
  `max_final`, `max_window`, `merge`, `min_final`, `min_window`,
  `key_on`, `key_assert`, `key_split`, `merge`, `unary`. Documentation
  for all operators are in `bytewax.operators` now.

- New operators can be added in Python, made by grouping existing
  operators. See `bytewax.dataflow` module docstring for more info.

- *Breaking change* Operators are now stand-alone functions; `import
  bytewax.operators as op` and use e.g. `op.map("step_id", upstream,
  lambda x: x + 1)`.

- *Breaking change* All operators must take a `step_id` argument now.

- *Breaking change* `fold` and `reduce` operators have been renamed to
  `fold_final` and `reduce_final`. They now only emit on EOF and are
  only for use in batch contexts.

- *Breaking change* `batch` operator renamed to `collect`, so as to
  not be confused with runtime batching. Behavior is unchanged.

- *Breaking change* `output` operator does not forward downstream its
  items. Add operators on the upstream handle instead.

- `next_batch` on input partitions can now return any `Iterable`, not
  just a `List`.

- `inspect` operator now has a default inspector that prints out items
  with the step ID.

- `collect_window` operator now can collect into `set`s and `dict`s.

- Adds a `get_fs_id` argument to `{Dir,File}Source` to allow handling
  non-identical files per worker.

- Adds a `TestingSource.EOF` and `TestingSource.ABORT` sentinel values
  you can use to test recovery.

- *Breaking change* Adds a `datetime` argument to
  `FixedPartitionSource.build_part`, `DynamicSource.build_part`,
  `StatefulSourcePartition.next_batch`, and
  `StatelessSourcePartition.next_batch`. You can now use this to
  update your `next_awake` time easily.

- *Breaking change* Window operators now emit `WindowMetadata` objects
  downstream. These objects can be used to introspect the open_time
  and close_time of windows. This changes the output type of windowing
  operators from: `(key, values)` to `(key, (metadata, values))`.

- *Breaking change* IO classes and connectors have been renamed to
  better reflect their semantics and match up with documentation.

- Moves the ability to start multiple Python processes with the
  `-p` or `--processes` to the `bytewax.testing` module.

- *Breaking change* `SimplePollingSource` moved from
  `bytewax.connectors.periodic` to `bytewax.inputs` since it is an
  input helper.

- `SimplePollingSource`'s `align_to` argument now works.

## v0.17.1

- Adds the `batch` operator to Dataflows. Calling `Dataflow.batch`
  will batch incoming items until either a batch size has been reached
  or a timeout has passed.

- Adds the `SimplePollingInput` source. Subclass this input source to
  periodically source new input for a dataflow.

- Re-adds GLIBC 2.27 builds to support older linux distributions.

## v0.17.0

### Changed

- *Breaking change* Recovery system re-worked. Kafka-based recovery
  removed. SQLite recovery file format changed; existing recovery DB
  files can not be used. See the module docstring for
  `bytewax.recovery` for how to use the new recovery system.

- Dataflow execution supports rescaling over resumes. You can now
  change the number of workers and still get proper execution and
  recovery.

- `epoch-interval` has been renamed to `snapshot-interval`

- The `list-parts` method of `PartitionedInput` has been changed to
  return a `List[str]` and should only reflect the available
  inputs that a given worker has access to. You no longer need
  to return the complete set of partitions for all workers.

- The `next` method of `StatefulSource` and `StatelessSource` has
  been changed to `next_batch` and should return a `List` of elements,
  or the empty list if there are no elements to return.

### Added

- Added new cli parameter `backup-interval`, to configure the length of
  time to wait before "garbage collecting" older recovery snapshots.

- Added `next_awake` to input classes, which can be used to schedule
  when the next call to `next_batch` should occur. Use `next_awake`
  instead of `time.sleep`.

- Added `bytewax.inputs.batcher_async` to bridge async Python libraries
  in Bytewax input sources.

- Added support for linux/aarch64 and linux/armv7 platforms.

### Removed

- `KafkaRecoveryConfig` has been removed as a recovery store.

## v0.16.2

- Add support for Windows builds - thanks @zzl221000!
- Adds a CSVInput subclass of FileInput

## v0.16.1

- Add a cooldown for activating workers to reduce CPU consumption.
- Add support for Python 3.11.

## v0.16.0

- *Breaking change* Reworked the execution model. `run_main` and `cluster_main`
  have been moved to `bytewax.testing` as they are only supposed to be used
  when testing or prototyping.
  Production dataflows should be ran by calling the `bytewax.run`
  module with `python -m bytewax.run <dataflow-path>:<dataflow-name>`.
  See `python -m bytewax.run -h` for all the possible options.
  The functionality offered by `spawn_cluster` are now only offered by the
  `bytewax.run` script, so `spawn_cluster` was removed.

- *Breaking change* `{Sliding,Tumbling}Window.start_at` has been
  renamed to `align_to` and both now require that argument. It's not
  possible to recover windowing operators without it.

- Fixes bugs with windows not closing properly.

- Fixes an issue with SQLite-based recovery. Previously you'd always
  get an "interleaved executions" panic whenever you resumed a cluster
  after the first time.

- Add `SessionWindow` for windowing operators.

- Add `SlidingWindow` for windowing operators.

- *Breaking change* Rename `TumblingWindowConfig` to `TumblingWindow`

- Add `filter_map` operator.

- *Breaking change* New partition-based input and output API. This
  removes `ManualInputConfig` and `ManualOutputConfig`. See
  `bytewax.inputs` and `bytewax.outputs` for more info.

- *Breaking change* `Dataflow.capture` operator is renamed to
  `Dataflow.output`.

- *Breaking change* `KafkaInputConfig` and `KafkaOutputConfig` have
  been moved to `bytewax.connectors.kafka.KafkaInput` and
  `bytewax.connectors.kafka.KafkaOutput`.

- *Deprecation warning* The `KafkaRecovery` store is being deprecated
  in favor of `SqliteRecoveryConfig`, and will be removed in a future
  release.

## 0.15.0

- *Breaking change* Fixes issue with multi-worker recovery. If the
  cluster crashed before all workers had completed their first epoch,
  the cluster would resume from the incorrect position. This requires
  a change to the recovery store. You cannot resume from recovery data
  written with an older version.

## 0.14.0

- Dataflow continuation now works. If you run a dataflow over a finite
  input, all state will be persisted via recovery so if you re-run the
  same dataflow pointing at the same input, but with more data
  appended at the end, it will correctly continue processing from the
  previous end-of-stream.

- Fixes issue with multi-worker recovery. Previously resume data was
  being routed to the wrong worker so state would be missing.

- *Breaking change* The above two changes require that the recovery
  format has been changed for all recovery stores. You cannot resume
  from recovery data written with an older version.

- Adds an introspection web server to dataflow workers.

- Adds `collect_window` operator.

## 0.13.1

- Added Google Colab support.

## 0.13.0

- Added tracing instrumentation and configurations for tracing backends.

## 0.12.0

- Fixes bug where window is never closed if recovery occurs after last
  item but before window close.

- Recovery logging is reduced.

- *Breaking change* Recovery format has been changed for all recovery stores.
  You cannot resume from recovery data written with an older version.

- Adds a `DynamoDB` and `Bigquery` output connector.

## 0.11.2

- Performance improvements.

- Support SASL and SSL for `bytewax.inputs.KafkaInputConfig`.


## 0.11.1

- KafkaInputConfig now accepts additional properties. See
  `bytewax.inputs.KafkaInputConfig`.

- Support for a pre-built Kafka output component. See
  `bytewax.outputs.KafkaOutputConfig`.

## 0.11.0

- Added the `fold_window` operator, works like `reduce_window` but allows
  the user to build the initial accumulator for each key in a `builder` function.

- Output is no longer specified using an `output_builder` for the
  entire dataflow, but you supply an "output config" per capture. See
  `bytewax.outputs` for more info.

- Input is no longer specified on the execution entry point (like
  `run_main`), it is instead using the `Dataflow.input` operator.

- Epochs are no longer user-facing as part of the input system. Any
  custom Python-based input components you write just need to be
  iterators and emit items. Recovery snapshots and backups now happen
  periodically, defaulting to every 10 seconds.

- Recovery format has been changed for all recovery stores. You cannot
  resume from recovery data written with an older version.

- The `reduce_epoch` operator has been replaced with
  `reduce_window`. It takes a "clock" and a "windower" to define the
  kind of aggregation you want to do.

- `run` and `run_cluster` have been removed and the remaining
  execution entry points moved into `bytewax.execution`. You can now
  get similar prototyping functionality with
  `bytewax.execution.run_main` and `bytewax.execution.spawn_cluster`
  using `Testing{Input,Output}Config`s.

- `Dataflow` has been moved into `bytewax.dataflow.Dataflow`.

## 0.10.0

- Input is no longer specified using an `input_builder`, but now an
  `input_config` which allows you to use pre-built input
  components. See `bytewax.inputs` for more info.

- Preliminary support for a pre-built Kafka input component. See
  `bytewax.inputs.KafkaInputConfig`.

- Keys used in the `(key, value)` 2-tuples to route data for stateful
  operators (like `stateful_map` and `reduce_epoch`) must now be
  strings. Because of this `bytewax.exhash` is no longer necessary and
  has been removed.

- Recovery format has been changed for all recovery stores. You cannot
  resume from recovery data written with an older version.

- Slight changes to `bytewax.recovery.RecoveryConfig` config options
  due to recovery system changes.

- `bytewax.run()` and `bytewax.run_cluster()` no longer take
  `recovery_config` as they don't support recovery.


## 0.9.0

- Adds `bytewax.AdvanceTo` and `bytewax.Emit` to control when processing
  happens.

- Adds `bytewax.run_main()` as a way to test input and output builders
  without starting a cluster.

- Adds a `bytewax.testing` module with helpers for testing.

- `bytewax.run_cluster()` and `bytewax.spawn_cluster()` now take a
  `mp_ctx` argument to allow you to change the multiprocessing
  behavior. E.g. from "fork" to "spawn". Defaults now to "spawn".

- Adds dataflow recovery capabilities. See `bytewax.recovery`.

- Stateful operators `bytewax.Dataflow.reduce()` and
  `bytewax.Dataflow.stateful_map()` now require a `step_id` argument
  to handle recovery.

- Execution entry points now take configuration arguments as kwargs.

## 0.8.0

- Capture operator no longer takes arguments. Items that flow through
  those points in the dataflow graph will be processed by the output
  handlers setup by each execution entry point. Every dataflow
  requires at least one capture.

- `Executor.build_and_run()` is replaced with four entry points for
  specific use cases:

  - `run()` for exeuction in the current process. It returns all
    captured items to the calling process for you. Use this for
    prototyping in notebooks and basic tests.

  - `run_cluster()` for execution on a temporary machine-local cluster
    that Bytewax coordinates for you. It returns all captured items to
    the calling process for you. Use this for notebook analysis where
    you need parallelism.

  - `spawn_cluster()` for starting a machine-local cluster with more
    control over input and output. Use this for standalone scripts
    where you might need partitioned input and output.

  - `cluster_main()` for starting a process that will participate in a
    cluster you are coordinating manually. Use this when starting a
    Kubernetes cluster.

- Adds `bytewax.parse` module to help with reading command line
  arguments and environment variables for the above entrypoints.

- Renames `bytewax.inp` to `bytewax.inputs`.

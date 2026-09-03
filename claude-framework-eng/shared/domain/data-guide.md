# Data guide

For projects that acquire, transform or store data coming from outside. A
defect here brings nothing down: it makes everything work with the wrong
values.

## Normalisation

- **Deterministic**: same input, same output, always and across different runs.
  If it depends on arrival order or on the clock, it is not.
- **Explicit units**, never implicit in the context: amounts as integers with
  the currency alongside, measures with the unit, instants with the time zone.
  Floating point is not used for money.
- **Text normalised before comparison**: unicode form, edge whitespace, case,
  invisible characters. Two strings that look identical may not be.
- **A missing value is not zero, is not the empty string, is not "unknown"**:
  they are four different things and must be represented as such.

## Keys and identity

- A stable key derives from attributes that **do not change**. If it derives
  from a name, an address or a price, it will produce duplicates at the next
  update.
- A key that is too permissive merges distinct entities: it is the opposite
  error and it is noticed much later.
- Reconciliation between different sources must be **verified on real cases**,
  ambiguous ones included: two similar products, two people with the same name,
  the same object written in two ways.

## Idempotence and repeatability

- Re-running an acquisition must not duplicate, increment, or rewrite with
  partial values.
- Every operation must be interruptible midway and resumable without leaving
  inconsistent state.
- An operation that is not idempotent must be declared as such and protected.

## Truth and derivatives

- **One single source of truth.** Indexes, caches, materialised views and
  aggregates are derivatives: rebuildable, never the only copy.
- If a change forces a rebuild, it must be declared with the procedure and the
  expected time.
- Two points that can diverge will diverge: if there is no way to realign them,
  it is a design defect.

## Untrusted input

Every external datum is validated at the boundary: schema, types, lengths,
encoding, ranges. Malformed rows are handled **without stopping everything and
without corrupting the rest**, and they end up in a count.

Explicit defences: archives and documents built to exhaust memory or disk,
references to external entities, paths that escape the intended folder,
requests to addresses supplied by the source.

## Observability

For every run and every source: how many records read, accepted, discarded and
**why**. Without these numbers, a silent loss is invisible — and silent losses
are the norm, not the exception.

No personal data in the logs.

## Migrations

Compatible with data already written · reversible or with a declared way back ·
applicable while the previous version of the code is still running · tested on
a realistic copy, not on sample data.

## In this project

[TO FILL IN — the sources and what they really promise, the acquisition
contract, the normalisation rules adopted, which the stable keys are, where the
truth lives and what is derived, the dirty cases already met, how a rebuild is
run.]

# Architecture guide

Boundaries, contracts and the direction of dependencies. Reference material for
whoever designs or reviews a structural change.

## Boundaries

A well-placed boundary answers three questions without opening the code: **what
this unit does, how it is used, what it depends on.** If answering requires
reading the implementation, the boundary is not a boundary.

Signs that a boundary is missing or in the wrong place:

- a file that grows and you cannot say in one sentence what it is about;
- two units that always have to be changed together;
- a unit that knows how another is built internally;
- an internal change that breaks its users;
- the same concept represented differently in two places.

**What changes together stays together.** You divide by responsibility, not by
technical category: separating by "kind of file" produces units that can
neither be understood nor changed on their own.

## Direction of dependencies

Domain logic does not depend on what surrounds it: it does not know the
interface, the database, the transport format, the external provider. They
depend on it.

The practical test: **the logic can be exercised without starting anything.**
If testing a rule needs a server, a browser or a connection, the rule is
coupled to a detail.

When the natural direction would be wrong, it is inverted with an interface
defined by the side that uses it — not by the side that implements it.

## Contracts

A contract is everything someone else relies on: public signatures, persisted
formats, protocols, schemas, key names, URLs, error codes, and **observable
behaviours** even undocumented ones.

Before changing one:

1. What is the contract, exactly?
2. Who uses it? Search everywhere, including what the compiler does not see.
3. Am I breaking compatibility or observable behaviour?
4. If so: is there a migration? Is a version needed? Is a period needed in
   which both work?

A contract changed silently is not a saving of time: it is a fault deferred to
when nobody will remember why.

## Deferred decisions

When a choice has not been made yet — which provider, which format, which
source — it is kept **behind an interface** instead of guessed. The cost is one
level of indirection; the benefit is that the decision, when it comes, touches
a single point.

This holds only for decisions that are **really open**. Abstracting what will
never change is pure complexity.

## State

The less shared state there is, the fewer ways there are to be inconsistent.
Where it is needed: one single source of truth, the other copies avowedly
derived and rebuildable. Two points that can diverge will diverge.

## In this project

[TO FILL IN — map of the modules with the responsibility of each, the
boundaries that must not be crossed, the declared contracts and who consumes
them, the decisions deliberately deferred and what keeps them open, the
architectural choices already made that are not reopened without a mandate.]

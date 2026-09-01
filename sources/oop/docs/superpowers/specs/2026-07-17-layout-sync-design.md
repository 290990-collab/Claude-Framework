# Layout sync between multiple PCs — design

**Date:** 2026-07-17
**Status:** SUPERSEDED — the cloud-folder transport and background poll described
here are replaced by explicit file Export/Import in
`2026-07-17-layout-sync-export-import-design.md`. The data model, merge rules
(`LayoutSync`, `AdoptMergedLayouts`, tombstones), and "missing plugins" marking
below still hold; only the transport changed.

## Goal

Let a user's favourite **layouts** follow them across several PCs, without a
backend, without an account, and without touching the socket protocol or the
remote script.

## Scope

**Synced:** layouts only (the switchable favourite sets).

**Never synced** (per-machine by nature):

- `catalog.json` — installed plugins differ per machine.
- Usage/frecency stats.
- Machine settings: `Port`, `AutoStart`, `CatalogScanned`, `CatalogScriptVersion`,
  UI prefs (`Theme`, `UiScale`, `AccentColor`).

This is why the sync file is **not** a copy of `config.json`: that file mixes
syncable layouts with per-machine settings.

## Transport

A **user-chosen folder** that the user has already made cloud-synced (Google
Drive, Dropbox, OneDrive, iCloud). The cloud client does the transport; the app
only reads and writes a file.

- **Opt-in**: off by default. The app touches nothing until the user enables
  sync and picks a folder in Settings.
- No network code, no auth → no new antivirus surface, and it works on macOS.

## Data model (contract change: persisted `config.json`)

`MenuLayout` gains two fields:

- `Id` (GUID string, stable) — identifies "the same layout" across PCs even
  after a rename.
- `UpdatedUtc` (DateTime) — refreshed when that layout's `Name` or `Entries`
  change.

Migration in `AppConfig.MigrateLayouts()`: existing layouts get a fresh `Id`
and an initial `UpdatedUtc`. The change is **additive** → an older app version
ignores the new fields without breaking.

`AppConfig` also gains **per-machine, never-synced** fields: `SyncEnabled`
(bool), `SyncFolder` (string?), `DeviceId` (string).

## Sync file (new contract between app instances)

Written into the chosen folder as `layouts-sync.json`:

```json
{
  "schema": 1,
  "device": "<device id>",
  "layouts": [ { "id": "...", "name": "...", "entries": [ ... ], "updatedUtc": "..." } ],
  "deleted": [ { "id": "...", "deletedUtc": "..." } ]
}
```

`schema` allows future evolution. `deleted` holds **tombstones**: without them a
layout deleted on one PC would be resurrected by the other on the next merge.

## Merge: per-layout last-writer-wins

Pure function in `Core` (`LayoutSync`), no I/O, fully unit-testable.

Union keyed by `Id`:

- present on both sides → the newer `UpdatedUtc` wins;
- only local → kept (will be pushed);
- only remote → adopted;
- a tombstone newer than the layout's `UpdatedUtc` → the layout is dropped;
  a layout edited after its tombstone survives (re-created).

`MaxLayouts = 5` cap: if the union exceeds 5, keep the 5 most recently updated.
Clock skew between PCs is accepted (UTC timestamps).

## When it runs

- **On startup**: read remote → merge → save local, and write back if changed.
- **On linking a folder**: immediate reconcile.
- **While running**: a stat of the shared file's write stamp on the existing status
  tick; it reconciles only when another PC actually published. One `stat` on the
  common path — no read, no parse.
- **Atomic write**: temp file + rename, so the other PC never reads a half-written
  file. Reads are tolerant: a missing/corrupt/partial file is ignored, never fatal.

### Why a poll and not a FileSystemWatcher

The watcher was the original plan and was dropped: cloud clients publish by writing a
temporary file and renaming it, which makes watcher events unreliable (missed or
duplicated) and forces debouncing. A write-stamp poll on a timer that already ticks is
smaller, needs no debounce, and cannot be defeated by how the cloud client writes.

A "restart the app to sync" prompt was also considered and rejected: to know a restart
is warranted the app must first detect that the file changed — and once it has, merging
costs less than restarting a tray app that owns the global keyboard hook.

## First link

Enable sync + pick folder:

- folder has no sync file → create it from local layouts (seed), no prompt: seeding an
  empty folder costs nothing;
- folder already has one (second PC) → **confirm first**, then merge.

The confirmation is not ceremony. Linking a folder that already holds another PC's
layouts is the one destructive, irreversible step in the feature: the five-layout cap
can drop layouts permanently, there is no backup of the pre-merge state, and turning
sync off afterwards does **not** restore it (it only stops future exchange — everything
already merged stays). The prompt says exactly that.

## Settings window and merges

The Settings window takes a snapshot of the layouts when it opens and writes it back
wholesale. A merge landing meanwhile would be overwritten by that snapshot — and the
stale copy, freshly stamped by `Save()`, would then *win* the next merge and propagate
to the other PC. Two guards:

- background syncing is **suspended while Settings is open** and resumes (with one
  reconcile) on close;
- the window writes back the layout it edits **by `Id`, not by position**, since a merge
  can reorder or drop layouts and a stale index would write into the wrong one.

Linking a folder is the one merge that must happen with the window open — the user asked
for it — so the window reloads its snapshot from the config right after.

## Missing plugins on a PC

A layout entry carries a browser `Uri`. On a PC where that plugin is not
installed the URI does not resolve. At menu-build time each entry is validated
against the **local** `catalog.json`: entries not present are shown marked
"unavailable on this PC" (greyed, non-clickable) rather than failing on load.

**Guard:** if the local catalog is empty (not built yet), mark nothing —
validation is impossible and everything would be greyed on a fresh install.

## Components

- **Core**: `MenuLayout` + `Id`/`UpdatedUtc`; migration in `AppConfig`;
  `LayoutSync` (pure merge) + sync payload model; per-machine sync fields.
- **App**: `SyncService` (atomic write, orchestration, later the watcher);
  Settings UI (toggle + folder picker + status); unavailable marking (phase 3).
- **Tests**: merge — LWW picks newer, additions from both sides, tombstone wins,
  re-creation after tombstone, cap to 5, empty/corrupt remote.

## Risks

- Cloud clients writing temp files → atomic write + tolerant reads + backstop poll.
- `FileSystemWatcher` reliability with cloud clients (phase 2).
- Clock skew affects LWW ordering (UTC; small skew accepted).
- The 5-layout cap can drop a layout in a crowded merge → documented, surfaced in UI.
- Socket protocol and remote script are **untouched**.

## Status

All three phases are implemented:

1. Data model + `LayoutSync` + tests + Settings (toggle/folder) + read-on-start +
   atomic write.
2. Write-stamp poll on the existing status tick (replaced the watcher, see above).
3. "Unavailable" marking in the menu (`LayoutAvailability`).

The Settings/merge race is closed (see above): suspension while the window is open,
write-back by `Id`, reload after an explicit link.

Not verified by tests: the visual result, and a real two-PC run against an actual cloud
client. The merge rules are covered; how Drive/Dropbox publish files is not.

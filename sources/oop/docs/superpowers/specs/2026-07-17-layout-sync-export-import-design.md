# Layout sync via file Export/Import — design

**Date:** 2026-07-17
**Status:** approved (supersedes the cloud-folder transport in
`2026-07-17-layout-sync-design.md`)

## Goal

Let a user's favourite **layouts** follow them across several PCs, without a
backend, without an account, and without touching the socket protocol or the
remote script. This revision replaces the automatic cloud-folder transport with
an explicit, user-driven **Export** and **Import** of a single file.

## Why the change

The folder transport synced in the background: a linked folder plus a write-stamp
poll on the status tick. This revision drops all of that in favour of a manual
model — the user exports a file, moves it however they like (cloud, USB, email),
and imports it on the other PC. Simpler surface, one thing to understand, no
background reconcile. The trade-off — accepted by the user — is that PCs no longer
update automatically; the user syncs when they choose to.

## What is unchanged (reused as-is)

- **Data model.** `MenuLayout` keeps `Id` (stable across PCs) and `UpdatedUtc`.
  `SyncPayload` (`schema`, `device`, `layouts`, `deleted` tombstones) is still the
  portable unit. Nothing in the model changes.
- **Merge.** `LayoutSync.Merge` (pure, per-layout last-writer-wins, tombstones,
  5-layout cap, stable order) and `AppConfig.AdoptMergedLayouts` are reused
  untouched. The existing 37 merge/adopt tests still cover the rules.
- **Missing plugins.** `LayoutAvailability` marking in the menu is unaffected.
- **`AppConfig.DeletedLayouts` and `DeviceId`** stay — the merge needs tombstones,
  the payload carries the device tag.

## What is exported / imported

The **`SyncPayload`** — layouts + tombstones — **not** the full `config.json`.
`config.json` mixes syncable layouts with per-machine settings (`Port`, `Theme`,
`UiScale`, `AccentColor`, catalog, scan flags) that must not travel between PCs.
Same reasoning as the original design; only the transport changes.

Default file name: **`liveloader-layouts.json`** (editable by the user in the OS
save dialog). It names the content, and a stable name means re-exporting
overwrites the same file.

## Export

Settings → **"Export layouts…"** → OS *save-file* dialog (suggested name above,
`.json` filter) → write the current local `SyncPayload` to the chosen path.

- **Not destructive → no warning.** Export only reads local layouts and writes a
  new file.
- Atomic write is unnecessary here (the user picks a fresh destination, no other
  process is mid-read), but the write is still tolerant of failure: a failed write
  reports an error status, never crashes.

## Import

Settings → **"Import layouts…"** → OS *open-file* dialog (`.json` filter) →
**the red warning first** → on confirm, read the file, **merge (LWW)** into the
local set, adopt, and reload the window's layout list.

- **Warning is mandatory and identical** to today's first-link warning: "for each
  layout the version edited most recently wins; only 5 layouts are kept; this
  cannot be undone." Importing always folds a foreign file into the local set, so
  it always carries the same irreversible merge risk → it always warns (danger
  button, "Import and merge" / "Cancel").
- **Merge, not replace.** Same `LayoutSync.Merge` + `AdoptMergedLayouts` path the
  folder sync used. A layout present on both sides resolves by `UpdatedUtc`; only
  in the file → adopted; a tombstone newer than a layout → that layout is dropped.
- **Tolerant read.** Missing / corrupt / empty file → a clear status message, no
  merge, no crash. A file from a **newer schema** is refused (not merged), same
  guard as `ReadRemote` today.
- After a successful merge the Settings window calls the existing
  `ReloadLayoutsFromConfig()` so the on-screen list reflects the result.

## What is removed (the folder + background machinery)

- **XAML** (`MainWindow.axaml`, LAYOUT SYNC section): the `ChkSync` toggle, the
  "Choose folder…" button, and the folder-oriented help text → replaced by two
  buttons ("Export layouts…", "Import layouts…"), a status line, and updated help
  text describing the manual model.
- **`MainWindow.axaml.cs`**: `ChkSync_Changed`, `BtnSyncFolder_Click`,
  `PickSyncFolderAsync`, `RefreshSyncStatus` → removed. New `BtnExport_Click` /
  `BtnImport_Click`. `ShowSyncOutcome` adapted to the export/import statuses.
  `ReloadLayoutsFromConfig()` is **kept** (now called after import).
- **`App.axaml.cs`**: startup `SyncNowAsync`, `Poll()` on the status tick, and
  `Suspend`/`Resume` around the MainWindow lifecycle → removed. There is no
  background sync to suspend anymore, so the Settings/merge race the folder design
  had to guard against **cannot occur** (merges happen only on explicit import,
  inside the window, followed by a reload).
- **`SyncService`**: the poll / suspend / reentrancy / write-stamp / folder-path
  machinery is removed. What remains is two file operations —
  `ExportToFile(string path)` and `ImportFromFile(string path)` (read → merge →
  adopt, returning an outcome). `LayoutsChanged` is dropped unless a live consumer
  is found during implementation (the popup menu rebuilds from config on open, so
  likely none).
- **`AppConfig`**: `SyncEnabled` and `SyncFolder` are removed (dead once the
  folder transport is gone). Safe: v1.0.0 is built but **not yet released**, so no
  user `config.json` carries these fields, and `System.Text.Json` ignores unknown
  fields on read regardless.

## Components after the change

- **Core**: unchanged (`MenuLayout`, `LayoutSync`, `AppConfig.AdoptMergedLayouts`,
  tombstones, `DeviceId`); minus the two dead `AppConfig` fields.
- **App**: `SyncService.ExportToFile` / `ImportFromFile`; Settings UI (two buttons
  + status); OS file pickers via `StorageProvider`
  (`SaveFilePickerAsync` / `OpenFilePickerAsync`, `TryGetLocalPath`).
- **Tests**: merge/adopt tests reused. Add coverage for the new file layer:
  export-then-import round-trips, corrupt/empty/newer-schema import is refused,
  import merges (does not replace).

## Risks

- **No new antivirus surface** — no network, same as before; only local file
  read/write the app already does for `config.json`/`catalog.json`.
- **Socket protocol and remote script untouched.**
- Removing two persisted `AppConfig` fields — mitigated: unreleased build, additive
  JSON tolerance.
- The 5-layout cap can still drop a layout in a crowded merge → surfaced by the
  same warning before import.
- Clock skew affects LWW ordering (UTC; small skew accepted) — unchanged.

## Not verified by tests

The visual result (the two buttons, the red warning, greyed unavailable entries)
and a real cross-PC round-trip with an actual moved file. The merge rules and the
file read/write are covered; the OS file-picker UX is not.

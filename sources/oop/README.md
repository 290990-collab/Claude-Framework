<p align="center">
  <img src="assets/icon-256.png" width="96" alt="LiveLoader icon" />
</p>

<h1 align="center">LiveLoader</h1>

<p align="center">
  <b>Load your favorite plugins in Ableton Live with one click.</b><br>
  Ctrl+Right-click any track → pick from your custom menu → the device is on the track. Done.
</p>

---

<!-- TODO: add a screenshot/GIF here before publishing: docs/screenshot.png -->

## What it does

With Ableton Live in the foreground, press **Ctrl + Right-click** on any track (audio, MIDI, return or master). A menu with your favorite devices opens at the cursor, and the one you pick is loaded **instantly onto that track** — no browser searching, no drag & drop.

Works with everything Live's browser can load:

- **VST3** and **VST2** plugins
- Ableton's built-in **audio effects, MIDI effects and instruments**
- **Max for Live** devices

## How it works

Two small pieces talking over UDP on localhost:

| Piece | Job |
|---|---|
| **LiveLoader app** (tray icon) | Catches Ctrl+Right-click only inside Live, shows the menu, sends the load command |
| **Remote Script** (Python, runs inside Live) | Loads the device onto the selected track through Live's own browser API |

No keystroke simulation, no fragile browser searches: loading uses the same internal API as established control surfaces. That's why it works with any plugin on any track, on any computer, wherever your plugin folders are — Live already knows them.

## Install

### Windows

1. Download **LiveLoader-Setup** (installer) or **LiveLoader-Portable** (single exe) from [Releases](../../releases).
2. Run LiveLoader. In the **Settings** tab click **Install remote script** — Ableton's folders are detected automatically.
3. **One-time step in Live** (restart Live first if it was open):
   `Options → Preferences → Link, Tempo & MIDI → Control Surface → LiveLoader` (Input and Output: `None`).
4. In the **Plugins** tab click **Scan Live browser** (with Live running), then **Add plugins…** and pick your favorites.

That's it: Ctrl+Right-click a track in Live.

### macOS

Coming soon — the app is cross-platform (Avalonia) and macOS builds are produced by CI, but they are still being tested. Watch the releases page.

## Tips

- **Drag rows** to reorder the menu — a multi-selection (Ctrl/Shift+click) moves as one block. Press **Del** to remove the selected rows.
- Give entries the same **Group** name to collect them in a submenu: grouped entries are kept together at the top, sorted alphabetically, separated from the rest by a bold divider.
- **Separators** keep long menus readable.
- Theme: light, dark, or follow the system — in **Settings**.
- The tray icon turns **green** when Live is reachable.

## Troubleshooting

| Problem | Fix |
|---|---|
| Menu doesn't open | Is the app running (tray icon)? Is Live's window focused? |
| "Live is not responding" | Is Live open? Is the `LiveLoader` control surface enabled in Preferences? Restart Live after installing the script |
| Device lands on the wrong track | Keep "Select the track under the cursor" enabled in Settings and click on the track area/header |
| Script disappears after a Live update | Live updates can clean its internal folder — click **Install remote script** again |
| Windows: script install fails with access denied | Run LiveLoader once as administrator, install, then close and reopen normally |

The remote script logs to Live's `Log.txt` (search for "LiveLoader").

## Antivirus

Built to be boring for antivirus software: plain .NET, no packers or obfuscation, no keyboard hook (only a standard mouse hook plus reading the Ctrl key state), one synthetic click for track selection, no network traffic except UDP on 127.0.0.1. Autostart uses a regular Startup-folder shortcut, not registry Run keys.

## Support this project ♥

LiveLoader is free. If it speeds up your workflow, consider a donation — it keeps the project alive.

<!-- TODO: replace with your real links (also update FUNDING.yml and the URLs in MainWindow.axaml.cs) -->
**[Donate](https://example.com/donate)**

## License

© Enrico Di Maria — free to use; see the license shipped with the release.

*LiveLoader is an independent project, not affiliated with or endorsed by Ableton AG. "Ableton" and "Ableton Live" are trademarks of Ableton AG.*

# iSIF Extra

Extra conditions for [Status Indicator Framework](https://www.nexusmods.com/skyrimspecialedition/mods/177587) (SIF).

Adds `actorValue`, `faction`, `isUnconscious`, and `package` conditions to SIF's icon rules. Write JSON, get icons above NPCs. No configuration needed.

**[Nexus Mods Page](https://www.nexusmods.com/skyrimspecialedition/mods/179310)** — download releases, screenshots, and discussion.

## Requirements

- [SKSE64](https://skse.silverlock.org/)
- [Address Library for SKSE Plugins](https://www.nexusmods.com/skyrimspecialedition/mods/32444)
- [Status Indicator Framework](https://www.nexusmods.com/skyrimspecialedition/mods/177587)

## Installation

Install with your mod manager. That's it.

## Usage

Write SIF JSON rules using the new conditions and place them in `SKSE/Plugins/SIF/` in your mod folder (MO2 and Vortex handle the `Data/` mapping automatically). An example file (`iSIFExtra.json.example`) is included; rename it to `iSIFExtra.json` (remove `.example`) to see the demo icons in action.

### Actor Value Range

Show icons based on any actor value (Health, Magicka, Paralysis, etc.):

```json
{
  "match": {
    "formType": "NPC",
    "actorValue": {
      "name": "Paralysis",
      "min": 1
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Actor value name (e.g. `Health`, `Paralysis`, `Aggression`) |
| `min` | float | no* | Minimum value (inclusive) |
| `max` | float | no* | Maximum value (inclusive) |

\* At least one of `min` or `max` is required.

### Faction Membership

Show icons for guards, merchants, thieves — any faction:

```json
{
  "match": {
    "formType": "NPC",
    "faction": {
      "formId": ["Skyrim.esm|0x00028470"],
      "minRank": 1
    }
  }
}
```

### Unconscious State

Show icons on knocked-out NPCs (works with Knockout and Surrender, etc.):

```json
{
  "match": {
    "formType": "NPC",
    "isUnconscious": true
  }
}
```

### AI Package

Show icons for NPCs running specific AI packages (following, sandboxing, fleeing):

```json
{
  "match": {
    "formType": "NPC",
    "package": ["Skyrim.esm|0x00072946", "Skyrim.esm|0x00072948"]
  }
}
```

## Creating Custom Icons

A Python tool is included for generating SIF-compatible icon SWFs from PNG images. Static icons only — animated icons require Flash CS6 or manual SWF assembly.

```
pip install Pillow
python tools/sif_icon_builder.py icon.png -n myIcon -o Data/Interface/MyMod/icons.swf
```

Options:
- `-n` — Export name (must match JSON `label` field, case-sensitive)
- `-r N` — Resize longest side to N pixels
- `-c HEX` — Tint color (e.g. `FF0000`), preserves alpha
- `-s N` — Stage size in pixels (default 64, does not affect icon size)
- `--fps` — Frame rate (default 30)

PNG pixel dimensions = in-game icon size (no auto-scaling). Typical SIF icons are 16–32px. The output SWF goes in `Data/Interface/` and is referenced by the `source` field in SIF JSON rules.

## Compatibility

No conflicts. Doesn't hook anything — only registers conditions via SIF's public API.

## Building

### Prerequisites

- Visual Studio 2022 with C++23 support (`cl.exe`)
- [vcpkg](https://vcpkg.io/) with `VCPKG_ROOT` environment variable set
- [Ninja](https://ninja-build.org/) build system
- CMake 3.21+

### Build

```bash
cd SKSE
cmake --preset release
cmake --build build/release
```

### Dependencies

Managed via vcpkg with a custom registry for `commonlibsse-ng`:

- **commonlibsse-ng** — Skyrim SE RE type definitions and SKSE bindings
- **jsoncpp** — JSON parsing (required by the SIF API header)
- **spdlog** — Logging framework

## Source Code

[GitHub](https://github.com/Gerkinfeltser/Skyrim-iSIFExtra)

## License

Provided as-is. The vendored `SIF_API.h` is from [Status Indicator Framework](https://github.com/JerryYOJ/Status-Indicator-Framework-SKSE).

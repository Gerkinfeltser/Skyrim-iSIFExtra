# iSIFExtra

Extra condition matchers for [Status Indicator Framework](https://www.nexusmods.com/skyrimspecialedition/mods/83246) (SIF). Registers `faction`, `isUnconscious`, and `package` conditions via the SIF plugin API — no need to fork SIF itself.

**[Nexus Mods Page](https://www.nexusmods.com/skyrimspecialedition/mods/83246)** — download releases, screenshots, and discussion.

## Conditions

| Condition | Description |
|-----------|-------------|
| `faction` | Match actors by faction membership and rank |
| `isUnconscious` | Match unconscious (knocked out) actors |
| `package` | Match actors running specific AI packages |

## Requirements

- Skyrim Special Edition / Anniversary Edition
- [SKSE64](https://skse.silverlock.org/)
- [Address Library for SKSE Plugins](https://www.nexusmods.com/skyrimspecialedition/mods/32444)
- [Status Indicator Framework](https://www.nexusmods.com/skyrimspecialedition/mods/83246)

## Building

### Prerequisites

- Visual Studio 2022 with C++23 support (`cl.exe`)
- [vcpkg](https://vcpkg.io/) with `VCPKG_ROOT` environment variable set
- [Ninja](https://ninja-build.org/) build system
- CMake 3.21+

### Build

```bash
cmake --preset release
cmake --build build/release
```

### Dependencies

Managed via vcpkg with a custom registry for `commonlibsse-ng`:

- **commonlibsse-ng** — Skyrim SE RE type definitions and SKSE bindings
- **jsoncpp** — JSON parsing (required by the SIF API header)
- **spdlog** — Logging framework

## Usage

Write SIF JSON rules using `faction`, `isUnconscious`, or `package` keys:

```json
{
  "rules": [
    {
      "icon": { "source": "MyMod/icons.swf", "label": "Guard" },
      "match": {
        "formType": "NPC",
        "faction": { "formId": ["Skyrim.esm|0x00028470"], "minRank": 1 }
      }
    }
  ]
}
```

Place JSON files in `Data/SKSE/Plugins/SIF/`.

## License

Provided as-is. The vendored `SIF_API.h` is from [Status Indicator Framework](https://github.com/JerryYOJ/Status-Indicator-Framework-SKSE).

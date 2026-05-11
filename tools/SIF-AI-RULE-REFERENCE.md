# SIF Icon Rule Generator Reference

This document helps AI assistants generate valid JSON rules for [Status Indicator Framework](https://www.nexusmods.com/skyrimspecialedition/mods/177587) (SIF) and the [iSIFExtra](https://www.nexusmods.com/skyrimspecialedition/mods/179310) companion plugin.

## Overview

SIF renders icons above actors and objects in Skyrim SE/AE. Rules are JSON files placed in:

```
Data/SKSE/Plugins/SIF/*.json
```

Each file has a `rules` array. Every rule has an `icon` (what to draw) and a `match` (who to draw it on). All match fields are AND-combined.

## Icon SWFs

Icons are SWF files in `Data/Interface/`. SIF loads symbols by export name from the SWF. Static icon SWFs can be created from PNG images using the included `sif_icon_builder.py` tool:

```bash
pip install Pillow
python sif_icon_builder.py icon.png -n myIcon -o Data/Interface/MyMod/icons.swf
```

The `-n` name must match the `label` field exactly (case-sensitive). PNG pixel dimensions = in-game icon size. Typical icons are 16–32px.

## Rule Structure

```json
{
  "rules": [
    {
      "icon": {
        "source": "relative/path/to/icons.swf",
        "label": "ExportName",
        "fadeMaxDistance": 1500,
        "fadeStartDistance": 300,
        "maxInstances": 5
      },
      "match": {
        "formType": "NPC"
      }
    }
  ]
}
```

### Icon Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `source` | yes | — | SWF path relative to `Data/Interface/` |
| `label` | yes | — | Export name inside the SWF (case-sensitive) |
| `fadeMaxDistance` | no | 1800 | Hard distance cutoff; icons past this are hidden |
| `fadeStartDistance` | no | 300 | Distance where alpha fade begins |
| `maxInstances` | no | 5 | Max on-screen copies of this icon (1–48) |
Do NOT reuse the same `label` across different `source` SWFs.

## Match Conditions

All fields are AND-combined. Field names are case-insensitive (except inside `magicEffect` and `encounterZone`).

### Reference Conditions (any TESObjectREFR)

| Field | Type | Description |
|-------|------|-------------|
| `formType` | string | `NPC`, `Door`, `Container`, or `Activator` |
| `formId` | string or array | Match reference FormID |
| `baseFormId` | string or array | Match base form FormID |
| `keywords` | string or array | All listed keyword FormIDs must be present |
| `isQuestAlias` | bool | True if ref has ExtraAliasInstanceArray |
| `worldspaceFormId` | string or array | Match parent cell worldspace FormID |
| `locationFormId` | string or array | Match GetCurrentLocation() FormID |
| `conditionPerk` | string | Perk FormID — its conditions evaluated with player as subject, ref as target |

### Actor Conditions (NPCs only)

| Field | Type | Description |
|-------|------|-------------|
| `raceFormId` | string or array | Actor race FormID |
| `level` | object | `{ "min": 10, "max": 50 }` — both optional |
| `isDead` | bool | Death state |
| `isHostile` | bool | Hostility to player |
| `isEssential` | bool | Essential flag |
| `isProtected` | bool | Protected flag |
| `isPlayerTeammate` | bool | Follower/teammate state |
| `isInCombat` | bool | Combat state |
| `combatState` | integer | 0=out, 1=combat (target known), 2=searching |
| `detectionLevel` | object | NPC detection toward player: `{ "min": 0, "max": 3 }` |
| `isWitness` | bool | In player's active crime witness list |
| `isWitnessedCrimeEstablished` | bool | Witness on an established crime |

### iSIFExtra Conditions

These require the [iSIFExtra](https://www.nexusmods.com/skyrimspecialedition/mods/179310) plugin.

#### `actorValue` — Actor Value Range

Show icons based on any actor value (Health, Magicka, Stamina, Paralysis, Aggression, etc.). Matches if the value falls within the specified range.

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

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | yes | — | Actor value name (resolved via ActorValueList) |
| `min` | float | no* | — | Minimum value (inclusive) |
| `max` | float | no* | — | Maximum value (inclusive) |

\* At least one of `min` or `max` is required.

Example with both bounds:
```json
"actorValue": { "name": "Health", "min": 50, "max": 100 }
```

#### `faction` — Faction Membership

Show icons for faction members. Actor matches if **any** faction meets the rank threshold.

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

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `formId` | string or array | yes | — | Faction FormIDs. Also accepts FormList IDs (auto-expanded) |
| `minRank` | integer | no | 0 | Minimum rank. Actor matches if any faction has rank >= this |

#### `isUnconscious` — Knockout State

Show icons on unconscious (knocked out) actors. Sleeping NPCs are not affected.

```json
{
  "match": {
    "formType": "NPC",
    "isUnconscious": true
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| (value) | bool | yes | `true` to match unconscious actors |

#### `package` — AI Package

Show icons for actors running specific AI packages.

```json
{
  "match": {
    "formType": "NPC",
    "package": "Skyrim.esm|0x0003558B"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| (value) | string or array | yes | Package FormIDs. Also accepts FormList IDs (auto-expanded) |

### `magicEffect` — Active Effect Matcher

Nested matcher. Actor must have at least one active effect satisfying all fields:

```json
{
  "match": {
    "formType": "NPC",
    "magicEffect": {
      "school": "Destruction",
      "primaryValue": "Health",
      "isHostile": true
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `formId` / `effectId` | string or array | Active effect base EffectSetting FormID |
| `keywords` / `effectKeywords` | string or array | All must exist on the EffectSetting |
| `school` | string | Actor value name (e.g. `Destruction`, `Restoration`) |
| `magnitude` | number or object | `{ "min": ..., "max": ... }` |
| `duration` | number or object | `{ "min": ..., "max": ... }` |
| `area` | number or object | `{ "min": ..., "max": ... }` |
| `archetype` | string | EffectSetting archetype |
| `deliveryType` | string | Delivery method |
| `castType` | string | Casting type |
| `primaryValue` | string | Actor value name (e.g. `Health`, `Magicka`) |
| `resistance` | string | Resist variable name (e.g. `FireResist`, `MagicResist`) |
| `secondaryValue` | string | Secondary actor value |
| `effectFlags` | string or array | EffectSetting flag bits |
| `skillLevel` | number or object | Minimum skill level |
| `isHostile` | bool | Hostile effect |
| `isDetrimental` | bool | Detrimental effect |

### `encounterZone` — Encounter Zone Matcher

Nested matcher for doors with teleport links:

```json
{
  "match": {
    "formType": "Door",
    "encounterZone": {
      "level": { "min": 20 },
      "deltaPlayerLevel": { "min": 5 }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `formId` | string or array | Encounter zone FormID |
| `locationFormId` | string or array | Zone location FormID |
| `level` | object | `{ "min": ..., "max": ... }` vs zone min/max |
| `deltaPlayerLevel` | number or object | `encounterLevel - playerLevel` |
| `neverResets` | bool | kNeverResets flag |
| `matchPCBelowMinimumLevel` | bool | kMatchPCBelowMinimumLevel flag |
| `disableCombatBoundary` | bool | kDisableCombatBoundary flag |

### Logical Operators

**`not`** — Negate conditions:

```json
{ "match": { "formType": "NPC", "not": { "isDead": true } } }
```

Object form: negates entire AND. Array form: each element independently negated, all must pass.

**`anyOf`** — OR logic (at least one must match):

```json
{ "match": { "anyOf": [{ "isEssential": true }, { "isPlayerTeammate": true }] } }
```

## FormID Format

All FormIDs use `"PluginName|0xHHHHHH"` format. Arrays also accepted.

```json
"Skyrim.esm|0x000A2C94"
["Skyrim.esm|0x00028470", "Dragonborn.esm|0x0001CDB9"]
```

Plugin names resolve through TESDataHandler. If a resolved FormID is a FormList (BGSListForm), all entries are checked automatically.

## Common Skyrim FormIDs

These are frequently useful for icon rules:

### Factions

| FormID | Faction |
|--------|---------|
| `Skyrim.esm\|0x00028470` | Whiterun Guards |
| `Skyrim.esm\|0x00029990` | JobMerchantFaction |
| `Skyrim.esm\|0x00029991` | JobThiefFaction |
| `Skyrim.esm\|0x0003B5DE` | PlayerFaction (followers, allies) |
| `Skyrim.esm\|0x0005C3A2` | KhajiitCaravanFaction |
| `Skyrim.esm\|0x0002634E` | TownRiftFaction (Riften) |
| `Skyrim.esm\|0x00028472` | CrimeFactionEastmarch (Windhelm) |
| `Skyrim.esm\|0x00028471` | CrimeFactionHaafingar (Solitude) |

### AI Packages

| FormID | Package |
|--------|---------|
| `Skyrim.esm\|0x00072946` | Follow player |
| `Skyrim.esm\|0x00072948` | Follow player (combat variant) |
| `Skyrim.esm\|0x0003558B` | DefaultSandbox |
| `Skyrim.esm\|0x0001B1E3` | DefaultEatPackage |
| `Skyrim.esm\|0x0001C3F6` | DefaultSleepPackage |

### Notable NPCs

| FormID | NPC |
|--------|-----|
| `Skyrim.esm\|0x000A2C94` | Lydia |
| `Skyrim.esm\|0x0001A6B7` | Jarl Balgruuf |

## Global Settings

Optional file at `Data/SKSE/Plugins/SIF.json`:

```json
{
  "actorOffsetZ": 20.0,
  "genericOffsetZ": 20.0,
  "markerOffsetZ": 20.0,
  "iconSpacing": 30.0,
  "scaleDepthNear": 200.0,
  "scaleDepthFar": 1000.0,
  "scaleMin": 35.0,
  "scaleMax": 100.0
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `actorOffsetZ` | 20.0 | Extra Z offset for actor anchors |
| `genericOffsetZ` | 20.0 | Extra Z offset for non-actor refs |
| `markerOffsetZ` | 20.0 | Extra Z offset for door anchors |
| `iconSpacing` | 30.0 | Horizontal gap between multiple icons |
| `scaleDepthNear` | 200.0 | Near depth clamp for scaling |
| `scaleDepthFar` | 1000.0 | Far depth clamp for scaling |
| `scaleMin` | 35.0 | Minimum icon scale % |
| `scaleMax` | 100.0 | Maximum icon scale % |

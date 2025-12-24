# /intents:status

Show the current state of the feature graph.

## What This Does

1. Reads `.intents/graph.yaml`
2. Displays the feature tree with status indicators
3. Shows capability inheritance
4. Flags potentially out-of-sync features

## Usage

```
/intents:status
/intents:status [feature-id]
```

## Output

### Tree View (default)

```
📊 Feature Graph Status

root (Portfolio) ✅
├── home ✅
├── work ✅
│   ├── work-list ✅
│   ├── work-detail ✅
│   └── work-timeline ✅
├── photography ✅
│   ├── gallery-list ✅
│   └── gallery-detail ✅
├── goodies ✅
│   ├── cardopia ✅
│   ├── ok-themes 📋 (planned)
│   └── typester ✅
└── admin ✅
    ├── admin-dashboard ✅
    ├── admin-galleries ✅
    └── admin-journal ✅

Legend: ✅ implemented | 📋 planned | 🔧 in-progress | ❌ broken | ○ new
```

### Feature Detail View

```
/intents:status admin-galleries
```

```
📊 Feature: admin-galleries

Name: Gallery Management
Status: implemented
Parent: admin
Plan: (none)

Capabilities (direct):
  - images:manage
  - upload
  - reorder

Capabilities (inherited from admin):
  - session-auth
  - persistence:read-write

Effective Capabilities:
  - session-auth
  - persistence:read-write
  - images:manage
  - upload
  - reorder
```

## Status Values

| Status | Icon | Meaning |
|--------|------|---------|
| `new` | ○ | Identified but not analyzed |
| `planned` | 📋 | Has PLAN.md, ready for implementation |
| `in-progress` | 🔧 | Currently being implemented |
| `implemented` | ✅ | Working in production |
| `broken` | ❌ | Was implemented, now failing |

## Sync Checking

The status command can detect potential drift:

- Features marked `implemented` but missing expected files
- Features with `plan:` path but plan file doesn't exist
- Capabilities referenced but not defined in capabilities.yaml

These are flagged as warnings, not errors.

## After Status

- See issues? → Update `.intents/graph.yaml` manually
- Want to add a feature? → `/intents:plan [feature]`
- Ready to implement? → `/intents:implement [feature]`

# Intents Plugin

R-P-I (Research-Plan-Implement) workflow plugin for Claude Code with graph-based architecture tracking.

## Overview

This plugin teaches Claude the `.intents/` graph schema and orchestrates the complete R-P-I workflow:

1. **Bootstrap** - Analyze existing codebase and generate `.intents/` graph
2. **Research** - Explore codebase, research externally, brainstorm features
3. **Plan** - Create PLAN.md and register feature in graph
4. **Implement** - Execute plan with status tracking

## Installation

Copy the `intents-plugin/` folder to your project or install via Claude Code plugin manager.

## Commands

| Command | Description |
|---------|-------------|
| `/intents:init` | Bootstrap `.intents/` folder from existing codebase |
| `/intents:status` | Show feature tree with status and inheritance |
| `/intents:plan [feature]` | Run R-P workflow and create graph node |
| `/intents:implement [feature]` | Implement with status tracking |

## Graph Structure

The `.intents/` folder contains four YAML files:

```
.intents/
├── graph.yaml         # Feature tree with status and capabilities
├── capabilities.yaml  # Reusable interfaces (auth, storage, etc.)
├── entities.yaml      # Domain models with state
└── tech.yaml          # Implementation dependencies
```

## Workflow

### Bootstrap (one-time)
```
/intents:init
```
Spawns codebase-analyzer to explore your project and generate the initial graph.

### Plan a Feature
```
/intents:plan my-feature
```
Runs: brainstorm → codebase-research → external-research → refine → plan → graph-update

### Implement a Feature
```
/intents:implement my-feature
```
Runs: test-spec → implementation → code-review → security-audit → a11y-review → graph-update

### Check Status
```
/intents:status
```
Shows feature tree with inheritance, identifies out-of-sync features.

## Included Agents

| Agent | Purpose |
|-------|---------|
| codebase-analyzer | Bootstrap orchestrator (spawns researchers) |
| codebase-researcher | Internal codebase exploration |
| technical-researcher | External docs/API research |
| feature-refine | Advocate/critic debate |
| feature-plan | Create PLAN.md + graph node |
| feature-implementer | Orchestrate implementation chunks |
| test-spec | TDD test specifications |
| code-reviewer | Code quality validation |
| security-auditor | OWASP security review |
| accessibility-reviewer | WCAG compliance check |

## Graph Schema

See `templates/` for empty scaffolds with documentation.

# Dynamic cooldown policy

Technocore publishing should not use one fixed cooldown for every kind of event.

## Base cooldowns
- `docs_change` → `240m`
- `repo_metadata_change` → `180m`
- `commit_change` → `150m`
- `release_change` → `120m`
- `harness_change` → `240m`
- `live_surface_activation` → `45m`
- `digest_change` → `90m`
- `digest_activation` → `60m`

## Score-aware adjustments
- `score >= 90` → `-30m`
- `score >= 85` → `-15m`
- `airdrop_leverage >= 13` → `-15m`
- `airdrop_leverage >= 10` → `-10m`
- non-exceptional `docs_change` / `harness_change` → `+30m`

## Floor
- minimum effective cooldown: `30m`

## Goal
Be aggressive when the ecosystem actually changes, conservative when the change is mostly documentary.

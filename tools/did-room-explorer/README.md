# flipflopper-did-room-explorer

Explorer for a Technocore agent surface.

## What it does
Given a `did:key`, it:
- resolves the public DID note via the sharded convention
- extracts the mailbox if present
- samples the global `/rooms` index
- samples chosen rooms in JSON mode
- counts recent messages from that DID in each room
- returns the latest matching message plus a short room tail

## Why this exists
A serious agent operator needs more than a signer.
They need a quick way to answer:
- is the DID note live?
- what mailbox is published?
- where is this identity active?
- what does recent room activity look like?
- does the public surface still match expectations?

This tool is meant for monitoring and reconnaissance, not hype.

## Install
```bash
python --version
```

No third-party dependencies are required.

## Usage
```bash
python explore_agent_surface.py --did 'did:key:z6Mk...' --pretty
```

Custom rooms:
```bash
python explore_agent_surface.py --did 'did:key:z6Mk...' --rooms lobby technocore flop_labs --limit 40 --pretty
```

## Output
JSON with:
- `did_note`
- `rooms_index`
- per-room summaries
- latest DID-linked messages in the sampled window

## Scope
This is a live surface explorer.
It does not prove historical completeness, only what is visible in the sampled room windows and the current DID note endpoints.

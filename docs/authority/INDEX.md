# Authority Artifact Index

Traceability guide linking the documentation in this folder to the generated authority data and scripts under `/authority`.

## Generated Artifacts

| Prefix | Count | Latest artifact | Location |
| --- | --- | --- | --- |
| Build-AuthorityMap | 1 | [Build-AuthorityMap.20250821_2145.ps1](../authority/Build-AuthorityMap.20250821_2145.ps1) | `/authority` |
| Build-ContractRegistry | 1 | [Build-ContractRegistry.ps1](../authority/Build-ContractRegistry.ps1) | `/authority` |
| Invoke-AuthorityDisambiguation | 1 | [Invoke-AuthorityDisambiguation.ps1](../authority/Invoke-AuthorityDisambiguation.ps1) | `/authority` |
| authority-map-20250822-2325-cf01 | 1 | [authority-map-20250822-2325-cf01.json](../authority/authority-map-20250822-2325-cf01.json) | `/authority` |
| authority-map-20250822-refactor | 1 | [authority-map-20250822-refactor.json](../authority/authority-map-20250822-refactor.json) | `/authority` |
| authority.map | 10 | [authority.map.20250822_112722.json](../authority/authority.map.20250822_112722.json) | `/authority` |
| authority.scan | 1 | [authority.scan.log.jsonl](../authority/authority.scan.log.jsonl) | `/authority` |
| disambiguation.20250821_171457 | 1 | [disambiguation.20250821_171457.json](../authority/disambiguation.20250821_171457.json) | `/authority` |
| disambiguation.20250821_171523 | 1 | [disambiguation.20250821_171523.json](../authority/disambiguation.20250821_171523.json) | `/authority` |
| disambiguation.20250821_172451 | 1 | [disambiguation.20250821_172451.json](../authority/disambiguation.20250821_172451.json) | `/authority` |
| disambiguation.20250822_080508 | 1 | [disambiguation.20250822_080508.json](../authority/disambiguation.20250822_080508.json) | `/authority` |
| disambiguation.20250822_080600 | 1 | [disambiguation.20250822_080600.json](../authority/disambiguation.20250822_080600.json) | `/authority` |
| disambiguation.20250822_081105 | 1 | [disambiguation.20250822_081105.json](../authority/disambiguation.20250822_081105.json) | `/authority` |
| disambiguation.20250822_090253 | 1 | [disambiguation.20250822_090253.json](../authority/disambiguation.20250822_090253.json) | `/authority` |
| disambiguation.20250822_090855 | 1 | [disambiguation.20250822_090855.json](../authority/disambiguation.20250822_090855.json) | `/authority` |
| disambiguation.20250822_112722 | 1 | [disambiguation.20250822_112722.json](../authority/disambiguation.20250822_112722.json) | `/authority` |
| disambiguation.post | 2 | [disambiguation.post.20250822_112722.json](../authority/disambiguation.post.20250822_112722.json) | `/authority` |
| gaps.20250821_171318 | 1 | [gaps.20250821_171318.json](../authority/gaps.20250821_171318.json) | `/authority` |
| gaps.20250821_171457 | 1 | [gaps.20250821_171457.json](../authority/gaps.20250821_171457.json) | `/authority` |
| gaps.20250821_171523 | 1 | [gaps.20250821_171523.json](../authority/gaps.20250821_171523.json) | `/authority` |
| gaps.20250821_172451 | 1 | [gaps.20250821_172451.json](../authority/gaps.20250821_172451.json) | `/authority` |
| gaps.20250822_080508 | 1 | [gaps.20250822_080508.json](../authority/gaps.20250822_080508.json) | `/authority` |
| gaps.20250822_080600 | 1 | [gaps.20250822_080600.json](../authority/gaps.20250822_080600.json) | `/authority` |
| gaps.20250822_081105 | 1 | [gaps.20250822_081105.json](../authority/gaps.20250822_081105.json) | `/authority` |
| gaps.20250822_090253 | 1 | [gaps.20250822_090253.json](../authority/gaps.20250822_090253.json) | `/authority` |
| gaps.20250822_090855 | 1 | [gaps.20250822_090855.json](../authority/gaps.20250822_090855.json) | `/authority` |
| gaps.20250822_112722 | 1 | [gaps.20250822_112722.json](../authority/gaps.20250822_112722.json) | `/authority` |
| promotion | 1 | [promotion.policy.20250822_140900.md](../authority/promotion.policy.20250822_140900.md) | `/authority` |
| registry | 1 | [registry.contracts.20250822_090752.json](../authority/registry.contracts.20250822_090752.json) | `/authority` |
| waivers | 1 | [waivers.20250822_140900.json](../authority/waivers.20250822_140900.json) | `/authority` |

## Key Scripts

- [`authority/Build-AuthorityMap.20250821_2145.ps1`](../authority/Build-AuthorityMap.20250821_2145.ps1): Builds authority map + coverage snapshots.
- [`authority/Invoke-AuthorityDisambiguation.ps1`](../authority/Invoke-AuthorityDisambiguation.ps1): Generates `disambiguation.post.*` data & `false_friends` lists.
- [`authority/Build-ContractRegistry.ps1`](../authority/Build-ContractRegistry.ps1): Maintains contract registry inputs referenced by coverage deltas.

## Conflicts & Follow-Ups

- Both `authority.map.*` and `authority-map-*` naming schemes are present; consolidate naming to avoid tooling confusion.
- `promotion.policy` and `waivers` artifacts (`../authority/promotion.policy.20250822_140900.md`, `../authority/waivers.20250822_140900.json`) should be cross-reviewed so waivers do not contradict promotion policies.
- Ensure every new artifact is captured in this table along with its producing command and timestamp.

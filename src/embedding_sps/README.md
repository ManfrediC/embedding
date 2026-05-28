# embedding_sps

Future Python package for SPSD embedding utilities.

Expected first modules:

- manifest loading from SPS review registries.
- provenance-preserving text chunking.
- local embedding/index adapters.
- retrieval evaluation helpers.

## Manifest Builder

Build the local full and 100-paper pilot manifests from the upstream SPS review
registries:

```bash
python src/embedding_sps/manifest.py
```

The command writes ignored generated outputs under `data/interim/manifest/` and
`results/manifest/` by default. It never writes to `C:\Projects\sps-review`.

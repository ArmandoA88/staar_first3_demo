# GitHub Upload Without LFS

This repo can exceed GitHub's per-file limit because some source PDFs are very large.

Use the split/restore tool:

```powershell
py scripts/split_large_files.py split
```

That command:

- finds large files above the configured threshold
- writes chunk files next to the original as `<filename>.parts/`
- records a `manifest.json` for reconstruction
- updates the managed block in `.gitignore`
- deletes the original file when `--delete-original` is enabled

To restore the original PDFs locally:

```powershell
py scripts/split_large_files.py restore
```

Useful options:

```powershell
py scripts/split_large_files.py status
py scripts/split_large_files.py split --threshold-mb 90 --chunk-mb 48
py scripts/split_large_files.py restore --force
```

The app and extracted catalogs do not need the original source PDFs to browse or print tests. The source PDFs are only needed if you want to rerun extraction.

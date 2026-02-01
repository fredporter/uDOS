## Groovebox Sample Library

Use this folder to store public-domain audio samples for the Groovebox playback/config workflows.

### Public samples
- Defined in `sample-library.json` with IDs, URLs, and metadata.
- Samples are downloaded locally (not committed) to `groovebox/library/`.

### Setup
Run the setup script to download the latest samples:

```bash
bash wizard/groovebox/setup-samples.sh
```

The script reads `sample-library.json`, fetches each file with `curl`, and writes it into `groovebox/library/<sample-id>`. The folder is gitignored so builds stay clean.

### Custom additions
Add new entries to `sample-library.json` with an `id`, `name`, and `source` URL. Re-run the setup script to download them locally.

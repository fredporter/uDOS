# REFRESH Command System - Documentation

**Version:** 1.0.0
**Phase:** v1.4.0 Phase 3.4 - Content Refresh System
**Status:** ✅ Complete

---

## Overview

The REFRESH command system provides automated quality checking, version tracking, and content migration for the uDOS knowledge bank. It ensures all guides and diagrams meet current design standards and quality requirements.

## Features

### 1. Version Tracking

Automatic semantic versioning for all content files:
- **Major Version** (X.0.0): Breaking changes or significant quality issues fixed
- **Minor Version** (0.X.0): Features added or moderate improvements
- **Patch Version** (0.0.X): Small fixes or forced refreshes

Metadata stored in hidden `.{filename}.metadata.json` files:
```json
{
  "version": "2.1.3",
  "created": "2025-11-25T10:00:00",
  "updated": "2025-11-25T14:30:00",
  "generator": "ok-assist",
  "checksum": "sha256_hash",
  "quality_score": 0.92,
  "history": [
    {"version": "2.1.2", "updated": "...", "checksum": "..."},
    {"version": "2.1.1", "updated": "...", "checksum": "..."}
  ]
}
```

### 2. Quality Checking

**Guide Quality Checks:**
- ✅ File size (warn if <1KB or >100KB)
- ✅ Structure (main heading, required sections)
- ✅ Metadata (attribution, author)
- ✅ Cross-references (internal links, external resources)
- ✅ Key sections (Description, Steps, Safety)

**Diagram Quality Checks:**
- ✅ File size targets by format:
  - ASCII: <10KB (warn if >25KB)
  - Teletext: <30KB (warn if >40KB)
  - SVG: <50KB (warn if >75KB)
- ✅ Valid format structure
- ✅ SVG-specific checks (viewBox, path count)
- ✅ Optimization opportunities

**Quality Scoring:** 0.0 to 1.0 scale
- **0.9-1.0:** Excellent - No issues
- **0.8-0.89:** Good - Minor issues only
- **0.6-0.79:** Fair - Needs improvement
- **0.0-0.59:** Poor - Significant issues

### 3. Automated Updates

**Update Logic:**
1. Check current quality score
2. Compare to minimum version requirement
3. Determine update type:
   - **Skip:** Quality ≥0.8 AND version current
   - **Patch:** Forced refresh or standards update
   - **Minor:** Quality 0.6-0.79
   - **Major:** Quality <0.6

**Version Bumping:**
- Preserves complete history
- Updates checksums
- Records timestamps
- Maintains quality scores

---

## Usage

### Command-Line Interface

```bash
# Check quality of all content (no updates)
python -m core.commands.refresh_command --check all

# Check single category
python -m core.commands.refresh_command --check water

# Refresh category (update low-quality files)
python -m core.commands.refresh_command water

# Force refresh all files in category
python -m core.commands.refresh_command --force fire

# Refresh single file
python -m core.commands.refresh_command knowledge/water/purification.md

# Force refresh with quality check
python -m core.commands.refresh_command --force --check shelter
```

### Python API

```python
from pathlib import Path
from core.commands.refresh_command import RefreshCommand, ContentVersion, QualityChecker

# Initialize command
workspace = Path("/path/to/uDOS")
refresh = RefreshCommand(workspace)

# Check single file
result = refresh.refresh_file(
    Path("knowledge/water/purification.md"),
    check_only=True
)
print(f"Quality: {result['quality_score']:.2f}")
print(f"Issues: {result['issues']}")

# Refresh category
results = refresh.refresh_category("water", force=False)
for r in results:
    print(f"{r['file']}: {r['action']} (v{r['new_version']})")

# Refresh all content
summary = refresh.refresh_all(check_only=False)
report = refresh.generate_report(summary)
print(report)

# Manual version tracking
version = ContentVersion(Path("knowledge/water/purification.md"))
print(f"Current: v{version.get_version()}")
version.bump_version("minor")  # Increment version
version.set_quality_score(0.92)  # Update quality
```

---

## Report Format

```
================================================================================
REFRESH COMMAND REPORT
================================================================================

Total Files Processed: 166
Files Updated: 23
Files Skipped: 140
Failed: 3
Average Quality Score: 0.87/1.0

MAJOR_UPDATE: 5 files
  - knowledge/water/well_digging_basics.md: Updated to v2.0.0 (quality: 0.60)
  - knowledge/fire/friction_fire_common_mistakes.md: Updated to v2.0.0 (quality: 0.55)
  ... and 3 more

MINOR_UPDATE: 18 files
  - knowledge/shelter/debris_hut_construction.md: Updated to v1.2.0 (quality: 0.75)
  - knowledge/food/foraging_safety_basics.md: Updated to v1.1.0 (quality: 0.78)
  ... and 16 more

SKIP: 140 files
  - knowledge/water/purification_methods.md: File up to date (v2.1.0, quality: 0.95)
  - knowledge/fire/fire_triangle_basics.md: File up to date (v1.8.0, quality: 0.92)
  ... and 138 more

FAILED: 3 files
  - knowledge/tools/missing_file.md: File does not exist
  ... and 2 more

================================================================================
```

---

## Quality Issues Examples

### Common Guide Issues

**Missing Sections:**
```
Issue: "Missing recommended section: Safety"
Fix: Add ## Safety section with warnings/precautions
```

**No Cross-References:**
```
Issue: "No cross-references or external links"
Fix: Add [[category/related-topic]] links or external URLs
```

**Missing Attribution:**
```
Issue: "Missing attribution/author metadata"
Fix: Add "OK Assist Generated: ✅" or "Author: Name"
```

**Small File:**
```
Issue: "File very small (0.8KB) - may be incomplete"
Fix: Expand content with more details, steps, examples
```

### Common Diagram Issues

**Oversized File:**
```
Issue: "SVG diagram too large (82.3KB, target <50KB)"
Fix: Optimize paths, reduce complexity, compress
```

**Missing Scalability:**
```
Issue: "Missing viewBox attribute (not scalable)"
Fix: Add viewBox="0 0 800 600" to <svg> tag
```

**Over-Complex:**
```
Issue: "Many paths - consider optimization"
Fix: Combine paths, use shapes instead of paths, simplify
```

---

## Integration with uDOS

### Workflow System

Add to `.uscript` files:
```
[REFRESH|--check|all] # Check quality of all content
[REFRESH|water]       # Update water category
[REFRESH|--force|$FILE] # Force refresh specific file
```

### Mission System

Add to `.mission` files:
```yaml
tasks:
  - name: "Quality Check"
    command: "REFRESH --check all"
    success_criteria: "avg_quality >= 0.8"

  - name: "Update Low Quality"
    command: "REFRESH all"
    success_criteria: "updated > 0"
```

### Automated Workflows

Schedule regular quality checks:
```bash
# Weekly quality audit
0 0 * * 0 cd /path/to/uDOS && python -m core.commands.refresh_command --check all > logs/quality_$(date +%Y%m%d).log

# Monthly forced refresh
0 0 1 * * cd /path/to/uDOS && python -m core.commands.refresh_command --force all
```

---

## Migration Tools

### Bulk Version Initialization

```python
from pathlib import Path
from core.commands.refresh_command import ContentVersion

# Initialize versions for all guides
knowledge_dir = Path("knowledge")
for guide in knowledge_dir.rglob("*.md"):
    if guide.name != "README.md":
        version = ContentVersion(guide)
        version.set_generator("ok-assist")
        version.set_quality_score(0.80)
        print(f"Initialized: {guide.name} v{version.get_version()}")
```

### Quality Improvement Workflow

```python
from core.commands.refresh_command import RefreshCommand

refresh = RefreshCommand(Path("."))

# Find all low-quality files
summary = refresh.refresh_all(check_only=True)
low_quality = [
    r for r in summary['results']
    if r.get('quality_score', 1.0) < 0.7
]

# Generate improvement list
print("Files needing improvement:")
for result in sorted(low_quality, key=lambda r: r['quality_score']):
    print(f"\n{result['file']} - Quality: {result['quality_score']:.2f}")
    print("Issues:")
    for issue in result['issues']:
        print(f"  - {issue}")
```

### Design Standards Update

```python
# Update all diagrams to new design standards
from core.commands.refresh_command import RefreshCommand

refresh = RefreshCommand(Path("."))

# Force refresh all diagrams (applies new standards)
categories = ['water', 'fire', 'shelter', 'food', 'medical',
              'navigation', 'tools', 'communication']

for category in categories:
    print(f"\nRefreshing {category} diagrams...")
    results = refresh.refresh_category(category, force=True)

    diagram_results = [r for r in results if 'diagrams' in r['file']]
    print(f"  Updated {len(diagram_results)} diagrams")
```

---

## Future Enhancements

### Planned Features (v1.5.0)

1. **Automated Content Regeneration**
   - Use OK Assist to automatically improve low-quality guides
   - Regenerate diagrams with new design standards
   - Preserve manual edits during updates

2. **Content Analytics**
   - Track quality trends over time
   - Identify frequently updated files
   - Generate quality dashboards

3. **Advanced Quality Metrics**
   - Readability scores
   - Completeness percentages
   - Cross-reference validation
   - Broken link detection

4. **Integration with OK Assist**
   - Direct regeneration from REFRESH command
   - Prompt-based improvements
   - Batch regeneration jobs

5. **Community Features**
   - Quality voting system
   - Peer review workflow
   - Collaborative improvement tracking

---

## Technical Details

### File Structure

```
knowledge/
  water/
    purification.md              # Guide file
    .purification.md.metadata.json  # Version metadata (hidden)
  diagrams/
    water/
      filter.svg                 # Diagram file
      .filter.svg.metadata.json  # Version metadata (hidden)
```

### Checksum Calculation

Uses SHA256 for content verification:
```python
import hashlib

def calculate_checksum(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
```

### Quality Score Algorithm

Weighted scoring system:
- File size: 20% (0.2 penalty if out of range)
- Structure: 30% (0.1 per missing section)
- Metadata: 10% (0.05 if missing)
- Cross-references: 10% (0.05 if none)
- Format-specific: 30% (varies by type)

---

## Best Practices

### For Content Creators

1. **Run quality checks before committing**
   ```bash
   python -m core.commands.refresh_command --check knowledge/category/new_guide.md
   ```

2. **Address all quality issues**
   - Fix issues flagged by quality checker
   - Aim for quality score ≥0.8
   - Add cross-references and metadata

3. **Use version metadata**
   - Let REFRESH manage versions automatically
   - Don't manually edit metadata files
   - Check quality after major edits

### For Maintainers

1. **Regular quality audits**
   ```bash
   # Weekly check
   python -m core.commands.refresh_command --check all > reports/quality_weekly.txt
   ```

2. **Batch updates**
   ```bash
   # Update all low-quality content
   python -m core.commands.refresh_command all
   ```

3. **Monitor quality trends**
   - Track average quality score over time
   - Identify problematic categories
   - Prioritize improvements

### For Automated Systems

1. **CI/CD Integration**
   ```yaml
   # GitHub Actions
   - name: Quality Check
     run: python -m core.commands.refresh_command --check all
     continue-on-error: true
   ```

2. **Pre-commit Hooks**
   ```bash
   # .git/hooks/pre-commit
   python -m core.commands.refresh_command --check $(git diff --name-only --cached)
   ```

3. **Scheduled Maintenance**
   ```bash
   # cron job
   0 2 * * * cd /uDOS && python -m core.commands.refresh_command all
   ```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'core.commands'"

**Solution:** Run from workspace root:
```bash
cd /path/to/uDOS
python -m core.commands.refresh_command --help
```

### "FileNotFoundError: knowledge directory not found"

**Solution:** Specify workspace path:
```bash
python -m core.commands.refresh_command --workspace /path/to/uDOS all
```

### "Quality score unexpectedly low"

**Check:**
1. File has proper structure (# heading, ## sections)
2. Attribution metadata present
3. File size reasonable (1-100KB for guides)
4. Cross-references included

### "Version not incrementing"

**Check:**
1. File content has actually changed (checksum different)
2. Using correct update mode (not `--check`)
3. Metadata file is writable

---

## Examples

See `extensions/core/ok-assist/examples/test_refresh_command.py` for comprehensive test suite demonstrating all features.

---

**Last Updated:** 2025-11-25
**Maintainer:** @fredporter
**License:** See LICENSE.txt

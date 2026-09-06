# Optional tools for user-supplied materials

Read this only for bulk ingestion, a scanned rulebook, CHM, an automatic character sheet, or a request to absorb a folder into the skill. Supported rules and workflows use the bundled references directly; ordinary users do not need a corpus index. The commands below describe optional research tooling, not the format of a user-facing citation. Local books remain outside the distributable package. The corpus is a retrieval resource; extracted text does not certify that every rule was read, resolved or implemented.

## Locate and read

When the current user asks to process their own materials, use their explicitly supplied paths or optional local configuration. Keep extraction caches outside the distributable skill. Never assume the maintainer's source collection is available or direct another user to its location.

```powershell
python -X utf8 scripts/corpus.py search "<corpus_index>" "招架" --source "江山雪" --limit 4
python -X utf8 scripts/corpus.py search "<corpus_index>" --source "战锤" --anchor "CHM:检定.htm"
python -X utf8 scripts/corpus.py search "<corpus_index>" "恢复" --source "迷踪" --chars 2400
```

Search returns a source ID, relative path, full SHA-256, anchor, bounded passage, extraction method and review state. `source_current: false` means the book moved, disappeared or changed: relocate by hash or rebuild before citing its cache as current evidence. Filter ambiguous titles by the returned source ID. Chinese substring retrieval does not depend on English word tokenization. A negative search is not evidence of absence; try synonyms, another translation and visual inspection.

PDF anchors use file page order. DOCX anchors identify the XML part and paragraph, including paragraphs in tables. XLSX anchors identify sheet and cell. CHM anchors name extracted HTML documents; a giant spell HTML document may contain many entries, so narrow by the spell name and inspect surrounding paragraphs. HTML scripts are ignored. Legacy DOC uses its Word piece table, without opening macros or embedded objects.

## Ingestion and traceability

```powershell
python -X utf8 scripts/corpus.py build "<materials>" --output "<private-index>/corpus.sqlite" --chm-root "<private-index>/chm" --ocr
```

Core readers use `pypdf` and `openpyxl`. Optional `requirements-corpus.txt` adds Chinese OCR, rendering, images and old Word support. If local configuration provides `python_executable` and `corpus_dependency_root`, use that interpreter and add the dependency directory to the process's Python import path for ingestion; ordinary cached searches need no OCR imports. Do not copy dependencies into the skill. For CHM, first extract with a local archive utility into `<chm-root>/<source-file-stem>/`; do not browse or execute its embedded pages. The ingestion run used a console copy obtained from the [7-Zip publisher's download page](https://www.7-zip.org/download.html), without installing it system-wide.

Each file is hashed and handled independently, including duplicates at different paths. The build records `extracted`, `partial` or `error`; image metadata alone and sparse PDF pages without OCR are partial. OCR confidence indicates text-recognition quality, not accuracy of a rule. Check page layout, columns, tables, superscripts, minus signs, inequalities and rounding on the original before implementing numerical rules. OCR may interleave columns even when individual characters are correct.

`--cache-dir` imports a trusted private extraction cache named `<first-16-SHA256>.jsonl`. Use it only with an inventory proving which source produced that cache. JSONL must split on ASCII newline; Unicode NEL and line separators may occur inside valid JSON strings. A rebuild invalidates passage reviews when the original file hash changes. Generated indexes and old upstream checkouts under `索引` are excluded from source ingestion and listed separately in the private coverage report.

Record specific human/agent review with:

```powershell
python -X utf8 scripts/corpus.py review "<corpus_index>" "<source-id>" "PDF:64" passage-verified "Checked recovery categories against the page; adopted in the TOC adapter."
```

Review states are `unreviewed`, `structure-reviewed`, `passage-verified`, `adopted`, `conflict`, `unreadable`. A note needs the actual scope: do not mark a whole book reviewed because its contents page was inspected. The per-file adoption matrix belongs in the private index and records references, decisions, limitations and acceptance cases.

## Turn passages into usable capability

For the user's current task, retrieve the full applicable rule and its exceptions, then record:

| Field | Required decision |
|---|---|
| Identity | System lineage, actual book version, author/translator, selected supplements |
| Trigger | Who can attempt the action and under what fictional conditions |
| Inputs | Attributes, skills, declared spends, equipment, status and environmental factors |
| Resolution | Dice, comparisons, success tiers, timing, rounding and tie rules |
| Consequences | Costs, damage, conditions, timers, cancellation and recovery |
| Persistence | Separate current/max/base values, per-turn/per-session use and pending rulings |
| Evidence | Author/publisher + title + edition + chapter/page; keep technical IDs in private research records |
| Acceptance | A normal case, a boundary case, a failure/cancellation and save/resume |

Only the selected system's budget establishes legal allocation. A genre-compatible book can suggest skill categories or scene ideas without supplying compatible arithmetic. See [corpus adapters](systems/corpus-adapters.md) and [corpus-informed preparation](corpus-preparation.md).

## Inspect automatic cards without damaging them

```powershell
python -X utf8 scripts/sheet_audit.py "<card.xlsx>" --output "<private-index>/card-audit.json"
```

This reads OOXML directly and reports formula expressions, saved values, errors, hidden sheets, data validation (including x14), protection, defined names and external links. It hashes the source before and after. It neither recalculates nor repairs a book. An empty cached result can be an intentional blank; a saved error may be an input-dependent failure. Trace dependencies before classifying its effect on a finished character.

The four ingested CoC workbooks contain saved `#REF!` at `附表!AB61`; the two blank cards also contain saved division errors at `附表!G8:L8`. Their arithmetic cannot be treated as authoritative just because a visible sheet looks complete. Compare a completed card with the source rules and an independent ledger. Preserve hidden formula sheets, list validations and source originals when creating a working copy. A missing or older matching automatic card never authorizes inventing version compatibility.

## Rights and output boundary

Rule facts and short original procedural explanations may be used with source attribution. Keep full texts, book tables, art, private module notes and real character data local. Do not replace a licensed book with a reconstructed distributable copy. The ingested files include different license terms: Daniel's Arknights 0.51 declares CC BY-NC-SA; the rules-horror booklet explicitly restricts modified redistribution; the fixer booklet states noncommercial use. Their text is not relicensed under the repository's code license. Use local retrieval and independently written adapters, without copying their chapters or setting prose.

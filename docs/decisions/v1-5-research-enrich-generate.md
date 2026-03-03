uDOS Autonomous Research & Universal Content Transformation Contract

Version: v1.2
Status: Canonical Candidate
Scope:
	•	Markdown ⇄ HTML transformation
	•	HTML ingestion & deterministic publish
	•	Autonomous research mode
	•	Multi-source ingestion (web, APIs, PDF, image, ebook, file)
	•	Data enrichment pipelines
	•	Cross-binder intelligence
	•	Project-aware tagging & output generation
	•	uDOS template-driven artifact production

Aligned with:
	•	Vault contract  
	•	Workspace filesystem & indexing  
	•	Wiki markdown spec  
	•	Spatial compatibility  
	•	World ownership model  

⸻

1. System Overview

uDOS now supports:

External Knowledge
    ↓
Ingest → Normalize → Enrich → Classify → Index
    ↓
Vault (Markdown canonical)
    ↓
Transform / Recompose
    ↓
Output (HTML / Guide / Image / PDF / Project Artifact)

The system supports both:
	•	Manual research ingestion
	•	Autonomous research mode

⸻

2. Content Transformation Core (Bidirectional)

2.1 Canonical Rule

Markdown in the vault is authoritative.

HTML, PDF, image text, API responses are ingestion sources or render targets — never canonical storage.

⸻

2.2 Reversible Transform Guarantees

Transform must support:

HTML → MD → HTML
MD → HTML → MD
PDF → MD
Image → Text → MD
API JSON → Structured MD

With:
	•	Metadata preservation
	•	Deterministic structure
	•	No loss of semantic content
	•	Stable uid

⸻

3. Multi-Source Ingestion Layer

The ingestion system must support:

Source Type	Processing Path
URL	HTML extraction
API Engine	Structured JSON ingestion
PDF	Text extraction + structure detection
Ebook (epub/mobi)	Chapter segmentation
Image	OCR + caption extraction
Local file	Type-based parsing
CSV/JSON	Table → Markdown conversion
Audio	Transcription
Video	Transcript extraction


⸻

4. Autonomous Research Mode

4.1 Definition

Autonomous research mode allows uDOS to:
	•	Identify research gaps in a project
	•	Collect new data
	•	Validate against existing vault knowledge
	•	Classify & enrich content
	•	Produce project-relevant artifacts

Without manual scraping.

⸻

4.2 Trigger Conditions

Autonomous research may trigger when:
	•	A project template specifies required research
	•	A binder has unresolved tasks
	•	A mission requires supporting evidence
	•	A topic cluster is incomplete
	•	A new keyword appears frequently in tasks

⸻

4.3 Autonomous Research Loop

Detect project need
 ↓
Generate research questions
 ↓
Query:
    - Web
    - API engines
    - Knowledge APIs
    - Internal vault
 ↓
Ingest sources
 ↓
Enrich + classify
 ↓
Score relevance to:
    - current project
    - active binders
 ↓
Produce summary + artifact


⸻

5. API Engine Research Integration

Autonomous mode may call:
	•	Academic APIs
	•	News APIs
	•	Market APIs
	•	AI model APIs
	•	Domain-specific data APIs

Rules:
	•	API responses converted to Markdown
	•	Structured JSON preserved in code blocks
	•	Source attribution required
	•	All responses assigned source_type: api

Example frontmatter addition:

source_type: api
api_engine: "research_api_v2"
query: "local LLM benchmarks"


⸻

6. Data Enrichment Pipeline

After ingestion, enrichment runs.

6.1 Enrichment Phases
	1.	Semantic summarisation
	2.	Key concept extraction
	3.	Entity recognition
	4.	Topic clustering
	5.	Duplicate detection
	6.	Cross-project matching
	7.	Relevance scoring

⸻

6.2 Cross-Project Relevance Tagging

Each ingested document must evaluate:

Which active projects?
Which binders?
Which missions?
Which tasks?

Add metadata:

related_projects:
  - udos-v1-5
related_binders:
  - research-ai
relevance_score:
  udos-v1-5: 0.91


⸻

6.3 Vault Impact Tagging

System must evaluate:
	•	Does this improve an existing document?
	•	Should it update a guide?
	•	Does it contradict stored data?
	•	Should it spawn a new task?

If yes:
	•	Generate suggestion
	•	Log proposal in 06_RUNS/
	•	Do not overwrite curated content (per vault contract  )

⸻

7. File-Type Processing

7.1 PDF Processing

Pipeline:

Extract text
 ↓
Detect headings
 ↓
Rebuild structure
 ↓
Convert to Markdown
 ↓
Attach metadata

If scanned PDF:
	•	OCR first
	•	Detect layout blocks
	•	Preserve tables as markdown tables

⸻

7.2 Image Processing

Pipeline:

Image
 ↓
OCR
 ↓
Caption extraction
 ↓
Context inference
 ↓
Structured Markdown

Attach:

source_type: image
ocr_confidence: 0.88


⸻

7.3 Ebook Processing
	•	Split by chapters
	•	Preserve structure
	•	Maintain chapter anchors
	•	Attach source reference

⸻

7.4 Structured Data

JSON / CSV → Markdown:
	•	Tables preserved
	•	JSON optionally preserved in fenced blocks
	•	Metadata auto-generated

⸻

8. Project Template Output Engine

Autonomous research must integrate with uDOS project templates.

Templates may require outputs:
	•	Article
	•	Whitepaper
	•	Guidebook
	•	Slide deck
	•	Image
	•	Dataset
	•	Strategy doc
	•	Brief
	•	Research summary

⸻

8.1 Template-Driven Output Example

Project template:

required_output: guidebook
format: markdown
target_path: 02_PROJECTS/udos-v1-5/guidebook.md

Autonomous mode:
	1.	Collect research
	2.	Cluster by topic
	3.	Generate structured guide
	4.	Insert citations
	5.	Write output file
	6.	Log generation report

⸻

8.2 Image or Media Output

If template requires:

required_output: image

System may:
	•	Use API image engine
	•	Generate diagram
	•	Generate visual summary
	•	Store in assets
	•	Reference in project doc

⸻

9. Intelligent Binder Integration

After ingestion:

System evaluates:
	•	Which binders contain related tags?
	•	Which binder chapters mention similar keywords?
	•	Which tasks reference related entities?

May:
	•	Suggest binder placement
	•	Auto-create chapter stub
	•	Propose merge into existing doc

Must never silently overwrite.

⸻

10. Research Scoring Model

Each ingested document receives:

quality_score: 0.76
novelty_score: 0.61
relevance_score:
  udos-v1-5: 0.91
  research-ai: 0.87

Scores used to:
	•	Prioritize summary generation
	•	Recommend integration
	•	Flag outdated research

⸻

11. Duplicate & Drift Detection

On new ingestion:

Compare:
	•	Content hash
	•	Semantic similarity
	•	Topic overlap
	•	Source URL

If overlap > threshold:
	•	Append change log
	•	Update version
	•	Preserve uid

⸻

12. Knowledge Drift Monitoring

Autonomous mode may:
	•	Re-check older research
	•	Detect outdated stats
	•	Flag for update
	•	Spawn task in 04_TASKS/

⸻

13. md_to_html Expansion

Publishing must:
	•	Group by topic
	•	Group by project
	•	Allow research archive pages
	•	Inject canonical source links
	•	Provide citation blocks
	•	Generate SEO-friendly URLs

Example:

/research/artificial-intelligence/local-llm-benchmarks/


⸻

14. Research Workspace Visibility

All research content must be searchable across:
	•	@vault
	•	@sandbox
	•	@shared
	•	@public

Per workspace index  

⸻

15. Security & Safety

Autonomous mode must:
	•	Respect workspace permissions
	•	Avoid private workspace leakage
	•	Avoid API key exposure
	•	Log all external calls
	•	Provide audit trail

⸻

16. System Outcomes

After implementation, uDOS can:
	•	Scrape & normalize web content
	•	Ingest PDFs, ebooks, images, APIs
	•	Autonomously research gaps
	•	Score & enrich knowledge
	•	Detect relevance to active projects
	•	Suggest integration
	•	Produce structured outputs via templates
	•	Publish deterministic HTML
	•	Maintain reversible transforms
	•	Preserve Markdown as canonical truth

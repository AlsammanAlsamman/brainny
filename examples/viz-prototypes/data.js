// Shared fabricated example dataset for the visualization prototypes
// (same data as ../demo/, never the maintainer's real ideas).
const DATA = {
  "nodes": [
    {
      "id": "idea_0001",
      "title": "Debounce search-as-you-type inputs at ~300ms",
      "summary": "Wait for a short pause in keystrokes before firing the search request.",
      "kind": "technique",
      "domain": "web-app",
      "origin": "human",
      "tags": [
        "ux"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0002",
      "title": "Never trust client-side validation alone",
      "summary": "Client-side checks are a UX convenience, not a security boundary.",
      "kind": "precaution",
      "domain": "web-app",
      "origin": "ai",
      "tags": [
        "security"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0003",
      "title": "Fixed a CORS preflight failure with an explicit OPTIONS handler",
      "summary": "The route only handled GET/POST; preflight needs its own handler.",
      "kind": "solution",
      "domain": "web-app",
      "origin": "collaborative",
      "tags": [
        "cors"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0004",
      "title": "Optimistic UI updates need a rollback path",
      "summary": "Showing success before the server confirms is fine, until the request fails and nothing reverts it.",
      "kind": "insight",
      "domain": "web-app",
      "origin": "ai",
      "tags": [
        "ux"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0005",
      "title": "ETL retry-with-backoff pattern",
      "summary": "Wrap each pipeline stage in exponential backoff with jitter.",
      "kind": "skill",
      "domain": "data-pipeline",
      "origin": "human",
      "tags": [
        "etl"
      ],
      "lastTouched": "2026-09-10T22:24:36+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": true,
      "hasSnippet": true,
      "opportunityCount": 1
    },
    {
      "id": "idea_0006",
      "title": "Idempotency keys prevent duplicate processing on retry",
      "summary": "Generate one key per logical operation, not per HTTP call.",
      "kind": "precaution",
      "domain": "data-pipeline",
      "origin": "ai",
      "tags": [
        "idempotency"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0007",
      "title": "Batch size trades latency for throughput, not for free",
      "summary": "Bigger batches improve throughput but delay the first result.",
      "kind": "insight",
      "domain": "data-pipeline",
      "origin": "collaborative",
      "tags": [
        "batching"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0008",
      "title": "Could retry-with-backoff apply to LLM API calls?",
      "summary": "Rate limits and transient 5xxs look like the ETL retry problem.",
      "kind": "seed",
      "domain": "data-pipeline",
      "origin": "ai",
      "tags": [
        "llm"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0009",
      "title": "Schema drift breaks silently without a contract check",
      "summary": "A producer changing a field type doesn't fail loudly downstream -- it just corrupts quietly.",
      "kind": "precaution",
      "domain": "data-pipeline",
      "origin": "human",
      "tags": [
        "schema"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0010",
      "title": "Manhattan-plot-style genome browser plot",
      "summary": "Chromosomes on x by cumulative position, -log10(p) on y, alternating colors, significance line.",
      "kind": "skill",
      "domain": "data-viz",
      "origin": "human",
      "tags": [
        "plotting"
      ],
      "lastTouched": "2026-09-10T22:24:37+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": true,
      "hasSnippet": true,
      "opportunityCount": 1
    },
    {
      "id": "idea_0011",
      "title": "Pick a color-blind-safe palette by default",
      "summary": "Use a palette validated for deuteranopia/protanopia as the default.",
      "kind": "technique",
      "domain": "data-viz",
      "origin": "ai",
      "tags": [
        "accessibility"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0012",
      "title": "Log scales hide small but real differences near zero",
      "summary": "A log-scale axis compresses exactly the range where small absolute changes matter most.",
      "kind": "insight",
      "domain": "data-viz",
      "origin": "collaborative",
      "tags": [
        "charts"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0013",
      "title": "Time-based splits leak information random splits hide",
      "summary": "A random split can let future information leak backward into training.",
      "kind": "insight",
      "domain": "ml",
      "origin": "collaborative",
      "tags": [
        "leakage"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0014",
      "title": "Never tune hyperparameters against the test set",
      "summary": "Repeatedly checking test performance turns it into a second validation set.",
      "kind": "precaution",
      "domain": "ml",
      "origin": "human",
      "tags": [
        "overfitting"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0015",
      "title": "Class imbalance fixed with focal loss, not just resampling",
      "summary": "Resampling alone kept overfitting the minority class; focal loss down-weighted easy majority examples instead.",
      "kind": "solution",
      "domain": "ml",
      "origin": "ai",
      "tags": [
        "imbalance"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0016",
      "title": "Could a small model pre-filter before the expensive model runs?",
      "summary": "A cheap classifier could triage obvious cases before the heavy model even runs.",
      "kind": "seed",
      "domain": "ml",
      "origin": "human",
      "tags": [
        "cost"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0017",
      "title": "Users pay more for saved time than for saved money",
      "summary": "A feature that saves an hour a week converts better than one saving comparable money.",
      "kind": "insight",
      "domain": "business",
      "origin": "human",
      "tags": [
        "pricing"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0018",
      "title": "Churn spikes right after the free-trial reminder email",
      "summary": "The reminder meant to reduce churn was itself prompting people to reconsider and leave.",
      "kind": "insight",
      "domain": "business",
      "origin": "collaborative",
      "tags": [
        "retention"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0019",
      "title": "Rotate API keys before revoking the old one, not after",
      "summary": "Revoke-then-rotate creates a window where nothing works.",
      "kind": "precaution",
      "domain": "devops",
      "origin": "collaborative",
      "tags": [
        "secrets"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0020",
      "title": "Blue-green deploys avoid downtime on schema migrations",
      "summary": "Run the new schema alongside the old one behind a flag.",
      "kind": "technique",
      "domain": "devops",
      "origin": "ai",
      "tags": [
        "deploys"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0021",
      "title": "Memory leak traced to an unbounded in-process cache",
      "summary": "A cache with no eviction policy grew until the process OOM'd under sustained load.",
      "kind": "solution",
      "domain": "devops",
      "origin": "human",
      "tags": [
        "memory"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0022",
      "title": "Health checks must not depend on the thing they're checking",
      "summary": "A health check that queries the same DB connection pool it's meant to protect can report healthy while the pool is exhausted.",
      "kind": "precaution",
      "domain": "devops",
      "origin": "ai",
      "tags": [
        "monitoring"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0023",
      "title": "A flaky test traced to unseeded random test data",
      "summary": "A fixture generating random data without a fixed seed let edge-case values occasionally slip through.",
      "kind": "solution",
      "domain": "testing",
      "origin": "human",
      "tags": [
        "flaky-tests"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0024",
      "title": "Headless-browser screenshot verification for UI changes",
      "summary": "Render, screenshot with a headless browser, and actually look at the image instead of trusting the diff.",
      "kind": "skill",
      "domain": "testing",
      "origin": "collaborative",
      "tags": [
        "verification"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": true,
      "opportunityCount": 0
    },
    {
      "id": "idea_0025",
      "title": "Mocking the database can hide a broken real migration",
      "summary": "Mocked tests passed while the actual migration silently failed against a real database.",
      "kind": "precaution",
      "domain": "testing",
      "origin": "human",
      "tags": [
        "mocks"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0026",
      "title": "SQL injection risk from string-built queries in admin tools",
      "summary": "Internal tools get the same injection risk as public ones -- trusted user is not a sanitizer.",
      "kind": "precaution",
      "domain": "security",
      "origin": "ai",
      "tags": [
        "injection"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0027",
      "title": "Fixed a session-fixation bug by rotating the session id on login",
      "summary": "The session id stayed the same across the login boundary, letting a pre-login id become valid post-login.",
      "kind": "solution",
      "domain": "security",
      "origin": "collaborative",
      "tags": [
        "sessions"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0028",
      "title": "Most security incidents start with a valid credential, not an exploit",
      "summary": "Phished or reused credentials beat zero-days as the actual common entry point.",
      "kind": "insight",
      "domain": "security",
      "origin": "human",
      "tags": [
        "credentials"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0029",
      "title": "Rate-limit by account, not just by IP",
      "summary": "IP-only limits miss distributed credential-stuffing attempts across many IPs against one account.",
      "kind": "technique",
      "domain": "security",
      "origin": "ai",
      "tags": [
        "rate-limiting"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0030",
      "title": "Virtualize long lists instead of rendering every row",
      "summary": "Only render the rows currently in the viewport, recycling DOM nodes as the user scrolls.",
      "kind": "technique",
      "domain": "frontend",
      "origin": "human",
      "tags": [
        "performance"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0031",
      "title": "A key prop tied to array index breaks reordering",
      "summary": "Reordered items keep stale local state when the key is the index instead of a stable id.",
      "kind": "precaution",
      "domain": "frontend",
      "origin": "ai",
      "tags": [
        "react"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0032",
      "title": "Fixed layout shift by reserving image dimensions upfront",
      "summary": "Images without explicit width/height caused the page to jump as they loaded.",
      "kind": "solution",
      "domain": "frontend",
      "origin": "collaborative",
      "tags": [
        "cls"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0033",
      "title": "Perceived performance matters more than raw load time",
      "summary": "A skeleton screen shown immediately beat a faster but blank-then-pop-in load in user testing.",
      "kind": "insight",
      "domain": "frontend",
      "origin": "human",
      "tags": [
        "perception"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0034",
      "title": "Use connection pooling with a sane max, not unlimited",
      "summary": "An unbounded pool just moves the bottleneck to the database instead of removing it.",
      "kind": "technique",
      "domain": "backend",
      "origin": "ai",
      "tags": [
        "db"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0035",
      "title": "N+1 queries hide behind an innocent-looking loop",
      "summary": "A loop calling one ORM method per item silently issues one query per iteration.",
      "kind": "precaution",
      "domain": "backend",
      "origin": "human",
      "tags": [
        "orm"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0036",
      "title": "Fixed a race condition with a database-level unique constraint",
      "summary": "Application-level check-then-insert wasn't atomic; the DB constraint made the race impossible instead of just unlikely.",
      "kind": "solution",
      "domain": "backend",
      "origin": "collaborative",
      "tags": [
        "concurrency"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0037",
      "title": "Could read replicas serve the N+1 pattern cheaply enough to ignore?",
      "summary": "Not a fix, but might make the problem cheap enough not to matter for read-heavy paths.",
      "kind": "seed",
      "domain": "backend",
      "origin": "ai",
      "tags": [
        "orm"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0038",
      "title": "Background app refresh drains battery if polling too aggressively",
      "summary": "A 30-second poll interval felt responsive in testing and drained batteries in the field.",
      "kind": "precaution",
      "domain": "mobile",
      "origin": "human",
      "tags": [
        "battery"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0039",
      "title": "Cache API responses on-device with a short TTL",
      "summary": "Most screens re-fetch data the user just saw seconds ago -- a short TTL cache avoids the redundant round trip.",
      "kind": "technique",
      "domain": "mobile",
      "origin": "collaborative",
      "tags": [
        "caching"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0040",
      "title": "Offline-first isn't optional once users are on mobile networks",
      "summary": "Even brief connectivity gaps produced visible errors until the app treated offline as a normal state, not an edge case.",
      "kind": "insight",
      "domain": "mobile",
      "origin": "ai",
      "tags": [
        "offline"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0041",
      "title": "Terraform state drift traced to a manual console change",
      "summary": "Someone edited a resource directly in the cloud console, and the next apply tried to revert it.",
      "kind": "solution",
      "domain": "infra",
      "origin": "human",
      "tags": [
        "terraform"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0042",
      "title": "Autoscaling on CPU alone misses memory-bound workloads",
      "summary": "A memory-bound service stayed under the CPU threshold while getting OOM-killed under load.",
      "kind": "precaution",
      "domain": "infra",
      "origin": "ai",
      "tags": [
        "autoscaling"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0043",
      "title": "Tag every cloud resource with an owner and a purpose",
      "summary": "Untagged resources are the ones nobody can safely delete six months later.",
      "kind": "technique",
      "domain": "infra",
      "origin": "collaborative",
      "tags": [
        "hygiene"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0044",
      "title": "Good docs answer why, code already answers what",
      "summary": "Comments restating what the code does go stale; the reasoning behind a non-obvious choice doesn't.",
      "kind": "insight",
      "domain": "docs",
      "origin": "human",
      "tags": [
        "writing"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0045",
      "title": "Put a runnable example at the top of every README",
      "summary": "Readers try the example before reading the explanation -- put it first, not buried after the theory.",
      "kind": "technique",
      "domain": "docs",
      "origin": "ai",
      "tags": [
        "readme"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0046",
      "title": "Most drop-off happens before the first real value moment",
      "summary": "Onboarding funnels lost more people before the first meaningful action than after it.",
      "kind": "insight",
      "domain": "onboarding",
      "origin": "collaborative",
      "tags": [
        "activation"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0047",
      "title": "Show progress, not just a spinner, for anything over 2 seconds",
      "summary": "A determinate progress indicator reduced abandonment even when the total time was unchanged.",
      "kind": "technique",
      "domain": "onboarding",
      "origin": "human",
      "tags": [
        "ux"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    },
    {
      "id": "idea_0048",
      "title": "P99 latency spike traced to GC pauses under load",
      "summary": "Average latency looked fine; the tail was dominated by stop-the-world garbage collection pauses.",
      "kind": "solution",
      "domain": "perf",
      "origin": "ai",
      "tags": [
        "gc"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0049",
      "title": "Profile before optimizing -- intuition about hot paths is often wrong",
      "summary": "The assumed bottleneck wasn't; a five-minute profile pointed at a completely different function.",
      "kind": "technique",
      "domain": "perf",
      "origin": "human",
      "tags": [
        "profiling"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 1
    },
    {
      "id": "idea_0050",
      "title": "Would a bloom filter cut the redundant lookups here?",
      "summary": "Most lookups check for existence and miss -- a bloom filter could short-circuit the common case cheaply.",
      "kind": "seed",
      "domain": "perf",
      "origin": "ai",
      "tags": [
        "data-structures"
      ],
      "lastTouched": "2026-09-10T22:24:23+00:00",
      "session": "example-build",
      "sessionTs": "2026-09-10T22:24:23+00:00",
      "hasAttachment": false,
      "hasSnippet": false,
      "opportunityCount": 0
    }
  ],
  "opportunities": [
    {
      "id": "opp_0001",
      "title": "Data pipeline reliability toolkit",
      "kind": "tool",
      "weight": 0.78,
      "summary": "Package retry-with-backoff, idempotency-key discipline, and schema-drift contract checks into one reusable reliability layer for data pipelines.",
      "ideaIds": [
        "idea_0005",
        "idea_0006",
        "idea_0009"
      ]
    },
    {
      "id": "opp_0002",
      "title": "Bioinformatics plotting library with sane defaults",
      "kind": "tool",
      "weight": 0.66,
      "summary": "A small plotting package baking in the Manhattan-plot layout and a color-blind-safe palette as defaults.",
      "ideaIds": [
        "idea_0010",
        "idea_0011",
        "idea_0012"
      ]
    },
    {
      "id": "opp_0003",
      "title": "\"Don't ship this mistake\" pre-launch checklist product",
      "kind": "business-idea",
      "weight": 0.42,
      "summary": "A short, paid pre-launch checklist (client-side-only validation, SQL injection in admin tools, test-set leakage) for small teams without a dedicated reviewer.",
      "ideaIds": [
        "idea_0002",
        "idea_0014",
        "idea_0026"
      ]
    },
    {
      "id": "opp_0004",
      "title": "Backend reliability lint rules",
      "kind": "tool",
      "weight": 0.71,
      "summary": "Static-analysis rules catching N+1 query loops, unbounded connection pools, and health checks that depend on the thing they check -- before code review has to.",
      "ideaIds": [
        "idea_0035",
        "idea_0034",
        "idea_0022"
      ]
    },
    {
      "id": "opp_0005",
      "title": "Mobile offline-resilience starter kit",
      "kind": "tool",
      "weight": 0.6,
      "summary": "A starter module combining on-device response caching, battery-aware polling, and offline-first state handling for mobile apps.",
      "ideaIds": [
        "idea_0038",
        "idea_0039",
        "idea_0040"
      ]
    },
    {
      "id": "opp_0006",
      "title": "Performance-tail dashboard product",
      "kind": "website",
      "weight": 0.55,
      "summary": "A hosted dashboard surfacing P99/GC-pause tail latency and profiler hotspots side by side, instead of the average-latency view most APM tools lead with.",
      "ideaIds": [
        "idea_0048",
        "idea_0049"
      ]
    }
  ],
  "kindColor": {
    "technique": "#3b6fd6",
    "precaution": "#c9432c",
    "solution": "#2f9e5e",
    "insight": "#8b5cd6",
    "seed": "#8a8f98",
    "skill": "#e8b23d"
  },
  "originColor": {
    "human": "#e05a9a",
    "ai": "#e8b23d",
    "collaborative": "#3bb0a8"
  },
  "unclassifiedColor": "#5c6b63"
};

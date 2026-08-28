# TrustTrack — delivery plan to the close of the build phase

**Team:** Hammad Qureshi, Muhammad Bilal Khan

## What is built

The first slice of TrustTrack is in place (~15% of the product):

- React frontend and FastAPI backend, with Postgres (SQLite for local work without Docker)
- Schema for NGOs, donors, donations, and proof uploads
- Every donation is issued a unique tracking ID at creation (`TT-XXXXXXXX`)
- NGOs can upload a proof photo against that ID, with claimed GPS, timestamp, and aid type
- Files and metadata are stored and can be looked up in the UI

Authenticity checks are **not** running yet. Uploads sit at `verification_status = pending`. That is the next slice.

## What is left, in what order, and who is doing it

| Order | Work | Owner |
| --- | --- | --- |
| 1 | **Image authenticity pipeline** — Error Level Analysis on JPEGs; perceptual hashing vs prior proofs to catch reused photos; EXIF GPS / DateTimeOriginal vs claimed delivery (missing EXIF = lower confidence, not an automatic fail) | Muhammad Bilal Khan (backend + verification) |
| 2 | **Aid-type content check** — lightweight vision-language call so the photo must match the declared aid type; failures are flagged for human review, not silently rejected | Muhammad Bilal Khan |
| 3 | **NGO trust score** — rolling pass rate and duplicate flags per organization, shown to donors | Muhammad Bilal Khan (API) with Hammad Qureshi (display) |
| 4 | **Donor Q&A** — pgvector on the same Postgres; retrieve only that donor’s verified records; LLM answers restricted to retrieved rows | Muhammad Bilal Khan |
| 5 | **End-to-end product UI** — NGO upload + flag/explain flow; donor tracking + trust score + Q&A | Hammad Qureshi |
| 6 | **Demo hardening** — seed data, public demo, README for judges | Both (Hammad leads the demo UI; Bilal leads deploy and API stability) |

**Roles in short**

- **Muhammad Bilal Khan** — backend, schema, tracking IDs, ELA / pHash / EXIF, VLM aid-type check, trust-score aggregation, RAG wiring.
- **Hammad Qureshi** — donor and NGO screens, upload and review flows, trust-score and Q&A UI, demo presentation.
- **Together** — any flagged delivery is reviewed by a person. The system supports audit; it does not auto-reject donations.

## Why this order

Tracking IDs and proof storage come first so every later check has a real donation to attach to. Image forensics next, because that is the problem TrustTrack solves: whether delivery evidence is genuine, not whether money moved on a ledger. Trust score and donor Q&A sit on top of verification history. Blockchain stays out of scope.

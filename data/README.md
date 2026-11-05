# Sample data

**Everything here is made up.** Companies, people, addresses and numbers are fictional. Never add
real invoices, receipts or personal data.

| Folder | What | Used from |
|---|---|---|
| `invoices/` | 5 business invoices: USD, EUR, GBP, INR; a discount; no due date; UK date format; GST | Module 0 |
| `receipts/` | 5 receipts: café, hardware, restaurant, groceries, fuel; tips, coupons, cash, card, Apple Pay | Module 0 |
| `golden/` | The hand-checked correct answer for each document, as JSON | Module 1 → 9 |

Each `golden/<name>.json` holds `doc_type` and the exact `fields` DocuMind should extract (the
same shape as `documind/schemas.py`). Every golden answer was checked so that line items add up
to the subtotal and subtotal + tax + tip = total.

Documents are plain text so the course can teach LLM calls without file parsing in the way.
PDFs and phone photos arrive in Module 4.

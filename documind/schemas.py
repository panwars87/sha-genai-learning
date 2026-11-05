"""The shapes DocuMind's answers must have: classification, invoice fields, receipt fields.

Concept taught: **structured output.** Instead of hoping the model writes tidy JSON, we hand
it a schema (these Pydantic models) and then *validate* whatever comes back. A missing field,
a wrong type or a malformed date fails loudly here instead of corrupting data downstream.

Fields that may be absent from a document are ``| None``. That is deliberate: a nullable field
gives the model an honest way to say "not there" instead of inventing a value (hallucination).

Added in Module 1.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

# Money is a float for simplicity; a ledger system would use Decimal.


class Classification(BaseModel):
    """What kind of document this is."""

    doc_type: Literal["invoice", "receipt", "other"]
    reason: str = Field(description="One short sentence: which clues decided it")


class LineItem(BaseModel):
    """One line on an invoice or receipt."""

    description: str
    quantity: float | None = Field(description="null if not printed")
    unit_price: float | None = Field(description="null if not printed")
    amount: float = Field(description="The line total as printed; discounts are negative")


class Invoice(BaseModel):
    """A bill from a business, usually paid later."""

    vendor: str = Field(description="Company that issued the invoice")
    invoice_no: str
    invoice_date: date
    due_date: date | None = Field(description="null if no due date is printed")
    currency: str = Field(description="ISO 4217 code, e.g. USD, EUR, GBP, INR")
    subtotal: float = Field(description="Total before tax")
    tax: float = Field(description="Total tax; 0 if none")
    total: float = Field(description="Amount payable")
    line_items: list[LineItem]


class Receipt(BaseModel):
    """Proof of a payment already made, usually at a shop or restaurant."""

    merchant: str
    date: date
    currency: str = Field(description="ISO 4217 code; infer from symbols or address if unprinted")
    subtotal: float | None = Field(description="null if not printed")
    tax: float | None = Field(description="null if not printed")
    tip: float | None = Field(description="null if no tip")
    total: float
    payment_method: Literal["card", "cash", "mobile", "other"] | None
    items: list[LineItem]


SCHEMAS: dict[str, type[Invoice] | type[Receipt]] = {"invoice": Invoice, "receipt": Receipt}

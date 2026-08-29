"""Seed optional fictional procurement data for a local portfolio demo."""

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import inspect

from app.core.config import settings
from app.database.session import SessionLocal, engine
from app.models.supplier_quote import SupplierQuote
from app.repositories.product import product_repository
from app.repositories.supplier import supplier_repository
from app.schemas.product import ProductCreate
from app.schemas.supplier import SupplierCreate
from app.schemas.supplier_quote import SupplierQuoteCreate, SupplierQuoteUpdate
from app.services.product import product_service
from app.services.supplier import supplier_service
from app.services.supplier_quote import supplier_quote_service


SUPPLIERS = (
    {
        "name": "Northstar Industrial Supply",
        "code": "DEMO-NORTHSTAR",
        "email": "quotes@northstar-industrial.example",
        "phone": "+1-555-0101",
        "country": "United States",
        "website": "https://northstar-industrial.example",
        "reliability_score": 94,
        "delivery_score": 90,
    },
    {
        "name": "Cedar Bridge Trading",
        "code": "DEMO-CEDAR",
        "email": "procurement@cedar-bridge.example",
        "phone": "+961-1-555-102",
        "country": "Lebanon",
        "website": "https://cedar-bridge.example",
        "reliability_score": 88,
        "delivery_score": 96,
    },
    {
        "name": "Alpine Materials Group",
        "code": "DEMO-ALPINE",
        "email": "sales@alpine-materials.example",
        "phone": "+41-44-555-0103",
        "country": "Switzerland",
        "website": "https://alpine-materials.example",
        "reliability_score": 82,
        "delivery_score": 84,
    },
    {
        "name": "Meridian Office Systems",
        "code": "DEMO-MERIDIAN",
        "email": "bids@meridian-office.example",
        "phone": "+44-20-5550-1040",
        "country": "United Kingdom",
        "website": "https://meridian-office.example",
        "reliability_score": 97,
        "delivery_score": 76,
    },
    {
        "name": "Harborline Wholesale",
        "code": "DEMO-HARBORLINE",
        "email": "quotes@harborline-wholesale.example",
        "phone": "+1-555-0105",
        "country": "Canada",
        "website": "https://harborline-wholesale.example",
        "reliability_score": 74,
        "delivery_score": 88,
    },
)


PRODUCTS = (
    {
        "name": "Industrial Safety Gloves",
        "sku": "DEMO-SAFETY-GLOVE",
        "description": "Cut-resistant work gloves for warehouse operations.",
        "category": "Safety",
        "unit": "pair",
    },
    {
        "name": "A4 Recycled Copy Paper",
        "sku": "DEMO-A4-PAPER",
        "description": "Eighty-gram recycled office paper, 500 sheets.",
        "category": "Office Supplies",
        "unit": "ream",
    },
    {
        "name": "Stainless Steel Fasteners M8",
        "sku": "DEMO-FASTENER-M8",
        "description": "Corrosion-resistant M8 bolts with matching nuts.",
        "category": "Industrial Components",
        "unit": "box",
    },
    {
        "name": "LED Warehouse High-Bay Light",
        "sku": "DEMO-LED-HIGHBAY",
        "description": "Energy-efficient 150W warehouse lighting fixture.",
        "category": "Facilities",
        "unit": "unit",
    },
    {
        "name": "Food-Grade Cleaning Concentrate",
        "sku": "DEMO-CLEANER-FG",
        "description": "Concentrated cleaner for food-handling environments.",
        "category": "Cleaning",
        "unit": "liter",
    },
    {
        "name": "USB-C Docking Station",
        "sku": "DEMO-USB-C-DOCK",
        "description": "Dual-display USB-C workstation docking station.",
        "category": "IT Equipment",
        "unit": "unit",
    },
    {
        "name": "Corrugated Shipping Carton",
        "sku": "DEMO-CARTON-L",
        "description": "Double-wall large shipping cartons, bundle of 20.",
        "category": "Packaging",
        "unit": "bundle",
    },
    {
        "name": "Thermal Shipping Label Roll",
        "sku": "DEMO-LABEL-THERMAL",
        "description": "Direct thermal 100 x 150 mm shipping labels.",
        "category": "Packaging",
        "unit": "roll",
    },
)


# Supplier code, product SKU, unit price, currency, quantity, note, active.
QUOTES = (
    ("DEMO-NORTHSTAR", "DEMO-SAFETY-GLOVE", 5.60, "USD", 1000, "Strong supplier performance at a mid-range price.", True),
    ("DEMO-CEDAR", "DEMO-SAFETY-GLOVE", 5.25, "USD", 1000, "Competitive price with excellent delivery performance.", True),
    ("DEMO-ALPINE", "DEMO-SAFETY-GLOVE", 5.80, "USD", 1000, "Higher-priced alternative for comparison.", True),
    ("DEMO-HARBORLINE", "DEMO-SAFETY-GLOVE", 5.10, "USD", 1000, "Lowest active USD price with lower reliability.", True),
    ("DEMO-MERIDIAN", "DEMO-SAFETY-GLOVE", 4.65, "USD", 1000, "Expired offer retained to demonstrate inactive-quote exclusion.", False),
    ("DEMO-ALPINE", "DEMO-SAFETY-GLOVE", 4.85, "EUR", 1000, "Independent EUR offer.", True),
    ("DEMO-CEDAR", "DEMO-SAFETY-GLOVE", 4.95, "EUR", 1000, "Second EUR offer for currency-isolated analysis.", True),
    ("DEMO-NORTHSTAR", "DEMO-A4-PAPER", 6.80, "USD", 400, "Reliable supply option.", True),
    ("DEMO-CEDAR", "DEMO-A4-PAPER", 6.35, "USD", 400, "Balanced price and delivery.", True),
    ("DEMO-MERIDIAN", "DEMO-A4-PAPER", 6.10, "USD", 400, "Lowest price from an office specialist.", True),
    ("DEMO-HARBORLINE", "DEMO-A4-PAPER", 6.50, "USD", 400, "Alternative paper quote.", True),
    ("DEMO-NORTHSTAR", "DEMO-FASTENER-M8", 28.50, "USD", 120, "Premium reliability option.", True),
    ("DEMO-CEDAR", "DEMO-FASTENER-M8", 27.90, "USD", 120, "Strong overall value.", True),
    ("DEMO-ALPINE", "DEMO-FASTENER-M8", 26.80, "USD", 120, "Lowest fastener price.", True),
    ("DEMO-HARBORLINE", "DEMO-FASTENER-M8", 29.00, "USD", 120, "Higher-price comparison quote.", True),
    ("DEMO-NORTHSTAR", "DEMO-LED-HIGHBAY", 84.00, "USD", 60, "High-reliability facilities supplier.", True),
    ("DEMO-CEDAR", "DEMO-LED-HIGHBAY", 82.00, "USD", 60, "Competitive delivery-led offer.", True),
    ("DEMO-ALPINE", "DEMO-LED-HIGHBAY", 79.00, "USD", 60, "Lower-priced lighting offer.", True),
    ("DEMO-HARBORLINE", "DEMO-LED-HIGHBAY", 77.00, "USD", 60, "Cheapest active lighting quote.", True),
    ("DEMO-NORTHSTAR", "DEMO-CLEANER-FG", 12.40, "EUR", 250, "High-reliability cleaning supply.", True),
    ("DEMO-CEDAR", "DEMO-CLEANER-FG", 11.60, "EUR", 250, "Excellent delivery and competitive price.", True),
    ("DEMO-ALPINE", "DEMO-CLEANER-FG", 11.20, "EUR", 250, "Lowest cleaning concentrate price.", True),
    ("DEMO-NORTHSTAR", "DEMO-USB-C-DOCK", 129.00, "USD", 45, "Reliable IT equipment offer.", True),
    ("DEMO-CEDAR", "DEMO-USB-C-DOCK", 122.00, "USD", 45, "Balanced docking-station quote.", True),
    ("DEMO-MERIDIAN", "DEMO-USB-C-DOCK", 118.00, "USD", 45, "Office specialist with strong reliability.", True),
    ("DEMO-HARBORLINE", "DEMO-USB-C-DOCK", 115.00, "USD", 45, "Lowest docking-station price.", True),
    ("DEMO-NORTHSTAR", "DEMO-CARTON-L", 24.50, "USD", 200, "Reliable packaging supply.", True),
    ("DEMO-CEDAR", "DEMO-CARTON-L", 23.80, "USD", 200, "Strong delivery and competitive price.", True),
    ("DEMO-ALPINE", "DEMO-CARTON-L", 25.10, "USD", 200, "Higher-priced packaging alternative.", True),
    ("DEMO-HARBORLINE", "DEMO-CARTON-L", 22.90, "USD", 200, "Lowest carton price.", True),
    ("DEMO-NORTHSTAR", "DEMO-LABEL-THERMAL", 18.40, "USD", 300, "High-reliability label supply.", True),
    ("DEMO-MERIDIAN", "DEMO-LABEL-THERMAL", 17.90, "USD", 300, "Competitive office-systems quote.", True),
    ("DEMO-HARBORLINE", "DEMO-LABEL-THERMAL", 16.80, "USD", 300, "Lowest thermal-label price.", True),
)


QUOTE_DATE = datetime(2026, 8, 15, tzinfo=UTC)
VALID_UNTIL = datetime(2026, 10, 31, tzinfo=UTC)


def _validate_target_database() -> None:
    if "supplier_intelligence_test" in settings.database_url.lower():
        raise SystemExit("Refusing to seed the pytest database.")

    required_tables = {"suppliers", "products", "supplier_quotes"}
    existing_tables = set(inspect(engine).get_table_names())

    if not required_tables.issubset(existing_tables):
        raise SystemExit(
            "Database schema is not ready. Run 'alembic upgrade head' first."
        )


def seed_demo_data() -> dict[str, int]:
    _validate_target_database()
    db = SessionLocal()
    counts = {
        "suppliers_created": 0,
        "suppliers_existing": 0,
        "products_created": 0,
        "products_existing": 0,
        "quotes_created": 0,
        "quotes_existing": 0,
    }

    try:
        suppliers = {}
        for data in SUPPLIERS:
            supplier = supplier_repository.get_by_code(db, data["code"])
            if supplier:
                counts["suppliers_existing"] += 1
            else:
                supplier = supplier_service.create_supplier(
                    db,
                    SupplierCreate(**data),
                )
                counts["suppliers_created"] += 1
            suppliers[data["code"]] = supplier

        products = {}
        for data in PRODUCTS:
            product = product_repository.get_by_sku(db, data["sku"])
            if product:
                counts["products_existing"] += 1
            else:
                product = product_service.create_product(
                    db,
                    ProductCreate(**data),
                )
                counts["products_created"] += 1
            products[data["sku"]] = product

        for (
            supplier_code,
            product_sku,
            unit_price,
            currency,
            quantity,
            note,
            is_active,
        ) in QUOTES:
            supplier = suppliers[supplier_code]
            product = products[product_sku]
            existing_quote = (
                db.query(SupplierQuote)
                .filter(
                    SupplierQuote.supplier_id == supplier.id,
                    SupplierQuote.product_id == product.id,
                    SupplierQuote.currency == currency,
                )
                .first()
            )

            if existing_quote:
                counts["quotes_existing"] += 1
                continue

            quote = supplier_quote_service.create_quote(
                db,
                SupplierQuoteCreate(
                    supplier_id=supplier.id,
                    product_id=product.id,
                    unit_price=unit_price,
                    currency=currency,
                    quantity=quantity,
                    quote_date=QUOTE_DATE,
                    valid_until=VALID_UNTIL,
                    notes=f"Portfolio demo data: {note}",
                ),
            )

            if not is_active:
                supplier_quote_service.update_quote(
                    db,
                    quote.id,
                    SupplierQuoteUpdate(is_active=False),
                )

            counts["quotes_created"] += 1

        return counts
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    counts = seed_demo_data()

    print("Demo data is ready.")
    print(
        "Suppliers: "
        f"{counts['suppliers_created']} created, "
        f"{counts['suppliers_existing']} already present."
    )
    print(
        "Products: "
        f"{counts['products_created']} created, "
        f"{counts['products_existing']} already present."
    )
    print(
        "Quotes: "
        f"{counts['quotes_created']} created, "
        f"{counts['quotes_existing']} already present."
    )


if __name__ == "__main__":
    main()

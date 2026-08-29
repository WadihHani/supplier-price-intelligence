# Portfolio Demo Guide

Target length: 2-4 minutes. Use only fictional data and keep credentials out of the recording.

## Local Demo Setup

Apply migrations and add the optional dataset:

~~~powershell
alembic upgrade head
python scripts/seed_demo_data.py
~~~

The seeder creates five fictional suppliers, eight products, and 33 quotes. Industrial Safety Gloves provides the strongest walkthrough: four active USD suppliers, an inactive lower-priced USD quote that analysis excludes, and two independent EUR offers. Other products demonstrate visible savings and cases where performance scores can change the preferred supplier.

Create a user separately; the password is entered through a hidden prompt and is not stored in documentation or shell arguments:

~~~powershell
python scripts/create_dev_user.py demo@example.com
~~~

A normal user can access every screen in this walkthrough. Administrator privileges are needed only for API delete operations. The project deliberately has no default administrator credential or public admin-promotion endpoint, so destructive operations should be omitted from the portfolio demo unless an administrator has been provisioned separately in a controlled local environment.

## Walkthrough

1. **Login** — Show that the dashboard is authenticated. Mention bcrypt password storage, expiring JWTs, and the absence of hardcoded credentials.
2. **Dashboard** — Point out the live totals for products, suppliers, quotes, and active quotes. Explain that every value comes from the FastAPI API.
3. **Suppliers** — Show supplier identity, status, reliability, and delivery inputs. Explain that missing performance values are handled neutrally during scoring.
4. **Products** — Show product and SKU management, then choose **Analyze** for a prepared product.
5. **Quotes** — Show supplier, product, unit price, currency, quantity, validity, and active status. Note that inactive quotes are excluded from advanced analysis.
6. **Price Comparison** — On Procurement Intelligence, show rank 1 for the lowest price in each currency. Emphasize that currencies are never mixed.
7. **Procurement Analysis** — Show lowest, highest, average, and potential savings. Briefly explain the business question: what could be saved by choosing the cheapest instead of the most expensive active quote?
8. **Supplier Ranking** — Compare price, reliability, delivery, activity, and final score. Explain the exact 50/20/15/15 weighting and why the highest score becomes the deterministic recommendation.
9. **AI Explanation** — Show the concise explanation. State that the AI receives structured facts after scoring and cannot override the chosen supplier; a deterministic fallback keeps the endpoint useful when AI is unavailable.
10. **Logout** — Sign out and show the return to the login page. Mention that the browser session token is removed.

## Suggested Screenshots

Store only reviewed, non-sensitive captures in docs/screenshots/:

- login.png — login form without credentials
- dashboard.png — overview cards
- products.png — product list and Analyze link
- suppliers.png — supplier performance fields
- quotes.png — multi-supplier quote table
- procurement-intelligence.png — price comparison and procurement analysis
- supplier-ranking.png — weighted supplier ranking table
- ai-recommendation.png — deterministic recommendation and explanation

For the root README, use the dashboard, quotes, procurement intelligence, supplier ranking, and AI recommendation images. Keep login, products, and suppliers available for the detailed demo guide or project gallery.

Crop browser chrome if it contains personal information. Never capture passwords, bearer tokens, .env values, Swagger authorization headers, or provider keys.

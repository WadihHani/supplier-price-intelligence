# Portfolio Demo Guide

Target length: 2-4 minutes. Prepare a local database with at least one product, two active supplier quotes in the same currency, and optionally another quote in a second currency. Do not use real company or personal data.

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
- procurement-intelligence.png — comparison, analysis, and scoring
- ai-recommendation.png — deterministic recommendation and explanation

Crop browser chrome if it contains personal information. Never capture passwords, bearer tokens, .env values, Swagger authorization headers, or provider keys.

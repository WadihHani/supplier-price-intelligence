import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { Empty, ErrorState, formatNumber, Loading } from "../components/State";
import type {
  PriceComparisonResponse,
  ProcurementAnalysisResponse,
  ProcurementRecommendationResponse,
  Product,
  SupplierScoringResponse,
} from "../types/api";

interface IntelligenceBundle {
  comparison?: PriceComparisonResponse;
  analysis?: ProcurementAnalysisResponse;
  scoring?: SupplierScoringResponse;
  recommendation?: ProcurementRecommendationResponse;
  errors: string[];
}

export function IntelligencePage() {
  const [params, setParams] = useSearchParams();
  const [products, setProducts] = useState<Product[]>([]);
  const [data, setData] = useState<IntelligenceBundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const productId = params.get("product");

  useEffect(() => {
    api<Product[]>("/api/v1/products")
      .then(setProducts)
      .catch((requestError: Error) => setError(requestError.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!productId) {
      setData(null);
      return;
    }

    setLoading(true);
    setError("");
    const requests = [
      api<PriceComparisonResponse>(`/api/v1/products/${productId}/price-comparison`),
      api<ProcurementAnalysisResponse>(`/api/v1/products/${productId}/procurement-analysis`),
      api<SupplierScoringResponse>(`/api/v1/products/${productId}/supplier-ranking`),
      api<ProcurementRecommendationResponse>(`/api/v1/products/${productId}/ai-recommendation`),
    ] as const;

    Promise.allSettled(requests)
      .then(([comparison, analysis, scoring, recommendation]) => {
        const failures = [comparison, analysis, scoring, recommendation]
          .filter((result) => result.status === "rejected")
          .map((result) =>
            result.status === "rejected" && result.reason instanceof Error
              ? result.reason.message
              : "An intelligence section could not be loaded.",
          );
        setData({
          comparison: comparison.status === "fulfilled" ? comparison.value : undefined,
          analysis: analysis.status === "fulfilled" ? analysis.value : undefined,
          scoring: scoring.status === "fulfilled" ? scoring.value : undefined,
          recommendation: recommendation.status === "fulfilled" ? recommendation.value : undefined,
          errors: [...new Set(failures)],
        });
      })
      .finally(() => setLoading(false));
  }, [productId]);

  if (loading && !products.length) return <Loading />;

  return <>
    <section className="panel">
      <h2>Procurement Intelligence</h2>
      <label>Select a product
        <select value={productId ?? ""} onChange={(event) => setParams(event.target.value ? { product: event.target.value } : {})}>
          <option value="">Choose a product</option>
          {products.map((product) => <option value={product.id} key={product.id}>{product.name} · {product.sku}</option>)}
        </select>
      </label>
    </section>
    {error && <ErrorState message={error} />}
    {loading && productId && <Loading label="Loading deterministic procurement intelligence…" />}
    {!loading && productId && data && <IntelligenceData data={data} />}
    {!loading && !productId && <Empty message={products.length ? "Select a product to view procurement intelligence." : "No products are available for analysis."} />}
  </>;
}

function IntelligenceData({ data }: { data: IntelligenceBundle }) {
  return <div className="intelligence">
    {data.errors.map((message) => <ErrorState key={message} message={message} />)}
    <section className="panel">
      <h2>Price Comparison</h2>
      {data.comparison?.quotes.length ? <div className="table-wrap"><table><thead><tr><th>Supplier</th><th>Price</th><th>Currency</th><th>Quantity</th><th>Rank</th></tr></thead><tbody>{data.comparison.quotes.map((quote) => <tr key={quote.quote_id}><td>{quote.supplier_name ?? `Supplier #${quote.supplier_id}`}</td><td>{formatNumber(quote.unit_price)}</td><td>{quote.currency}</td><td>{quote.quantity}</td><td>{quote.rank}</td></tr>)}</tbody></table></div> : <Empty message="No price comparison is available." />}
    </section>
    <section className="panel">
      <h2>Procurement Analysis</h2>
      <div className="currency-grid">{data.analysis?.currency_analyses.map((item) => <article key={item.currency} className="currency-card"><h3>{item.currency}</h3><dl><dt>Lowest price</dt><dd>{formatNumber(item.lowest_price)}</dd><dt>Highest price</dt><dd>{formatNumber(item.highest_price)}</dd><dt>Average price</dt><dd>{formatNumber(item.average_price)}</dd><dt>Potential savings</dt><dd>{formatNumber(item.potential_savings)} ({formatNumber(item.savings_percentage)}%)</dd></dl></article>)}</div>
      {!data.analysis?.currency_analyses.length && <Empty message="No procurement analysis is available for this product." />}
    </section>
    <section className="panel">
      <h2>Supplier Ranking</h2>
      {data.scoring?.currency_rankings.map((group) => <div key={group.currency} className="currency-section"><h3>{group.currency} · Recommended: {group.recommendation.supplier_name}</h3><div className="table-wrap"><table><thead><tr><th>Rank</th><th>Supplier</th><th>Price</th><th>Price Score</th><th>Reliability</th><th>Delivery</th><th>Activity</th><th>Final Score</th></tr></thead><tbody>{group.ranked_suppliers.map((supplier) => <tr className={supplier.rank === 1 ? "recommended" : ""} key={supplier.quote_id}><td>{supplier.rank}</td><td>{supplier.supplier_name}</td><td>{formatNumber(supplier.unit_price)}</td><td>{formatNumber(supplier.price_score)}</td><td>{formatNumber(supplier.reliability_score)}</td><td>{formatNumber(supplier.delivery_score)}</td><td>{formatNumber(supplier.activity_score)}</td><td><strong>{formatNumber(supplier.final_score)}</strong></td></tr>)}</tbody></table></div></div>)}
      {!data.scoring?.currency_rankings.length && <Empty message="No supplier ranking is available for this product." />}
    </section>
    <section className="panel">
      <h2>AI Explanation</h2>
      {data.recommendation?.recommendations.map((item) => <article className="recommendation" key={item.currency}><p className="eyebrow">{item.currency} · DETERMINISTIC RECOMMENDATION</p><h3>{item.supplier_name} <span>{formatNumber(item.final_score)} score</span></h3><p>Unit price: {formatNumber(item.unit_price)} {item.currency}</p><p>{item.explanation}</p></article>)}
      {!data.recommendation?.recommendations.length && <Empty message="No AI explanation is available for this product." />}
    </section>
  </div>;
}

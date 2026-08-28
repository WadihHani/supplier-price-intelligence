export function Loading({ label = "Loading data…" }: { label?: string }) { return <div className="state loading" role="status">{label}</div>; }
export function Empty({ message }: { message: string }) { return <div className="state">{message}</div>; }
export function ErrorState({ message }: { message: string }) { return <div className="state error" role="alert">{message}</div>; }
export const formatDate = (value?: string | null) => value ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value)) : "—";
export const formatNumber = (value: number) => new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value);

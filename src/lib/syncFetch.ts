import { PageConfig, RowData } from "../types";

export async function fetchFreshPageData(pageName: string): Promise<{
  name: string;
  config: PageConfig;
  rows: RowData[];
} | null> {
  try {
    const res = await fetch(`/api/pages/${encodeURIComponent(pageName)}`, {
      cache: "no-store",
    });
    if (!res.ok) {
      return null;
    }
    const data = await res.json();
    if (!data || data.error || !data.config || !Array.isArray(data.rows)) {
      return null;
    }
    return {
      name: data.name,
      config: data.config,
      rows: data.rows,
    };
  } catch (err) {
    console.error("Failed to fetch fresh page data:", err);
    return null;
  }
}

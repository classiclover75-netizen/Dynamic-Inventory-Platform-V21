import { v4 as uuidv4 } from "uuid";
import { PageConfig } from "../types";

export function isTrackerPage(config: PageConfig | null | undefined): boolean {
  return !!(config?.linkedSourcePage && typeof config.linkedSourcePage === 'string' && config.linkedSourcePage.trim() !== '');
}

interface ResolveOptions {
  allowCrossPageSharedIds: boolean;
  externalIdSet: Set<string>;
}

export function resolveRowIds(rows: any[], options: ResolveOptions): any[] {
  const { allowCrossPageSharedIds, externalIdSet } = options;
  const payloadIds = new Set<string>();
  
  const resolved = rows.map((row) => {
    const newRow = { ...row };
    const originalId = String(newRow.id);
    const hasValidId = newRow.id && originalId !== 'undefined' && originalId !== 'null' && originalId.trim() !== '';
    
    let needsNewId = !hasValidId;
    
    if (hasValidId) {
      if (payloadIds.has(originalId)) {
        needsNewId = true; // Duplicate within the SAME payload
      } else if (!allowCrossPageSharedIds && externalIdSet.has(originalId)) {
        needsNewId = true; // Duplicate across pages and not allowed
      }
    }
    
    if (needsNewId) {
      newRow.id = uuidv4();
    }
    
    payloadIds.add(String(newRow.id));
    return newRow;
  });
  
  // Safety Verification Check: assert no intra-payload duplicates
  const finalIds = new Set<string>();
  for (const r of resolved) {
    if (finalIds.has(String(r.id))) {
      throw new Error(`Safety Violation: duplicate ID ${r.id} generated or preserved in payload.`);
    }
    finalIds.add(String(r.id));
  }
  
  return resolved;
}

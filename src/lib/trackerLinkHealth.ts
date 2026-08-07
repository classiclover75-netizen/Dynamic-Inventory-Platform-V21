import { PageConfig, RowData } from "../types";

export type TrackerLinkStatus = 'healthy' | 'out_of_sync' | 'broken' | 'not_a_tracker';

export interface TrackerLinkHealth {
  status: TrackerLinkStatus;
  sourcePageName: string | null;
  sourcePageExists: boolean;
  sourceRowCount: number;
  trackerRowCount: number;
  matchedRowCount: number;
  missingInTrackerCount: number;
  ghostRowCount: number;
  issues: string[];
}

export function checkTrackerLinkHealth(
  pageName: string,
  pageConfigs: Record<string, PageConfig | undefined>,
  pageRows: Record<string, RowData[] | undefined>
): TrackerLinkHealth {
  const result: TrackerLinkHealth = {
    status: 'not_a_tracker',
    sourcePageName: null,
    sourcePageExists: false,
    sourceRowCount: 0,
    trackerRowCount: 0,
    matchedRowCount: 0,
    missingInTrackerCount: 0,
    ghostRowCount: 0,
    issues: [],
  };

  try {
    const config = pageConfigs?.[pageName];
    if (!config) return result;

    const isTrackerPage = !!config.isTrackerPage; // actually we check if it has linkedSourcePage based on instructions, but let's see. Wait, types.ts says isTrackerPage. Or linkedSourcePage.
    // "1. If the page config is missing, or isTrackerPage is not true AND linkedSourcePage is empty or undefined, return status not_a_tracker with all counts 0 and empty issues."
    
    // Note: Actually, in this codebase, some trackers might not have isTrackerPage strictly set if it relies on linkedSourcePage. Let's check config.isTrackerPage. Wait, the instructions say:
    // "1. If the page config is missing, or isTrackerPage is not true AND linkedSourcePage is empty or undefined, return status not_a_tracker with all counts 0 and empty issues."
    
    // Let's implement literally.
    const hasLinkedSourcePage = typeof config.linkedSourcePage === 'string' && config.linkedSourcePage.trim() !== '';
    const isTrackerFlag = !!config.isTrackerPage || hasLinkedSourcePage; // Usually it's either. Actually, instruction says "isTrackerPage is not true AND linkedSourcePage is empty or undefined".

    if (!config.isTrackerPage && !hasLinkedSourcePage) {
      return result;
    }

    // "2. If isTrackerPage is true but linkedSourcePage is missing, not a string, or empty/whitespace-only, return status broken with issue: This tracker has no linked source page."
    if (config.isTrackerPage && !hasLinkedSourcePage) {
      result.status = 'broken';
      result.issues.push("This tracker has no linked source page.");
      return result;
    }

    const sourcePageName = config.linkedSourcePage?.trim() || "";
    result.sourcePageName = sourcePageName;

    // "3. If linkedSourcePage is set but pageConfigs does not contain that page, return status broken with sourcePageExists false and an issue naming the missing page."
    const sourceConfig = pageConfigs[sourcePageName];
    if (!sourceConfig) {
      result.status = 'broken';
      result.sourcePageExists = false;
      result.issues.push(`Source page "${sourcePageName}" could not be found.`);
      return result;
    }

    result.sourcePageExists = true;

    // "4. If linkedSourcePage points at the tracker itself, return status broken with issue: Tracker is linked to itself."
    if (sourcePageName === pageName) {
      result.status = 'broken';
      result.issues.push("Tracker is linked to itself.");
      return result;
    }

    // "5. If the source page exists but that source page's own config also has linkedSourcePage set (meaning the source is itself a tracker), return status broken with issue: Source page is itself a tracker, which creates an invalid link chain."
    if (typeof sourceConfig.linkedSourcePage === 'string' && sourceConfig.linkedSourcePage.trim() !== '') {
      result.status = 'broken';
      result.issues.push("Source page is itself a tracker, which creates an invalid link chain.");
      return result;
    }

    // "6. If the source page is valid, compute row-level drift. Build a Set of String(row.id) from source rows and from tracker rows. Use Set and Map lookups only. The algorithm must be O(n) with no nested loops, because pages can hold thousands of rows."
    
    const sourceRowsArray = pageRows?.[sourcePageName] || [];
    const trackerRowsArray = pageRows?.[pageName] || [];

    const sourceIds = new Set<string>();
    for (const row of sourceRowsArray) {
      if (row && typeof row === 'object' && row.id != null && String(row.id).trim() !== '') {
        sourceIds.add(String(row.id));
      }
    }

    const trackerIds = new Set<string>();
    for (const row of trackerRowsArray) {
      if (row && typeof row === 'object' && row.id != null && String(row.id).trim() !== '') {
        trackerIds.add(String(row.id));
      }
    }

    result.sourceRowCount = sourceIds.size;
    result.trackerRowCount = trackerIds.size;

    let matched = 0;
    let ghost = 0;

    for (const tid of trackerIds) {
      if (sourceIds.has(tid)) {
        matched++;
      } else {
        ghost++;
      }
    }

    let missing = 0;
    for (const sid of sourceIds) {
      if (!trackerIds.has(sid)) {
        missing++;
      }
    }

    result.matchedRowCount = matched;
    result.ghostRowCount = ghost;
    result.missingInTrackerCount = missing;

    if (ghost === 0 && missing === 0) {
      result.status = 'healthy';
    } else {
      result.status = 'out_of_sync';
      if (missing > 0) result.issues.push(`${missing} rows in source are missing from tracker.`);
      if (ghost > 0) result.issues.push(`${ghost} tracker rows do not exist in source.`);
    }

    return result;
  } catch (error: any) {
    result.status = 'broken';
    result.issues = [error?.message || "An unexpected error occurred during health check."];
    return result;
  }
}

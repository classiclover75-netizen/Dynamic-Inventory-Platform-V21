import React, { useState } from 'react';
import { TrackerLinkHealth } from '../lib/trackerLinkHealth';
import { CheckCircle2 } from 'lucide-react';

export interface TrackerLinkStatusPillProps {
  health?: TrackerLinkHealth;
}

export function TrackerLinkStatusPill({ health }: TrackerLinkStatusPillProps) {
  const [isHovered, setIsHovered] = useState(false);

  if (!health || health.status !== 'healthy') {
    return null;
  }

  return (
    <span 
      className="relative inline-flex"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsHovered(true)}
      onBlur={() => setIsHovered(false)}
      tabIndex={0}
    >
      <span className="inline-flex items-center gap-1 rounded-full border border-green-200 bg-green-50 px-2 py-0.5 text-[11px] font-bold text-green-800 whitespace-nowrap cursor-default">
        <CheckCircle2 size={12} className="text-green-600 shrink-0" />
        {health.matchedRowCount ?? 0} in sync
      </span>
      {isHovered && (
        <div className="absolute right-0 top-full mt-1 z-30 w-max max-w-[260px] rounded-md border border-gray-300 bg-white px-2.5 py-2 text-[11px] leading-relaxed text-gray-700 shadow-lg pointer-events-none">
          <div>Linked to <strong>{health.sourcePageName || 'Unknown'}</strong></div>
          <div>Source rows: {health.sourceRowCount ?? 0}</div>
          <div>Tracker rows: {health.trackerRowCount ?? 0}</div>
          <div>Matched: {health.matchedRowCount ?? 0}</div>
        </div>
      )}
    </span>
  );
}

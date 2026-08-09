export function computeAutoFitWidth(handleEl: HTMLElement, colKey: string): number | null {
  try {
    if (colKey === 'sr') return null;
    if (!handleEl || !document.body.contains(handleEl)) return null;

    const thEl = handleEl.closest('th');
    if (!thEl) return null;

    const tableEl = thEl.closest('table');
    if (!tableEl) return null;

    const cellsToMeasure: HTMLElement[] = [thEl];
    const tds = tableEl.querySelectorAll(`td[data-col-key="${colKey}"]`);
    tds.forEach(td => cellsToMeasure.push(td as HTMLElement));

    if (cellsToMeasure.length === 0) return null;

    let maxWidth = -1;

    for (const cell of cellsToMeasure) {
      const target = (cell.firstElementChild as HTMLElement) || cell;

      const prevWhiteSpace = target.style.whiteSpace;
      const prevWidth = target.style.width;
      const prevMaxWidth = target.style.maxWidth;
      const prevMinWidth = target.style.minWidth;
      const prevOverflow = target.style.overflow;

      try {
        target.style.whiteSpace = 'nowrap';
        target.style.width = 'max-content';
        target.style.maxWidth = 'none';
        target.style.minWidth = '0';
        target.style.overflow = 'visible';

        const offsetWidth = target.offsetWidth;
        if (offsetWidth > maxWidth) {
          maxWidth = offsetWidth;
        }
      } finally {
        target.style.whiteSpace = prevWhiteSpace;
        target.style.width = prevWidth;
        target.style.maxWidth = prevMaxWidth;
        target.style.minWidth = prevMinWidth;
        target.style.overflow = prevOverflow;
      }
    }

    if (maxWidth <= 0 || Number.isNaN(maxWidth)) return null;

    let finalWidth = Math.round(maxWidth + 24);
    if (finalWidth < 60) finalWidth = 60;
    if (finalWidth > 600) finalWidth = 600;

    return finalWidth;
  } catch (err) {
    return null;
  }
}

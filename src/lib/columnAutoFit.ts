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
    let styleEl: HTMLStyleElement | null = null;

    try {
      for (const cell of cellsToMeasure) {
        cell.setAttribute('data-autofit-target', '1');
      }

      const existingStyle = document.getElementById('autofit-measure-style');
      if (existingStyle) {
        existingStyle.remove();
      }

      styleEl = document.createElement('style');
      styleEl.id = 'autofit-measure-style';
      styleEl.textContent = `
        [data-autofit-target="1"] { overflow: visible !important; }
        [data-autofit-target="1"] *:not(img):not(svg):not(canvas):not(video) { width: auto !important; max-width: none !important; min-width: 0 !important; white-space: nowrap !important; flex-shrink: 0 !important; text-overflow: clip !important; }
        [data-autofit-target="1"] > * { width: max-content !important; }
      `;
      document.head.appendChild(styleEl);

      for (const cell of cellsToMeasure) {
        const firstChild = cell.firstElementChild as HTMLElement;
        const width = firstChild ? firstChild.offsetWidth : cell.scrollWidth;
        if (width > maxWidth) {
          maxWidth = width;
        }
      }
    } finally {
      if (styleEl && styleEl.parentNode) {
        styleEl.parentNode.removeChild(styleEl);
      }
      for (const cell of cellsToMeasure) {
        cell.removeAttribute('data-autofit-target');
      }
    }

    if (maxWidth <= 0 || !Number.isFinite(maxWidth)) return null;

    let finalWidth = Math.round(maxWidth + 24);
    if (finalWidth < 60) finalWidth = 60;
    if (finalWidth > 600) finalWidth = 600;

    return finalWidth;
  } catch (err) {
    return null;
  }
}

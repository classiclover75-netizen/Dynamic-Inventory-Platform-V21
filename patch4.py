import sys

with open('src/components/ImagePreviewModal.tsx', 'r') as f:
    content = f.read()

target1 = """    if (!reference) {
      setActualSize({ loading: false, size: null, error: false });
      return;
    }

    setActualSize({ loading: true, size: null, error: false });

    fetch(`/api/local-image-size?filename=${encodeURIComponent(reference)}`)"""

replacement1 = """    if (!reference) {
      setActualSize({ loading: false, size: null, error: false });
      setImageUsage(null);
      return;
    }

    const isExternalUrl = reference.startsWith('http://') || reference.startsWith('https://');

    if (!isExternalUrl) {
      setImageUsage({ loading: true, count: 0, rows: [], error: false });
      fetch(`/api/image-usage?filename=${encodeURIComponent(reference)}`)
        .then(res => {
          if (!res.ok) throw new Error('Failed');
          return res.json();
        })
        .then(data => {
          const currentRawVal = row[imageColKey];
          let currentRef = '';
          if (typeof currentRawVal === 'object' && currentRawVal !== null && typeof currentRawVal.data === 'string') {
            currentRef = currentRawVal.data;
          } else if (typeof currentRawVal === 'string') {
            currentRef = currentRawVal;
          }
          if (currentRef !== reference) return;
          setImageUsage({ loading: false, count: data.count, rows: data.rows || [], error: false });
        })
        .catch(err => {
          console.error("Failed to fetch image usage:", err);
          setImageUsage({ loading: false, count: 0, rows: [], error: true });
        });
    } else {
      setImageUsage(null);
    }

    setActualSize({ loading: true, size: null, error: false });

    fetch(`/api/local-image-size?filename=${encodeURIComponent(reference)}`)"""

target2 = """              )}

              <div className="flex gap-2">
                <Button variant="green" onClick={handleApplyReplace}>Apply</Button>"""

replacement2 = """              )}

              {renderUsageWarning('replace')}
              <div className="flex gap-2">
                <Button variant="green" onClick={handleApplyReplace}>Apply</Button>"""

if target1 in content:
    content = content.replace(target1, replacement1)
    print("Replaced 1.")
else:
    print("Target 1 not found.")

if target2 in content:
    content = content.replace(target2, replacement2)
    print("Replaced 2.")
else:
    print("Target 2 not found.")

with open('src/components/ImagePreviewModal.tsx', 'w') as f:
    f.write(content)


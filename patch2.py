import sys

with open('src/components/ImagePreviewModal.tsx', 'r') as f:
    content = f.read()

target = """    if (!reference) {
      setActualSize({ loading: false, size: null, error: false });
      return;
    }
    setActualSize({ loading: true, size: null, error: false });
    fetch(`/api/local-image-size?filename=${encodeURIComponent(reference)}`)"""

replacement = """    if (!reference) {
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

if target in content:
    content = content.replace(target, replacement)
    with open('src/components/ImagePreviewModal.tsx', 'w') as f:
        f.write(content)
    print("Replaced successfully.")
else:
    print("Target not found.")


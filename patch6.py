import sys

with open('src/components/ImagePreviewModal.tsx', 'r') as f:
    content = f.read()

target = "{r.pageName} — row {r.rowNumber}"
replacement = "{r.pageName} - row {r.rowNumber}"

if target in content:
    content = content.replace(target, replacement)
    print("Replaced.")
else:
    print("Target not found.")

with open('src/components/ImagePreviewModal.tsx', 'w') as f:
    f.write(content)


import sys

with open('src/components/ImagePreviewModal.tsx', 'r') as f:
    content = f.read()

target2 = """              )}
              <div className="flex gap-2">
                <Button variant="green" onClick={handleApplyReplace}>Apply</Button>"""

replacement2 = """              )}
              {renderUsageWarning('replace')}
              <div className="flex gap-2">
                <Button variant="green" onClick={handleApplyReplace}>Apply</Button>"""

if target2 in content:
    content = content.replace(target2, replacement2)
    print("Replaced 2.")
else:
    print("Target 2 not found.")

with open('src/components/ImagePreviewModal.tsx', 'w') as f:
    f.write(content)


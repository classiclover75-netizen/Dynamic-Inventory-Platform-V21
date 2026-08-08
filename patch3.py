import sys

with open('src/components/ImagePreviewModal.tsx', 'r') as f:
    content = f.read()

target1 = """              <div className="flex flex-col gap-2 w-full bg-red-50 p-3 rounded-md border border-red-200">
                <div className="text-xs font-bold text-red-700">Are you sure you want to remove this image?</div>
                <div className="flex gap-2">"""

replacement1 = """              <div className="flex flex-col gap-2 w-full bg-red-50 p-3 rounded-md border border-red-200">
                {renderUsageWarning('delete')}
                <div className="flex gap-2">"""

target2 = """                </div>
              )}
              <div className="flex gap-2">
                <Button variant="green" onClick={handleApplyReplace}>Apply</Button>"""

replacement2 = """                </div>
              )}
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


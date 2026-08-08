import sys

with open('src/components/ImagePreviewModal.tsx', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "fetch(`/api/local-image-size" in line:
        print(f"Match found at line {i+1}:")
        for j in range(max(0, i-5), min(len(lines), i+5)):
            print(f"{j+1}: {repr(lines[j])}")


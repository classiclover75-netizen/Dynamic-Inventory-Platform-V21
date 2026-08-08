import sys

with open('src/App.tsx', 'r') as f:
    content = f.read()

target1 = """          onConfirm: () => {
            setConfirmationModal({ isOpen: false, title: '', message: '', onConfirm: () => {} });
            triggerExtraStep(currentStep + 1);
          }"""
rep1 = """          onConfirm: () => { setTimeout(() => triggerExtraStep(currentStep + 1), 0); }"""

target2 = """          onConfirm: () => {
            setConfirmationModal({ isOpen: false, title: '', message: '', onConfirm: () => {} });
            triggerExtraStep(1);
          }"""
rep2 = """          onConfirm: () => { setTimeout(() => triggerExtraStep(1), 0); }"""

target3 = """        onConfirm: () => {
          setConfirmationModal({ isOpen: false, title: '', message: '', onConfirm: () => {} });
          triggerExtraStep(1);
        }"""
rep3 = """        onConfirm: () => { setTimeout(() => triggerExtraStep(1), 0); }"""

content = content.replace(target1, rep1)
content = content.replace(target2, rep2)
content = content.replace(target3, rep3)

with open('src/App.tsx', 'w') as f:
    f.write(content)
print("done")

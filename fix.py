import sys

with open('server.ts', 'r') as f:
    content = f.read()

# We need to remove the block from "      await PageRow.updateMany({ pageName: name }, { pageName: newName });" down to the next "});"
# wait, actually the duplicate starts right after the first `  }
#});` of the rename block.

start_str = """  }
});
      await PageRow.updateMany({ pageName: name }, { pageName: newName });"""

end_str = """    res.status(500).json({ error: err.message || 'Failed to rename page' });
  }
});"""

start_idx = content.find(start_str)
end_idx = content.find(end_str, start_idx) + len(end_str)

if start_idx != -1 and end_idx != -1:
    # remove the junk
    # Actually wait, the `  }\n});` at `start_idx` is the END of the rename function. We should KEEP that, and remove everything after it until `end_idx`.
    junk_start = start_idx + len("  }\n});\n")
    content = content[:junk_start] + content[end_idx+1:]
    with open('server.ts', 'w') as f:
        f.write(content)
    print("Fixed junk")
else:
    print("Junk not found")

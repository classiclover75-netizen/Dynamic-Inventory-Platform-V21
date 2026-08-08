import sys

with open('server.ts', 'r') as f:
    content = f.read()

target = """    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message || 'Failed to create page' });
  }
});

app.put('/api/pages/:name(*)/rename', async (req, res) => {"""

replacement = """    res.json({ success: true });
  } catch (err: any) {
    if (err.code === 11000) {
      return res.status(409).json({ error: 'A page with that name already exists.' });
    }
    res.status(500).json({ error: err.message || 'Failed to create page' });
  }
});

app.put('/api/pages/:name(*)/rename', async (req, res) => {"""

if target in content:
    content = content.replace(target, replacement)
    with open('server.ts', 'w') as f:
        f.write(content)
    print("Replaced create")
else:
    print("Create target not found")

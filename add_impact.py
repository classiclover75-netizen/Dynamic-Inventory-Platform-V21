import sys

with open('server.ts', 'r') as f:
    content = f.read()

target = "app.delete('/api/pages/:name(*)', async (req, res) => {"

new_endpoint = """app.get('/api/pages/delete-impact', async (req, res) => {
  try {
    const name = typeof req.query.name === 'string' ? req.query.name : '';
    if (!name) return res.status(400).json({ error: 'Missing name' });

    if (isUsingMongoDB) {
      const pageExists = await Page.findOne({ name }).lean();
      if (!pageExists) {
        return res.status(404).json({ error: 'Page not found' });
      }
      
      const pageRows = await getSortedPageRows({ pageName: name });
      const rowCount = pageRows.length;
      
      const linkedPages = await Page.find({ "config.linkedSourcePage": name }).lean();
      const linkedNames = linkedPages.map((p: any) => p.name);
      
      let linkedRowCount = 0;
      for (const pName of linkedNames) {
        const pRows = await getSortedPageRows({ pageName: pName });
        linkedRowCount += pRows.length;
      }
      
      return res.json({
        ok: true,
        pageName: name,
        rowCount,
        linkedPages: linkedNames,
        linkedRowCount
      });
    } else {
      const db = await getLocalDB();
      const page = db.pages.find((p: any) => p.name === name);
      if (!page) {
        return res.status(404).json({ error: 'Page not found' });
      }
      
      const rowCount = (page.rows || []).length;
      
      const linkedPages = db.pages.filter((p: any) => p.config && p.config.linkedSourcePage === name);
      const linkedNames = linkedPages.map((p: any) => p.name);
      
      let linkedRowCount = 0;
      for (const p of linkedPages) {
        linkedRowCount += (p.rows || []).length;
      }
      
      return res.json({
        ok: true,
        pageName: name,
        rowCount,
        linkedPages: linkedNames,
        linkedRowCount
      });
    }
  } catch (err: any) {
    res.status(500).json({ error: err.message || 'Failed to check delete impact' });
  }
});

"""

if target in content:
    content = content.replace(target, new_endpoint + target)
    with open('server.ts', 'w') as f:
        f.write(content)
    print("Added delete-impact")
else:
    print("Target not found for delete-impact")

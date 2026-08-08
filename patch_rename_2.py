import sys

with open('current_rename.ts', 'r') as f:
    content = f.read()
    
# check where rename is
start_idx = content.find("app.put('/api/pages/:name(*)/rename'")
end_idx = content.find("});", start_idx) + 3

target = content[start_idx:end_idx]

replacement = """app.put('/api/pages/:name(*)/rename', async (req, res) => {
  try {
    const { name } = req.params;
    const { newName } = req.body;

    if (!newName || typeof newName !== 'string' || !newName.trim()) {
      return res.status(400).json({ error: 'Invalid new name' });
    }
    const trimmedNewName = newName.trim();

    if (trimmedNewName === name) {
      return res.json({ success: true });
    }

    if (isUsingMongoDB) {
      const existingPage = await Page.findOne({ name });
      if (!existingPage) {
        return res.status(404).json({ error: 'Page not found' });
      }
      const duplicatePage = await Page.findOne({ name: trimmedNewName });
      if (duplicatePage) {
        return res.status(409).json({ error: 'A page with that name already exists.' });
      }

      let session = null;
      if (transactionsSupported !== false) {
        try {
          session = await mongoose.startSession();
          session.startTransaction();
        } catch (e) {
          transactionsSupported = false;
          session = null;
        }
      }

      try {
        const opts = session ? { session } : {};
        await Page.findOneAndUpdate({ name }, { name: trimmedNewName }, opts);
        await PageRow.updateMany({ pageName: name }, { pageName: trimmedNewName }, opts);
        
        const linkedPages = await Page.find({ "config.linkedSourcePage": name }, null, opts);
        for (const p of linkedPages) {
          const newConfig = { ...(p.config || {}) };
          newConfig.linkedSourcePage = trimmedNewName;
          await Page.findByIdAndUpdate(p._id, { config: newConfig }, opts);
        }

        const searchLinkedPages = await Page.find({ "config.secondarySearchPage": name }, null, opts);
        for (const p of searchLinkedPages) {
          const newConfig = { ...(p.config || {}) };
          newConfig.secondarySearchPage = trimmedNewName;
          await Page.findByIdAndUpdate(p._id, { config: newConfig }, opts);
        }

        if (session) {
          await session.commitTransaction();
          transactionsSupported = true;
        }
      } catch (txnErr: any) {
        if (session) {
          await session.abortTransaction().catch(() => {});
        }
        
        const errMsg = (txnErr.message || '').toLowerCase();
        const isUnsupported = errMsg.includes('replica set') || errMsg.includes('transaction') || errMsg.includes('not supported') || txnErr.code === 20 || txnErr.code === 263 || txnErr.name === 'IllegalOperation';
        
        if (session && isUnsupported) {
          console.warn("Transaction not supported on write, falling back to non-transactional bulk write:", txnErr.message);
          transactionsSupported = false;
          await Page.findOneAndUpdate({ name }, { name: trimmedNewName });
          await PageRow.updateMany({ pageName: name }, { pageName: trimmedNewName });
          
          const linkedPages = await Page.find({ "config.linkedSourcePage": name });
          for (const p of linkedPages) {
            const newConfig = { ...(p.config || {}) };
            newConfig.linkedSourcePage = trimmedNewName;
            await Page.findByIdAndUpdate(p._id, { config: newConfig });
          }

          const searchLinkedPages = await Page.find({ "config.secondarySearchPage": name });
          for (const p of searchLinkedPages) {
            const newConfig = { ...(p.config || {}) };
            newConfig.secondarySearchPage = trimmedNewName;
            await Page.findByIdAndUpdate(p._id, { config: newConfig });
          }
        } else {
          throw txnErr;
        }
      } finally {
        if (session) {
          session.endSession();
        }
      }

      await triggerLocalBackup();
    } else {
      const db = await getLocalDB();
      const page = db.pages.find((p: any) => p.name === name);
      if (!page) {
        return res.status(404).json({ error: 'Page not found' });
      }
      if (db.pages.some((p: any) => p.name === trimmedNewName)) {
        return res.status(409).json({ error: 'A page with that name already exists.' });
      }

      page.name = trimmedNewName;
      
      db.pages.forEach((p: any) => {
        if (p.config && p.config.linkedSourcePage === name) {
          p.config.linkedSourcePage = trimmedNewName;
        }
        if (p.config && p.config.secondarySearchPage === name) {
          p.config.secondarySearchPage = trimmedNewName;
        }
      });
      
      await saveLocalDB(db);
    }

    res.json({ success: true });
  } catch (err: any) {
    if (err.code === 11000) {
      return res.status(409).json({ error: 'A page with that name already exists.' });
    }
    res.status(500).json({ error: err.message || 'Failed to rename page' });
  }
});"""

with open('server.ts', 'r') as f:
    full_content = f.read()

if target in full_content:
    full_content = full_content.replace(target, replacement)
    with open('server.ts', 'w') as f:
        f.write(full_content)
    print("Replaced rename")
else:
    print("Rename target not found")

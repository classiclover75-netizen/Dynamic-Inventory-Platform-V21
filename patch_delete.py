import sys

with open('server.ts', 'r') as f:
    content = f.read()

target = """app.delete('/api/pages/:name(*)', async (req, res) => {
  try {
    const { name } = req.params;
    let deletedRows: any[] = [];
    if (isUsingMongoDB) {
      const pageRows = await getSortedPageRows({ pageName: name });
      deletedRows = pageRows.map((r: any) => r.data);
      await Page.findOneAndDelete({ name });
      await PageRow.deleteMany({ pageName: name });
      
      const linkedPages = await Page.find({ "config.linkedSourcePage": name });
      const linkedNames = linkedPages.map((p: any) => p.name);
      const allDeletedNames = [name, ...linkedNames];
      
      for (const p of linkedPages) {
        const linkedPageRows = await getSortedPageRows({ pageName: p.name });
        deletedRows.push(...linkedPageRows.map((r: any) => r.data));
        await Page.findOneAndDelete({ name: p.name });
        await PageRow.deleteMany({ pageName: p.name });
      }
      
      const searchLinkedPages = await Page.find({ "config.secondarySearchPage": { $in: allDeletedNames } });
      for (const p of searchLinkedPages) {
        const newConfig = { ...(p.config || {}) };
        delete newConfig.secondarySearchPage;
        await Page.findByIdAndUpdate(p._id, { config: newConfig });
      }
      
      await triggerLocalBackup();
    } else {
      const db = await getLocalDB();
      const page = db.pages.find((p: any) => p.name === name);
      if (page) {
        deletedRows = page.rows || [];
        db.pages = db.pages.filter((p: any) => p.name !== name);
      }
      
      const linkedPageNames: string[] = [];
      db.pages = db.pages.filter((p: any) => {
        if (p.config && p.config.linkedSourcePage === name) {
          linkedPageNames.push(p.name);
          if (p.rows) deletedRows.push(...p.rows);
          return false;
        }
        return true;
      });
      
      const allDeletedNames = [name, ...linkedPageNames];
      db.pages.forEach((p: any) => {
        if (p.config && p.config.secondarySearchPage && allDeletedNames.includes(p.config.secondarySearchPage)) {
          delete p.config.secondarySearchPage;
        }
      });
      
      await saveLocalDB(db);
    }
    await cleanupOrphanImages(deletedRows, [], false, name);
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message || 'Failed to delete page' });
  }
});"""

replacement = """app.delete('/api/pages/:name(*)', async (req, res) => {
  try {
    const { name } = req.params;
    let deletedRows: any[] = [];
    if (isUsingMongoDB) {
      const pageExists = await Page.findOne({ name });
      if (!pageExists) {
        return res.status(404).json({ error: 'Page not found' });
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
        const pageRows = await getSortedPageRows({ pageName: name });
        deletedRows = pageRows.map((r: any) => r.data);
        await Page.findOneAndDelete({ name }, opts);
        await PageRow.deleteMany({ pageName: name }, opts);
        
        const linkedPages = await Page.find({ "config.linkedSourcePage": name }, null, opts);
        const linkedNames = linkedPages.map((p: any) => p.name);
        const allDeletedNames = [name, ...linkedNames];
        
        for (const p of linkedPages) {
          const linkedPageRows = await getSortedPageRows({ pageName: p.name });
          deletedRows.push(...linkedPageRows.map((r: any) => r.data));
          await Page.findOneAndDelete({ name: p.name }, opts);
          await PageRow.deleteMany({ pageName: p.name }, opts);
        }
        
        const searchLinkedPages = await Page.find({ "config.secondarySearchPage": { $in: allDeletedNames } }, null, opts);
        for (const p of searchLinkedPages) {
          const newConfig = { ...(p.config || {}) };
          delete newConfig.secondarySearchPage;
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
          const pageRows = await getSortedPageRows({ pageName: name });
          deletedRows = pageRows.map((r: any) => r.data);
          await Page.findOneAndDelete({ name });
          await PageRow.deleteMany({ pageName: name });
          
          const linkedPages = await Page.find({ "config.linkedSourcePage": name });
          const linkedNames = linkedPages.map((p: any) => p.name);
          const allDeletedNames = [name, ...linkedNames];
          
          for (const p of linkedPages) {
            const linkedPageRows = await getSortedPageRows({ pageName: p.name });
            deletedRows.push(...linkedPageRows.map((r: any) => r.data));
            await Page.findOneAndDelete({ name: p.name });
            await PageRow.deleteMany({ pageName: p.name });
          }
          
          const searchLinkedPages = await Page.find({ "config.secondarySearchPage": { $in: allDeletedNames } });
          for (const p of searchLinkedPages) {
            const newConfig = { ...(p.config || {}) };
            delete newConfig.secondarySearchPage;
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
      
      deletedRows = page.rows || [];
      db.pages = db.pages.filter((p: any) => p.name !== name);
      
      const linkedPageNames: string[] = [];
      db.pages = db.pages.filter((p: any) => {
        if (p.config && p.config.linkedSourcePage === name) {
          linkedPageNames.push(p.name);
          if (p.rows) deletedRows.push(...p.rows);
          return false;
        }
        return true;
      });
      
      const allDeletedNames = [name, ...linkedPageNames];
      db.pages.forEach((p: any) => {
        if (p.config && p.config.secondarySearchPage && allDeletedNames.includes(p.config.secondarySearchPage)) {
          delete p.config.secondarySearchPage;
        }
      });
      
      await saveLocalDB(db);
    }
    await cleanupOrphanImages(deletedRows, [], false, name);
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message || 'Failed to delete page' });
  }
});"""

if target in content:
    content = content.replace(target, replacement)
    with open('server.ts', 'w') as f:
        f.write(content)
    print("Replaced delete")
else:
    print("Delete target not found")

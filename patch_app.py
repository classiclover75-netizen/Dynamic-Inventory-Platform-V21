import sys

with open('src/App.tsx', 'r') as f:
    content = f.read()

target = """  const handleDeletePage = async () => {
    const pageToDelete = state.activePage;
    try {
      await deletePageSafe(pageToDelete);

      setState((prev) => {
        const linkedTrackers = Object.entries(prev.pageConfigs)
          .filter(([name, config]: [string, any]) => config.linkedSourcePage === pageToDelete)
          .map(([name]) => name);

        const newPages = prev.pages.filter((p) => p !== pageToDelete && !linkedTrackers.includes(p));

        // Safety Verification Check: Deep clone to guarantee immutability
        // ensures other pages like 'Main Page' have zero risk of shared reference mutation
        const newConfigs = JSON.parse(JSON.stringify(prev.pageConfigs));
        const newRows = JSON.parse(JSON.stringify(prev.pageRows));

        // Strictly target and remove ONLY the selected page's data and its linked trackers
        delete newConfigs[pageToDelete];
        delete newRows[pageToDelete];
        
        linkedTrackers.forEach(trackerName => {
          delete newConfigs[trackerName];
          delete newRows[trackerName];
        });

        const deletedNames = [pageToDelete, ...linkedTrackers];
        const syncedConfigs = cleanDeletedPageRefs(newConfigs, deletedNames);

        return {
          ...prev,
          pages: newPages,
          activePage: newPages.length > 0 ? newPages[0] : "",
          pageConfigs: syncedConfigs,
          pageRows: newRows,
        };
      });
      closeAllModals();
      toast(`Page "${pageToDelete}" deleted`);
    } catch (err: any) {
      console.error(err);
      toast(err.message || "Failed to delete page from database");
    }
  };"""

replacement = """  const handleDeletePage = async () => {
    const pageToDelete = state.activePage;
    
    const performDeletion = async () => {
      try {
        await deletePageSafe(pageToDelete);

        setState((prev) => {
          const linkedTrackers = Object.entries(prev.pageConfigs)
            .filter(([name, config]: [string, any]) => config.linkedSourcePage === pageToDelete)
            .map(([name]) => name);

          const newPages = prev.pages.filter((p) => p !== pageToDelete && !linkedTrackers.includes(p));

          // Safety Verification Check: Deep clone to guarantee immutability
          // ensures other pages like 'Main Page' have zero risk of shared reference mutation
          const newConfigs = JSON.parse(JSON.stringify(prev.pageConfigs));
          const newRows = JSON.parse(JSON.stringify(prev.pageRows));

          // Strictly target and remove ONLY the selected page's data and its linked trackers
          delete newConfigs[pageToDelete];
          delete newRows[pageToDelete];
          
          linkedTrackers.forEach(trackerName => {
            delete newConfigs[trackerName];
            delete newRows[trackerName];
          });

          const deletedNames = [pageToDelete, ...linkedTrackers];
          const syncedConfigs = cleanDeletedPageRefs(newConfigs, deletedNames);

          return {
            ...prev,
            pages: newPages,
            activePage: newPages.length > 0 ? newPages[0] : "",
            pageConfigs: syncedConfigs,
            pageRows: newRows,
          };
        });
        closeAllModals();
        toast(`Page "${pageToDelete}" deleted`);
      } catch (err: any) {
        console.error(err);
        toast(err.message || "Failed to delete page from database");
      }
    };

    try {
      const res = await fetch(`/api/pages/delete-impact?name=${encodeURIComponent(pageToDelete)}`);
      if (!res.ok) throw new Error('Impact check failed');
      const data = await res.json();
      if (data.linkedPages && data.linkedPages.length > 0) {
        setConfirmationModal({
          isOpen: true,
          title: 'Confirm Deletion',
          message: `Deleting this page will also permanently delete the linked tracker pages: ${data.linkedPages.join(', ')}. A total of ${data.linkedRowCount + data.rowCount} rows will be removed across all of them. This action cannot be undone.`,
          onConfirm: () => {
            setConfirmationModal({ isOpen: false, title: '', message: '', onConfirm: () => {} });
            performDeletion();
          }
        });
        return;
      }
    } catch (e) {
      console.error('Failed to fetch delete impact', e);
    }
    
    performDeletion();
  };"""

if target in content:
    content = content.replace(target, replacement)
    with open('src/App.tsx', 'w') as f:
        f.write(content)
    print("Replaced app")
else:
    print("App target not found")


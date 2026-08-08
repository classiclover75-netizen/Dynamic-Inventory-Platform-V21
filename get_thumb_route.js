const fs = require('fs');
const content = fs.readFileSync('server.ts', 'utf8');
const lines = content.split('\n');
const start = lines.findIndex(l => l.includes("app.get('/uploads/thumb/:filename'"));
console.log(lines.slice(start - 2, start + 30).join('\n'));

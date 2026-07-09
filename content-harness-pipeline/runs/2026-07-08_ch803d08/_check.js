const fs = require('fs');
const d = __dirname + '/output';
const html = fs.readFileSync(d + '/index.html', 'utf8');
const refs = [...html.matchAll(/assets[/]([A-Za-z0-9_]+\.png)/g)].map(m => m[1]);
const uniq = [...new Set(refs)];
const have = fs.readdirSync(d + '/assets');
console.log('referenced:', uniq.length);
console.log('missing:', JSON.stringify(uniq.filter(f => !have.includes(f))));
const s = html.indexOf('<' + 'script>');
const e = html.indexOf('</' + 'script>');
const js = html.slice(s + 8, e);
try { new Function(js); console.log('JS syntax: OK'); }
catch (err) { console.log('JS ERROR:', err.message); }
console.log('unused:', JSON.stringify(have.filter(f => f.endsWith('.png') && !uniq.includes(f))));
// check qa scenes
const scenes = [...html.matchAll(/data-qa-scene="([^"]+)"/g)].map(m => m[1]);
console.log('qa-scenes:', JSON.stringify(scenes));

// QR (ink on white) for the live demo URL, using the qrcode-generator already in web/node_modules.
import qrcode from '../../web/node_modules/qrcode-generator/qrcode.js'
const url = process.argv[2], q = qrcode(0, 'M'); q.addData(url); q.make()
const n = q.getModuleCount(), m = 4; let d = ''
for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (q.isDark(r, c)) d += `M${c + m} ${r + m}h1v1h-1z`
console.log(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${n + 2 * m} ${n + 2 * m}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#fff"/><path d="${d}" fill="#071A1C"/></svg>`)

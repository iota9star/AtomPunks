import fs from 'fs';

function toBase64Url(hex) {
    const base64 = btoa(hex.match(/\w{2}/g).map(function (a) {
        return String.fromCharCode(parseInt(a, 16));
    }).join(""));
    return "data:image/png;base64," + base64;
}

const punks = JSON.parse(fs.readFileSync('10kpunk_data.json', 'utf8'));
const atomicals = JSON.parse(fs.readFileSync('atompunk_data_list_v0.json', 'utf8'));

const atomicalsMap = {};
let maxAtomicalNumber = 0;
for (const atomical of atomicals) {
    atomicalsMap[atomical.punk_id] = atomical;
    maxAtomicalNumber = Math.max(maxAtomicalNumber, atomical.atomical_number);
}

const newPunks = [];
for (const punk of punks) {
    const atomical = atomicalsMap[punk.punk_id] || {};
    newPunks.push({
        pi: punk.punk_id,
        u: toBase64Url(punk.hex),
        ai: atomical.atomical_id,
        an: atomical.atomical_number,
    });
}

const list = newPunks.sort((a, b) => parseInt(a.pi) - parseInt(b.pi));
const json = JSON.stringify({
    list,
    last: maxAtomicalNumber,
    minted: atomicals.length,
}, (_, v) => v === undefined ? undefined : v);

fs.mkdirSync('dist', {recursive: true});
fs.writeFileSync('dist/punks.json', json, 'utf8');
fs.writeFileSync('dist/v.json', `{"v":${Date.now()}}`, 'utf8')

// Exporta una selección editorial de 40 fichajes desde los datos de origin/main.
const fs = require('fs'), vm = require('vm');
const src = fs.readFileSync('index.html', 'utf8');
const ctx = vm.createContext({});
vm.runInContext(src.slice(src.indexOf('const TYPES ='), src.indexOf('// color de cada familia')) + ';globalThis.types=TYPES', ctx);
vm.runInContext(src.slice(src.indexOf('const START_UNLOCKED ='), src.indexOf('// ===================== OBJETOS EXCLUSIVOS')) + ';globalThis.costs=UNLOCK_COST', ctx);
const section = src.slice(src.indexOf('var SUPERS ='), src.indexOf('const EXT='));
const supers = {};
for (const match of section.matchAll(/(?:^|\n)\s*([a-z][a-z0-9]*):\s*\{\s*name:('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*"),\s*grito:('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")/g)) {
  const parse = text => vm.runInContext(text, ctx);
  supers[match[1]] = {name: parse(match[2]), grito: parse(match[3])};
}
const regular = Object.keys(ctx.types).filter(id => id !== 'pringao' && !ctx.types[id].prize);
const selected = [...regular, 'bombero', 'enfermera'];
if (regular.length !== 38 || selected.length !== 40 || selected.filter(id=>!supers[id]).join(',') !== 'filtrador') throw Error('Fuente cambiada: revisar selección de 40 y supers: '+selected.filter(id=>!supers[id]).join(','));
const entries = selected.map(id => {
  const t = ctx.types[id], s = supers[id] || {name:null,grito:null};
  const item = id === 'tertuliano' ? 'cafe' : t.role === 'tanque' ? 'paella' : t.role === 'cura' ? 'churros' : 'tortillaC';
  return {id, nombre:t.name, rol:t.role, grito:s.grito, super:s.name,
    coste_desbloqueo: t.prize ? null : (ctx.costs[id] ?? 0),
    desbloqueo: t.prize ? 'Premio; no se compra' : (id in ctx.costs ? 'Puntos' : 'Inicial'),
    objeto_recomendado:item};
});
fs.writeFileSync('fichajes.json', JSON.stringify({fuente:'origin/main:index.html', nota:'Selección editorial de 40: 38 fichables y 2 premios (Bombero, Enfermera). Fontanero y Espetero son premios reales no incluidos; Nini no es fichaje.', fichajes:entries},null,2)+'\n');
console.log('fichajes:', entries.length, 'regulares:',regular.length, 'premios:',selected.length-regular.length, 'grito tertuliano:',supers.tertuliano.grito);

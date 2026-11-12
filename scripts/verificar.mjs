import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const js=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(new Set(ids).size,ids.length,'IDs duplicados');
for(const file of ['oferta.js','experiencia.css','universidades.js','assets/atenea/atenea.png','assets/atenea/educacion-posmedia.jpg']) assert.ok(fs.existsSync(new URL('../'+file,import.meta.url)));
new vm.Script(js);
const nodes=new Map();
function node(id){if(!nodes.has(id))nodes.set(id,{value:'',checked:false,hidden:false,style:{},dataset:{},classList:{toggle(){}},setAttribute(){},listeners:{},addEventListener(type,fn){this.listeners[type]=fn;},parentElement:{addEventListener(){}},focus(){},scrollIntoView(){}});return nodes.get(id);}
const context=vm.createContext({window:{OFERTA:[],addEventListener(){},scrollTo(){}},document:{getElementById:node,querySelectorAll(){return []},querySelector:node,addEventListener(){}},localStorage:{getItem(){return null},setItem(){}},location:{hash:''},history:{pushState(){}},matchMedia(){return {matches:false}}});
vm.runInContext(fs.readFileSync(new URL('../oferta.js',import.meta.url),'utf8'),context);
vm.runInContext(fs.readFileSync(new URL('../universidades.js',import.meta.url),'utf8'),context);
vm.runInContext(js,context);
for(const item of context.window.OFERTA){const logo=context.window.LOGOS_UNIVERSIDADES[item.i];assert.ok(logo,'Logo faltante: '+item.i);assert.ok(fs.existsSync(new URL('../'+logo.src,import.meta.url)));}
assert.ok(vm.runInContext('tarjeta(OFERTA[0])',context).includes('universidad-logo'),'Logo ausente en tarjeta');
vm.runInContext('elegidos=[OFERTA[0].id];pintarOpciones()',context);assert.ok(node('mias').innerHTML.includes('universidad-logo'),'Logo ausente en opciones');
const run=s=>vm.runInContext(s,context);
assert.ok(run('OFERTA.length')>0,'Oferta vacía');
assert.equal(run('PUNTAJE'),0);
run('S=VACIO();S.e={etnia:true,rural:true};S.sisben=0;S.saber=100;S.t={utc:true,je:true};calcular()');
assert.equal(run('PUNTAJE'),100,'Topes acumulados');
assert.equal(run('PARTES.e'),15);assert.equal(run('PARTES.t'),5);
for(const [percentil,puntos] of [[49,0],[50,5],[94,35],[95,40]]){run('S=VACIO();S.saber='+percentil+';calcular()');assert.equal(run('PARTES.m'),puntos);}
run('S=VACIO();S.e={hijos:true};calcular()');assert.equal(run('PARTES.e'),0,'Dependencia mujer con hijos');
run('S=VACIO();S.modo="puesto";S.saber=50;calcular()');assert.equal(run('PARTES.m'),40);
run('S.saber=51;calcular()');assert.equal(run('PARTES.m'),35);
run('irA("carreras",false)');assert.equal(node('carreras').hidden,false);assert.equal(node('inicio').hidden,true);
run('irA("inicio",false)');assert.equal(node('inicio').hidden,false);assert.equal(node('puntaje').hidden,true);
assert.ok(node('inicio-intereses').innerHTML.includes('data-inicio-campo'));
const institution=context.window.OFERTA[0].i;
node('f_nivel').value='filtro anterior';node('f_mod').value='filtro anterior';node('f_alcance').checked=true;
node('universidades-inicio').listeners.click({target:{closest(){return {dataset:{universidad:institution}}}}});
assert.equal(node('f_nivel').value,'');assert.equal(node('f_mod').value,'');assert.equal(node('f_alcance').checked,false);
assert.equal(run('filtrados().length'),context.window.OFERTA.filter(o=>o.i===institution).length);
assert.equal(node('carreras').hidden,false);
assert.equal((node('universidades-inicio').innerHTML.match(/data-universidad=/g)||[]).length,new Set(context.window.OFERTA.map(o=>o.i)).size);
console.log('OK: sintaxis, recursos, IDs, inicio, navegación y límites de puntajes. No sustituye pruebas de navegador.');

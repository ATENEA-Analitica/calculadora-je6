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
// Trayectoria Saber 11 V2: selección expresa y máximo no acumulable.
run('S=VACIO();S.t={saber2026:true};todo()');assert.equal(run('PARTES.t'),0);assert.equal(run('PUNTAJE'),0);
run('S.t.utc=true;S.t.jco=true;calcular()');assert.equal(run('PARTES.t'),5);
run('S=VACIO();S.saber=99;calcular()');assert.equal(run('PARTES.t'),0,'El percentil no acredita las demás condiciones');
run('S.t.saber2026=true;calcular()');assert.equal(run('PUNTAJE'),45);
assert.ok(node('f_trayectorias').innerHTML.includes('calendario A'));
assert.ok(node('v_trayectorias').innerHTML.includes('SIMAT'));
// Recorrido sin condiciones: permite avanzar, informa el cero y conserva respuestas al volver.
run('S=VACIO();paso=0;todo()');assert.ok(node('siguiente').innerHTML.includes('Ninguna me aplica'));
node('siguiente').listeners.click();assert.equal(run('paso'),1);assert.equal(run('PARTES.e'),0);
assert.ok(node('siguiente').innerHTML.includes('sin este dato'));
node('siguiente').listeners.click();assert.equal(run('paso'),2);
run('S.saber=101;todo()');assert.equal(node('siguiente').disabled,true);node('siguiente').listeners.click();assert.equal(run('paso'),2);
run('S.saber="";todo()');node('siguiente').listeners.click();assert.equal(run('paso'),3);
assert.ok(node('siguiente').innerHTML.includes('Ninguna me aplica: ver resultado'));
node('siguiente').listeners.click();assert.equal(run('paso'),4);assert.equal(run('PUNTAJE'),0);
run('S.saber=99;S.t.saber2026=true;todo();cambiarPaso(3)');assert.ok(node('siguiente').innerHTML.includes('Ver mi resultado'));
node('atras').listeners.click();assert.equal(run('S.t.saber2026'),true);
console.log('OK: sintaxis, recursos, IDs, inicio, navegación y límites de puntajes. No sustituye pruebas de navegador.');

// Oferta completa, datos faltantes y selección sin referencia histórica.
assert.equal(run('OFERTA.length'),214);
assert.equal(run('OFERTA.filter(o=>o.min===null).length'),44);
assert.equal(run('OFERTA.reduce((n,o)=>n+o.cupos,0)'),2454);
run('filtroCampo=null;S=VACIO();S.saber=100;calcular()');
for(const id of ['f_texto','f_nivel','f_mod','f_jor']) node(id).value='';
node('f_alcance').checked=false;node('f_orden').value='az';
assert.equal(run('filtrados().length'),214);
assert.equal(run('estado(null)'), 'sinref');
const nueva=run('tarjeta(OFERTA.find(o=>o.min===null))');
assert.ok(nueva.includes('Sin referencia JE4'));assert.ok(!nueva.includes('regla-min'));assert.ok(!nueva.includes('null'));
node('f_alcance').checked=true;assert.ok(run('filtrados().every(o=>Number.isFinite(o.min))'));
node('f_alcance').checked=false;
for(let n=0;n<10;n++) assert.ok(fs.existsSync(new URL('../assets/intereses/interes-'+n+'.webp',import.meta.url)));
console.log('OK: 214 ofertas, 44 sin histórico, 2454 cupos, filtros sin puntaje inventado.');

assert.ok(!html.includes('id="opciones"'));assert.ok(!html.includes('data-ir="opciones"'));run('irA("opciones",false)');assert.equal(node("inicio").hidden,false);

// Comparación desde el resultado: limpiar filtros antiguos y mostrar la lista pertinente.
run('S=VACIO();S.e={etnia:true};calcular();filtroCampo=Object.keys(CAMPOS)[0]');
node("f_texto").value="búsqueda anterior";node("f_nivel").value="otro";node("selector-intereses").open=true;
run("abrirComparacion()");
assert.equal(node("f_texto").value,"");assert.equal(node("f_nivel").value,"");
assert.equal(node("selector-intereses").open,true);assert.equal(node("f_alcance").checked,true);
assert.equal(run("filtrados().length"),run("OFERTA.filter(o=>Number.isFinite(o.min)&&o.min<=PUNTAJE).length"));
assert.equal(node("comparacion-activa").hidden,false);assert.equal(node("carreras").hidden,false);
node("ver-toda-oferta").listeners.click();assert.equal(run("filtrados().length"),214);assert.equal(node("comparacion-activa").hidden,true);
console.log("OK: comparación directa, filtro explícito y retorno a toda la oferta.");

// Coherencia Saber 11: no modificar percentil, no activar condición automáticamente.
for(const valor of ["",80,98,99.5,101]){run("S=VACIO();S.saber="+JSON.stringify(valor)+";S.t.saber2026=true;todo()");assert.equal(run("S.saber"),valor);assert.equal(run("PARTES.t"),0);assert.equal(run("S.t.saber2026"),false);}
for(const valor of [99,100]){run("S=VACIO();S.saber="+valor+";todo()");assert.equal(run("PARTES.t"),0);run("S.t.saber2026=true;todo()");assert.equal(run("PARTES.t"),5);assert.equal(run("PUNTAJE"),45);}
run("S.modo=\"puesto\";todo()");assert.equal(run("S.saber"),100);assert.equal(run("S.t.saber2026"),false);assert.equal(run("PARTES.t"),0);
run("S=VACIO();S.saber=80;S.t={saber2026:true,utc:true};todo()");assert.equal(run("PARTES.t"),5);assert.equal(run("S.t.saber2026"),false);
console.log("OK: regla percentil 99/100, cambio de modalidad y selección guardada incompatible.");

// Host fixture-only controls. Neither HDL syntax nor hashes prove FPGA execution.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root=new URL('../generated/',import.meta.url);
const bytes=name=>readFileSync(new URL(name,root));
const text=name=>bytes(name).toString('utf8');
const provenance=()=>JSON.parse(text('provenance.json'));
const sha=b=>createHash('sha256').update(b).digest('hex');
const gitBlob=b=>createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');

test('source and RTL fixtures have exact independently derived hashes',()=>{
 const p=provenance(),src=bytes('add8.ores'),rtl=bytes('add8.generated.sv');
 assert.equal(sha(src),p.sourceSha256);
 assert.equal(sha(rtl),p.rtlSha256);
 assert.equal(gitBlob(rtl),p.rtlGitBlobSha);
 assert.notEqual(sha(Buffer.concat([src,Buffer.from(' ')])),p.sourceSha256);
 assert.notEqual(gitBlob(Buffer.concat([rtl,Buffer.from('// extra\n')])),p.rtlGitBlobSha);
});

test('the experimental HDL fixture is a single bounded add8 combinational module',()=>{
 const src=text('add8.ores'),rtl=text('add8.generated.sv');
 assert.match(src,/pub fnc add8\(u8 a, u8 b\): u8 \{/);
 assert.equal((src.match(/return a \+ b;/g)||[]).length,1);
 assert.equal((rtl.match(/\bmodule\s+ores_add8\s*\(/g)||[]).length,1);
 assert.equal((rtl.match(/\bassign\s+out_result\s*=\s*\(in_a \+ in_b\);/g)||[]).length,1);
 assert.equal((rtl.match(/\bendmodule\b/g)||[]).length,1);
 assert.doesNotMatch(rtl,/\b(?:always|initial|include|specify|bind|force|release)\b|\$[A-Za-z_]/);
});

test('pinned source identity remains upstream fixture metadata, not hardware authority',()=>{
 const p=provenance();
 assert.equal(p.schemaVersion,1);
 assert.equal(p.sourceRepo,'ores-truffle-oreslang/oreslang-source.hdl');
 assert.equal(p.sourcePath,'tests/fixtures/add8.ores');
 assert.equal(p.compilerFixturePath,'tests/fixtures/add8.generated.sv');
 assert.match(p.sourceCommit,/^[0-9a-f]{40}$/);
 assert.equal(p.hardwareVerified,false);
 assert.ok(!Object.hasOwn(p,'hardwareAttested'));
 assert.ok(!Object.hasOwn(p,'timingClosurePassed'));
 assert.ok(!Object.hasOwn(p,'synthesisPassed'));
 assert.match(p.provenance,/independently reverify upstream/);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parsePinnedProvenance} from '../tools/parse-pinned-provenance.mjs';
const original=readFileSync(new URL('../generated/provenance.json',import.meta.url),'utf8');

test('checked-in FPGA provenance is canonical with exact member set',()=>{
  const p=parsePinnedProvenance(original);
  assert.equal(p.hardwareVerified,false);
  assert.equal(p.sourceRepo,'ores-truffle-oreslang/oreslang-source.hdl');
});
test('duplicate last-wins hardware claim and escaped key alias are denied',()=>{
  const duplicate=original.replace('"hardwareVerified": false,',
    '"hardwareVerified": true,\n  "hardwareVerified": false,');
  assert.throws(()=>parsePinnedProvenance(duplicate),/canonical/);
  const alias=original.replace('"hardwareVerified"',
    '"hardware\\u0056erified"');
  assert.throws(()=>parsePinnedProvenance(alias),/canonical/);
});
test('extra fields, missing fields and changed whitespace are denied',()=>{
  const extra={...JSON.parse(original),boardVerified:true};
  assert.throws(()=>parsePinnedProvenance(JSON.stringify(extra,null,2)+'\n'),/missing or unexpected/);
  const missing=JSON.parse(original);
  delete missing.sourceRepo;
  assert.throws(()=>parsePinnedProvenance(JSON.stringify(missing,null,2)+'\n'),/missing or unexpected/);
  const spoof={...JSON.parse(original),sourceRepo:'attacker/hardware'};
  assert.throws(()=>parsePinnedProvenance(JSON.stringify(spoof,null,2)+'\n'),/untrusted/);
  assert.throws(()=>parsePinnedProvenance(JSON.stringify(JSON.parse(original))),/canonical/);
});
test('invalid input and oversized provenance are denied',()=>{
  for(const raw of ['', 'null', '{}', '[]', 'not json', original+'x', original+' '.repeat(65536)])
    assert.throws(()=>parsePinnedProvenance(raw));
});

// Fixture provenance only. No FPGA synthesis, place-and-route or hardware evidence.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const digest=(algorithm,bytes)=>createHash(algorithm).update(bytes).digest('hex');
const provenance=()=>JSON.parse(readFileSync('generated/provenance.json','utf8'));
const source=()=>readFileSync('generated/add8.ores');
const rtl=()=>readFileSync('generated/add8.generated.sv');
const gitBlob=bytes=>createHash('sha1')
 .update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');

test('compiler source and RTL SHA-256 digests bind exact checked-in bytes',()=>{
 const p=provenance();
 assert.equal(digest('sha256',source()),p.sourceSha256);
 assert.equal(digest('sha256',rtl()),p.rtlSha256);
 assert.equal(p.sourceSha256,'26d446e1d903edca9691d37fc55c946033b590687468449103507c61b7026e80');
 assert.equal(p.rtlSha256,'7888f715405fb1207ee4988d9b9cf9cd03ecc9eeca58b85782654d46104e01cd');
});

test('the pinned RTL Git blob proves byte identity, not hardware verification',()=>{
 const p=provenance();
 assert.equal(gitBlob(rtl()),p.rtlGitBlobSha);
 assert.equal(p.rtlGitBlobSha,'93f75db8bf1725a7fe0f1150f1c949f8919863ce');
 assert.equal(p.hardwareVerified,false);
 assert.equal(Object.hasOwn(p,'siliconQualified'),false);
 assert.equal(Object.hasOwn(p,'tapeoutReady'),false);
});

test('source identity is a fully qualified upstream commit and exact fixture path',()=>{
 const p=provenance();
 assert.match(p.sourceCommit,/^[0-9a-f]{40}$/);
 assert.equal(p.sourceCommit,'2be4899ec3ad2e8dd38d6514d06e38d3d81a6b13');
 assert.equal(p.sourceRepo,'ores-truffle-oreslang/oreslang-source.hdl');
 assert.equal(p.sourcePath,'tests/fixtures/add8.ores');
 assert.equal(p.compilerFixturePath,'tests/fixtures/add8.generated.sv');
});

test('provenance metadata cannot acquire unreviewed authority fields',()=>{
 const p=provenance();
 const keys=['schemaVersion','sourceRepo','sourcePath','sourceSha256',
   'compilerFixturePath','rtlSha256','provenance','hardwareVerified',
   'sourceCommit','rtlGitBlobSha'];
 assert.deepEqual(Object.keys(p).sort(),keys.sort());
 assert.equal(p.schemaVersion,1);
 assert.match(p.provenance,/independently reverify upstream/);
 assert.match(rtl().toString('utf8'),/assign out_result = \(in_a \+ in_b\);/);
});

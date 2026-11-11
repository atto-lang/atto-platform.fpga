// Strict admission for the committed, flat provenance record.
// This is not an attestation that an upstream compiler ran or a board was tested.
const FIELDS=Object.freeze([
  'schemaVersion','sourceRepo','sourcePath','sourceSha256',
  'compilerFixturePath','rtlSha256','provenance','hardwareVerified',
  'sourceCommit','rtlGitBlobSha'
]);

export function parsePinnedProvenance(raw){
  if(typeof raw!=='string' || Buffer.byteLength(raw,'utf8')>65536)
    throw Error('bounded UTF-8 provenance string required');
  const parsed=JSON.parse(raw);
  if(!parsed || Array.isArray(parsed) || typeof parsed!=='object')
    throw Error('provenance must be an object');
  // JSON.parse accepts duplicate/escaped aliases with last-wins semantics.
  // Requiring canonical source bytes makes those attacks fail closed.
  if(raw!==JSON.stringify(parsed,null,2)+'\n')
    throw Error('provenance must be unique-key canonical JSON');
  const keys=Object.keys(parsed).sort();
  if(JSON.stringify(keys)!==JSON.stringify([...FIELDS].sort()))
    throw Error('provenance contains missing or unexpected fields');
  return parsed;
}

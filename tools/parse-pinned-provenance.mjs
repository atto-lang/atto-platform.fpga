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
  // Immutable identity/claim values belong inside the reusable admission gate;
  // a caller must not accidentally omit the checks and accept a substituted
  // repository, source artifact or fictional board result.
  const pinned={
    schemaVersion:1,
    sourceRepo:'ores-truffle-oreslang/oreslang-source.hdl',
    sourcePath:'tests/fixtures/add8.ores',
    sourceSha256:'26d446e1d903edca9691d37fc55c946033b590687468449103507c61b7026e80',
    compilerFixturePath:'tests/fixtures/add8.generated.sv',
    rtlSha256:'7888f715405fb1207ee4988d9b9cf9cd03ecc9eeca58b85782654d46104e01cd',
    provenance:'byte-exact copy of compiler-generated golden fixture; independently reverify upstream PR',
    hardwareVerified:false,
    sourceCommit:'2be4899ec3ad2e8dd38d6514d06e38d3d81a6b13',
    rtlGitBlobSha:'93f75db8bf1725a7fe0f1150f1c949f8919863ce'
  };
  for(const [field,expected] of Object.entries(pinned))
    if(parsed[field]!==expected)throw Error('untrusted pinned provenance '+field);
  return parsed;
}

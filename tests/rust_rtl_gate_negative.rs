//! Negative mutation tests for the pinned two-stage add8 RTL runner.
//! The deliberately broken DUT must fail: a PASS on only the golden fixture
//! is insufficient evidence that the runner actually catches wrong hardware.
use std::{env,fs,process::Command,path::PathBuf,time::{SystemTime,UNIX_EPOCH}};
struct Cleanup(PathBuf);
impl Drop for Cleanup { fn drop(&mut self) { let _ = fs::remove_file(&self.0); } }
fn test_inputs() -> (PathBuf,PathBuf,PathBuf) {
    (env::var_os("RTL_GATE_BIN").expect("missing RTL_GATE_BIN").into(),
     env::var_os("RTL_GATE_RTL").expect("missing RTL_GATE_RTL").into(),
     env::var_os("RTL_GATE_TB").expect("missing RTL_GATE_TB").into())
}
#[test]
fn rejects_mutated_adder_without_success_marker() {
    let (gate,rtl,tb)=test_inputs();
    let good=Command::new(&gate).arg(&rtl).arg(&tb).output().expect("execute golden RTL gate");
    assert!(good.status.success(), "golden RTL failed: {}",String::from_utf8_lossy(&good.stderr));
    let original=fs::read_to_string(&rtl).expect("read RTL source");
    let from="assign out_result = (in_a + in_b);";
    assert_eq!(original.matches(from).count(),1,"expected unique pinned add8 assignment");
    let corrupt=original.replacen(from,"assign out_result = (in_a - in_b);",1);
    let stamp=SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos();
    let file=env::temp_dir().join(format!("ores-corrupt-add8-{}-{stamp}.sv",std::process::id()));
    let _cleanup=Cleanup(file.clone());
    fs::write(&file,corrupt).expect("write mutated RTL");
    let bad=Command::new(&gate).arg(&file).arg(&tb).output().expect("execute mutated RTL gate");
    assert!(!bad.status.success(), "wrong RTL was incorrectly accepted");
    let stdout=String::from_utf8_lossy(&bad.stdout);
    assert!(!stdout.contains("_65536_PASS"),"wrong RTL emitted pass marker");
}
#[test]
fn rejects_missing_rtl_input() {
    let (gate,_,tb)=test_inputs();
    let no_such_file=env::temp_dir().join(format!("oreslang-missing-rtl-{}.sv",std::process::id()));
    let result=Command::new(gate).arg(no_such_file).arg(tb).output().expect("run gate");
    assert!(!result.status.success(),"missing RTL was incorrectly accepted");
}

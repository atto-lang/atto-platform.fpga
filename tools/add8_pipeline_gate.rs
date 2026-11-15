//! Host reference runner for a two-stage add8 RTL simulation.
//! An Icarus pass is not compiler provenance, physical timing or device evidence.
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process::{Command,ExitCode};
use std::time::{SystemTime,UNIX_EPOCH};
const PASS: &str = "FPGA_ADD8_PIPELINE_65536_PASS";
struct RemoveOnDrop(PathBuf);
impl Drop for RemoveOnDrop {fn drop(&mut self){let _=fs::remove_file(&self.0);}}
fn run() -> Result<(),String> {
    let args: Vec<_> = env::args_os().collect();
    if args.len()!=3 {return Err("usage: add8_pipeline_gate RTL.sv TESTBENCH.sv".into());}
    let suffix=SystemTime::now().duration_since(UNIX_EPOCH).map_err(|e|e.to_string())?.as_nanos();
    let binary=env::temp_dir().join(format!("ores_add8_{}_{}.vvp",std::process::id(),suffix));
    let _guard=RemoveOnDrop(binary.clone());
    let build=Command::new("iverilog").arg("-g2012").arg("-s").arg("tb").arg("-o")
        .arg(&binary).arg(&args[1]).arg(&args[2]).output().map_err(|e|format!("iverilog unavailable: {e}"))?;
    if !build.status.success(){return Err(format!("compile failed: {}",String::from_utf8_lossy(&build.stderr)));}
    let result=Command::new("vvp").arg(&binary).output().map_err(|e|format!("vvp unavailable: {e}"))?;
    if !result.status.success(){return Err(format!("simulation failed: {}",String::from_utf8_lossy(&result.stderr)));}
    let stdout=String::from_utf8(result.stdout).map_err(|e|e.to_string())?;
    if !stdout.lines().any(|line|line.trim_end_matches('\r')==PASS){return Err("simulator did not emit exact completion marker".into());}
    println!("{PASS}");
    Ok(())
}
fn main() -> ExitCode {match run(){Ok(())=>ExitCode::SUCCESS,Err(e)=>{eprintln!("{e}");ExitCode::FAILURE}}}
#[cfg(test)] mod tests {
    #[test] fn modular_oracle_all_pairs(){for a in 0u32..256 {for b in 0u32..256 {
        let c=a^b;
        let expected=((a+b+c)&255) as u8;
        let staged=((a+b)&255) as u8;
        assert_eq!(staged.wrapping_add(c as u8),expected);
    }}}
}

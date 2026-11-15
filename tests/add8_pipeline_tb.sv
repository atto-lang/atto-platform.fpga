// Two actual instances of pinned compiler-emitted RTL; host simulation only.
// Third input is a deterministic function of each input pair, not exhaustive
// over all 24-bit triples. This is NOT timing, board or silicon evidence.
module tb;
  reg [7:0] in_a, in_b, in_c;
  wire [7:0] intermediate, output_value;
  ores_add8 first(.in_a(in_a), .in_b(in_b), .out_result(intermediate));
  ores_add8 second(.in_a(intermediate), .in_b(in_c), .out_result(output_value));
  integer a, b;
  initial begin
    for (a=0; a<256; a=a+1) begin
      for (b=0; b<256; b=b+1) begin
        in_a=a[7:0]; in_b=b[7:0]; in_c=(a ^ b) & 8'hff;
        #1;
        if (intermediate !== ((a+b) & 8'hff))
          $fatal(1, "first-stage mismatch a=%0d b=%0d",a,b);
        if (output_value !== ((a+b+(a^b)) & 8'hff))
          $fatal(1, "second-stage mismatch a=%0d b=%0d",a,b);
      end
    end
    $display("FPGA_ADD8_PIPELINE_65536_PASS");
    $finish;
  end
endmodule

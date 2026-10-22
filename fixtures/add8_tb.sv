module add8_tb;
  reg [7:0] a, b;
  wire [7:0] result;
  integer i, j;
  reg [7:0] expected;
  add8 dut(.a(a), .b(b), .result(result));
  initial begin
    for (i=0; i<256; i=i+1)
      for (j=0; j<256; j=j+1) begin
        a=i; b=j; expected=(i+j)&255;
        #1;
        if (result !== expected) $fatal(1, "FPGA smoke mismatch a=%0d b=%0d", i, j);
      end
    $display("PASS: FPGA platform fixture 65536 simulation vectors");
    $finish;
  end
endmodule

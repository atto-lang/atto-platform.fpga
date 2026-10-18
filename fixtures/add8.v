// Independent synthetic reference: NOT yet emitted by the Oreslang HDL compiler; unsigned modulo 2^8
module add8 (
  input wire [7:0] a,
  input wire [7:0] b,
  output wire [7:0] result
);
  assign result = a + b;
endmodule

`default_nettype none
`timescale 1ns / 1ps

module tb();

  // Dump the signals to a VCD file
  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0, tb);
  end

  // Clock and reset
  reg clk;
  reg rst_n;

  // I/O signals
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;

  // Power signals for gate-level simulations
  supply1 VPWR;
  supply0 VGND;

  // Instantiate the DUT
  tt_um_Richard28277 user_project (
    `ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
    `endif
      .ui_in  (ui_in),
      .uo_out (uo_out),
      .uio_in (uio_in),
      .uio_out(uio_out),
      .uio_oe (uio_oe),
      .ena    (ena),
      .clk    (clk),
      .rst_n  (rst_n)
  );

  // Clock generation
  initial begin
    clk = 0;
    forever #5 clk = ~clk;  // 10 ns clock period
  end

  // Reset initialization
  initial begin
    rst_n = 0;  // Start in reset
    #50 rst_n = 1;  // Release reset after 50 ns
  end

endmodule

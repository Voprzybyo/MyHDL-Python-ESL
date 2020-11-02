module tb_classic_fsm;

reg clk_i;
reg [1:0] inputs_i;
wire [3:0] outputs_o;

initial begin
    $from_myhdl(
        clk_i,
        inputs_i
    );
    $to_myhdl(
        outputs_o
    );
end

classic_fsm dut(
    clk_i,
    inputs_i,
    outputs_o
);

endmodule

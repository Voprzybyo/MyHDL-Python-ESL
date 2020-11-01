module tb_blinker;

reg clk_i;
wire led_o;

initial begin
    $from_myhdl(
        clk_i
    );
    $to_myhdl(
        led_o
    );
end

blinker dut(
    clk_i,
    led_o
);

endmodule

module tb_ram;

reg clk_i;
reg en_i;
reg wr_i;
reg [7:0] addr_i;
reg [7:0] data_i;
wire [7:0] data_o;

initial begin
    $from_myhdl(
        clk_i,
        en_i,
        wr_i,
        addr_i,
        data_i
    );
    $to_myhdl(
        data_o
    );
end

ram dut(
    clk_i,
    en_i,
    wr_i,
    addr_i,
    data_i,
    data_o
);

endmodule

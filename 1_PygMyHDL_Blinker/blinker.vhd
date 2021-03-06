-- File: blinker.vhd
-- Generated by MyHDL 0.11
-- Date: Sun Oct 25 11:41:46 2020


library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.all;

use work.pck_myhdl_011.all;

entity blinker is
    port (
        clk_i: in std_logic;
        led_o: out std_logic
    );
end entity blinker;


architecture MyHDL of blinker is



signal cnt: unsigned(21 downto 0);

begin




BLINKER_LOC_INSTS_CHUNK_INSTS_0: process (clk_i) is
begin
    if rising_edge(clk_i) then
        cnt <= (cnt + 1);
    end if;
end process BLINKER_LOC_INSTS_CHUNK_INSTS_0;


led_o <= cnt((22 - 1));

end architecture MyHDL;

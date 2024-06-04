# MIT License
#
# Copyright (c) 2024 zen0-5338
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, 8and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# File Paths for storing output
x1_output_file_path = "../sim_output/x1_wave.txt"
x2_output_file_path = "../sim_output/x2_wave.txt"
x3_output_file_path = "../sim_output/x3_wave.txt"

# Variables to configure simulation
simulation_timescale_precision = "10ps"
simulation_timescale_step = "1ns"
simulation_clock_period = 10
# Number of output values to generate
num_output_samples = 20000

# Verilog hexadecimal representation of IEEE 754 single precision
# initial values of chaos signal generator inputs
x1_initial_value_hex = "'h3dcccd53"
x2_initial_value_hex = "'h3c23d70a"
x3_initial_value_hex = "'h0"

print(
    f"""\
`include "../rtl_verilog/chaos_signal_generator.v"

`timescale {simulation_timescale_step}/{simulation_timescale_precision}

`define CLOCK_PERIOD {simulation_clock_period}

module chaos_signal_generator_tb;

    reg clk;
    reg rst;
    reg [31:0] x1_initial, x2_initial, x3_initial;
    wire [31:0] x1_out, x2_out, x3_out;

    localparam samples = {num_output_samples};
    
    chaos_signal_generator DUT(
        x1_out,
        x2_out,
        x3_out,
        x1_initial,
        x2_initial,
        x3_initial,
        clk,
        rst
    );

    always #(`CLOCK_PERIOD/2) clk=~clk;

    initial	begin
        clk = 1'b0;
        x1_initial = {x1_initial_value_hex};
        x2_initial = {x2_initial_value_hex};
        x3_initial = {x3_initial_value_hex};
        rst = 1'b1;
        #(`CLOCK_PERIOD + 3);
        rst = 1'b0;
    end

    reg [31:0] x1_mem[0:samples-1];
    reg [31:0] x2_mem[0:samples-1];
    reg [31:0] x3_mem[0:samples-1];
    int i;
    initial	begin
        i=0;
        while(i < samples) begin
            @(posedge clk);
            x1_mem[i] = x1_out;
            x2_mem[i] = x2_out;
            x3_mem[i] = x3_out;
            i = i+1;
        end
        $writememh({x1_output_file_path},x1_mem);
        $writememh({x2_output_file_path},x2_mem);
        $writememh({x3_output_file_path},x3_mem);
        $stop();
    end

endmodule"""
)

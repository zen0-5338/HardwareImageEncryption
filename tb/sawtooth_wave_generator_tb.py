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


sawtooth_output_file_path = "../sim_output/sawtooth_wave_output.txt"

print(
    f"""\
`include "../rtl_verilog/sawtooth_wave_generator.v

`timescale 1ns/10ps

`define CLOCK_PERIOD 10

module sawtooth_wave_generator_tb;

    reg clk;
    reg [31:0] x_in;
    wire [31:0] y_out;
    reg[31:0] swap;

    localparam samples = 1000;

    reg [31:0] output_mem[0:samples-1];
    
    sawtooth_wave DUT(.y_out(y_out), .x_in(x_in), .clk(clk));
    
    always #(`CLOCK_PERIOD/2) clk = ~clk;

    initial begin
        clk = 'b1;
        x_in = 'b0;
        #`CLOCK_PERIOD;
    end

    int i;
    initial begin
        i = 0;
        while (i < samples) begin
            @(posedge clk);
            output_mem[i] = y_out;
            x_in = output_mem[i];
            i = i+1;
        end
        $writememh({sawtooth_output_file_path}, output_mem);
        $stop();
    end

endmodule"""
)

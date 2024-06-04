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

substitution_box_output_file_path = "../sim_output/substitution_box.txt"

# Variables to configure simulation
simulation_timescale_precision = "10ps"
simulation_timescale_step = "1ns"
simulation_clock_period = 10

# Module parameters
table_rows = 16
key_size = 128

print(
    f"""\
`include "../rtl_verilog/chaos_signal_generator.v"
`include "../rtl_verilog/substitution_box_generator.v"

`define CLOCK_PERIOD {simulation_clock_period}

module substitution_box_generator_tb;

    localparam TABLE_ROWS = {table_rows};
    localparam KEY_SIZE = {key_size};

    reg clk;
    reg reset = 'b1;
    reg enable_bar = 'b0;
    wire [31:0] chaotic_signal_x1, chaotic_signal_x2, chaotic_signal_x3;
    reg [31:0] x1_initial, x2_initial, x3_initial;
    wire ready;
    
    wire [KEY_SIZE-1:0] substitution_box_row[0:TABLE_ROWS-1];

    chaos_generator chaos_generator_object(
        chaotic_signal_x1,
        chaotic_signal_x2,
        chaotic_signal_x3,
        x1_initial,
        x2_initial,
        x3_initial,
        clk,
        reset
    );
    
    substitution_box_generator DUT("""
)
for i in range(table_rows):
    print(
        f"""\
        substitution_box_row[{i}],"""
    )
    
print(
    f"""\
        ready,
        chaotic_signal_x1,
        chaotic_signal_x2,
        chaotic_signal_x3,
        reset,
        enable_bar,
        clk
    );

    reg [KEY_SIZE-1:0] mem[0:TABLE_ROWS-1];

    always #(`CLOCK_PERIOD/2) clk = ~clk;

    initial	begin
        clk = 1'b0;
        enable_bar = 1'b0;
        reset = 1'b1;
        x1_initial = 32'h3DCC_CD53; // 0.1
        x2_initial = 32'h3C23_D70A; // 0.01
        x3_initial = 32'h0;
        #`CLOCK_PERIOD reset = 'b0;
        
        wait(ready == 1);
        for (integer i = 0; i < TABLE_ROWS; i++) begin
                mem[i] = sbox_row[i];
            end
        $writememh({substitution_box_output_file_path}, mem);
        $stop();
    end

endmodule"""
)
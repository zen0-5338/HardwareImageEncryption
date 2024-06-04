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

# Module Parameters
table_rows = 16
key_size = 128

print(
    f"""\
`include "../RTL/multiplier/Multiplication.v"

module substitution_box_generator
#(
    parameter TABLE_ROWS = {table_rows},
    parameter KEY_SIZE = {key_size}, // TODO: implement variable key size
)
("""
)

for i in range(table_rows):
    print(
        f"""\
    output reg [KEY_SIZE-1:0] substitution_box_row{i},"""
    )

print(
    """\
    output reg substitution_box_ready,
    input wire [31:0] chaotic_signal_x1,
    input wire [31:0] chaotic_signal_x2,
    input wire [31:0] chaotic_signal_x3,
    input wire reset,
    input wire enable_bar,
    input wire clk
);
    
    localparam power10_6_ieee_754_sp = 32'h4974_2400;
    
    // Map to track stored s-box values
    reg sbox_value_map[0:255];
    
    // TODO: implement parameterised counter and address size 
    // Counter to track number of stored values.
    reg [7:0] sbox_counter;
    wire [3:0] sbox_row_address, sbox_column_address; 
    
    // ieee 754 sp vars containing position 3, 4, 5 decimal digits
    wire [31:0] x1_decimal_shifted, x2_decimal_shifted, x3_decimal_shifted;
    // trash/temp vars
    wire [22:0] x1_decimal_shifted_mantissa, x2_decimal_shifted_mantissa, x3_decimal_shifted_mantissa;
    // sbox vector generation bytes
    wire [7:0] m1, m2, m3, v;
    
    // TODO: Implement custom decimal digit extractor in ieee 754 std numbers with hi-lo indices
    // using mantissa multiplication and bit shifting based on exponent OR using GRISU algo
    // Algo Logic: Multiplying a number by 1e6 will make 3,4,5 decimal digit become H,T,O 
    Multiplication x1_decimal_digit_shifter(.a_operand(chaotic_signal_x1), .b_operand(power10_6_ieee_754_sp), .result(x1_decimal_shifted));
    Multiplication x2_decimal_digit_shifter(.a_operand(chaotic_signal_x2), .b_operand(power10_6_ieee_754_sp), .result(x2_decimal_shifted));
    Multiplication x3_decimal_digit_shifter(.a_operand(chaotic_signal_x3), .b_operand(power10_6_ieee_754_sp), .result(x3_decimal_shifted));
    
    // Obtain the part of mantissa having the digits left of decimal point by shifting exponent amount
    assign {m1, x1_decimal_shifted_mantissa} = {8'h01, x1_decimal_shifted[22:0]} << ((x1_decimal_shifted[30-:8] <= 127) ? 'd0 : x1_decimal_shifted[30-:8] - 'd127);
    assign {m2, x2_decimal_shifted_mantissa} = {8'h01, x2_decimal_shifted[22:0]} << ((x2_decimal_shifted[30-:8] <= 127) ? 'd0 : x2_decimal_shifted[30-:8] - 'd127);
    assign {m3, x3_decimal_shifted_mantissa} = {8'h01, x3_decimal_shifted[22:0]} << ((x3_decimal_shifted[30-:8] <= 127) ? 'd0 : x3_decimal_shifted[30-:8] - 'd127);
    
    // generate vector to be stored in sbox 
    assign v = (m1 ^ m2 ^ m3);
    // determine cell coords to store vector
    assign {sbox_row_address, sbox_column_address} = sbox_counter;
    
    always @(posedge(clk)) begin
        if (reset) begin
            substitution_box_ready <= 1'b0;
            sbox_counter <= 'b0;"""
)

for i in range(table_rows):
    print(
        f"""\
            substitution_box_row{i} <= 'b0;"""
    )

print(
    """\
            for(integer i = 0; i < 256; i=i+1) begin
                sbox_value_map[i] <= 1'b0;
            end
        end
        else if (!reset && !enable_bar) begin
            if (!sbox_value_map[v]) begin
                case(sbox_row_address)"""
)

for i in range(table_rows):
    print(
        f"""\
                {i} : substitution_box_row{i}[8*sbox_column_address+:8] <= v;"""
    )

print(
    """\
                    default: sbox_counter <= 'bx;
                endcase
                sbox_value_map[v] <= 1'b1;
                {substitution_box_ready, sbox_counter} <= sbox_counter + 1;
            end
        end
    end

endmodule"""
)

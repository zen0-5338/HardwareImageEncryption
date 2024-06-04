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


print(
    f"""\
`include "../include/adder/float_adder_v2.v"

module sawtooth_wave(
    output wire [31:0] y_out,
    output wire y_out_val,
    input wire [31:0] x_in,
    input wire x_in_val,
    input wire y_out_rdy,
    input wire clk,
    input wire rstn
);

    wire x_sign;
    wire [7:0] x_exponent;
    wire [22:0] x_mantissa;

    assign x_sign = x_in[31];
    assign x_exponent = x_in[30:23];
    assign x_mantissa = x_in[22:0];

    wire [7:0] shift_initial;
    assign shift_initial = (x_exponent < 8'd127) ? 8'd0 : x_exponent-8'd127;

    wire [22:0] x_mantissa_shifted_initial;
    assign x_mantissa_shifted_initial = (x_mantissa << shift_initial);

    wire [7:0] x_exponent_initial;
    assign x_exponent_initial = (x_exponent - shift_initial);

    //now need to get most significant 1
    reg [4:0] most_significant_one;

    always @(*)	begin
        most_significant_one = ";"""
)

for i in range(1, 24):
    print(
        f"""\
           x_mantissa_shifted_initial[{23-i}] ? 5'd{i} :"""
    )
print("5'd0;")

print(
    f"""\
    end

    wire [22:0] x_mantissa_shifted_final;
    assign x_mantissa_shifted_final = (x_exponent < 8'd127) ? x_mantissa_shifted_initial : (x_mantissa_shifted_initial << most_significant_one);

    wire [7:0] x_exponent_final;
    assign x_exponent_final =  (x_exponent < 8'd127) ? x_exponent_initial : 
                    ((x_exponent_initial - most_significant_one) == 8'd127 && (x_mantissa_shifted_final == 23'd0)) ? 8'd0 : (x_exponent_initial - most_significant_one);

    wire [31:0] floor_x;
    assign floor_x = {{x_sign,x_exponent_final,x_mantissa_shifted_final}};


    //5 adder we need here
    //how to do with a single adder :think:
    //If I do in five iterations, :think: 
    //as soon as shit is ready, we give a val and when rdy comes from next side, we start again
    //opposite to the sign, we would add/subtract 0.2 = 32'b00111110010011001100110011001101
    //the point where sign changes, we would take the previous shit
    reg [2:0] normalised_x_counter;
    wire [31:0] result_of_subtraction;
    reg [31:0] result_of_subtraction_stored;
    wire [31:0] subtraction_in;

    float_adder A(.Number1(subtraction_in),.Number2({{~x_sign,31'b0111110010011001100110011001101}}),.Result(result_of_subtraction));

    assign subtraction_in = (normalised_x_counter == 3'd0) ? floor_x : result_of_subtraction_stored;

    wire[31:0] normalized_x;
    assign normalized_x = subtraction_in;

    assign y_out_val = (result_of_subtraction[31] != x_sign);

    //This counter keeps increasing and we'll keep on using float_adder
    //output of this adder, we need to store since we'll use that in next cycle
    //as soon as sign changes, we stop counting more and make val high
    reg x_in_val_d;

    always @(posedge clk, negedge rstn)	begin
        if(!rstn) begin
            normalised_x_counter <= 3'd0;
            result_of_subtraction_stored <= 32'd0;
            x_in_val_d = 1'd0;
        end
        else begin
            x_in_val_d = x_in_val;
            normalised_x_counter <= ((x_in_val == 1'd1 && x_in_val_d == 1'd0) || (y_out_rdy && y_out_val)) ? 3'd0 : 
                y_out_val ? normalised_x_counter : normalised_x_counter + 3'd1;
            result_of_subtraction_stored <= result_of_subtraction;
        end
    end"""
)

for i in range(5):
    if i == 0:
        print(
            f"""\
    float_adder A{i}(.Number1(floor_x),.Number2({{~x_sign,31'b0111110010011001100110011001101}}),.Result(subtracted_{i}));"""
        )
    else:
        print(
            f"""\
    float_adder A{i}(.Number1(subtracted_${i-1}),.Number2({{~x_sign,31'b0111110010011001100110011001101}}),.Result(subtracted_{i}));"""
        )

print(
    f"""\	
    wire [31:0] normalized_x_m_0p5;
    wire [31:0] normalized_x_m_1p5;

    float_adder x_m_0p5(.Number1({{1'b0,normalized_x[30:0]}}),.Number2(32'b10111101010011001100110011001101),.Result(normalized_x_m_0p5));
    float_adder x_m_1p5(.Number1({{1'b0,normalized_x[30:0]}}),.Number2(32'b10111110000110011001100110011010),.Result(normalized_x_m_1p5));

    wire sign_normalized_x_m_0p5;
    wire sign_normalized_x_m_1p5;

    assign sign_normalized_x_m_0p5 = normalized_x_m_0p5[31];
    assign sign_normalized_x_m_1p5 = normalized_x_m_1p5[31];

    reg [31:0] number_to_be_added;
    reg sign_of_x_while_calculation;

    always @(*)	begin
        case({{sign_normalized_x_m_0p5,sign_normalized_x_m_1p5}})
            2'b00 : begin
                number_to_be_added = 32'b10111110010011001100110011001101;		//-0.2
                sign_of_x_while_calculation = 1'b0;
            end
            2'b01 : begin
                   number_to_be_added = 32'b00111101110011001100110011001101;		//0.1
                sign_of_x_while_calculation = 1'b1;
            end
            2'b10 : begin
                number_to_be_added = 32'd0;
                sign_of_x_while_calculation = 1'b0;
            end
            2'b11 : begin
                number_to_be_added = 32'd0;
                sign_of_x_while_calculation = 1'b0;
            end
            default : begin
                   number_to_be_added = 32'd0; 
                sign_of_x_while_calculation = 1'b0;
            end
        endcase
    end

    wire [31:0] sawtooth_final_pre;
                                                                    
    float_adder sawtooth_function(.Number1({{sign_of_x_while_calculation,normalized_x[30:0]}}),.Number2(number_to_be_added),.Result(sawtooth_final_pre));

    wire sawtooth_final_sign;
    assign sawtooth_final_sign = x_sign ^ sawtooth_final_pre[31];

    assign y_out = {{sawtooth_final_sign,sawtooth_final_pre[30:0]}};

endmodule"""
)

# We want only the decimal part, not the other
# 85.125
# 85 = 1010101
# 0.125 = 001
# 85.125 = 1010101.001
#       =1.010101001 x 2^6
#
# biased exponent 127+6=133
# 133 = 10000101
# Normalised mantisa = 010101001
#
# 	        127+6
# 85.125 = 0 10000101 01010100100000000000000
# 00.125 = 0 01111100 00000000000000000000000  shift = 9
# 		127-3
#
#              127+3
# 08.370 = 0 10000010 00001011110101110000101
#                   22
# 00.370 = 0 01111101 01111010111000010100100   shift = 5
# 	        127-2
#
# NO NEED IF EXPONENT LESS THAN 127
# 0.0001 = 0 01110001 10100011011011100010111
#
#              127+0
# 01.000 = 0 01111111 00000000000000000000000  shift = 0
#
# 	        127+5
# 37.000 = 0 10000100 00101000000000000000000  shift = 5
#
#
#
#
# Just need to calculate the shift, that will make my life ez
# a) exponent - 127
# b) left shift by that much
# c) after that,if msb is 0, find the next most significant 1, if there is
# none, leave
# d) left shift again by this much and subtract result from the exponent_new
# e) if after shift, we are left with 127 + 0, change it to 0
# 	    127-1
# 0.880 = 0 0111_1110 11000010100011110101110
#
#  127-1
# 1 0111_1110 10001010001111010111000		//-0.77
# 1 0111_1101 10001111010111000010100		//-0.39
#  127-2

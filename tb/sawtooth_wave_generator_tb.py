print(
    f"""\
`include "../rtl_verilog/sawtooth_wave.v

`timescale 1ns/10ps

`define CLOCK_PERIOD 10

module sawtooth_wave_generator_tb;

reg clk;
reg [31:0] x_in;
wire [31:0] y_out;
reg[31:0] swap;
shortreal initial_value;

localparam samples = 1000;

reg [31:0] output_mem[0:samples-1];
sawtooth_wave DUT(clk, x_in, y_out);
always #(`CLOCK_PERIOD/2) clk = ~clk;

initial begin
    clk = 'b1;
    initial_value = 0;
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
    $writememh("../sim_output/sawtooth_wave_output.txt", output_mem);
    $stop();
end

endmodule"""
)

#!/bin/bash

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


# Create folders
mkdir data, rtl_verilog, sim_output, tb_verilog

# Generate source files
for python_file in $(find ./rtl -name *.py)
do
    filename=$(basename "$python_file")
    nohup python $python_file > ./rtl_verilog/${filename%.*}.v & disown
done

# Generate testbenches
for python_file in $(find ./tb -name *.py)
do
    filename=$(basename "$python_file")
    nohup python $python_file > ./tb_verilog/${filename%.*}.sv & disown
done


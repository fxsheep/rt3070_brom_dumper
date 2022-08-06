#!/bin/sh
NAME=rt2870read
mkdir -p bin
sdcc --model-small --nostdlib -mmcs51 -pdefcpu -c -o bin/$NAME.rel $NAME.c
sdcc --model-small --nostdlib -o bin/$NAME.hex bin/$NAME.rel
objcopy --input-target=ihex --output-target=binary bin/$NAME.hex $NAME.bin

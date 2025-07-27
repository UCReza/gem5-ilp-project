# gem5 ILP Project - Step 1: Hello World Simulation

## Overview

This project shows how to compile a simple ARM "Hello World" program using Docker cross-compilation on macOS, and run it on gem5.

## Commands Used

### 1. Compile ARM Binary using Docker

I used Docker on macOS to cross-compile the ARM binary because native ARM compilers might not be installed or compatible. The command mounts the local  directory inside the container, installs the ARM cross-compiler, and compiles a static ARM binary.

```bash
docker run --rm -v /Users/rezashrestha/Documents/MSCS-531/Week5/workload:/work -w /work debian:bullseye bash -c "\
apt update && \
apt install -y gcc-aarch64-linux-gnu && \
aarch64-linux-gnu-gcc -static -o hello_arm hello.c"
```

### 2.Command in the gem5 simulator with the ARM binary to verify it prints "Hello World": Used config file to run hello world

```bash
./build/ARM/gem5.opt /Users/rezashrestha/Documents/MSCS-531/Week5/workload/config/hello_config.py




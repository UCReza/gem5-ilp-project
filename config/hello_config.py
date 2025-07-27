# hello_run.py - A simple ARM SE mode config for gem5 v25

from m5.objects import *
from gem5.simulate.simulator import Simulator
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.isas import ISA
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.processors.cpu_types import CPUTypes  
from gem5.resources.resource import CustomResource



import os

# Create the processor (TimingSimpleCPU, ARM)
processor = SimpleProcessor(cpu_type=CPUTypes.TIMING, isa=ISA.ARM, num_cores=1)


# Create the board (clock, memory, cache, etc.)
board = SimpleBoard(
    clk_freq="1GHz",
    processor=processor,
    memory=SingleChannelDDR3_1600(size="512MB"),
    cache_hierarchy=NoCache()
)

# Set the workload binary path
binary = CustomResource("/Users/rezashrestha/Documents/MSCS-531/Week5/workload/hello_arm")
board.set_se_binary_workload(binary)


# Set up the simulator
simulator = Simulator(board=board)

# Run the simulation
simulator.run()

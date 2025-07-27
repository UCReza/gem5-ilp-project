# ILP_pipeline.py
# Minimal ARM SE gem5 config with MinorCPU/DerivO3CPU, L1/L2 caches,
# branch predictor selection, issue width, and SMT. v25+ port naming.

import os
import argparse
import m5
from m5.objects import (
    System, SrcClockDomain, VoltageDomain, AddrRange,
    SystemXBar, Cache, L2XBar, Process, SEWorkload,
    SimpleMemory, MinorCPU, DerivO3CPU, Root
)

# ----------------------------
# Cache models + helpers
# ----------------------------
class L1ICache(Cache):
    assoc = 2
    tag_latency = data_latency = response_latency = 2
    mshrs = 4
    tgts_per_mshr = 16
    size = '32kB'
    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port
    def connectBus(self, bus):
        # L1s sit on the CPU side of the L2 bus
        self.mem_side = bus.cpu_side_ports

class L1DCache(Cache):
    assoc = 2
    tag_latency = data_latency = response_latency = 2
    mshrs = 4
    tgts_per_mshr = 16
    size = '32kB'
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port
    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports

class L2Cache(Cache):
    assoc = 8
    tag_latency = data_latency = response_latency = 12
    mshrs = 16
    tgts_per_mshr = 16
    size = '512kB'
    def connectCPUSideBus(self, bus):
        # L2's CPU side faces the L1 bus's MEM side
        self.cpu_side = bus.mem_side_ports
    def connectMemSideBus(self, bus):
        # L2's MEM side faces the system membus CPU side
        self.mem_side = bus.cpu_side_ports

# ----------------------------
# Branch predictor helper
# ----------------------------
def make_branch_pred(kind: str):
    if kind == "none":
        try:
            from m5.objects import NullBranchPredictor
            return NullBranchPredictor()
        except Exception:
            from m5.objects import LocalBP
            return LocalBP()  # fallback
    elif kind == "local":
        from m5.objects import LocalBP
        return LocalBP()
    else:
        from m5.objects import TournamentBP
        return TournamentBP()

# ----------------------------
# CLI
# ----------------------------
ap = argparse.ArgumentParser(description="ILP pipeline config (ARM SE)")
ap.add_argument("--binary", required=True, help="Path to ARM (AArch64) binary")
ap.add_argument("--cpu-type", choices=["minor","o3"], default="minor",
               help="minor=in-order; o3=out-of-order")
ap.add_argument("--bp", choices=["tournament","local","none"], default="tournament",
               help="branch predictor")
ap.add_argument("--issue-width", type=int, default=1,
               help="O3: fetch/decode/issue/dispatch/commit width")
ap.add_argument("--smt-threads", type=int, default=1,
               help="O3: number of hardware threads")
ap.add_argument("--mem-size", default="512MB", help="SE memory size")
args = ap.parse_args()

if not os.path.exists(args.binary):
    raise SystemExit(f"[ERROR] Binary not found: {args.binary}")

# ----------------------------
# System
# ----------------------------
system = System()
system.clk_domain = SrcClockDomain(clock="2GHz", voltage_domain=VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange(args.mem_size)]
system.membus = SystemXBar()

# CPU
if args.cpu_type == "minor":
    cpu = MinorCPU()
    cpu.branchPred = make_branch_pred(args.bp)
    system.cpu = [cpu]
else:
    cpu = DerivO3CPU()
    w = max(1, int(args.issue_width))
    cpu.fetchWidth = w
    cpu.decodeWidth = w
    cpu.issueWidth  = w
    cpu.dispatchWidth = w
    cpu.commitWidth = w
    cpu.squashWidth = w
    cpu.wbWidth = w
    cpu.numROBEntries = 192 if w > 2 else 128
    cpu.numIQEntries  = 64
    cpu.LQEntries = 32
    cpu.SQEntries = 32
    cpu.branchPred = make_branch_pred(args.bp)
    t = max(1, int(args.smt_threads))
    cpu.numThreads = t
    system.cpu = [cpu]

# Workload (ARM SE)
def make_proc(path):
    p = Process()
    p.executable = path
    p.cmd = [path]
    return p

if args.cpu_type == "o3" and cpu.numThreads > 1:
    system.cpu[0].workload = [ make_proc(args.binary) for _ in range(cpu.numThreads) ]
else:
    system.cpu[0].workload = make_proc(args.binary)

# v25+ compatible SE setup
try:
    system.workload = SEWorkload.init_compatible(args.binary)
except Exception:
    pass

system.cpu[0].createInterruptController()
system.cpu[0].createThreads()

# Caches + buses
system.cpu[0].icache = L1ICache()
system.cpu[0].dcache = L1DCache()
system.l2cache = L2Cache()
system.l2bus = L2XBar()

system.cpu[0].icache.connectCPU(system.cpu[0])
system.cpu[0].dcache.connectCPU(system.cpu[0])

system.cpu[0].icache.connectBus(system.l2bus)
system.cpu[0].dcache.connectBus(system.l2bus)

system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

# Memory
system.mem = SimpleMemory(range=system.mem_ranges[0], latency='50ns')
system.mem.port = system.membus.mem_side_ports

# System port
system.system_port = system.membus.cpu_side_ports

# Run
root = Root(full_system=False, system=system)
m5.instantiate()
print("Starting simulation...")
ev = m5.simulate()
print(f"Exited @ {m5.curTick()} because {ev.getCause()}")
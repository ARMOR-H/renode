from pyrenode3.wrappers import Analyzer, Emulation, Monitor
from Antmicro.Renode import Emulator
import time
import os
import re

symbol_re = re.compile(r'\d+:\d+:\d+.\d+ \[WARNING\] sysbus: \[cpu: 0x[\d\w]+ \((.+)\)\]')

pipe_path = '/tmp/renode_pipe'
os.mkfifo(pipe_path)

skip_symbols = ['SystemInit']

def scan_for_invalid_access():
    with open(pipe_path, 'r') as pipe:
        while True:
            line = pipe.readline()
            access_warning = symbol_re.match(line)
            if access_warning:
                return access_warning.group(1)
                

def setup():
    e = Emulation()
    m = Monitor()
    m.execute('include @/workspaces/renode/automation/functions.resc')
    m.execute("logFile @/tmp/renode_pipe")

    return e,m

def skip_symbol(m, symbol):
    m.execute('sysbus.cpu.AddSymbolHook "{}" $skip_function_script'.format(symbol))

def run_until_missing_symbol(e, m):
    aya_ppg = e.add_mach('aya_ppg')
    aya_ppg.load_repl('platforms/cpus/stm32wb05_empty.repl')
    aya_ppg.load_elf('/workspaces/renode/automation/aya_ppg.elf')

    for symbol in skip_symbols:
        skip_symbol(m, symbol)

    e.StartAll()
    invalid_access = scan_for_invalid_access()
    return invalid_access

def single_run():
    e,m = setup()
    invalid_access = run_until_missing_symbol(e, m)
    skip_symbols.append(invalid_access)
    return invalid_access

for i in range(5):
    invalid_access = single_run()
    if invalid_access is None:
        break
    print('Invalid access at symbol: {}'.format(invalid_access))
os.remove(pipe_path)
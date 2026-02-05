import asyncio
import os, re
import subprocess

RENODE_EXECUTABLE = os.getenv('RENODE_EXECUTABLE', '/workspaces/renode/renode')
symbol_re = re.compile(r'\d+:\d+:\d+.\d+ \[WARNING\] sysbus: \[cpu: 0x[\d\w]+ \((.+)\)\]')
function_entry_re = re.compile(r'\d+:\d+:\d+.\d+ \[INFO\] cpu: Entering function (\S+)( \(entry\))? at 0x[\d\w]+')

restricted_symbols = []
allowed_symbols = []

class RenodeProcess:
        def __init__(self, executable_path):
            self.executable_path = executable_path
            self.process = None

        async def start(self):
            self.process = await asyncio.create_subprocess_exec(
                self.executable_path,
                '--console',
                '--disable-xwt',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

        async def send_command(self, command):
            if self.process:
                self.process.stdin.write((command + '\n').encode())
                await self.process.stdin.drain()

        async def read_output(self):
            if self.process:
                line = await self.process.stdout.readline()
                return line.decode()
            return None

        async def read_error(self):
            if self.process:
                line = await self.process.stderr.readline()
                return line.decode()
            return None

        async def stop(self):
            if self.process:
                await self.send_command('quit')
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=1)
                except asyncio.TimeoutError:
                    self.process.terminate()

async def scan_for_invalid_access(proc):
    last_symbol = None
    while True:
        line = await proc.read_output()
        if line:
            print('\tLOG: {}'.format(line.strip()))
            function_entry = function_entry_re.match(line)
            if function_entry:
                symbol = function_entry.group(1)
                if symbol != last_symbol:
                    last_symbol = symbol
                    if function_entry.group(2) is not None:
                        print('\tFunction entry: {}'.format(symbol))
                    else:
                        print('\tFunction resume: {}'.format(symbol))
            access_warning = symbol_re.match(line)
            # if access_warning:
            #     offending_symbol = access_warning.group(1)
            #     if offending_symbol not in allowed_symbols:
            #         return offending_symbol
        else:
            print('No output from Renode process.')

async def setup():
    print('Setting up emulation...')
    renode_proc = RenodeProcess(RENODE_EXECUTABLE)
    await renode_proc.start()
    print('Loading macros...')
    await renode_proc.send_command('include @/workspaces/renode/automation/functions.resc')
    return renode_proc

async def create_machine(renode_proc):
    print('Creating machine...')
    await renode_proc.send_command('mach create')
    await renode_proc.send_command('machine LoadPlatformDescription @platforms/cpus/stm32wb05_empty.repl')
    await renode_proc.send_command('sysbus LoadELF @/workspaces/renode/automation/aya_ppg.elf')
    await skip_wait_for_interrupts(renode_proc)
    await enable_function_traces(renode_proc)

async def skip_wait_for_interrupts(proc):
    print('Enabling skip for wait for interrupts...')
    await proc.send_command('sysbus.cpu WfiAsNop True')

async def enable_function_traces(proc):
    print('Enabling function traces...')
    await proc.send_command('sysbus.cpu LogFunctionNames True')

async def skip_symbol(proc, symbol):
    print('Skipping symbol: {}'.format(symbol))
    await proc.send_command('sysbus.cpu AddHook `sysbus GetSymbolAddress "{}" 0` $skip_function_return_0_script'.format(symbol))

async def run_until_missing_symbol(proc):
    print('Running until missing symbol...')
    await proc.send_command('start')
    print('Emulation started, scanning for invalid access...')
    missing_symbol = await scan_for_invalid_access(proc)
    print('Found missing symbol: {}'.format(missing_symbol))
    return missing_symbol


# main coroutine
async def main():

    for i in range(10):
        print('--- Iteration {} ---'.format(i))
        proc = await setup()
        await create_machine(proc)
        for symbol in restricted_symbols:
            await skip_symbol(proc, symbol)
        missing_symbol = await run_until_missing_symbol(proc)
        restricted_symbols.append(missing_symbol)
        await proc.stop()
    

# entry point
if __name__ == '__main__':
    asyncio.run(main())
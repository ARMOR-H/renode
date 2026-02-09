using System;

using Antmicro.Renode.Core;
using Antmicro.Renode.Peripherals.Bus;
using Antmicro.Renode.Peripherals.CPU;

using Newtonsoft.Json;

namespace Antmicro.Renode.WebSockets.Providers
{
    public class RemoteExecutionProvider : IWebSocketAPIProvider
    {
        public RemoteExecutionProvider()
        { }

        public bool Start(WebSocketAPISharedData sharedData)
        {
            this.SharedData = sharedData;
            var emulationManager = EmulationManager.Instance;
            emulationManager.EmulationChanged += EmulationChangedEventHandler;

            EmulationChangedEventHandler();
            return true;
        }

        private void EmulationChangedEventHandler()
        {
            var emulation = EmulationManager.Instance.CurrentEmulation;
            emulation.MachineStateChanged += MachineStateChangedEventHandler;
            emulation.MachineAdded += MachineAddedEventHandler;

            EmulatorStateChangedEvent.RaiseEvent(new EmulatorStateChangedEventData
            {
                Value = "emulation-cleared"
            });
        }

        private void MachineStateChangedEventHandler(IMachine machine, MachineStateChangedEventArgs args)
        {
            switch(args.CurrentState)
            {
            case MachineStateChangedEventArgs.State.Started:
                EmulatorStateChangedEvent.RaiseEvent(new EmulatorStateChangedEventData
                {
                    Value = "machine-started"
                });
                break;

            case MachineStateChangedEventArgs.State.Paused:
                EmulatorStateChangedEvent.RaiseEvent(new EmulatorStateChangedEventData
                {
                    Value = "machine-paused"
                });
                break;
            }
        }

        private void MachineAddedEventHandler(IMachine machine)
        {
            machine.PeripheralsChanged += MachinePeripheralsChangedEventHandler;
            machine.SystemBus.OnUnhandledAccess += UnhandledAccessHandler;
        }

        private void MachinePeripheralsChangedEventHandler(IMachine machine, PeripheralsChangedEventArgs args)
        {
            if(args.Operation == PeripheralsChangedEventArgs.PeripheralChangeType.Addition)
            {
                var cpu = args.Peripheral as TranslationCPU;
                if(cpu != null)
                {
                    cpu.OnFunctionCall += FunctionCallHandler;
                }
            }
        }

        private void UnhandledAccessHandler(UnhandledAccess access)
        {
            UnknownSymbolEvent.RaiseEvent(new UnknownSymbolEventData
            {
                Name = access.Symbol.Name,
                PC = access.PC,
                Write = access.Access == Access.Write,
            });
        }

        private void FunctionCallHandler(Tuple<ulong, Symbol> tuple)
        {
            var pc = tuple.Item1;
            var symbol = tuple.Item2;

            var entry = pc == symbol.Start;
            FunctionCallEvent.RaiseEvent(new FunctionCallEventData
            {
                Name = symbol.Name,
                Entry = entry
            });
        }

        private WebSocketAPISharedData SharedData;

        // 649:  Field '...' is never assigned to, and will always have its default value null
#pragma warning disable 649
        [WebSocketAPIEvent("emulation-state-changed", "1.5.0")]
        private readonly WebSocketAPIEventHandler EmulatorStateChangedEvent;

        [WebSocketAPIEvent("unknown-symbol", "1.5.0")]
        private readonly WebSocketAPIEventHandler UnknownSymbolEvent;

        [WebSocketAPIEvent("function-call", "1.5.0")]
        private readonly WebSocketAPIEventHandler FunctionCallEvent;
#pragma warning restore 649

        private class EmulatorStateChangedEventData
        {
            [JsonProperty("value")]
            public string Value;
        }

        private class UnknownSymbolEventData
        {
            [JsonProperty("name")]
            public string Name;
            [JsonProperty("pc")]
            public ulong PC;
            [JsonProperty("write")]
            public bool Write;
        }

        private class FunctionCallEventData
        {
            [JsonProperty("name")]
            public string Name;
            [JsonProperty("entry")]
            public bool Entry;
        }
    }
}
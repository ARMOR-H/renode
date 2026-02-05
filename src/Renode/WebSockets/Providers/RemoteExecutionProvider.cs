using Antmicro.Renode.Core;

namespace Antmicro.Renode.WebSockets.Providers
{
    public class RemoteExecutionProvider : IWebSocketAPIProvider
    {
        public RemoteExecutionProvider()
        { }

        public bool Start(WebSocketAPISharedData sharedData)
        {
            this.SharedData = sharedData;
            return true;
        }

        private void EmulationChangedEventHandler()
        {
            var emulation = EmulationManager.Instance.CurrentEmulation;
            // emulation.MachineStateChanged
        }

        private void

        private WebSocketAPISharedData SharedData;

        private readonly WebSocketAPIEventHandler EmulatorStateChangedEvent;
        private readonly WebSocketAPIEventHandler UnknownSymbolEvent;
        private readonly WebSocketAPIEventHandler FunctionCallEvent;
    }
}
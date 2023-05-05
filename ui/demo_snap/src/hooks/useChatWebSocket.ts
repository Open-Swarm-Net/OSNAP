import useWebsocket from 'react-use-websocket';
import { JsonValue, WebSocketHook } from 'react-use-websocket/dist/lib/types';

export const useChatWebsocket = (wsURL: string, setMessages: (message: string) => void) => {
    const socket = useWebsocket(wsURL, {
        onOpen: () => console.log('opened'),
        onMessage: (event) => {
            const message = event.data;
            setMessages(message);
        },
        shouldReconnect: (closeEvent) => true,
        reconnectAttempts: 10,
        reconnectInterval: 3000,
    });

    return socket;
};

export const sendMessage = (socket: WebSocketHook<JsonValue | null>, message: string | undefined) => {
    if (message)
        socket.sendMessage(message);
    else console.log('no message to send');
};
import {
  SET_WEBSOCKET,
  SET_WEBSOCKET_CONNECTED,
  SET_WEBSOCKET_DISCONNECTED,
} from '../types'

const initialState = {
  socket: null,
  isConnected: false,
}

export default function (state = initialState, action) {
  switch (action.type) {
    case SET_WEBSOCKET:
      return {
        ...state,
        socket: action.payload,
      }

    case SET_WEBSOCKET_CONNECTED:
      return {
        ...state,
        isConnected: true,
      }

    case SET_WEBSOCKET_DISCONNECTED:
      return {
        ...state,
        isConnected: false,
      }

    default:
      return state
  }
}

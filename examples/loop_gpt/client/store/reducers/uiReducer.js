import {
  OPEN_FILE_UPLOAD_DIALOG,
  CLOSE_FILE_UPLOAD_DIALOG,
  APPEND_WEBSOCKET_MESSAGES,
  CLEAR_WEBSOCKET_MESSAGES,
  SET_FIRST_START,
  SHOW_AGENT_CONFIG_DRAWER,
  HIDE_AGENT_CONFIG_DRAWER,
} from '../types'

const initialState = {
  isStarted: false,
  messages: [],
  fileUploadDialog: {
    isOpen: false,
  },
  agentConfigDrawer: {
    isOpen: false,
    config: {},
    settings: {},
  },
}

export default function (state = initialState, action) {
  switch (action.type) {
    case OPEN_FILE_UPLOAD_DIALOG:
      return {
        ...state,
        fileUploadDialog: {
          isOpen: true,
        },
      }

    case CLOSE_FILE_UPLOAD_DIALOG:
      return {
        ...state,
        fileUploadDialog: {
          isOpen: false,
        },
      }

    case SHOW_AGENT_CONFIG_DRAWER:
      return {
        ...state,
        agentConfigDrawer: {
          isOpen: true,
        },
      }

    case HIDE_AGENT_CONFIG_DRAWER:
      return {
        ...state,
        agentConfigDrawer: {
          isOpen: false,
        },
      }

    case SET_FIRST_START:
      return {
        ...state,
        isStarted: true,
      }

    case CLEAR_WEBSOCKET_MESSAGES:
      return {
        ...state,
        messages: [],
      }

    case APPEND_WEBSOCKET_MESSAGES:
      return {
        ...state,
        messages: [...state.messages, action.payload],
      }

    default:
      return state
  }
}

import {
  SET_AGENT_INIT_STATE,
  RESTORE_AGENT_STATE,
  SAVE_AGENT_STATE,
  SET_CONFIG_ITEM,
} from '../types'

const initialState = {
  config: {},
  initState: false,
  stateHistory: [],
}

export default function (state = initialState, action) {
  switch (action.type) {
    case SET_AGENT_INIT_STATE:
      return {
        ...state,
        initState: action.payload,
      }
    case SAVE_AGENT_STATE:
      return {
        ...state,
        stateHistory: [...state.stateHistory, action.payload],
      }

    case RESTORE_AGENT_STATE:
      return {
        ...state,
        config: action.payload,
      }

    case SET_CONFIG_ITEM:
      let { key, value } = action.payload
      let newState = { ...state }

      if (typeof value !== 'undefined') {
        if (value !== '') {
          newState['config'] = {
            ...newState['config'],
            [key]: value,
          }
        }
      }

      return {
        ...newState,
      }

    default:
      return state
  }
}

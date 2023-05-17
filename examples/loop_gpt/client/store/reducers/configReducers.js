import { SET_CONFIG_ITEM } from '../types'

const initialState = {
  config: {},
  settings: {
    maxcycles: 5
  },
}

export default function (state = initialState, action) {
  switch (action.type) {
    case SET_CONFIG_ITEM:
      let { configType, key, value } = action.payload
      let newState = { ...state }

      if (typeof value !== 'undefined') {
        if (value !== '') {
          newState[configType] = {
            ...newState[configType],
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

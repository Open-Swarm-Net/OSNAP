import { UPDATE_CYCLE_COUNT, UPDATE_AGENT_CYCLE_STATE } from '../types'

const initialState = {
  cycleCount: 0,
  agentCycleState: undefined,
}

export default function (state = initialState, action) {
  switch (action.type) {
    case UPDATE_CYCLE_COUNT:
      return {
        ...state,
        cycleCount: state.cycleCount + 1,
      }

    case UPDATE_AGENT_CYCLE_STATE:
      return {
        ...state,
        agentCycleState: action.payload,
      }

    default:
      return state
  }
}

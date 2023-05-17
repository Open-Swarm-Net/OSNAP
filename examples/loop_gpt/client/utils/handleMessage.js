import { store } from '@/store/store'
import {
  APPEND_WEBSOCKET_MESSAGES,
  SAVE_AGENT_STATE,
  SET_AGENT_INIT_STATE,
  UPDATE_AGENT_CYCLE_STATE,
  UPDATE_CYCLE_COUNT,
} from '@/store/types'
import { parseHistory } from './parseHistory'

export function handleMessage(message) {
  const prop = Object.keys(message)
  const exclusions = ['init_state', 'message']
  const parsed = parseHistory(message)

  if (!!parsed && !exclusions.includes(`${prop}`)) {
    const label = prop.toString().slice(0, -7)
    const {
      cycle,
      plan,
      state,
      staging_response,
      staging_tool,
      tool_response,
    } = message[prop]
    const parsedHistory = parsed.length > 2 ? parsed.slice(-3) : [...parsed]
    const agentResponse = parsedHistory
      .filter((v) => v.role === 'assistant')
      .pop().content
    const payload = {
      [label]: {
        agentResponse,
        parsedHistory,
        cycle,
        state,
        staging_response,
        staging_tool,
        tool_response,
        plan,
      },
    }

    console.log(payload)

    store.dispatch({ type: APPEND_WEBSOCKET_MESSAGES, payload })

    if (label === 'run_tool') {
      store.dispatch({ type: SAVE_AGENT_STATE, payload: message[prop] })
      store.dispatch({ type: UPDATE_AGENT_CYCLE_STATE, payload: message[prop] })
      store.dispatch({ type: UPDATE_CYCLE_COUNT })
    }

    if (label === 'init_resp') {
      store.dispatch({ type: SET_AGENT_INIT_STATE, payload: message[prop] })
      store.dispatch({ type: UPDATE_CYCLE_COUNT })
    }
  } else {
    store.dispatch({ type: APPEND_WEBSOCKET_MESSAGES, payload: { ...message } })
  }
}

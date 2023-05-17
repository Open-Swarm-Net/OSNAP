import { combineReducers } from 'redux'
import uiReducer from './uiReducer'
import agentReducers from './agentReducers'
import socketReducer from './socketReducer'
import cycleReducer from './cycleReducer'
import configReducers from './configReducers'

export default combineReducers({
  uiStates: uiReducer,
  socketStates: socketReducer,
  agentState: agentReducers,
  cycleState: cycleReducer,
  configState: configReducers,
})

import React, { useEffect } from 'react'
import { Box, Typography } from '@mui/material'
import { useDispatch, useSelector } from 'react-redux'
import { DynamicReactJson } from '@/pages/chat'
import { RESTORE_AGENT_STATE } from '@/store/types'

export function AgentConfigComponent() {
  const dispatch = useDispatch()
  const { initState, config: stateConfig, stateHistory } = useSelector((state) => state.agentState)
  const currentCycleState = useSelector(
    (state) => state.cycleState.agentCycleState
  )
  const [lastHistoryEntry] = stateHistory.slice(-1)
  const lastReportedConfig = lastHistoryEntry ? lastHistoryEntry : false

  useEffect(() => {
    if (!stateConfig.goals && !!initState) {
      dispatch({ type: RESTORE_AGENT_STATE, payload: initState })
    }
  }, [stateConfig, initState, dispatch])

  return (
    <Box sx={{ paddingBottom: '1em' }}>
      <Typography variant="h6" component="strong">
        Start Config
      </Typography>

      <Box>
        <DynamicReactJson
          name={'agent_config'}
          src={stateConfig}
          theme={'harmonic'}
          collapsed
        />
      </Box>

      <p>Model: {stateConfig?.model?.model}</p>
      <p>Agent Name: {stateConfig?.name}</p>
      <p>Agent Description: {stateConfig?.description}</p>
      <p>Goals: {stateConfig?.goals}</p>
      <p>Constraints: {stateConfig?.constraints}</p>
      <p>Init Prompt</p>
      <p>Next Prompt</p>
      <p>Tools</p>
      {!!currentCycleState && (
        <p>Staging Tool: {currentCycleState.command?.name}</p>
      )}
      {!!currentCycleState && (
        <p>Args: {JSON.stringify(currentCycleState.command?.args)}</p>
      )}

      <Typography variant="h6" component="strong">
        Last Reported Config
      </Typography>

      <Box>
        <DynamicReactJson
          name={'last_config'}
          src={lastReportedConfig ? lastReportedConfig : {}}
          theme={'harmonic'}
          collapsed
        />
      </Box>
      {!!lastReportedConfig && (
        <p>Staging Tool: {lastReportedConfig.staging_tool?.name}</p>
      )}
      {!!lastReportedConfig && (
        <p>Args: {JSON.stringify(lastReportedConfig.staging_tool?.args)}</p>
      )}
    </Box>
  )
}

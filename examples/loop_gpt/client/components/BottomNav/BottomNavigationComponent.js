import React, { useState } from 'react'
import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material'
import StartIcon from '@mui/icons-material/Start'
import RestoreIcon from '@mui/icons-material/Restore'
import SaveAltIcon from '@mui/icons-material/SaveAlt'
import ArchiveIcon from '@mui/icons-material/Archive'
import CreateIcon from '@mui/icons-material/Create'
import { useDispatch, useSelector } from 'react-redux'
import {
  CLEAR_WEBSOCKET_MESSAGES,
  HIDE_AGENT_CONFIG_DRAWER,
  OPEN_FILE_UPLOAD_DIALOG,
  SET_FIRST_START,
  SHOW_AGENT_CONFIG_DRAWER,
} from '@/store/types'
import { getSocket } from '@/utils/socket'

export function BottomNavigationComponent() {
  const dispatch = useDispatch()
  const state = useSelector((state) => state)
  const [value, setValue] = useState()

  const handleSocketConnect = (websocketUrl) => {
    getSocket(websocketUrl)
  }

  const handleStartClick = () => {
    // Make HTTP POST request to start the chat and obtain WebSocket URL
    fetch(process.env.NEXT_PUBLIC_INIT_CHAT_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const { websocketUrl } = data
        handleSocketConnect(websocketUrl)
      })
      .catch((error) => {
        console.error('Error starting chat:', error)
      })
  }

  return (
    <Paper
      sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }}
      elevation={3}
    >
      <BottomNavigation
        showLabels
        value={value}
        onChange={(_event, newValue) => {
          setValue(newValue)
          if (newValue === 'start') {
            if (!state.uiStates.isStarted) {
              dispatch({ type: CLEAR_WEBSOCKET_MESSAGES }) // clear sample messages
              dispatch({ type: SET_FIRST_START })
            }
            handleStartClick()
          }
          if (newValue === 'load') {
            dispatch({ type: OPEN_FILE_UPLOAD_DIALOG })
          }
          if (newValue === 'configure') {
            const isDrawerOpen = state.uiStates.agentConfigDrawer.isOpen
            if (!isDrawerOpen) {
              dispatch({ type: SHOW_AGENT_CONFIG_DRAWER })
            } else {
              dispatch({ type: HIDE_AGENT_CONFIG_DRAWER })
              setValue(0)
            }
          }
        }}
      >
        <BottomNavigationAction
          value="start"
          label="Start Agent"
          icon={<StartIcon />}
        />
        <BottomNavigationAction
          value="load"
          label="Restore State"
          icon={<RestoreIcon />}
        />
        <BottomNavigationAction
          value="save"
          label="Save Last State"
          icon={<SaveAltIcon />}
          onClick={() => {
            const config = state.agentState.config
            const [lastHistoryEntry] = state.agentState.stateHistory.slice(-1)
            const lastReportedConfig = lastHistoryEntry ? lastHistoryEntry : config
            const jsonConfig = new Blob([JSON.stringify(lastReportedConfig)], {
              type: 'application/json'
            })
            const a = document.createElement('a')
            a.href = URL.createObjectURL(jsonConfig)
            a.download = `${state.agentState.config.name}-config`
            a.click()          
          }}
        />
        <BottomNavigationAction
          value="archive"
          label="Archive Messages"
          icon={<ArchiveIcon />} 
          onClick={() => {
            const messages = state.uiStates.messages
            const jsonConfig = new Blob([JSON.stringify(messages)], {
              type: 'application/json'
            })
            const a = document.createElement('a')
            a.href = URL.createObjectURL(jsonConfig)
            a.download = `${state.agentState.config.name}-messages`
            a.click()
          }}
        />
        <BottomNavigationAction
          value="configure"
          label="Configure Agent"
          icon={<CreateIcon />}
        />
      </BottomNavigation>
    </Paper>
  )
}

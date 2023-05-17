import React from 'react'
import ScrollableFeed from 'react-scrollable-feed'
import { ListItem } from '@mui/material'
import { Paper } from '@mui/material'
import { CycleReportComponent } from './CycleReportComponent'
import { SystemMessageComponent } from './SystemMessageComponent'
import { useSelector } from 'react-redux'

export const MessagesComponent = () => {
  const messages = useSelector((state) => state.uiStates.messages)
  return (
    <ScrollableFeed>
      {messages.map(
        (message, index) =>
          !message.init_state && (
            <Paper
              sx={{ margin: '16px auto' }}
              key={
                message.id ? message.id : `${index}-${new Date().toISOString()}`
              }
            >
              <ListItem disableGutters={true}>
                {!!message.init_resp && CycleReportComponent(message.init_resp)}
                {!!message.run_tool && CycleReportComponent(message.run_tool)}

                {!!message.message && SystemMessageComponent(message.message)}
              </ListItem>
            </Paper>
          )
      )}
    </ScrollableFeed>
  )
}

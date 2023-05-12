import React, { useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Box, Container, Typography } from '@mui/material'

import { useSelector } from 'react-redux'
import { sampleMessages } from '@/sample-data/sample-messages'

import { BottomNavigationComponent } from '../components/BottomNav/BottomNavigationComponent'
import { MessagesComponent } from '../components/MessageView'

import { UploadFileDialog } from '../components/BottomNav/UploadFileDialog'
import { AgentConfigComponent } from '../components/AgentConfig/AgentConfigComponent'
import { AgentConfigDrawer } from '../components/AgentConfig/AgentConfigDrawer'
import { CycleOverviewComponent } from '@/components/AgentConfig/CycleOverviewComponent'
import { handleMessage } from '@/utils/handleMessage'

export const DynamicReactJson = dynamic(import('react-json-view'), {
  ssr: false,
})

const contentAreaHeight = 'calc(90vh  - 100px)'

const Chat = () => {
  const isStarted = useSelector((state) => state.uiStates.isStarted)
  const messages = useSelector((state) => state.uiStates.messages)

  // trace redux states
  const state = useSelector((state) => state)
  useEffect(() => {
    console.log({ state })
  }, [state])

  // load sample messages so we can view page elements.
  // will be cleared on first run and replaced by incoming messages
  useEffect(() => {
    if (!isStarted) {
      if (messages.length === 0) {
        sampleMessages.forEach((msg, index) => {
          // simulate delay
          setTimeout(() => {
            handleMessage(msg)
          }, 1200 * index)
        })
      }
    }
    // console.log(messages)
  }, [isStarted, messages])

  return (
    <Box>
      <Box
        sx={{
          width: '99vw',
          display: 'grid',
          gridTemplateColumns: '60vw 3fr',
          borderBottom: '2px grey solid',
        }}
      >
        <Container>
          <Typography variant="h4" component="h">
            Autonomous GPT Cycle Explorer
          </Typography>
          <Typography variant="subtitle1">
            A user interface to explore the process cycles of self-prompting
            autonomous AI agents, for the purpose of understanding the mechanics
            and creating better initial prompts
          </Typography>
        </Container>
        <Container>
          <Typography variant="h4" component="h2">
            Agent Setup
          </Typography>
        </Container>
      </Box>

      <Box
        sx={{ width: '98vw', display: 'grid', gridTemplateColumns: '60vw 3fr' }}
      >
        <Box>
          <Container sx={{ height: contentAreaHeight }}>
            <MessagesComponent />
          </Container>
        </Box>
        <Container sx={{ overflowY: 'scroll', height: contentAreaHeight }}>
          <AgentConfigComponent />
          <CycleOverviewComponent />
        </Container>
      </Box>
      <BottomNavigationComponent />
      <UploadFileDialog />
      <AgentConfigDrawer />
    </Box>
  )
}

export default Chat

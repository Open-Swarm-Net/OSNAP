import React from 'react'
import WysiwygIcon from '@mui/icons-material/Wysiwyg'
import { DynamicReactJson } from '@/pages/chat'
import { CycleNumberComponent } from './shared/CycleNumberComponent'
import { CycleStageContainer } from './shared/CycleStageContainer'
import { Box, Card, CardContent, CardHeader } from '@mui/material'
import { RowPanelContainer } from './shared/RowPanelContainer'
import { ThoughtsMessage } from './shared/ThoughtsMessageComponent'
import { IconListLine } from './shared/IconListLine'
import HistoryIcon from '@mui/icons-material/History'

export function CycleReportComponent(message) {
  const {
    agentResponse,
    parsedHistory,
    cycle,
    state,
    staging_response,
    staging_tool,
    tool_response,
    plan,
  } = message
  const { thoughts, command } = agentResponse

  return (
    <CycleStageContainer>
      <CycleNumberComponent cycleNumber={cycle} />

      <Box sx={{ display: 'flex' }}>
        <IconListLine icon={<WysiwygIcon />}>
          <span>Cycle report: </span>
          <DynamicReactJson
            name={'run_tool'}
            src={message}
            theme={'harmonic'}
            collapsed
          />
        </IconListLine>

        <IconListLine icon={<HistoryIcon />}>
          <span>Conversation History: </span>
          <DynamicReactJson
            name={'history'}
            src={parsedHistory}
            theme={'harmonic'}
            collapsed
          />
        </IconListLine>
      </Box>

      <RowPanelContainer panelCount={'5'}>
        <ThoughtsMessage thoughts={thoughts} />
      </RowPanelContainer>
      <RowPanelContainer panelCount={'2'}>
        <Card>
          <CardHeader title={'Tool Results'} />
          <CardContent>
            <pre style={{ whiteSpace: 'normal' }}>
              {JSON.stringify(tool_response, null, 4)}
            </pre>
          </CardContent>
        </Card>

        <Card>
          <CardHeader title={'Staging Tool'} />
          <CardContent>
            <pre style={{ whiteSpace: 'normal' }}>
              {JSON.stringify(staging_tool, null, 4)}
            </pre>
          </CardContent>
        </Card>
      </RowPanelContainer>

      {/* {!!message.this_cycle.next_thoughts && (
        <>
          <IconListLine icon={<NextPlanIcon />}>Next thoughts: </IconListLine>
          <RowPanelContainer panelCount={'5'}>
            <ThoughtsMessage thoughts={message.this_cycle.next_thoughts} />
          </RowPanelContainer>
        </>
      )} */}
    </CycleStageContainer>
  )
}

const CycleProgress = ({ data }) => {
  const { cycle_progress, id } = data
  const progressArr = cycle_progress
    .split(/\r?\n|\r|\n/g)
    .map((s) => s.slice(2))
  return progressArr.map((v, i) => <p key={`${id}-progress-${i}`}>{v}</p>)
}

const CycleToolReport = ({ data }) => {
  const { staging_tool, command, tool_results } = data

  return (
    <>
      {/* <Card>
        <CardHeader title={'Staging Tool'} />
        <CardContent>
          <pre style={{ whiteSpace: 'normal' }}>{JSON.stringify(staging_tool, null, 4)}</pre>
        </CardContent>
      </Card> */}
      {/* <Card>
        <CardHeader title={'Progress'} />
        <CardContent>
          <CycleProgress {...{ data }} />
        </CardContent>
      </Card> */}
      {/* <Card>
        <CardHeader title={'Command'} />
        <CardContent>
          <pre style={{ whiteSpace: 'normal' }}>
            {JSON.stringify(command, null, 4)}
          </pre>
        </CardContent>
      </Card> */}
      {/* <Card>
        <CardHeader title={'Next Command'} />
        <CardContent>
          <pre style={{ whiteSpace: 'normal' }}>
            {JSON.stringify(next_command, null, 4)}
          </pre>
        </CardContent>
      </Card> */}
    </>
  )
}

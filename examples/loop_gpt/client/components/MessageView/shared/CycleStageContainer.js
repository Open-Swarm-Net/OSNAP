import { Box } from '@mui/material'

export function CycleStageContainer(props) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column' }}>
      {props.children}
    </Box>
  )
}

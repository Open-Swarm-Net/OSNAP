import React from 'react'
import { Box, Typography } from '@mui/material'
import { useSelector } from 'react-redux'

export function CycleOverviewComponent() {
  const state = useSelector((state) => state.cycleState)
  return (
    <Box>
      <Typography variant="h6" component="strong">
        Cycles
      </Typography>

      <p>Number of Cycles: {state.cycleCount}</p>
    </Box>
  )
}

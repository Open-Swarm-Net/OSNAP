import React from 'react'
import { Box, Chip } from '@mui/material'
import UpdateIcon from '@mui/icons-material/Update'

export const CycleNumberComponent = ({ cycleNumber }) => {
  return (
    <Box sx={{ width: '150px' }}>
      <Chip
        sx={{ marginBottom: '8px', marginLeft: '16px' }}
        variant="outlined"
        icon={<UpdateIcon />}
        label={`Cycle #${cycleNumber}`}
      />
    </Box>
  )
}

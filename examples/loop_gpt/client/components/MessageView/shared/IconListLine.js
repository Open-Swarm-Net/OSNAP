import React from 'react'
import { Box, ListItemIcon, ListItemText } from '@mui/material'

export function IconListLine(props) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', padding: '16px' }}>
      <ListItemText>
        <Box sx={{ display: 'flex' }}>
          <ListItemIcon>
            {/* <WysiwygIcon /> */}
            {props.icon}
          </ListItemIcon>
          {props.children}
        </Box>
      </ListItemText>
    </Box>
  )
}

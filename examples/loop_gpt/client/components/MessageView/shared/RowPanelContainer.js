import React, { useEffect, useState } from 'react'
import { Container } from '@mui/material'

export function RowPanelContainer({ children, panelCount }) {
  const [value, setValue] = useState(5)
  useEffect(() => {
    if (panelCount) {
      setValue(panelCount)
    }
  }, [panelCount])
  return (
    <Container
      sx={{
        border: 'grey.500 solid 1px',
        borderRadius: '16px',
        padding: '16px',
        display: 'grid',
        gap: '8px',
        gridTemplateColumns: `repeat(${value}, 1fr)`,
        justifyContent: 'space-evenly',
      }}
    >
      {children}
    </Container>
  )
}

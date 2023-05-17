import React from 'react'
import { Card, CardContent, CardHeader } from '@mui/material'

export const ThoughtsMessage = ({ thoughts }) => {
  const { text, reasoning, progress, plan, speak, id, cycle } = thoughts
  const thoughtForms = Object.assign({}, thoughts)
  delete thoughtForms.id
  delete thoughtForms.cycle

  return Object.keys(thoughtForms).map((key, index) => (
    <Card key={`${id}-${key}-${index}`}>
      <CardHeader title={key.toUpperCase()} />
      <CardContent>
        <pre style={{ whiteSpace: 'normal' }}>{thoughtForms[key]}</pre>
      </CardContent>
    </Card>
  ))
}

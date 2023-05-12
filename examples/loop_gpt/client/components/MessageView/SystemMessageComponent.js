import React from 'react'
import NotificationsIcon from '@mui/icons-material/Notifications'
import { IconListLine } from './shared/IconListLine'

export function SystemMessageComponent(message) {
  return (
    <IconListLine icon={<NotificationsIcon />}>{message.content}</IconListLine>
  )
}

import React, { useEffect, useState } from 'react'
import {
  Box,
  Container,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  TextField,
  Typography,
} from '@mui/material'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import SaveIcon from '@mui/icons-material/Save'
import ModelTrainingIcon from '@mui/icons-material/ModelTraining'
import AndroidIcon from '@mui/icons-material/Android'
import DescriptionIcon from '@mui/icons-material/Description'
import AddTaskIcon from '@mui/icons-material/AddTask'
import BlockIcon from '@mui/icons-material/Block'
import HandymanIcon from '@mui/icons-material/Handyman'

import Forward5Icon from '@mui/icons-material/Forward5'

import { useDispatch, useSelector } from 'react-redux'
import { HIDE_AGENT_CONFIG_DRAWER, SET_CONFIG_ITEM } from '@/store/types'

const drawerWidth = '25vw'

export function AgentConfigDrawer() {
  const isDrawerOpen = useSelector(
    (state) => state.uiStates.agentConfigDrawer.isOpen
  )
  const dispatch = useDispatch()

  const handleDrawerClose = () => {
    dispatch({ type: HIDE_AGENT_CONFIG_DRAWER })
  }

  return (
    <Drawer
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
      variant="persistent"
      anchor="right"
      open={isDrawerOpen}
      onClose={handleDrawerClose}
    >
      <Box>
        <IconButton onClick={handleDrawerClose}>
          <ChevronRightIcon />
        </IconButton>
      </Box>
      <Divider />
      <Container sx={{ padding: '8px' }}>
        <Typography variant="h6" component="strong">
          Configure Agent Initial State
        </Typography>
      </Container>
      <List>
        {[
          { text: 'Model', icon: <ModelTrainingIcon />, id: 'config-model' },
          { text: 'Agent Name', icon: <AndroidIcon />, id: 'config-name' },
          {
            text: 'Description',
            icon: <DescriptionIcon />,
            id: 'config-description',
          },
          { text: 'Goals', icon: <AddTaskIcon />, id: 'config-goals' },
          {
            text: 'Constraints',
            icon: <BlockIcon />,
            id: 'config-constraints',
          },
          { text: 'Tools', icon: <HandymanIcon />, id: 'config-tools' },
        ].map((value, index) => EditableListItem(value))}
      </List>
      <Divider />
      <Container sx={{ padding: '8px' }}>
        <Typography variant="h6" component="strong">
          Other Settings
        </Typography>
      </Container>
      <List>
        {[
          {
            text: 'Cycles Per Run',
            icon: <Forward5Icon />,
            id: 'settings-maxcycles',
          },
        ].map((value, index) => EditableListItem(value))}
      </List>
    </Drawer>
  )
}
function EditableListItem(value) {
  const state = useSelector((state) => state.configState)
  const agentConfig = useSelector((state) => state.agentState.config)
  const exclusions = ['model', 'tools', 'history']
  const dispatch = useDispatch()
  const { text, icon, id } = value

  const idStrArr = id.split('-')
  const configType = idStrArr[0]
  const key = idStrArr.slice(1)[0]
  const fieldValue =
    !exclusions.includes(key) && (state[configType]?.[key] || agentConfig[key])

  const [isEditing, setIsEditing] = useState(false)
  const [inputValue, setInputValue] = useState('')

  const setConfigItem = (value) => {
    dispatch({
      type: SET_CONFIG_ITEM,
      payload: { configType, key, value },
    })
  }

  const handleEditStart = () => {
    setIsEditing(true)
  }

  const handleEditStop = () => {
    if (inputValue) {
      setConfigItem(inputValue)
    }
    setIsEditing((prevState) => !prevState)
  }

  const handleInputChange = (e) => {
    const { target } = e
    const { value } = target
    setInputValue(value)
  }

  useEffect(() => {
    if (!exclusions.includes(key)) {
      setInputValue(fieldValue)
      setConfigItem(fieldValue)
    }
  }, [key, fieldValue])

  return (
    <ListItem key={text} disablePadding>
      <ListItemButton sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <ListItemIcon>{icon}</ListItemIcon>
        {!fieldValue ? EditField() : !isEditing ? DisplayField() : EditField()}
      </ListItemButton>
    </ListItem>
  )

  function EditField() {
    return (
      <>
        <TextField
          sx={{ width: '100%' }}
          placeholder={text}
          defaultValue={inputValue}
          onFocus={handleEditStart}
          onBlur={handleInputChange}
          id={id}
        />
        <IconButton onClick={handleEditStop}>
          <SaveIcon />
        </IconButton>
      </>
    )
  }

  function DisplayField() {
    return (
      <ListItemText
        onClick={handleEditStart}
        primary={!fieldValue ? text : `${text}: ${fieldValue}`}
      />
    )
  }
}

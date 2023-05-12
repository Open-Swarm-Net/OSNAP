export function parseHistory(message) {
  const prop = Object.keys(message)
  const data = message[prop]
  const { history, type } = data
  let formattedEntries = []

  if (type === 'agent') {
    history.map((entry) => {
      let formattedEntry
      try {
        let parsedContent = JSON.parse(entry.content)
        formattedEntry = {}
        formattedEntry.role = entry.role
        formattedEntry.content = parsedContent
      } catch (error) {
        try {
          let parsedContent = JSON.parse(JSON.parse(entry.content))
          formattedEntry = {}
          formattedEntry.role = entry.role
          formattedEntry.content = parsedContent
        } catch (error) {
          formattedEntry = {}
          formattedEntry.role = entry.role
          formattedEntry.content = entry.content
        }
      }

      !!formattedEntry && formattedEntries.push(formattedEntry)
    })

    return formattedEntries
  }
}

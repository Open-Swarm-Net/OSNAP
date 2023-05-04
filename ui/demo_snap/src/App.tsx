import React from 'react';
import { LoadingSpinner } from './components/loadingSpinner'
type Agent = {
  name: string,
  id: string,
  tools: string[],
  description: string,
  scope: string,
}

function App() {

  const [loading, setLoading] = React.useState(false)
  const [agents, setAgents] = React.useState<Agent[]>([])
  const controller = new AbortController()
  const signal = controller.signal

  const urls = ['http://localhost:8000/agents', 'http://localhost:8005/agents']

  const fetchAgents = async (signal: AbortSignal) => {
    setLoading(true)
    Promise.all(
      urls.map(url => fetch(url, { signal })))
      .then(responses => Promise.all(responses.map(res => res.json())))
      .then(data => {
        setAgents(data.flat() as Agent[])
        console.log(data.flat())

        setTimeout(() => {//simulate longer loading time
          setLoading(false)
        }, 500)
      }
      )
      .catch(err => {
        setLoading(false)
        console.log(err)
      })
  }

  React.useEffect(() => {
    fetchAgents(signal)

    return () => {
      controller.abort()
      setAgents([])
    }
  }, [])

  return (
    <div className="flex flex-col items-center bg-base min-h-screen text-primary">
      <div className="flex flex-col items-center justify-center w-full h-16 bg-neutral">
        <h1 className="text-2xl font-bold">OSNAP</h1>
        <div className={`absolute top-1/3 w-1/3 h-1/3 bg-accent rounded-md ${loading ? 'flex flex-col justify-center' : null}`} >
          {loading ? <LoadingSpinner /> : agents.map((agent: any) => {
            return (
              <div className='flex flex-col items-center justify-center'>
                <pre>{agent.name}</pre>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  );
}

export default App;

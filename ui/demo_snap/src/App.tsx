import React from 'react';
import { LoadingSpinner } from './components/loadingSpinner'
type Agent = {
  agent_name: string,
  agent_id: string,
  tools: string[],
  description: string,
  invoke_endpoint: string,
}

function App() {

  const [loding, setLoding] = React.useState(false)
  const [agents, setAgents] = React.useState<Agent[]>([])
  const controller = new AbortController()
  const signal = controller.signal

  const urls = ['http://localhost:8000/agents', 'http://localhost:8005/agents']

  const fetchAgents = async (signal: AbortSignal) => {
    setLoding(true)
    Promise.all(urls.map(url => fetch(url)))
      .then(responses => Promise.all(responses.map(res => res.json())))
      .then(data => {
        setAgents(data as Agent[])

        setTimeout(() => {//simulate longer loading time
          setLoding(false)
        }, 500)
      }
      )
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
        <div className={`absolute top-1/3 w-1/3 h-1/3 bg-accent rounded-md ${loding ? 'flex flex-col justify-center' : null}`} >
          {loding ? <LoadingSpinner /> : agents.map((agent: any) => {
            return (
              <div className='flex flex-col items-center justify-center'>
                <pre>{agent.agent_name}</pre>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  );
}

export default App;

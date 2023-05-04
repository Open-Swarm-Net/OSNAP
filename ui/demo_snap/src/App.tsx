import React from 'react'
import { LoadingSpinner } from './components/loadingSpinner'
import { useChatWebsocket, sendMessage } from './components/useChatWebSocket'
import useFetchAgents from './components/useFetchAgents'


const wsURL = `ws://localhost:8000/ws/${Date.now()}`

function App() {

  const urls = ['http://localhost:8000/agents', 'http://localhost:8005/agents']

  const [messages, setMessages] = React.useState<string>()
  const textRef = React.useRef<HTMLInputElement>(null)
  const { loading, agents } = useFetchAgents({ urls: urls })
  const socket = useChatWebsocket(wsURL, setMessages)

  return (
    <div className="flex flex-col items-center bg-base min-h-screen text-primary">
      <div className="flex flex-col items-center justify-center w-full h-16 bg-neutral">
        <h1 className="text-2xl font-bold">OSNAP</h1>
        <div>
          {socket.readyState === 1 ? 'connected' : 'not connected'}
        </div>
      </div>
      <input ref={textRef} type="text" />
      <button className='btn btn-outline btn-primary m-1' onClick={() => { sendMessage(socket, textRef.current?.value) }}>Send</button>
      <div className='relative flex flex-col items-center'>
        <div className=' top-1/3 w-[400px] m-1 bg-accent rounded-md flex justify-center'>
          <p>{messages}</p>
        </div>
      </div>
      <div className={`relative  bg-neutral w-4/5 rounded-md ${loading ? 'flex flex-col justify-center' : null}`} >
        {loading ? <LoadingSpinner /> : agents?.map((agent: any) => {
          return (
            <div className='flex flex-col items-center justify-center'>
              <pre>{agent.name}</pre>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default App

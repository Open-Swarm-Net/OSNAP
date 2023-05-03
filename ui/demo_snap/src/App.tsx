import React from 'react';

function App() {
  const [loding, setLoding] = React.useState(false)
  const [senderAgents, setSenderAgents] = React.useState([])
  const [receiverAgents, setReceiverAgents] = React.useState([])

  const fetchData = async () => {
    setLoding(true)
    const res = await fetch('http://localhost:8005/agents', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    }
    )
    const data = await res.json()
    setSenderAgents(data);
    setLoding(false)
    console.log(data)
  }

  React.useEffect(() => {
    fetchData()

    return () => {
      setSenderAgents([])
    }
  }, [])
  return (
    <div className="flex flex-col items-center bg-accent min-h-screen text-white">
      <div className="min-w-screen h-36">
        <h1 className="text-primary text-3xl p-3 font-serif font-extrabold">DemOsnap</h1>
      </div>
      <div className="border-2 border-gray-600 focus:border-white w-screen h-16 rounded-md flex items-center" tabIndex={0}>
        <input tabIndex={0} type="text" placeholder="Endpoint" className="input w-full max-w-xs bg-neutral border-2 border-gray-600 focus:border-white" />
        <button className="btn btn-primary btn-outline ">Connect</button>
      </div>
      <div className="border-2 w-[49%] border-gray-600 focus:border-white  left-0 m-1 fixed top-56 h-96 rounded-md flex flex-col items-center"
        tabIndex={2}>
        <h1>Sender</h1>
        {loding ? <h1>Loading...</h1> : senderAgents.map((agent: any) => {
          return (
            <div className="flex flex-col items-center justify-center h-fit p-1">
              {agent.AgentName}
            </div>
          )
        })}

      </div>
      <div className="border-2 border-gray-600 w-[49%] right-0 m-1 focus:border-white fixed top-56 h-96 rounded-md flex flex-col items-center"
        tabIndex={3}>
        <h1>Receiver</h1>
        <div className="relative border-2 border-gray-600 w-[99%] top-56 h-32   focus:border-white  rounded-md flex flex-col items-center"></div>
      </div>
    </div>
  );
}

export default App;

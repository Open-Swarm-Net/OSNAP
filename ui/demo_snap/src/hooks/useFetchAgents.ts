import React from 'react'

type Agent = {
    name: string,
    id: string,
    tools: string[],
    description: string,
    scope: string,
}

type Props = {
    urls: string[]
}

const useFetchAgents = (props: Props) => {

    const [loading, setLoading] = React.useState(false)
    const [agents, setAgents] = React.useState<Agent[]>([])

    const controller = new AbortController()
    const signal = controller.signal

    const fetchAgents = async (signal: AbortSignal) => {
        setLoading(true)
        Promise.all(
            props.urls.map(url => fetch(url, { signal })))
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
        }
    }, [])

    return { loading, agents }

}

export default useFetchAgents
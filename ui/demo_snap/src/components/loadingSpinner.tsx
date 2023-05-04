

export const LoadingSpinner = () => {
    return (<div className="relative flex flex-col items-center justify-center">
        <div className="radial-progress text-primary animate-spin " style={{ '--value': 70 }}></div>
    </div>
    )
}


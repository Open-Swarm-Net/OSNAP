from fastapi import FastAPI

app = FastAPI()


# Describes the agent's role
@app.get("/info")
async def root():
    return {"message": "Hello World"}

# Describe the agent's available tools
@app.get("/tools")
async def root():
    return {"message": "Hello World"}

# Run a certain task
@app.post("/run")
async def root():
    return {"message": "Hello World"}

# Listen for task results distributed to other agents
@app.get("/listen")
async def root():
    return {"message": "Hello World"}

# Agents try and agree they are done
@app.get("/finish")
async def root():
    return {"message": "Hello World"}
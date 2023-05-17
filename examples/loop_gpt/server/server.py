# import FastAPI

from loopgpt import Agent


# app = FastAPI()

# # uvicorn server:app --reload --host 0.0.0.0 --port 8081

agent = Agent(
    name="ResearchGPT",
    description="an AI assistant that researches and finds the best tech products",
    goals=[
        "Search for the best headphones on Google",
        "Analyze specs, prices and reviews to find the top 5 best headphones",
        "Write the list of the top 5 best headphones and their prices to a file",
        "Summarize the pros and cons of each headphone and write it to a different file called 'summary.txt'",
    ],
)

agent.cli()

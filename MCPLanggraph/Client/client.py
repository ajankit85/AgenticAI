from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain.agents import create_agent
import asyncio
import os

# Initialize Environment Variables
from dotenv import load_dotenv
load_dotenv()

async def main():
    # Initialize the MCP Client
    mcp_client = MultiServerMCPClient(
        {
            "MathServer":{
                "command": "python",
                "args": ["../tools/mathserver.py"], ## Ensure correct absolute path
                "transport": "stdio"
            },        
            "WeatherServer": {                
                "url": "http://localhost:8000/mcp", ## Ensure server is running here
                "transport": "streamable-http"
            }
        }
    )   

    # Initialize the Groq LLM
    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")    
    llm = ChatGroq(model="openai/gpt-oss-120b")    

    # Create an Agent using the MCP Client and the Groq LLM
    tools=await mcp_client.get_tools()    
    agent = create_agent(llm, tools)

    # Run the Agent with a sample query
    #response = await agent.run("What is the current status of all servers?")
    #print(response)

    # Test Math Server
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print("Math response:", math_response['messages'][-1].content)

    # Test Weather Server
    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in Indore in Fahrenheit?"}]}
    )
    print("Weather response:", weather_response['messages'][-1].content)

asyncio.run(main())
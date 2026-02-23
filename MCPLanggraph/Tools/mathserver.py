from mcp.server.fastmcp import FastMCP

mcp=FastMCP("MathServer")

@mcp.tool()
def add(a:int,b:int)->int:
    """_summary_
    Add two numbers
    """
    return a + b

@mcp.tool()
def multiple(a:int,b:int)-> int:
    """Multiply two numbers"""
    return a * b


@mcp.tool()
def subtract(a:int,b:int)-> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool()
def divide(a:int,b:int)-> int:
    """Divide two numbers"""
    return a // b if b != 0 else 0


#The transport="stdio" argument tells the server to:
#Use standard input/output (stdin and stdout) to receive and respond to tool function calls.

if __name__=="__main__":
    mcp.run(transport="stdio")
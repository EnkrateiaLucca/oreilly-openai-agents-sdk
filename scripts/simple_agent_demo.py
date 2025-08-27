from agents import Agent, Runner, WebSearchTool, function_tool, guardrail

@function_tool
def submit_refund_request(item_id: str, reason: str):
    # Your refund logic goes here
    return "success"

support_agent = Agent(
    name="Support & Returns",
    instructions="You are a support agent who can submit refunds [...]",
    tools=[submit_refund_request],
)

shopping_agent = Agent(
    name="Shopping Assistant",
    instructions="You are a shopping assistant who can search the web [...]",
    tools=[WebSearchTool()],
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route the user to the correct agent.",
    handoffs=[shopping_agent, support_agent],
)

output = Runner.run_sync(
    starting_agent=triage_agent,
    input="What shoes might work best with my outfit so far?",
)

print(output)
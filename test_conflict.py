#!/usr/bin/env python3

from src.agents.conflict_008 import conflict_agent


def test_conflict_agent():
    """Test the conflict agent directly"""

    # Test message - asking to check for conflicts
    test_query = (
        "Check for scheduling conflicts for painting task in zone B.200 at 15:00-17:00"
    )

    try:
        print("🔍 Testing Conflict Agent...")
        print(f"Query: {test_query}")
        print("-" * 50)

        # Invoke the conflict agent directly
        result = conflict_agent.invoke({"messages": [("human", test_query)]})

        print("✅ Conflict Agent Response:")
        print(result["messages"][-1].content)

    except Exception as e:
        print(f"❌ Error testing conflict agent: {e}")


if __name__ == "__main__":
    test_conflict_agent()

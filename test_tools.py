#!/usr/bin/env python3
"""
Test script to evaluate LLM tool selection and hallucination resistance
"""

import json
import time
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
import tools.manager as t

# Test cases to evaluate tool selection
TEST_CASES = [
    # Distance/Duration queries - should use distance_matrix_tool
    {
        "query": "How long does it take to drive from Paris to Lyon?",
        "expected_tool": "distance_matrix",
        "category": "distance",
    },
    {
        "query": "What's the distance between Eiffel Tower and Arc de Triomphe?",
        "expected_tool": "distance_matrix",
        "category": "distance",
    },
    # Places search - should use places_nearby_tool
    {
        "query": "Find restaurants near the Louvre Museum",
        "expected_tool": "places_nearby",
        "category": "places",
    },
    {
        "query": "Show me parks around Champs-Élysées within 500m",
        "expected_tool": "places_nearby",
        "category": "places",
    },
    # Address to coordinates - should use geocode_tool
    {
        "query": "What are the coordinates of 5 Place Jules Massenet, Paris?",
        "expected_tool": "geocode",
        "category": "geocoding",
    },
    # Coordinates to address - should use reverse_geocode_tool
    {
        "query": "What's the address at coordinates 48.8566, 2.3522?",
        "expected_tool": "reverse_geocoding",
        "category": "reverse_geocoding",
    },
    # Ambiguous/trick questions - test hallucination resistance
    {
        "query": "What's the weather like in Paris?",
        "expected_tool": None,  # No weather tool available
        "category": "invalid",
    },
    {
        "query": "Book me a restaurant reservation",
        "expected_tool": None,  # No booking tool available
        "category": "invalid",
    },
]


def setup_agent():
    """Set up the LLM agent with tools"""
    llm = ChatAnthropic(
        model_name="claude-3-5-haiku-20241022",  # Use newer, less loade # type: ignored model
        temperature=0,  # Reduce randomness for consistent testing
        # timeout=60,  # Increase timeout
        max_retries=3,  # Add retries
    )

    tools = [
        t.distance_matrix_tool,
        t.places_nearby_tool,
        t.geocode_tool,
        t.reverse_geocode_tool,
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful assistant with access to location and mapping tools.
        
                Available tools:
                - distance_matrix: Get distance/duration between two locations
                - places_nearby: Find places near a location  
                - geocode: Convert address to coordinates
                - reverse_geocoding: Convert coordinates to address
                
                IMPORTANT: Only use the tools you have access to. If you cannot help with a request using your available tools, say so clearly.""",
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def run_tests():
    """Run all test cases and evaluate results"""
    agent_executor = setup_agent()
    results = []

    print("🧪 Starting LLM Tool Selection Tests\n")
    print("=" * 60)

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n📋 Test {i}/{len(TEST_CASES)}: {test_case['category']}")
        print(f"Query: {test_case['query']}")
        print(f"Expected tool: {test_case['expected_tool']}")
        print("-" * 40)

        try:
            # Run the query
            response = agent_executor.invoke({"input": test_case["query"]})

            # Extract tools used (this is a simplified check)
            used_tools = []
            if "intermediate_steps" in response:
                for step in response["intermediate_steps"]:
                    if hasattr(step[0], "tool"):
                        used_tools.append(step[0].tool)

            # Evaluate result
            test_result = {
                "test_id": i,
                "query": test_case["query"],
                "expected_tool": test_case["expected_tool"],
                "used_tools": used_tools,
                "response": response["output"],
                "category": test_case["category"],
            }

            # Check if correct tool was used
            if test_case["expected_tool"]:
                correct = test_case["expected_tool"] in [tool for tool in used_tools]
                test_result["correct_tool_used"] = correct
                status = "✅ PASS" if correct else "❌ FAIL"
            else:
                # For invalid queries, success means no tools were used
                correct = len(used_tools) == 0
                test_result["correct_tool_used"] = correct
                status = "✅ PASS" if correct else "❌ FAIL (hallucination)"

            print(f"Status: {status}")
            print(f"Tools used: {used_tools}")
            print(f"Response: {response['output'][:100]}...")

            results.append(test_result)

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append(
                {
                    "test_id": i,
                    "query": test_case["query"],
                    "expected_tool": test_case["expected_tool"],
                    "error": str(e),
                    "category": test_case["category"],
                    "correct_tool_used": False,
                }
            )

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r.get("correct_tool_used", False))
    total = len(results)
    success_rate = (passed / total) * 100

    print(f"Tests passed: {passed}/{total} ({success_rate:.1f}%)")

    # Category breakdown
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "total": 0}
        categories[cat]["total"] += 1
        if result.get("correct_tool_used", False):
            categories[cat]["passed"] += 1

    print("\n📈 Results by category:")
    for cat, stats in categories.items():
        rate = (stats["passed"] / stats["total"]) * 100
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")

    # Save detailed results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to test_results.json")

    return results


if __name__ == "__main__":
    run_tests()

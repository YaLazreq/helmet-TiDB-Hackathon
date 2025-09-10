#!/usr/bin/env python3
"""
Simple test file to verify vector search functions work correctly.
Tests find_best_workers, search_similar_tasks, and search_similar_users.
"""

import sys
import os
import json

# Add paths
sys.path.append("/Users/yan/Development/TiDB/tiDB-Hackathon/src/mcp/mcp_db")
sys.path.append(
    "/Users/yan/Development/TiDB/tiDB-Hackathon/src/mcp/mcp_db/tools/embedding"
)

from src.mcp.mcp_db.tools.embedding.repositories.find_best_workers import (
    find_best_workers_for_task,
)
from src.mcp.mcp_db.tools.embedding.repositories import search_similar_tasks
from src.mcp.mcp_db.tools.embedding.vector import TiDBVectorManager


def test_find_best_workers():
    """Test finding best workers for a task"""
    print("🔍 Testing find_best_workers_for_task...")

    result = find_best_workers_for_task(
        title="Office Lighting Repair",
        description="Replace broken fluorescent bulbs in conference room",
        skill_requirements=["electrical_installation", "lighting"],
        trade_category="electrical",
        k=3,
    )

    data = json.loads(result)
    if data["success"]:
        print(f"✅ Found {data['returned_workers']} workers")
        for worker in data["best_workers"]:
            print(f"   - {worker['name']}: {worker['similarity_score']}% match")
    else:
        print(f"❌ Error: {data['error']}")


def test_search_similar_tasks():
    """Test searching similar tasks"""
    print("\n🔍 Testing search_similar_tasks...")

    result = search_similar_tasks(query="electrical lighting repair office", k=3)

    data = json.loads(result)
    if data["success"]:
        print(f"✅ Found {data['total_results']} similar tasks")
        for task in data["results"]:
            print(f"   - Task {task['task_id']}: {task['similarity_score']}% match")
    else:
        print(f"❌ Error: {data['error']}")


def test_search_similar_users():
    """Test searching similar users directly"""
    print("\n🔍 Testing search_similar_users...")

    try:
        vm = TiDBVectorManager()
        results = vm.search_similar_users("electrician lighting repair", k=3)

        print(f"✅ Found {len(results)} similar users")
        for result in results:
            similarity = (1 - result.distance) * 100
            name = result.metadata.get("name", "Unknown")
            print(f"   - {name}: {similarity:.1f}% match")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests"""
    print("🧪 SIMPLE VECTOR SEARCH TESTS")
    print("=" * 50)

    # Test 1: Find best workers
    test_find_best_workers()

    # # Test 2: Search similar tasks
    # test_search_similar_tasks()

    # # Test 3: Search similar users
    # test_search_similar_users()

    print("\n" + "=" * 50)
    print("✅ Tests completed!")


if __name__ == "__main__":
    main()

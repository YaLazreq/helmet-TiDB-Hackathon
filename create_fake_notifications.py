#!/usr/bin/env python3
"""
Script to create fake notifications in the database for testing purposes.
Based on the notification schema with title, what_you_need_to_know, what_we_can_trigger, action_list, etc.
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta

# Add path to access MCP tools
sys.path.append("/Users/yan/Development/TiDB/tiDB-Hackathon/src/mcp/mcp_db")

# Import the notification creation tool
from src.mcp.mcp_db.tools.notifications.repositories.create_notification import (
    create_notification,
)


def generate_fake_notifications():
    """Generate a variety of fake notifications for testing"""

    notifications_data = [
        # Task Assignment Notifications
        {
            "title": "Electrical Work Assignment",
            "what_you_need_to_know": "New electrical installation task has been assigned to Zone B.200. Worker John Doe needs to complete wiring by Friday.",
            "what_we_can_trigger": "Accept assignment, request reassignment, or mark as completed",
            "action_list": [
                {
                    "action": "update_task",
                    "parameters": {"task_id": 101, "status": "accepted"},
                },
                {
                    "action": "update_task",
                    "parameters": {"task_id": 101, "status": "declined"},
                },
                {
                    "action": "request_reassignment",
                    "parameters": {"task_id": 101, "reason": "conflict"},
                },
            ],
            "is_triggered": False,
            "is_readed": False,
        },
        # Safety Alert Notifications
        {
            "title": "Safety Alert - Zone A.100",
            "what_you_need_to_know": "Structural inspection found potential hazard in Zone A.100. All personnel must evacuate immediately until further notice.",
            "what_we_can_trigger": "Acknowledge safety alert and confirm evacuation",
            "action_list": [
                {
                    "action": "acknowledge_alert",
                    "parameters": {"alert_id": "SAFETY_001", "zone": "A.100"},
                },
                {
                    "action": "update_zone_status",
                    "parameters": {"zone": "A.100", "status": "restricted"},
                },
            ],
            "is_triggered": False,
            "is_readed": False,
        },
        # Equipment Request Notifications
        {
            "title": "Crane Request Approval",
            "what_you_need_to_know": "Electrical team requests crane access for overhead lighting installation in main hall. Estimated duration: 4 hours.",
            "what_we_can_trigger": "Approve request, deny request, or request more information",
            "action_list": [
                {
                    "action": "approve_equipment_request",
                    "parameters": {"request_id": 205, "equipment": "crane"},
                },
                {
                    "action": "deny_equipment_request",
                    "parameters": {"request_id": 205, "reason": "scheduling_conflict"},
                },
                {
                    "action": "request_more_info",
                    "parameters": {"request_id": 205, "info_needed": "timeline"},
                },
            ],
            "is_triggered": False,
            "is_readed": False,
        },
        # Schedule Change Notifications
        {
            "title": "Schedule Change - Weather",
            "what_you_need_to_know": "Due to heavy rain forecast, all outdoor construction tasks for tomorrow are postponed. Workers should report to indoor assignments.",
            "what_we_can_trigger": "Acknowledge schedule change and update work assignments",
            "action_list": [
                {
                    "action": "update_schedule",
                    "parameters": {"date": "2025-09-12", "outdoor_tasks": "postponed"},
                },
                {
                    "action": "reassign_workers",
                    "parameters": {"from": "outdoor", "to": "indoor"},
                },
            ],
            "is_triggered": True,
            "is_readed": False,
        },
        # Information Only Notifications
        {
            "title": "Daily Progress Report",
            "what_you_need_to_know": "Today's progress: 15 tasks completed, 8 in progress, 3 pending. Overall project completion at 67%.",
            "what_we_can_trigger": "View detailed report or mark as read",
            "action_list": [],
            "is_triggered": True,
            "is_readed": False,
        },
        # Material Request Notifications
        {
            "title": "Material Shortage Alert",
            "what_you_need_to_know": "Running low on electrical cables and junction boxes. Current stock will last 2 days. Urgent reorder needed.",
            "what_we_can_trigger": "Place urgent order, check alternative suppliers, or adjust project timeline",
            "action_list": [
                {
                    "action": "place_order",
                    "parameters": {
                        "items": ["electrical_cables", "junction_boxes"],
                        "priority": "urgent",
                    },
                },
                {"action": "check_suppliers", "parameters": {"category": "electrical"}},
                {
                    "action": "adjust_timeline",
                    "parameters": {
                        "affected_tasks": ["electrical_installation"],
                        "delay": 2,
                    },
                },
            ],
            "is_triggered": False,
            "is_readed": False,
        },
        # Quality Control Notifications
        {
            "title": "Quality Inspection Required",
            "what_you_need_to_know": "Plumbing work in Zone C.300 completed. Quality control inspection needed before proceeding to next phase.",
            "what_we_can_trigger": "Schedule inspection, assign inspector, or request re-work",
            "action_list": [
                {
                    "action": "schedule_inspection",
                    "parameters": {
                        "zone": "C.300",
                        "type": "plumbing",
                        "priority": "normal",
                    },
                },
                {
                    "action": "assign_inspector",
                    "parameters": {"zone": "C.300", "inspector_id": 42},
                },
                {
                    "action": "request_rework",
                    "parameters": {"zone": "C.300", "reason": "quality_issues"},
                },
            ],
            "is_triggered": False,
            "is_readed": False,
        },
        # Urgent Maintenance Notifications
        {
            "title": "Urgent Maintenance - HVAC",
            "what_you_need_to_know": "HVAC system malfunction detected in Building Section North. Temperature control affected. Immediate maintenance required.",
            "what_we_can_trigger": "Dispatch maintenance team, activate backup systems, or evacuate affected areas",
            "action_list": [
                {
                    "action": "dispatch_maintenance",
                    "parameters": {
                        "system": "HVAC",
                        "location": "Building_North",
                        "priority": "urgent",
                    },
                },
                {
                    "action": "activate_backup",
                    "parameters": {"system": "HVAC", "backup_id": "HVAC_B1"},
                },
                {
                    "action": "partial_evacuation",
                    "parameters": {"building": "North", "reason": "HVAC_failure"},
                },
            ],
            "is_triggered": False,
            "is_readed": False,
        },
        # Training Notifications
        {
            "title": "Safety Training Reminder",
            "what_you_need_to_know": "Monthly safety training session scheduled for next Tuesday. All workers with expired certifications must attend.",
            "what_we_can_trigger": "Confirm attendance, request alternative date, or mark as completed",
            "action_list": [
                {
                    "action": "confirm_attendance",
                    "parameters": {
                        "training_id": "SAFETY_2025_09",
                        "date": "2025-09-17",
                    },
                },
                {
                    "action": "request_alternative",
                    "parameters": {
                        "training_id": "SAFETY_2025_09",
                        "reason": "schedule_conflict",
                    },
                },
                {
                    "action": "mark_completed",
                    "parameters": {
                        "user_id": "worker_123",
                        "training_id": "SAFETY_2025_09",
                    },
                },
            ],
            "is_triggered": False,
            "is_readed": False,
        },
        # Budget Approval Notifications
        {
            "title": "Budget Exceeded - Approval",
            "what_you_need_to_know": "Material costs for electrical phase exceeded budget by 15%. Additional approval required to continue with premium fixtures.",
            "what_we_can_trigger": "Approve additional budget, use standard fixtures, or postpone installations",
            "action_list": [
                {
                    "action": "approve_budget",
                    "parameters": {
                        "phase": "electrical",
                        "additional_amount": 15000,
                        "reason": "premium_fixtures",
                    },
                },
                {
                    "action": "switch_materials",
                    "parameters": {"phase": "electrical", "grade": "standard"},
                },
                {
                    "action": "postpone_phase",
                    "parameters": {
                        "phase": "electrical",
                        "postpone_until": "budget_review",
                    },
                },
            ],
            "is_triggered": False,
            "is_readed": False,
        },
    ]

    return notifications_data


def create_notifications_in_db():
    """Create all fake notifications in the database"""
    print("🔔 Creating fake notifications in database...")
    print("=" * 60)

    notifications = generate_fake_notifications()
    created_count = 0
    failed_count = 0

    for i, notification in enumerate(notifications, 1):
        print(
            f"\n📋 Creating notification {i}/{len(notifications)}: {notification['title']}"
        )

        try:
            result = create_notification(
                title=notification["title"],
                what_you_need_to_know=notification["what_you_need_to_know"],
                what_we_can_trigger=notification["what_we_can_trigger"],
                action_list=notification["action_list"],
                is_triggered=notification["is_triggered"],
                is_readed=notification["is_readed"],
            )

            # Parse the result to check if it was successful
            result_data = json.loads(result)
            if result_data.get("success", False):
                print(
                    f"✅ Created successfully - ID: {result_data['notification']['id']}"
                )
                created_count += 1
            else:
                print(f"❌ Failed: {result_data.get('error', 'Unknown error')}")
                failed_count += 1

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            failed_count += 1

    print("\n" + "=" * 60)
    print(f"📊 SUMMARY:")
    print(f"✅ Successfully created: {created_count} notifications")
    print(f"❌ Failed: {failed_count} notifications")
    print(f"📝 Total attempted: {len(notifications)} notifications")

    if created_count > 0:
        print(
            f"\n🎯 You can now test your notification system with {created_count} fake notifications!"
        )
        print("🔍 Use get_notifications or other tools to retrieve and test them.")


def main():
    """Main function"""
    print("🚀 FAKE NOTIFICATION GENERATOR")
    print(
        "Creating realistic test notifications for the construction site management system"
    )
    print()

    create_notifications_in_db()


if __name__ == "__main__":
    main()

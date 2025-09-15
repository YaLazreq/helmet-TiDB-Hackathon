-- Database Schema Creation Script
-- Creates tables for users and tasks management system
-- Author: Assistant
-- Date: 2025-09-06

-- DROP TABLE IF EXISTS tasks;

-- -- Create tasks table with all fields from create_task.py
-- CREATE TABLE IF NOT EXISTS tasks (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     title VARCHAR(255) NOT NULL,
--     description TEXT NOT NULL,

--     -- Location fields
--     room VARCHAR(100) NOT NULL,
--     floor INT NOT NULL,
--     building_section VARCHAR(100) NOT NULL,
--     zone_type VARCHAR(50) NOT NULL,

--     -- Assignment fields
--     assigned_workers JSON, -- List of worker IDs
--     required_worker_count INT NOT NULL,
--     skill_requirements JSON, -- List of required skills
--     trade_category VARCHAR(100) NOT NULL,
--     created_by INT NOT NULL,  -- ✅ CORRIGÉ: INT au lieu de VARCHAR(50)
--     supervisor_id INT NOT NULL,  -- ✅ CORRIGÉ: INT au lieu de VARCHAR(50)

--     -- Task properties
--     priority TINYINT DEFAULT 0 CHECK (priority BETWEEN 0 AND 3), -- 0=low, 1=normal, 2=high, 3=critical
--     status ENUM('pending', 'in_progress', 'completed', 'blocked') DEFAULT 'pending',
    
--     -- Time management
--     start_date DATETIME NOT NULL,
--     due_date DATETIME NOT NULL,
--     min_estimated_hours DECIMAL(8,2) NOT NULL,
--     max_estimated_hours DECIMAL(8,2) NOT NULL,
--     actual_hours DECIMAL(8,2) DEFAULT 0.0,
--     completion_percentage TINYINT DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    
--     -- Dependencies
--     dependencies JSON, -- List of prerequisite task IDs
--     blocks_tasks JSON, -- List of task IDs this task blocks
    
--     -- Resources
--     required_materials JSON, -- Materials needed with quantities
--     required_equipment JSON, -- Equipment needed
    
--     -- Conditions
--     weather_dependent BOOLEAN DEFAULT FALSE,
--     noise_level ENUM('low', 'medium', 'high') NOT NULL,
--     safety_requirements JSON, -- Safety requirements
--     notes TEXT NOT NULL,
--     requirements_vector TEXT,
    
--     -- Timestamps
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
--     -- Foreign key constraints - ✅ MAINTENANT COMPATIBLES
--     FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
--     FOREIGN KEY (supervisor_id) REFERENCES users(id) ON DELETE CASCADE,
    
--     -- Indexes for performance
--     INDEX idx_created_by (created_by),
--     INDEX idx_supervisor_id (supervisor_id),
--     INDEX idx_status (status),
--     INDEX idx_priority (priority),
--     INDEX idx_due_date (due_date),
--     INDEX idx_start_date (start_date),
--     INDEX idx_completion (completion_percentage),
--     INDEX idx_created_at (created_at),
--     INDEX idx_room (room),
--     INDEX idx_floor (floor),
--     INDEX idx_building_section (building_section),
--     INDEX idx_zone_type (zone_type),
--     INDEX idx_trade_category (trade_category),
--     INDEX idx_noise_level (noise_level),
--     INDEX idx_weather_dependent (weather_dependent),
    
--     -- Composite indexes for common queries
--     INDEX idx_status_priority (status, priority),
--     INDEX idx_location (building_section, floor, room),
--     INDEX idx_due_status (due_date, status),
--     INDEX idx_trade_status (trade_category, status)
-- );

-- Add requirements_vector column to existing tasks table (safe migration)
-- ALTER TABLE tasks ADD COLUMN IF NOT EXISTS requirements_vector TEXT;

-- Remove old vector column (uncomment to execute)
-- ALTER TABLE tasks DROP COLUMN vector;
------------------------------------------------------------------
-- First drop foreign key constraints, then drop users table
-- SET FOREIGN_KEY_CHECKS = 0;
-- DROP TABLE IF EXISTS orders;
-- DROP TABLE IF EXISTS users;
-- SET FOREIGN_KEY_CHECKS = 1;

-- Add requirements_vector column to existing tasks table (safe migration)
-- ALTER TABLE users ADD COLUMN IF NOT EXISTS skills_vector TEXT;

-- Remove old vector column (uncomment to execute)
-- ALTER TABLE users DROP COLUMN vector;


-- -- Users table optimized for vector matching
-- CREATE TABLE users (
--    -- Basic identity
--    id INT AUTO_INCREMENT PRIMARY KEY,
--    first_name VARCHAR(100) NOT NULL,
--    last_name VARCHAR(100) NOT NULL,
--    email VARCHAR(255) UNIQUE NOT NULL,
--    password_hash VARCHAR(255) NOT NULL,
--    phone VARCHAR(20),

-- -- Geolocation
--    address VARCHAR(100), -- "North_Paris_Site"

--    -- Role and status
--    role ENUM('worker', 'team_leader', 'supervisor', 'site_manager') DEFAULT 'worker',
--    is_active BOOLEAN DEFAULT TRUE,
--    hire_date DATE,
   
--    -- 🎯 VECTORIZATION CORE - Skills & Experience
--    role_description TEXT, -- "Experienced electrician with plumbing skills"
--    primary_skills JSON NOT NULL, -- ["electrical_installation", "plumbing_repair"]
--    secondary_skills JSON, -- ["welding", "height_work"]
--    trade_categories JSON NOT NULL, -- ["electricity", "plumbing"]
--    experience_years DECIMAL(4,1), -- 5.5 years
--    skill_levels JSON, -- {"plumbing": 8, "electricity": 6}
--    work_preferences JSON, -- ["height_work", "indoor", "teamwork"]
--    equipment_mastery JSON, -- ["scaffolding", "drill", "multimeter"]
--    project_experience JSON, -- ["residential", "industrial", "renovation"]
   

--    -- Certifications & Training
--    certifications JSON, -- ["crane_license", "electrical_permit_B1V"]
--    safety_training JSON, -- ["fall_prevention", "first_aid"]
--    last_training_date DATE,
--    skills_vector TEXT,
   
--    -- Metadata
--    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   
--    -- Indexes for frequent searches
--    INDEX idx_active_role (is_active, role),
--    INDEX idx_location (address(100))
-- );

ALTER TABLE notifications ADD COLUMN IF NOT EXISTS total_time_saved INT DEFAULT 0;

-- CREATE TABLE notifications (
--    -- Basic identity
--    id INT AUTO_INCREMENT PRIMARY KEY,
--    title TEXT NOT NULL,
--    what_you_need_to_know TEXT NOT NULL,
--    what_we_can_trigger TEXT NOT NULL,
--    is_triggered BOOLEAN DEFAULT FALSE,
--    action_list JSON, -- List of actions to take
--    is_readed BOOLEAN DEFAULT FALSE
-- );

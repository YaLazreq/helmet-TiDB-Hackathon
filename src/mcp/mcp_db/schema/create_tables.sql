-- Database Schema Creation Script
-- Creates tables for users and tasks management system
-- Author: Assistant
-- Date: 2025-09-06

DROP TABLE IF EXISTS tasks;

-- Create tasks table with all fields from create_task.py
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Location fields
    room VARCHAR(100) NOT NULL,
    floor INT NOT NULL,
    building_section VARCHAR(100) NOT NULL,
    zone_type VARCHAR(50) NOT NULL,
    
    -- Assignment fields
    assigned_workers JSON NOT NULL, -- List of worker IDs
    required_worker_count INT NOT NULL,
    skill_requirements JSON, -- List of required skills
    trade_category VARCHAR(100) NOT NULL,
    created_by INT NOT NULL,  -- ✅ CORRIGÉ: INT au lieu de VARCHAR(50)
    supervisor_id INT NOT NULL,  -- ✅ CORRIGÉ: INT au lieu de VARCHAR(50)
    
    -- Task properties
    priority TINYINT DEFAULT 0 CHECK (priority BETWEEN 0 AND 3), -- 0=low, 1=normal, 2=high, 3=critical
    status ENUM('pending', 'in_progress', 'completed', 'blocked') DEFAULT 'pending',
    
    -- Time management
    start_date DATETIME NOT NULL,
    due_date DATETIME NOT NULL,
    min_estimated_hours DECIMAL(8,2) NOT NULL,
    max_estimated_hours DECIMAL(8,2) NOT NULL,
    actual_hours DECIMAL(8,2) DEFAULT 0.0,
    completion_percentage TINYINT DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    
    -- Dependencies
    dependencies JSON, -- List of prerequisite task IDs
    blocks_tasks JSON, -- List of task IDs this task blocks
    
    -- Resources
    required_materials JSON, -- Materials needed with quantities
    required_equipment JSON, -- Equipment needed
    
    -- Conditions
    weather_dependent BOOLEAN DEFAULT FALSE,
    noise_level ENUM('low', 'medium', 'high') NOT NULL,
    safety_requirements JSON, -- Safety requirements
    notes TEXT NOT NULL,
    vector TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key constraints - ✅ MAINTENANT COMPATIBLES
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (supervisor_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_created_by (created_by),
    INDEX idx_supervisor_id (supervisor_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_due_date (due_date),
    INDEX idx_start_date (start_date),
    INDEX idx_completion (completion_percentage),
    INDEX idx_created_at (created_at),
    INDEX idx_room (room),
    INDEX idx_floor (floor),
    INDEX idx_building_section (building_section),
    INDEX idx_zone_type (zone_type),
    INDEX idx_trade_category (trade_category),
    INDEX idx_noise_level (noise_level),
    INDEX idx_weather_dependent (weather_dependent),
    
    -- Composite indexes for common queries
    INDEX idx_status_priority (status, priority),
    INDEX idx_location (building_section, floor, room),
    INDEX idx_due_status (due_date, status),
    INDEX idx_trade_status (trade_category, status)
);

-- Insert sample tasks with all required fields - ✅ CORRIGÉ: IDs numériques
INSERT INTO tasks (
    title, description, room, floor, building_section, zone_type,
    assigned_workers, required_worker_count, skill_requirements, trade_category,
    created_by, supervisor_id, priority, status, start_date, due_date,
    min_estimated_hours, max_estimated_hours, actual_hours, completion_percentage,
    dependencies, blocks_tasks, required_materials, required_equipment,
    weather_dependent, noise_level, safety_requirements, notes
) VALUES
(
    'Réparer éclairage Bureau A201',
    'Remplacer les néons défaillants dans le bureau A201 et vérifier l\'installation électrique',
    'A201', 2, 'Aile A', 'bureau',
    '[3, 4]', 2, '["électricien"]', 'électricité',
    1, 2, 2, 'pending', '2025-09-07 08:00:00', '2025-09-09 17:00:00',
    2.0, 4.0, 0.0, 0,
    '[]', '[]', '[{"nom": "Néons LED", "quantite": 4}, {"nom": "Ballasts", "quantite": 2}]', '["échelle", "multimètre"]',
    FALSE, 'low', '["EPI électrique", "coupure courant"]', 'Urgent - bureau utilisé quotidiennement'
),
(
    'Maintenance plomberie Sanitaires B100',
    'Déboucher et nettoyer les évacuations des sanitaires du rez-de-chaussée bloc B',
    'B100', 0, 'Bloc B', 'sanitaire',
    '[3]', 1, '["plombier"]', 'plomberie',
    2, 2, 1, 'in_progress', '2025-09-06 09:00:00', '2025-09-08 16:00:00',
    3.0, 5.0, 1.5, 30,
    '[]', '[]', '[{"nom": "Produits débouchage", "quantite": 2}, {"nom": "Gants", "quantite": 1}]', '["furet", "aspirateur_eau"]',
    FALSE, 'medium', '["gants protection", "masque"]', 'Maintenance préventive semestrielle'
),
(
    'Peinture couloir C-Nord',
    'Repeindre entièrement le couloir nord du bâtiment C suite aux dégâts des eaux',
    'C-Nord', 1, 'Bâtiment C', 'circulation',
    '[4]', 2, '["peintre"]', 'peinture',
    1, 2, 3, 'completed', '2025-09-01 07:00:00', '2025-09-05 18:00:00',
    12.0, 16.0, 14.5, 100,
    '[]', '[5]', '[{"nom": "Peinture acrylique", "quantite": 15}, {"nom": "Rouleaux", "quantite": 5}]', '["échafaudage", "bâches_protection"]',
    TRUE, 'high', '["ventilation", "EPI_peinture"]', 'Travail terminé avec succès - très bon rendu'
),
(
    'Installation caméra sécurité Ext-Sud',
    'Installer nouvelle caméra de surveillance côté sud du bâtiment avec raccordement réseau',
    'Ext-Sud', 0, 'Extérieur', 'technique',
    '[3, 4]', 2, '["électricien", "informatique"]', 'électricité',
    1, 2, 2, 'blocked', '2025-09-10 08:00:00', '2025-09-15 17:00:00',
    6.0, 10.0, 0.0, 0,
    '[1]', '[]', '[{"nom": "Caméra IP", "quantite": 1}, {"nom": "Câble réseau", "quantite": 50}]', '["perceuse", "échelle", "testeur_réseau"]',
    TRUE, 'medium', '["harnais", "casque", "EPI_hauteur"]', 'En attente livraison matériel - prévu semaine prochaine'
);

------------------------------------------------------------------
-- First drop foreign key constraints, then drop users table
-- SET FOREIGN_KEY_CHECKS = 0;
-- DROP TABLE IF EXISTS orders;
-- DROP TABLE IF EXISTS users;
-- SET FOREIGN_KEY_CHECKS = 1;

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
--    vector TEXT,
   
--    -- Metadata
--    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   
--    -- Indexes for frequent searches
--    INDEX idx_active_role (is_active, role),
--    INDEX idx_location (address(100))
-- );

-- -- Painter specialist
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Emma', 'Wilson', 'e.wilson@email.com', '$2b$12$hash101', '+33123456789', '15 Rue de la Paix, Paris 1er',
--    'worker', TRUE, '2018-03-15',
--    '["interior_painting", "exterior_painting", "spray_painting", "surface_preparation"]',
--    '["wallpaper_removal", "color_matching", "texture_application"]',
--    '["painting"]',
--    6.0,
--    '{"interior_painting": 9, "exterior_painting": 8, "spray_painting": 7, "surface_preparation": 8}',
--    '["indoor", "detail_oriented", "clean_work", "color_precision"]',
--    '["spray_gun", "rollers", "brushes", "scaffolding", "drop_cloths", "airless_sprayer"]',
--    '["residential", "commercial", "renovation", "new_construction"]',
--    '["lead_paint_certification", "hazmat_training", "color_theory_certification"]',
--    '["respiratory_protection", "chemical_safety", "ladder_safety", "confined_space"]',
--    '2024-01-15'
-- );

-- -- Crane operator
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Robert', 'Brown', 'r.brown@email.com', '$2b$12$hash102', '+33987654321', '45 Avenue des Champs, Paris 8e',
--    'team_leader', TRUE, '2009-06-01',
--    '["tower_crane_operation", "mobile_crane_operation", "load_calculation", "rigging"]',
--    '["signal_communication", "maintenance_inspection", "safety_oversight", "crew_training"]',
--    '["heavy_machinery", "lifting_equipment"]',
--    15.0,
--    '{"tower_crane_operation": 10, "mobile_crane_operation": 9, "load_calculation": 9, "rigging": 8}',
--    '["outdoor", "high_responsibility", "early_hours", "precision_work"]',
--    '["tower_crane", "mobile_crane", "rigging_equipment", "radio_communication", "load_charts"]',
--    '["industrial", "commercial", "high_rise", "infrastructure", "bridge_construction"]',
--    '["crane_operator_license_A", "rigging_certification", "safety_supervisor", "instructor_certification"]',
--    '["fall_protection", "crane_safety", "rigging_safety", "first_aid", "emergency_response"]',
--    '2024-02-20'
-- );

-- -- Carpenter/Framer
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'David', 'Miller', 'd.miller@email.com', '$2b$12$hash103', '+33555123456', '78 Rue Saint-Antoine, Paris 4e',
--    'worker', TRUE, '2014-09-10',
--    '["framing", "finish_carpentry", "cabinet_installation", "drywall"]',
--    '["trim_work", "door_installation", "window_installation", "custom_millwork"]',
--    '["carpentry", "woodworking"]',
--    10.0,
--    '{"framing": 9, "finish_carpentry": 8, "cabinet_installation": 9, "drywall": 7}',
--    '["indoor", "precision_work", "problem_solving", "teamwork"]',
--    '["circular_saw", "nail_gun", "level", "measuring_tools", "chisels", "router"]',
--    '["residential", "commercial", "custom_homes", "renovation"]',
--    '["osha_10", "carpentry_certification", "cabinet_maker_license"]',
--    '["power_tool_safety", "fall_protection", "cut_protection", "dust_protection"]',
--    '2023-11-05'
-- );

-- -- HVAC technician
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Lisa', 'Garcia', 'l.garcia@email.com', '$2b$12$hash104', '+33666789012', '23 Boulevard Voltaire, Paris 11e',
--    'worker', TRUE, '2017-04-12',
--    '["hvac_installation", "ductwork", "system_maintenance", "troubleshooting"]',
--    '["electrical_wiring", "refrigerant_recovery", "air_balancing", "energy_efficiency"]',
--    '["hvac", "mechanical"]',
--    7.0,
--    '{"hvac_installation": 8, "ductwork": 9, "troubleshooting": 8, "system_maintenance": 7}',
--    '["indoor", "technical_work", "confined_spaces", "problem_solving"]',
--    '["multimeter", "refrigerant_tools", "ductwork_tools", "leak_detector", "gauges", "vacuum_pump"]',
--    '["commercial", "residential", "industrial", "data_centers"]',
--    '["epa_certification", "refrigerant_handling", "energy_efficiency", "gas_license"]',
--    '["confined_space", "electrical_safety", "refrigerant_safety", "ladder_safety"]',
--    '2024-01-08'
-- );

-- -- Roofer
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'James', 'Anderson', 'j.anderson@email.com', '$2b$12$hash105', '+33777890123', '67 Rue de Rivoli, Paris 1er',
--    'worker', TRUE, '2015-02-28',
--    '["shingle_installation", "flat_roof", "roof_repair", "waterproofing"]',
--    '["gutter_installation", "skylight_installation", "insulation", "solar_panel_mounting"]',
--    '["roofing", "waterproofing"]',
--    9.0,
--    '{"shingle_installation": 9, "flat_roof": 8, "waterproofing": 9, "roof_repair": 8}',
--    '["outdoor", "height_work", "weather_dependent", "physical_work"]',
--    '["nail_gun", "roofing_hatchet", "safety_harness", "ladder", "chalk_line", "torch"]',
--    '["residential", "commercial", "emergency_repair", "historical_buildings"]',
--    '["fall_protection", "osha_10", "roofing_safety", "hot_work_permit"]',
--    '["fall_protection", "ladder_safety", "weather_awareness", "fire_safety"]',
--    '2023-12-10'
-- );

-- -- Welder
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Carlos', 'Martinez', 'c.martinez@email.com', '$2b$12$hash106', '+33888901234', '34 Avenue de la République, Paris 11e',
--    'worker', TRUE, '2013-07-20',
--    '["mig_welding", "tig_welding", "stick_welding", "structural_welding"]',
--    '["plasma_cutting", "metal_fabrication", "blueprint_reading", "pipe_welding"]',
--    '["welding", "metal_fabrication"]',
--    11.0,
--    '{"mig_welding": 9, "tig_welding": 10, "structural_welding": 9, "stick_welding": 8}',
--    '["indoor", "outdoor", "precision_work", "confined_spaces"]',
--    '["welding_machine", "plasma_cutter", "angle_grinder", "welding_helmet", "measuring_tools", "cutting_torch"]',
--    '["industrial", "commercial", "structural", "pipeline", "artistic_metalwork"]',
--    '["aws_certification", "structural_welding", "pipe_welding", "underwater_welding"]',
--    '["welding_safety", "confined_space", "hot_work_permit", "fire_safety", "gas_safety"]',
--    '2024-03-05'
-- );

-- -- Forklift operator / Material handler
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Kevin', 'Taylor', 'k.taylor@email.com', '$2b$12$hash107', '+33999012345', '89 Rue de la Bastille, Paris 12e',
--    'worker', TRUE, '2020-11-03',
--    '["forklift_operation", "material_handling", "inventory_management", "loading_unloading"]',
--    '["crane_signals", "warehouse_organization", "delivery_coordination", "safety_inspection"]',
--    '["logistics", "material_handling"]',
--    4.0,
--    '{"forklift_operation": 8, "material_handling": 7, "inventory_management": 6, "loading_unloading": 8}',
--    '["outdoor", "physical_work", "fast_paced", "organization"]',
--    '["forklift", "pallet_jack", "hand_truck", "crane_signals", "scanner", "reach_truck"]',
--    '["commercial", "industrial", "warehouse", "construction_supply"]',
--    '["forklift_license", "osha_certification", "hazmat_handling", "reach_truck_certification"]',
--    '["forklift_safety", "material_handling", "hazmat_awareness", "loading_dock_safety"]',
--    '2023-10-15'
-- );

-- -- Tile installer
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Maria', 'Rodriguez', 'm.rodriguez@email.com', '$2b$12$hash108', '+33101112131', '56 Rue Saint-Germain, Paris 6e',
--    'worker', TRUE, '2016-08-18',
--    '["ceramic_tile", "stone_installation", "grouting", "surface_preparation"]',
--    '["mosaic_work", "waterproofing", "pattern_layout", "natural_stone"]',
--    '["tiling", "flooring"]',
--    8.0,
--    '{"ceramic_tile": 9, "stone_installation": 8, "grouting": 9, "surface_preparation": 8}',
--    '["indoor", "precision_work", "detail_oriented", "kneeling_work"]',
--    '["tile_cutter", "level", "trowel", "grout_float", "spacers", "wet_saw"]',
--    '["residential", "commercial", "bathroom_renovation", "luxury_hotels"]',
--    '["tile_installation_certification", "stone_masonry_certification"]',
--    '["dust_protection", "chemical_safety", "ergonomic_training", "knee_protection"]',
--    '2023-09-22'
-- );

-- -- Site supervisor
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Michael', 'Thompson', 'm.thompson@email.com', '$2b$12$hash109', '+33121314151', '12 Boulevard Haussmann, Paris 9e',
--    'supervisor', TRUE, '2004-01-15',
--    '["project_management", "safety_oversight", "quality_control", "team_coordination"]',
--    '["scheduling", "budget_management", "client_communication", "risk_assessment"]',
--    '["management", "supervision"]',
--    20.0,
--    '{"project_management": 10, "safety_oversight": 9, "team_coordination": 9, "quality_control": 8}',
--    '["leadership", "problem_solving", "communication", "multitasking"]',
--    '["tablet", "safety_equipment", "measuring_tools", "radio", "planning_software", "drone"]',
--    '["commercial", "residential", "industrial", "renovation", "government_projects"]',
--    '["pmp_certification", "osha_30", "construction_management", "lean_construction"]',
--    '["osha_30", "first_aid", "cpr", "emergency_response", "incident_investigation"]',
--    '2024-01-30'
-- );

-- -- Demolition worker
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Tony', 'Lee', 't.lee@email.com', '$2b$12$hash110', '+33131415161', '91 Rue de Belleville, Paris 20e',
--    'worker', TRUE, '2018-05-22',
--    '["controlled_demolition", "debris_removal", "salvage_operations", "heavy_machinery"]',
--    '["asbestos_removal", "lead_abatement", "site_cleanup", "excavation"]',
--    '["demolition", "hazmat"]',
--    6.0,
--    '{"controlled_demolition": 8, "debris_removal": 9, "heavy_machinery": 7, "salvage_operations": 8}',
--    '["outdoor", "physical_work", "dust_tolerance", "noise_tolerance"]',
--    '["jackhammer", "sledgehammer", "mini_excavator", "safety_gear", "dumpster", "concrete_saw"]',
--    '["commercial", "residential", "industrial_cleanup", "environmental_remediation"]',
--    '["demolition_safety", "hazmat_awareness", "confined_space", "asbestos_certification"]',
--    '["hazmat_training", "respiratory_protection", "confined_space", "heavy_machinery", "lead_safety"]',
--    '2023-08-14'
-- );

-- -- Glazier (window installer)
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Rachel', 'White', 'r.white@email.com', '$2b$12$hash111', '+33141516171', '37 Rue du Faubourg Saint-Honoré, Paris 8e',
--    'worker', TRUE, '2019-03-08',
--    '["window_installation", "glass_cutting", "glazing", "weatherproofing"]',
--    '["mirror_installation", "storefront_glass", "custom_cutting", "curtain_wall"]',
--    '["glazing", "glass_installation"]',
--    5.0,
--    '{"window_installation": 8, "glass_cutting": 9, "weatherproofing": 7, "glazing": 8}',
--    '["indoor", "outdoor", "precision_work", "height_work"]',
--    '["glass_cutter", "suction_cups", "glazing_tools", "caulk_gun", "measuring_tape", "glass_lifter"]',
--    '["commercial", "residential", "storefront", "high_end_residential"]',
--    '["fall_protection", "glass_handling_safety", "glazier_certification"]',
--    '["fall_protection", "glass_safety", "cut_protection", "lifting_techniques"]',
--    '2023-07-19'
-- );

-- -- Insulation installer
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Steve', 'Clark', 's.clark@email.com', '$2b$12$hash112', '+33151617181', '83 Avenue Parmentier, Paris 11e',
--    'worker', TRUE, '2017-10-12',
--    '["blown_insulation", "batt_insulation", "spray_foam", "vapor_barriers"]',
--    '["air_sealing", "energy_auditing", "crawl_space_work", "attic_ventilation"]',
--    '["insulation", "energy_efficiency"]',
--    7.0,
--    '{"blown_insulation": 8, "spray_foam": 9, "vapor_barriers": 8, "batt_insulation": 7}',
--    '["indoor", "confined_spaces", "attic_work", "crawl_spaces"]',
--    '["blowing_machine", "staple_gun", "utility_knife", "respirator", "protective_suits", "spray_equipment"]',
--    '["residential", "commercial", "energy_retrofit", "new_construction"]',
--    '["respiratory_protection", "confined_space", "asbestos_awareness", "energy_auditor_certification"]',
--    '["respiratory_protection", "confined_space", "chemical_safety", "heat_stress_prevention"]',
--    '2023-11-28'
-- );

-- -- Junior apprentice
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Alex', 'Young', 'a.young@email.com', '$2b$12$hash113', '+33161718192', '29 Rue de la Roquette, Paris 11e',
--    'worker', TRUE, '2024-01-08',
--    '["general_labor", "tool_assistance", "material_transport", "cleanup"]',
--    '["basic_measurement", "safety_awareness", "equipment_maintenance", "documentation"]',
--    '["general", "apprentice"]',
--    0.5,
--    '{"general_labor": 6, "cleanup": 7, "tool_assistance": 5, "material_transport": 6}',
--    '["learning", "teamwork", "physical_work", "flexible"]',
--    '["hand_tools", "wheelbarrow", "basic_power_tools", "broom", "shovel", "tape_measure"]',
--    '["residential", "light_commercial", "training_projects"]',
--    '["osha_10", "first_aid_basic"]',
--    '["basic_safety", "tool_safety", "lifting_techniques", "hazard_recognition"]',
--    '2024-01-15'
-- );

-- -- Flooring specialist
-- INSERT INTO users (
--    first_name, last_name, email, password_hash, phone, address,
--    role, is_active, hire_date,
--    primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
--    work_preferences, equipment_mastery, project_experience,
--    certifications, safety_training, last_training_date
-- ) VALUES (
--    'Jennifer', 'Hall', 'j.hall@email.com', '$2b$12$hash114', '+33171819202', '74 Rue Saint-Maur, Paris 11e',
--    'worker', TRUE, '2015-06-25',
--    '["hardwood_flooring", "laminate_installation", "vinyl_flooring", "subfloor_preparation"]',
--    '["carpet_installation", "floor_refinishing", "moisture_testing", "radiant_heating"]',
--    '["flooring", "interior_finishing"]',
--    9.0,
--    '{"hardwood_flooring": 9, "laminate_installation": 8, "subfloor_preparation": 9, "vinyl_flooring": 8}',
--    '["indoor", "precision_work", "kneeling_work", "detail_oriented"]',
--    '["flooring_nailer", "saw", "measuring_tools", "knee_pads", "tapping_block", "pull_bar"]',
--    '["residential", "commercial", "luxury_homes", "renovation"]',
--    '["flooring_certification", "hardwood_specialist", "moisture_testing_certification"]',
--    '["dust_protection", "knee_protection", "tool_safety", "chemical_safety"]',
--    '2023-12-01'
-- );
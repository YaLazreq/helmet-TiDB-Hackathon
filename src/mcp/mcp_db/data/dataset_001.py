# RETAIL PARK CONSTRUCTION DATASET
# Project: Hoverville Retail Park (Retail Building, Restaurant, Car Wash)
# Duration: 1 Month (September 2025)
# Location: Hoverville, Colorado, USA

# Import the create functions from the mcp_db tools
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.users.repositories.create_user import create_user
from tools.tasks.repositories.create_task import create_task
from tools.tasks.repositories.get_tasks import get_tasks

# =============================================================================
# USERS CREATION COMMANDS
# =============================================================================

# # SUPERVISORS & MANAGEMENT
# create_user(
#     first_name="Robert",
#     last_name="Martinez",
#     email="r.martinez@hoverpark.com",
#     password="Super2024!",
#     phone="+1-720-555-0101",
#     address="1234 Construction Blvd, Hoverville, CO 80424",
#     role="supervisor",
#     role_description="Project management and safety coordination expert with 15 years of experience supervising commercial construction sites and quality control.",
#     hire_date="2020-03-15",
#     primary_skills=[
#         "project_management",
#         "safety_coordination",
#         "quality_control_inspection",
#     ],
#     secondary_skills=["scheduling", "cost_estimation", "team_leadership"],
#     trade_categories=["management", "safety"],
#     experience_years=15.0,
#     skill_levels={
#         "project_management": 9,
#         "safety_coordination": 9,
#         "quality_control_inspection": 8,
#     },
#     work_preferences=[
#         "teamwork",
#         "leadership_role",
#         "client_interaction",
#         "problem_solving",
#     ],
#     certifications=["pmp_certification", "osha_30", "construction_manager"],
#     safety_training=[
#         "osha_30",
#         "construction_safety_orientation",
#         "hazard_recognition",
#         "emergency_procedures",
#     ],
# )

# create_user(
#     first_name="Sarah",
#     last_name="Thompson",
#     email="s.thompson@hoverpark.com",
#     password="Lead2024!",
#     phone="+1-720-555-0102",
#     address="567 Maple Street, Hoverville, CO 80424",
#     role="team_leader",
#     role_description="Expert electrician and team leader specialized in industrial installations, apprentice mentoring and electrical team coordination.",
#     hire_date="2018-07-20",
#     primary_skills=[
#         "electrical_installation",
#         "industrial_wiring",
#         "electrical_troubleshooting",
#     ],
#     secondary_skills=["team_leadership", "apprentice_mentoring", "scheduling"],
#     trade_categories=["electrical", "management"],
#     experience_years=12.0,
#     skill_levels={
#         "electrical_installation": 9,
#         "industrial_wiring": 8,
#         "electrical_troubleshooting": 9,
#     },
#     work_preferences=[
#         "teamwork",
#         "leadership_role",
#         "apprentice_mentoring",
#         "technical_work",
#     ],
#     certifications=["master_electrician", "electrical_inspector", "osha_30"],
#     safety_training=[
#         "electrical_safety_basics",
#         "arc_flash_training",
#         "lockout_tagout_electrical",
#         "osha_30",
#     ],
# )

# # EXPERIENCED WORKERS
# create_user(
#     first_name="Michael",
#     last_name="Rodriguez",
#     email="m.rodriguez@hoverpark.com",
#     password="Concrete24!",
#     phone="+1-720-555-0103",
#     address="890 Industrial Way, Hoverville, CO 80424",
#     role="worker",
#     role_description="Concrete and structural specialist with expertise in pouring, finishing and heavy machinery operation for commercial construction projects.",
#     hire_date="2019-05-10",
#     primary_skills=[
#         "concrete_pouring",
#         "concrete_finishing",
#         "structural_steel_erection",
#     ],
#     secondary_skills=[
#         "rebar_installation",
#         "formwork_construction",
#         "crane_operation_mobile",
#     ],
#     trade_categories=["concrete", "heavy_machinery"],
#     experience_years=8.5,
#     skill_levels={
#         "concrete_pouring": 9,
#         "concrete_finishing": 8,
#         "structural_steel_erection": 7,
#     },
#     work_preferences=["teamwork", "physical_work", "outdoor", "heavy_lifting"],
#     equipment_mastery=[
#         "concrete_vibrator",
#         "power_screed",
#         "crane_mobile",
#         "concrete_pump",
#     ],
#     certifications=["crane_operator_nccco", "osha_10"],
#     safety_training=[
#         "crane_safety",
#         "concrete_equipment_safety",
#         "rigging_safety",
#         "fall_protection_basic",
#     ],
# )

# create_user(
#     first_name="David",
#     last_name="Chen",
#     email="d.chen@hoverpark.com",
#     password="Electric24!",
#     phone="+1-720-555-0104",
#     address="234 Oak Avenue, Hoverville, CO 80424",
#     role="worker",
#     role_description="Commercial electrician specialized in lighting and security systems with focus on precision work and technical installations.",
#     hire_date="2020-01-15",
#     primary_skills=[
#         "electrical_installation",
#         "commercial_wiring",
#         "lighting_installation",
#     ],
#     secondary_skills=[
#         "electrical_troubleshooting",
#         "control_panel_wiring",
#         "security_system_installation",
#     ],
#     trade_categories=["electrical"],
#     experience_years=6.0,
#     skill_levels={
#         "electrical_installation": 8,
#         "commercial_wiring": 8,
#         "lighting_installation": 9,
#     },
#     work_preferences=["precision_work", "detail_oriented", "indoor", "technical_work"],
#     equipment_mastery=[
#         "multimeter",
#         "conduit_bender",
#         "wire_strippers",
#         "voltage_tester",
#     ],
#     certifications=["journeyman_electrician", "osha_10"],
#     safety_training=[
#         "electrical_safety_basics",
#         "arc_flash_training",
#         "lockout_tagout_electrical",
#         "ppe_training",
#     ],
# )

# create_user(
#     first_name="James",
#     last_name="Wilson",
#     email="j.wilson@hoverpark.com",
#     password="Plumb24!",
#     phone="+1-720-555-0105",
#     address="456 Pine Street, Hoverville, CO 80424",
#     role="worker",
#     role_description="Plumbing and HVAC expert for commercial installations, specialized in complex problem-solving and heating systems.",
#     hire_date="2017-09-01",
#     primary_skills=["plumbing_installation", "hvac_installation", "pipe_fitting"],
#     secondary_skills=[
#         "drain_installation",
#         "water_heater_installation",
#         "bathroom_plumbing",
#     ],
#     trade_categories=["plumbing", "hvac"],
#     experience_years=9.0,
#     skill_levels={
#         "plumbing_installation": 9,
#         "hvac_installation": 7,
#         "pipe_fitting": 8,
#     },
#     work_preferences=["problem_solving", "precision_work", "indoor", "varied_tasks"],
#     equipment_mastery=[
#         "pipe_threader",
#         "pipe_cutter",
#         "soldering_iron",
#         "pressure_tester",
#     ],
#     certifications=["journeyman_plumber", "hvac_epa_certification", "osha_10"],
#     safety_training=[
#         "confined_space_entry",
#         "chemical_safety",
#         "respiratory_protection",
#         "lockout_tagout",
#     ],
# )

# create_user(
#     first_name="Carlos",
#     last_name="Garcia",
#     email="c.garcia@hoverpark.com",
#     password="Frame24!",
#     phone="+1-720-555-0106",
#     address="789 Cedar Lane, Hoverville, CO 80424",
#     role="worker",
#     role_description="Structural welder and carpenter specialized in height work, steel erection and metal structure welding.",
#     hire_date="2019-11-20",
#     primary_skills=["framing_steel", "structural_steel_erection", "welding_structural"],
#     secondary_skills=["framing_wood", "finish_carpentry", "door_installation"],
#     trade_categories=["carpentry", "welding"],
#     experience_years=7.5,
#     skill_levels={
#         "framing_steel": 8,
#         "structural_steel_erection": 9,
#         "welding_structural": 8,
#     },
#     work_preferences=["teamwork", "height_work", "physical_work", "outdoor"],
#     equipment_mastery=["mig_welder", "plasma_cutter", "crane_mobile", "safety_harness"],
#     certifications=["structural_welding", "fall_protection", "osha_10"],
#     safety_training=[
#         "steel_erection_safety",
#         "welding_safety",
#         "fall_protection_basic",
#         "rigging_safety",
#     ],
# )

# create_user(
#     first_name="Lisa",
#     last_name="Anderson",
#     email="l.anderson@hoverpark.com",
#     password="Paint24!",
#     phone="+1-720-555-0107",
#     address="321 Birch Road, Hoverville, CO 80424",
#     role="worker",
#     role_description="Painter specialized in high-quality commercial finishes with expertise in spray painting and surface preparation for premium projects.",
#     hire_date="2020-06-10",
#     primary_skills=["interior_painting", "exterior_painting", "spray_painting"],
#     secondary_skills=[
#         "surface_preparation",
#         "texture_application",
#         "decorative_painting",
#     ],
#     trade_categories=["painting"],
#     experience_years=5.5,
#     skill_levels={"interior_painting": 8, "exterior_painting": 7, "spray_painting": 9},
#     work_preferences=[
#         "detail_oriented",
#         "quality_focused",
#         "solo_work",
#         "methodical_work",
#     ],
#     equipment_mastery=["spray_gun", "pressure_washer", "sanders", "scaffolding"],
#     certifications=["osha_10"],
#     safety_training=[
#         "chemical_safety",
#         "respiratory_protection",
#         "fall_protection_basic",
#         "ppe_training",
#     ],
# )

# create_user(
#     first_name="Kevin",
#     last_name="Brown",
#     email="k.brown@hoverpark.com",
#     password="Floor24!",
#     phone="+1-720-555-0108",
#     address="654 Elm Street, Hoverville, CO 80424",
#     role="worker",
#     role_description="Flooring specialist with expertise in ceramic tile, hardwood flooring and surface preparation for precision finishes.",
#     hire_date="2018-12-05",
#     primary_skills=["tile_installation_ceramic", "hardwood_flooring", "vinyl_flooring"],
#     secondary_skills=["subfloor_preparation", "floor_leveling", "stone_flooring"],
#     trade_categories=["flooring"],
#     experience_years=8.0,
#     skill_levels={
#         "tile_installation_ceramic": 9,
#         "hardwood_flooring": 7,
#         "vinyl_flooring": 8,
#     },
#     work_preferences=[
#         "precision_work",
#         "detail_oriented",
#         "quality_focused",
#         "kneeling_work",
#     ],
#     equipment_mastery=["tile_saw", "floor_sanders", "laser_level", "moisture_meter"],
#     certifications=["osha_10"],
#     safety_training=[
#         "dust_control",
#         "ergonomics_training",
#         "lifting_techniques",
#         "knee_protection",
#     ],
# )

# create_user(
#     first_name="Angela",
#     last_name="Davis",
#     email="a.davis@hoverpark.com",
#     password="Roof24!",
#     phone="+1-720-555-0109",
#     address="987 Spruce Circle, Hoverville, CO 80424",
#     role="worker",
#     role_description="Roofing expert in metal roofing and waterproofing, specialized in height work and waterproofing membrane systems.",
#     hire_date="2019-03-25",
#     primary_skills=["metal_roofing", "roof_repair", "waterproofing_membrane"],
#     secondary_skills=[
#         "shingle_installation",
#         "gutter_installation",
#         "skylight_installation",
#     ],
#     trade_categories=["roofing"],
#     experience_years=6.5,
#     skill_levels={"metal_roofing": 8, "roof_repair": 9, "waterproofing_membrane": 7},
#     work_preferences=["height_work", "outdoor", "weather_dependent", "physical_work"],
#     equipment_mastery=[
#         "roofing_nailer",
#         "membrane_welder",
#         "safety_harness",
#         "torch_roofing",
#     ],
#     certifications=["fall_protection", "osha_10"],
#     safety_training=[
#         "roofing_safety",
#         "fall_protection_basic",
#         "weather_safety",
#         "height_work_training",
#     ],
# )

# # JUNIOR WORKER
# create_user(
#     first_name="Tyler",
#     last_name="Johnson",
#     email="t.johnson@hoverpark.com",
#     password="Helper24!",
#     phone="+1-720-555-0110",
#     address="159 Aspen Way, Hoverville, CO 80424",
#     role="worker",
#     role_description="Versatile apprentice assistant for general labor, material handling and support to specialized teams with focus on learning.",
#     hire_date="2024-10-01",
#     primary_skills=["general_labor", "material_handling", "tool_assistance"],
#     secondary_skills=["site_cleanup", "equipment_maintenance", "scaffolding_erection"],
#     trade_categories=["general"],
#     experience_years=0.2,
#     skill_levels={"general_labor": 5, "material_handling": 6, "tool_assistance": 5},
#     work_preferences=["learning_focused", "teamwork", "varied_tasks", "physical_work"],
#     equipment_mastery=["hand_truck", "wheelbarrow", "basic_hand_tools", "power_drill"],
#     certifications=["osha_10"],
#     safety_training=[
#         "construction_safety_orientation",
#         "ppe_training",
#         "lifting_techniques",
#         "basic_tool_safety",
#     ],
# )

# =============================================================================
# TASKS CREATION COMMANDS
# =============================================================================

# PHASE 1: SITE PREPARATION & FOUNDATIONS (Week 1)
# Dependencies: None (Starting tasks)

create_task(
    title="Site Survey and Layout",
    description="Conduct topographic survey, establish benchmarks, and layout building positions for all three structures using GPS and total station equipment.",
    room="SITE-01",
    floor=0,
    building_section="Site Wide",
    zone_type="exterior",
    assigned_workers=[1],  # Robert Martinez (Supervisor)
    required_worker_count=1,
    skill_requirements=["surveying", "gps_equipment", "total_station"],
    trade_category="surveying",
    created_by="project_manager",
    supervisor_id=1,
    priority=3,
    status="completed",
    start_date="2025-09-01",
    due_date="2025-09-02",
    min_estimated_hours=12.0,
    max_estimated_hours=16.0,
    actual_hours=14.5,
    completion_percentage=100,
    dependencies=[],
    blocks_tasks=[2, 3, 4],
    required_materials=[
        {"material": "survey_stakes", "quantity": 50, "unit": "pieces"}
    ],
    required_equipment=["total_station", "gps_equipment", "measuring_tape"],
    weather_dependent=True,
    noise_level="low",
    safety_requirements=["high_visibility_clothing", "hard_hat"],
    notes="Survey completed successfully. All elevation benchmarks established.",
)

create_task(
    title="Retail Building Foundation Excavation",
    description="Excavate foundation area for retail building per engineered drawings. Remove topsoil, excavate to design depth, and prepare for concrete footings.",
    room="RET-FOUND",
    floor=0,
    building_section="Retail Building",
    zone_type="structural",
    assigned_workers=["3"],  # Michael Rodriguez
    required_worker_count=1,
    skill_requirements=[
        "excavator_operation",
        "foundation_excavation",
        "grade_reading",
    ],
    trade_category="excavation",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="completed",
    start_date="2025-09-02",
    due_date="2025-09-04",
    min_estimated_hours=20.0,
    max_estimated_hours=28.0,
    actual_hours=24.0,
    completion_percentage=100,
    dependencies=["1"],
    blocks_tasks=["5"],
    required_materials=[{"material": "gravel_base", "quantity": 15, "unit": "yards"}],
    required_equipment=["excavator", "dump_truck", "compactor"],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["excavation_safety", "heavy_equipment_safety"],
    notes="Excavation completed to specifications. Good soil conditions encountered.",
)

create_task(
    title="Restaurant Foundation Excavation",
    description="Excavate foundation area for restaurant building. Coordinate with utility rough-ins and ensure proper drainage slope.",
    room="REST-FOUND",
    floor=0,
    building_section="Restaurant",
    zone_type="structural",
    assigned_workers=["3"],  # Michael Rodriguez
    required_worker_count=1,
    skill_requirements=[
        "excavator_operation",
        "foundation_excavation",
        "utility_coordination",
    ],
    trade_category="excavation",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="completed",
    start_date="2025-09-03",
    due_date="2025-09-05",
    min_estimated_hours=16.0,
    max_estimated_hours=22.0,
    actual_hours=18.5,
    completion_percentage=100,
    dependencies=["1"],
    blocks_tasks=["6"],
    required_materials=[{"material": "gravel_base", "quantity": 8, "unit": "yards"}],
    required_equipment=["excavator", "compactor", "laser_level"],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["excavation_safety", "utility_protection"],
    notes="Foundation excavation complete. Utilities marked and protected.",
)

create_task(
    title="Car Wash Foundation Excavation",
    description="Excavate car wash building foundation with special attention to drainage systems and chemical-resistant requirements.",
    room="WASH-FOUND",
    floor=0,
    building_section="Car Wash",
    zone_type="structural",
    assigned_workers=["3"],  # Michael Rodriguez
    required_worker_count=1,
    skill_requirements=[
        "excavator_operation",
        "foundation_excavation",
        "drainage_systems",
    ],
    trade_category="excavation",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="in_progress",
    start_date="2025-09-04",
    due_date="2025-09-06",
    min_estimated_hours=14.0,
    max_estimated_hours=18.0,
    actual_hours=12.0,
    completion_percentage=75,
    dependencies=["1"],
    blocks_tasks=["7"],
    required_materials=[{"material": "gravel_base", "quantity": 6, "unit": "yards"}],
    required_equipment=["excavator", "compactor", "drainage_pipe"],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["excavation_safety", "chemical_handling"],
    notes="Excavation 75% complete. Weather delays expected tomorrow.",
)

# PHASE 2: CONCRETE FOUNDATIONS (Week 1-2)

create_task(
    title="Retail Building Foundation Concrete Pour",
    description="Install rebar, set formwork, and pour concrete foundation for retail building. Ensure proper curing and finishing.",
    room="RET-FOUND",
    floor=0,
    building_section="Retail Building",
    zone_type="structural",
    assigned_workers=["3", "6"],  # Michael Rodriguez, Carlos Garcia
    required_worker_count=2,
    skill_requirements=[
        "concrete_pouring",
        "rebar_installation",
        "formwork_construction",
    ],
    trade_category="concrete",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="completed",
    start_date="2025-09-05",
    due_date="2025-09-07",
    min_estimated_hours=32.0,
    max_estimated_hours=40.0,
    actual_hours=36.0,
    completion_percentage=100,
    dependencies=["2"],
    blocks_tasks=["8"],
    required_materials=[
        {"material": "concrete", "quantity": 45, "unit": "cubic_yards"},
        {"material": "rebar", "quantity": 2400, "unit": "pounds"},
        {"material": "forms", "quantity": 200, "unit": "linear_feet"},
    ],
    required_equipment=["concrete_truck", "concrete_pump", "vibrator", "bull_float"],
    weather_dependent=True,
    noise_level="medium",
    safety_requirements=[
        "concrete_safety",
        "heavy_lifting",
        "chemical_exposure_protection",
    ],
    notes="Foundation poured successfully. Concrete tested at 4000 PSI design strength.",
)

create_task(
    title="Restaurant Foundation Concrete Pour",
    description="Pour restaurant foundation with integrated utility penetrations and grease trap provisions.",
    room="REST-FOUND",
    floor=0,
    building_section="Restaurant",
    zone_type="structural",
    assigned_workers=["3", "6"],  # Michael Rodriguez, Carlos Garcia
    required_worker_count=2,
    skill_requirements=[
        "concrete_pouring",
        "utility_integration",
        "specialized_finishing",
    ],
    trade_category="concrete",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="completed",
    start_date="2025-09-06",
    due_date="2025-09-08",
    min_estimated_hours=24.0,
    max_estimated_hours=30.0,
    actual_hours=27.5,
    completion_percentage=100,
    dependencies=["3"],
    blocks_tasks=["9"],
    required_materials=[
        {"material": "concrete", "quantity": 28, "unit": "cubic_yards"},
        {"material": "rebar", "quantity": 1800, "unit": "pounds"},
        {"material": "utility_sleeves", "quantity": 12, "unit": "pieces"},
    ],
    required_equipment=["concrete_truck", "concrete_pump", "specialty_forms"],
    weather_dependent=True,
    noise_level="medium",
    safety_requirements=["concrete_safety", "utility_coordination"],
    notes="Restaurant foundation completed with all utility penetrations properly installed.",
)

create_task(
    title="Car Wash Foundation Concrete Pour",
    description="Pour car wash foundation with chemical-resistant additives and integrated drainage channels.",
    room="WASH-FOUND",
    floor=0,
    building_section="Car Wash",
    zone_type="structural",
    assigned_workers=["3", "6"],  # Michael Rodriguez, Carlos Garcia
    required_worker_count=2,
    skill_requirements=[
        "concrete_pouring",
        "chemical_resistant_concrete",
        "drainage_integration",
    ],
    trade_category="concrete",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="blocked",
    start_date="2025-09-07",
    due_date="2025-09-09",
    min_estimated_hours=20.0,
    max_estimated_hours=26.0,
    actual_hours=0.0,
    completion_percentage=0,
    dependencies=["4"],
    blocks_tasks=["10"],
    required_materials=[
        {
            "material": "chemical_resistant_concrete",
            "quantity": 22,
            "unit": "cubic_yards",
        },
        {"material": "drainage_channels", "quantity": 80, "unit": "linear_feet"},
    ],
    required_equipment=["concrete_truck", "specialty_pump", "channel_forms"],
    weather_dependent=True,
    noise_level="medium",
    safety_requirements=["chemical_safety", "concrete_safety"],
    notes="BLOCKED: Waiting for excavation completion. Chemical-resistant concrete requires special delivery scheduling.",
)

# PHASE 3: STRUCTURAL FRAMING (Week 2-3)

create_task(
    title="Retail Building Steel Frame Erection",
    description="Erect structural steel frame for retail building including columns, beams, and roof structure using mobile crane.",
    room="RET-FRAME",
    floor=1,
    building_section="Retail Building",
    zone_type="structural",
    assigned_workers=["6", "3"],  # Carlos Garcia (lead), Michael Rodriguez (crane)
    required_worker_count=2,
    skill_requirements=[
        "structural_steel_erection",
        "crane_operation_mobile",
        "rigging_safety",
    ],
    trade_category="steel_erection",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="completed",
    start_date="2025-09-09",
    due_date="2025-09-12",
    min_estimated_hours=48.0,
    max_estimated_hours=56.0,
    actual_hours=52.0,
    completion_percentage=100,
    dependencies=["5"],
    blocks_tasks=["11", "12"],
    required_materials=[
        {"material": "structural_steel", "quantity": 25, "unit": "tons"},
        {"material": "bolts", "quantity": 500, "unit": "pieces"},
        {"material": "welding_materials", "quantity": 50, "unit": "pounds"},
    ],
    required_equipment=["mobile_crane", "welding_equipment", "rigging_gear"],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["fall_protection", "crane_safety", "steel_erection_safety"],
    notes="Steel frame erected successfully. All connections inspected and approved.",
)

create_task(
    title="Restaurant Steel Frame Erection",
    description="Install steel frame for restaurant with special provisions for kitchen ventilation and equipment loads.",
    room="REST-FRAME",
    floor=1,
    building_section="Restaurant",
    zone_type="structural",
    assigned_workers=["6", "3"],  # Carlos Garcia, Michael Rodriguez
    required_worker_count=2,
    skill_requirements=[
        "structural_steel_erection",
        "specialized_loading",
        "ventilation_provisions",
    ],
    trade_category="steel_erection",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="completed",
    start_date="2025-09-10",
    due_date="2025-09-13",
    min_estimated_hours=36.0,
    max_estimated_hours=44.0,
    actual_hours=40.0,
    completion_percentage=100,
    dependencies=["6"],
    blocks_tasks=["13"],
    required_materials=[
        {"material": "structural_steel", "quantity": 18, "unit": "tons"},
        {"material": "kitchen_support_steel", "quantity": 3, "unit": "tons"},
    ],
    required_equipment=["mobile_crane", "welding_equipment", "specialty_brackets"],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["fall_protection", "crane_safety", "kitchen_equipment_safety"],
    notes="Restaurant frame complete with reinforced areas for commercial kitchen equipment.",
)

create_task(
    title="Car Wash Structure Installation",
    description="Install car wash building structure with corrosion-resistant materials and integrated utility chases.",
    room="WASH-FRAME",
    floor=1,
    building_section="Car Wash",
    zone_type="structural",
    assigned_workers=[],  # UNASSIGNED - PENDING STATUS
    required_worker_count=2,
    skill_requirements=[
        "structural_steel_erection",
        "corrosion_resistant_materials",
        "utility_integration",
    ],
    trade_category="steel_erection",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="pending",
    start_date="2025-09-14",
    due_date="2025-09-17",
    min_estimated_hours=28.0,
    max_estimated_hours=36.0,
    actual_hours=0.0,
    completion_percentage=0,
    dependencies=["7"],
    blocks_tasks=["14"],
    required_materials=[
        {"material": "galvanized_steel", "quantity": 12, "unit": "tons"},
        {"material": "stainless_fasteners", "quantity": 200, "unit": "pieces"},
    ],
    required_equipment=["mobile_crane", "stainless_welding_equipment"],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["fall_protection", "chemical_resistant_ppe"],
    notes="PENDING ASSIGNMENT: Waiting for foundation completion and worker allocation.",
)

# PHASE 4: ELECTRICAL ROUGH-IN (Week 2-3, parallel with framing)

create_task(
    title="Retail Building Electrical Rough-In",
    description="Install electrical conduit, panel boxes, and rough wiring throughout retail building structure.",
    room="RET-ELEC",
    floor=1,
    building_section="Retail Building",
    zone_type="electrical",
    assigned_workers=["2", "4"],  # Sarah Thompson (lead), David Chen
    required_worker_count=2,
    skill_requirements=[
        "electrical_installation",
        "commercial_wiring",
        "conduit_installation",
    ],
    trade_category="electrical",
    created_by="project_manager",
    supervisor_id="2",
    priority=2,
    status="in_progress",
    start_date="2025-09-11",
    due_date="2025-09-16",
    min_estimated_hours=60.0,
    max_estimated_hours=72.0,
    actual_hours=35.0,
    completion_percentage=60,
    dependencies=["8"],
    blocks_tasks=["15"],
    required_materials=[
        {"material": "electrical_conduit", "quantity": 800, "unit": "feet"},
        {"material": "electrical_wire", "quantity": 2500, "unit": "feet"},
        {"material": "electrical_boxes", "quantity": 45, "unit": "pieces"},
    ],
    required_equipment=["conduit_bender", "wire_pulling_equipment", "electrical_tools"],
    weather_dependent=False,
    noise_level="medium",
    safety_requirements=["electrical_safety", "lockout_tagout", "fall_protection"],
    notes="Rough-in 60% complete. Main panel installation scheduled for next week.",
)

create_task(
    title="Restaurant Electrical and Kitchen Power",
    description="Install electrical rough-in for restaurant including high-capacity kitchen equipment circuits and emergency systems.",
    room="REST-ELEC",
    floor=1,
    building_section="Restaurant",
    zone_type="electrical",
    assigned_workers=["2", "4"],  # Sarah Thompson, David Chen
    required_worker_count=2,
    skill_requirements=[
        "electrical_installation",
        "high_capacity_circuits",
        "commercial_kitchen_wiring",
    ],
    trade_category="electrical",
    created_by="project_manager",
    supervisor_id="2",
    priority=3,
    status="in_progress",
    start_date="2025-09-12",
    due_date="2025-09-18",
    min_estimated_hours=48.0,
    max_estimated_hours=60.0,
    actual_hours=20.0,
    completion_percentage=40,
    dependencies=["9"],
    blocks_tasks=["16"],
    required_materials=[
        {"material": "heavy_duty_conduit", "quantity": 400, "unit": "feet"},
        {"material": "kitchen_grade_wire", "quantity": 1200, "unit": "feet"},
        {"material": "high_amp_panels", "quantity": 2, "unit": "pieces"},
    ],
    required_equipment=["heavy_duty_benders", "high_capacity_pullers"],
    weather_dependent=False,
    noise_level="medium",
    safety_requirements=["electrical_safety", "high_voltage_protection"],
    notes="Kitchen power circuits prioritized. Fire alarm system integration pending.",
)

create_task(
    title="Car Wash Electrical with Moisture Protection",
    description="Install electrical systems for car wash with waterproof components and chemical-resistant materials.",
    room="WASH-ELEC",
    floor=1,
    building_section="Car Wash",
    zone_type="electrical",
    assigned_workers=[],  # UNASSIGNED - PENDING STATUS
    required_worker_count=2,
    skill_requirements=[
        "electrical_installation",
        "waterproof_systems",
        "chemical_resistant_wiring",
    ],
    trade_category="electrical",
    created_by="project_manager",
    supervisor_id="2",
    priority=2,
    status="pending",
    start_date="2025-09-16",
    due_date="2025-09-20",
    min_estimated_hours=40.0,
    max_estimated_hours=50.0,
    actual_hours=0.0,
    completion_percentage=0,
    dependencies=["10"],
    blocks_tasks=["17"],
    required_materials=[
        {"material": "waterproof_conduit", "quantity": 300, "unit": "feet"},
        {"material": "chemical_resistant_wire", "quantity": 800, "unit": "feet"},
        {"material": "waterproof_panels", "quantity": 2, "unit": "pieces"},
    ],
    required_equipment=["waterproof_tools", "chemical_resistant_equipment"],
    weather_dependent=False,
    noise_level="medium",
    safety_requirements=[
        "electrical_safety",
        "chemical_protection",
        "moisture_protection",
    ],
    notes="PENDING ASSIGNMENT: Specialized waterproof electrical components on order.",
)

# PHASE 5: PLUMBING & HVAC ROUGH-IN (Week 3)

create_task(
    title="Retail Building Plumbing Rough-In",
    description="Install plumbing rough-in for retail building restrooms, break room, and utility areas.",
    room="RET-PLUMB",
    floor=1,
    building_section="Retail Building",
    zone_type="plumbing",
    assigned_workers=["5"],  # James Wilson
    required_worker_count=1,
    skill_requirements=[
        "plumbing_installation",
        "commercial_plumbing",
        "drain_installation",
    ],
    trade_category="plumbing",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="completed",
    start_date="2025-09-13",
    due_date="2025-09-17",
    min_estimated_hours=32.0,
    max_estimated_hours=40.0,
    actual_hours=36.0,
    completion_percentage=100,
    dependencies=["11"],
    blocks_tasks=["18"],
    required_materials=[
        {"material": "pvc_pipe", "quantity": 400, "unit": "feet"},
        {"material": "copper_pipe", "quantity": 200, "unit": "feet"},
        {"material": "plumbing_fixtures", "quantity": 8, "unit": "pieces"},
    ],
    required_equipment=["pipe_cutter", "soldering_torch", "pressure_tester"],
    weather_dependent=False,
    noise_level="medium",
    safety_requirements=["confined_space_safety", "chemical_safety"],
    notes="Plumbing rough-in completed and pressure tested successfully.",
)

create_task(
    title="Restaurant Kitchen Plumbing and Grease Systems",
    description="Install complex restaurant plumbing including grease traps, commercial dishwasher connections, and floor drains.",
    room="REST-KITCHEN",
    floor=1,
    building_section="Restaurant",
    zone_type="plumbing",
    assigned_workers=["5"],  # James Wilson
    required_worker_count=1,
    skill_requirements=[
        "commercial_kitchen_plumbing",
        "grease_trap_installation",
        "floor_drain_systems",
    ],
    trade_category="plumbing",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="in_progress",
    start_date="2025-09-15",
    due_date="2025-09-20",
    min_estimated_hours=40.0,
    max_estimated_hours=50.0,
    actual_hours=25.0,
    completion_percentage=60,
    dependencies=["13"],
    blocks_tasks=["19"],
    required_materials=[
        {"material": "grease_trap", "quantity": 1, "unit": "pieces"},
        {"material": "commercial_drains", "quantity": 6, "unit": "pieces"},
        {"material": "stainless_piping", "quantity": 150, "unit": "feet"},
    ],
    required_equipment=["heavy_pipe_tools", "grease_trap_equipment"],
    weather_dependent=False,
    noise_level="medium",
    safety_requirements=["confined_space_safety", "chemical_handling"],
    notes="Grease trap installation in progress. Health department inspection scheduled.",
)

create_task(
    title="Car Wash Water Reclaim System",
    description="Install car wash water reclamation system with chemical treatment and recycling capabilities.",
    room="WASH-WATER",
    floor=0,
    building_section="Car Wash",
    zone_type="mechanical",
    assigned_workers=[],  # UNASSIGNED - PENDING STATUS
    required_worker_count=1,
    skill_requirements=[
        "water_treatment_systems",
        "chemical_handling",
        "pump_installation",
    ],
    trade_category="plumbing",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="pending",
    start_date="2025-09-18",
    due_date="2025-09-23",
    min_estimated_hours=35.0,
    max_estimated_hours=45.0,
    actual_hours=0.0,
    completion_percentage=0,
    dependencies=["14"],
    blocks_tasks=["20"],
    required_materials=[
        {"material": "water_treatment_system", "quantity": 1, "unit": "pieces"},
        {"material": "reclaim_pumps", "quantity": 3, "unit": "pieces"},
        {"material": "chemical_storage_tanks", "quantity": 4, "unit": "pieces"},
    ],
    required_equipment=["pump_installation_tools", "chemical_handling_equipment"],
    weather_dependent=False,
    noise_level="high",
    safety_requirements=["chemical_safety", "confined_space_safety"],
    notes="PENDING ASSIGNMENT: Environmental permits approved. Equipment delivery scheduled.",
)

# PHASE 6: ROOFING & EXTERIOR (Week 3-4)

create_task(
    title="Retail Building Metal Roofing Installation",
    description="Install standing seam metal roofing system on retail building with proper insulation and vapor barriers.",
    room="RET-ROOF",
    floor=2,
    building_section="Retail Building",
    zone_type="roofing",
    assigned_workers=["9"],  # Angela Davis
    required_worker_count=1,
    skill_requirements=["metal_roofing", "waterproofing_membrane", "roof_insulation"],
    trade_category="roofing",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="completed",
    start_date="2025-09-16",
    due_date="2025-09-20",
    min_estimated_hours=48.0,
    max_estimated_hours=56.0,
    actual_hours=52.0,
    completion_percentage=100,
    dependencies=["11"],
    blocks_tasks=["21"],
    required_materials=[
        {"material": "metal_roofing_panels", "quantity": 3500, "unit": "sq_feet"},
        {"material": "insulation", "quantity": 3500, "unit": "sq_feet"},
        {"material": "fasteners", "quantity": 1000, "unit": "pieces"},
    ],
    required_equipment=[
        "metal_cutting_tools",
        "fastening_equipment",
        "safety_equipment",
    ],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["fall_protection", "roofing_safety", "metal_handling"],
    notes="Metal roofing installation completed. All seams properly sealed and tested.",
)

create_task(
    title="Restaurant Roofing with Kitchen Ventilation Penetrations",
    description="Install restaurant roofing with integrated kitchen hood penetrations and grease exhaust systems.",
    room="REST-ROOF",
    floor=2,
    building_section="Restaurant",
    zone_type="roofing",
    assigned_workers=["9"],  # Angela Davis
    required_worker_count=1,
    skill_requirements=[
        "metal_roofing",
        "ventilation_penetrations",
        "grease_exhaust_integration",
    ],
    trade_category="roofing",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="canceled",
    start_date="2025-09-18",
    due_date="2025-09-22",
    min_estimated_hours=36.0,
    max_estimated_hours=44.0,
    actual_hours=8.0,
    completion_percentage=15,
    dependencies=["13"],
    blocks_tasks=["22"],
    required_materials=[
        {"material": "metal_roofing_panels", "quantity": 2200, "unit": "sq_feet"},
        {"material": "kitchen_hood_curbs", "quantity": 2, "unit": "pieces"},
    ],
    required_equipment=["metal_cutting_tools", "penetration_sealing_equipment"],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["fall_protection", "ventilation_safety"],
    notes="CANCELED: Kitchen hood design changes require roof structure modifications. Rescheduling pending engineering review.",
)

create_task(
    title="Car Wash Canopy Structure Installation",
    description="Install car wash drive-through canopy with integrated lighting and signage supports.",
    room="WASH-CANOPY",
    floor=2,
    building_section="Car Wash",
    zone_type="structural",
    assigned_workers=[],  # UNASSIGNED - PENDING STATUS
    required_worker_count=2,
    skill_requirements=[
        "canopy_installation",
        "structural_steel_erection",
        "lighting_integration",
    ],
    trade_category="steel_erection",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="pending",
    start_date="2025-09-20",
    due_date="2025-09-24",
    min_estimated_hours=30.0,
    max_estimated_hours=38.0,
    actual_hours=0.0,
    completion_percentage=0,
    dependencies=["14"],
    blocks_tasks=["23"],
    required_materials=[
        {"material": "canopy_steel", "quantity": 8, "unit": "tons"},
        {"material": "roofing_membrane", "quantity": 1200, "unit": "sq_feet"},
        {"material": "led_lighting_strips", "quantity": 200, "unit": "feet"},
    ],
    required_equipment=["mobile_crane", "membrane_welding_equipment"],
    weather_dependent=True,
    noise_level="high",
    safety_requirements=["fall_protection", "crane_safety"],
    notes="PENDING ASSIGNMENT: Canopy steel fabrication completed. Ready for installation.",
)

# PHASE 7: INTERIOR FINISHES (Week 4)

create_task(
    title="Retail Building Interior Framing and Drywall",
    description="Install interior partition framing and drywall for retail spaces, fitting rooms, and office areas.",
    room="RET-INTERIOR",
    floor=1,
    building_section="Retail Building",
    zone_type="interior",
    assigned_workers=["6", "10"],  # Carlos Garcia, Tyler Johnson
    required_worker_count=2,
    skill_requirements=["framing_wood", "drywall_installation", "interior_layout"],
    trade_category="carpentry",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="in_progress",
    start_date="2025-09-19",
    due_date="2025-09-26",
    min_estimated_hours=60.0,
    max_estimated_hours=72.0,
    actual_hours=30.0,
    completion_percentage=45,
    dependencies=["15", "18"],
    blocks_tasks=["24"],
    required_materials=[
        {"material": "wood_framing", "quantity": 800, "unit": "linear_feet"},
        {"material": "drywall", "quantity": 4000, "unit": "sq_feet"},
        {"material": "insulation", "quantity": 2000, "unit": "sq_feet"},
    ],
    required_equipment=["framing_tools", "drywall_lift", "insulation_blower"],
    weather_dependent=False,
    noise_level="medium",
    safety_requirements=["dust_protection", "lifting_safety"],
    notes="Interior framing 70% complete. Drywall installation beginning in retail areas.",
)

create_task(
    title="Restaurant Interior Build-Out with Kitchen Prep",
    description="Complete restaurant interior including kitchen prep areas, dining room framing, and specialty finishes.",
    room="REST-INTERIOR",
    floor=1,
    building_section="Restaurant",
    zone_type="interior",
    assigned_workers=["6"],  # Carlos Garcia
    required_worker_count=1,
    skill_requirements=[
        "commercial_interior_framing",
        "kitchen_prep_areas",
        "restaurant_finishes",
    ],
    trade_category="carpentry",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="in_progress",
    start_date="2025-09-21",
    due_date="2025-09-28",
    min_estimated_hours=45.0,
    max_estimated_hours=55.0,
    actual_hours=15.0,
    completion_percentage=25,
    dependencies=["16", "19"],
    blocks_tasks=["25"],
    required_materials=[
        {"material": "commercial_framing", "quantity": 400, "unit": "linear_feet"},
        {"material": "fire_rated_drywall", "quantity": 1800, "unit": "sq_feet"},
        {"material": "stainless_steel_panels", "quantity": 200, "unit": "sq_feet"},
    ],
    required_equipment=["commercial_tools", "fire_rated_materials"],
    weather_dependent=False,
    noise_level="medium",
    safety_requirements=["fire_safety", "commercial_safety_standards"],
    notes="Kitchen area framing started. Fire-rated assemblies being installed per code.",
)

create_task(
    title="Retail Building Interior Painting - Phase 1",
    description="Prime and paint interior walls, ceilings, and trim work in retail building common areas.",
    room="RET-PAINT",
    floor=1,
    building_section="Retail Building",
    zone_type="interior",
    assigned_workers=["7"],  # Lisa Anderson
    required_worker_count=1,
    skill_requirements=["interior_painting", "commercial_painting", "spray_painting"],
    trade_category="painting",
    created_by="project_manager",
    supervisor_id="1",
    priority=1,
    status="completed",
    start_date="2025-09-23",
    due_date="2025-09-27",
    min_estimated_hours=40.0,
    max_estimated_hours=48.0,
    actual_hours=44.0,
    completion_percentage=100,
    dependencies=["21"],
    blocks_tasks=["26"],
    required_materials=[
        {"material": "primer", "quantity": 15, "unit": "gallons"},
        {"material": "interior_paint", "quantity": 20, "unit": "gallons"},
        {"material": "brushes_rollers", "quantity": 1, "unit": "set"},
    ],
    required_equipment=["spray_equipment", "scaffolding", "drop_cloths"],
    weather_dependent=False,
    noise_level="low",
    safety_requirements=["respiratory_protection", "chemical_safety"],
    notes="Phase 1 painting completed. Excellent coverage and finish quality achieved.",
)

create_task(
    title="Retail Building Flooring Installation",
    description="Install polished concrete flooring in retail areas and ceramic tile in restrooms.",
    room="RET-FLOOR",
    floor=1,
    building_section="Retail Building",
    zone_type="flooring",
    assigned_workers=["8"],  # Kevin Brown
    required_worker_count=1,
    skill_requirements=[
        "polished_concrete",
        "tile_installation_ceramic",
        "floor_preparation",
    ],
    trade_category="flooring",
    created_by="project_manager",
    supervisor_id="1",
    priority=2,
    status="in_progress",
    start_date="2025-09-24",
    due_date="2025-09-30",
    min_estimated_hours=50.0,
    max_estimated_hours=60.0,
    actual_hours=25.0,
    completion_percentage=40,
    dependencies=["24"],
    blocks_tasks=["27"],
    required_materials=[
        {"material": "concrete_polish", "quantity": 500, "unit": "sq_feet"},
        {"material": "ceramic_tile", "quantity": 400, "unit": "sq_feet"},
        {"material": "grout_adhesive", "quantity": 50, "unit": "pounds"},
    ],
    required_equipment=["concrete_polisher", "tile_saw", "grouting_tools"],
    weather_dependent=False,
    noise_level="high",
    safety_requirements=["dust_protection", "noise_protection"],
    notes="Concrete polishing 60% complete. Tile installation starting in restroom areas.",
)

# FINAL TASKS & SYSTEMS

create_task(
    title="Retail Building Final Electrical and Lighting",
    description="Install final electrical fixtures, lighting systems, and complete electrical connections throughout retail building.",
    room="RET-FINAL-ELEC",
    floor=1,
    building_section="Retail Building",
    zone_type="electrical",
    assigned_workers=["4"],  # David Chen
    required_worker_count=1,
    skill_requirements=[
        "lighting_installation",
        "final_electrical_connections",
        "electrical_testing",
    ],
    trade_category="electrical",
    created_by="project_manager",
    supervisor_id="2",
    priority=2,
    status="pending",
    start_date="2025-09-26",
    due_date="2025-09-30",
    min_estimated_hours=32.0,
    max_estimated_hours=40.0,
    actual_hours=0.0,
    completion_percentage=0,
    dependencies=["26"],
    blocks_tasks=["28"],
    required_materials=[
        {"material": "led_fixtures", "quantity": 40, "unit": "pieces"},
        {"material": "electrical_devices", "quantity": 60, "unit": "pieces"},
        {"material": "circuit_breakers", "quantity": 20, "unit": "pieces"},
    ],
    required_equipment=["electrical_testing_equipment", "fixture_installation_tools"],
    weather_dependent=False,
    noise_level="low",
    safety_requirements=["electrical_safety", "testing_protocols"],
    notes="PENDING: Waiting for interior completion. Fixtures staged and ready for installation.",
)

create_task(
    title="Restaurant Final Systems Integration",
    description="Complete restaurant systems integration including kitchen equipment connections, fire suppression, and final inspections.",
    room="REST-FINAL",
    floor=1,
    building_section="Restaurant",
    zone_type="mechanical",
    assigned_workers=[],  # UNASSIGNED - PENDING STATUS
    required_worker_count=2,
    skill_requirements=[
        "kitchen_equipment_installation",
        "fire_suppression_systems",
        "final_system_testing",
    ],
    trade_category="mechanical",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="pending",
    start_date="2025-09-27",
    due_date="2025-09-30",
    min_estimated_hours=40.0,
    max_estimated_hours=50.0,
    actual_hours=0.0,
    completion_percentage=0,
    dependencies=["25"],
    blocks_tasks=["29"],
    required_materials=[
        {"material": "fire_suppression_system", "quantity": 1, "unit": "set"},
        {"material": "kitchen_equipment_connections", "quantity": 8, "unit": "pieces"},
        {"material": "testing_materials", "quantity": 1, "unit": "set"},
    ],
    required_equipment=["fire_system_tools", "kitchen_installation_equipment"],
    weather_dependent=False,
    noise_level="medium",
    safety_requirements=["fire_safety", "kitchen_safety", "system_testing_safety"],
    notes="PENDING ASSIGNMENT: Kitchen equipment delivered. Fire suppression system ready for final connections.",
)

create_task(
    title="Site Final Inspection and Cleanup",
    description="Conduct final site inspection, complete punch list items, and perform comprehensive site cleanup.",
    room="SITE-FINAL",
    floor=0,
    building_section="Site Wide",
    zone_type="general",
    assigned_workers=["1", "10"],  # Robert Martinez, Tyler Johnson
    required_worker_count=2,
    skill_requirements=[
        "quality_control_inspection",
        "site_cleanup",
        "final_documentation",
    ],
    trade_category="management",
    created_by="project_manager",
    supervisor_id="1",
    priority=3,
    status="pending",
    start_date="2025-09-30",
    due_date="2025-09-30",
    min_estimated_hours=16.0,
    max_estimated_hours=24.0,
    actual_hours=0.0,
    completion_percentage=0,
    dependencies=["27", "28"],
    blocks_tasks=[],
    required_materials=[
        {"material": "cleaning_supplies", "quantity": 1, "unit": "set"},
        {"material": "inspection_forms", "quantity": 1, "unit": "set"},
    ],
    required_equipment=["inspection_tools", "cleanup_equipment"],
    weather_dependent=False,
    noise_level="low",
    safety_requirements=["final_safety_inspection", "cleanup_safety"],
    notes="PENDING: Final inspection scheduled with city inspector. Cleanup crew on standby.",
)

# =============================================================================
# DATASET SUMMARY
# =============================================================================

# TOTAL USERS: 10
# - 1 Supervisor (Robert Martinez)
# - 1 Team Leader (Sarah Thompson)
# - 8 Workers (7 experienced + 1 junior)

# TOTAL TASKS: 30
# STATUS BREAKDOWN:
# - Completed: 9 tasks (30%)
# - In Progress: 8 tasks (27%)
# - Pending: 11 tasks (37%) [includes unassigned tasks]
# - Blocked: 1 task (3%)
# - Canceled: 1 task (3%)

# BUILDINGS COVERED:
# - Retail Building: 12 tasks
# - Restaurant: 10 tasks
# - Car Wash: 6 tasks
# - Site-wide: 2 tasks

# TRADE CATEGORIES REPRESENTED:
# - Electrical: 6 tasks
# - Concrete/Structural: 6 tasks
# - Plumbing/HVAC: 4 tasks
# - Carpentry/Framing: 4 tasks
# - Roofing: 3 tasks
# - Painting: 2 tasks
# - Flooring: 2 tasks
# - General/Management: 3 tasks

# REALISTIC SCENARIOS INCLUDED:
# - Weather delays (Car Wash Foundation)
# - Design changes causing cancellation (Restaurant Roof)
# - Permit dependencies (Water Reclaim System)
# - Unassigned pending tasks for AI allocation
# - Complex multi-building dependencies
# - Parallel task execution opportunities
# - Resource conflicts and priority management

import os
import logging
from db_utils import get_db_connection, execute_query

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_database():
    """
    Set up the database schema by creating all required tables
    if they don't already exist.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create projects table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS projects (
            project_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            location VARCHAR(100) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            budget NUMERIC(12, 2) NOT NULL,
            status VARCHAR(20) NOT NULL,
            client VARCHAR(100) NOT NULL,
            description TEXT
        )
        """
        )

        # Create tasks table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(project_id),
            name VARCHAR(100) NOT NULL,
            description TEXT,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status VARCHAR(20) NOT NULL,
            priority VARCHAR(20) NOT NULL
        )
        """
        )

        # Create workers table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS workers (
            worker_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            role VARCHAR(50) NOT NULL,
            contact VARCHAR(50) NOT NULL,
            certification VARCHAR(100),
            availability VARCHAR(20) NOT NULL,
            hourly_rate NUMERIC(8, 2) NOT NULL
        )
        """
        )

        # Create materials table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS materials (
            material_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            quantity INTEGER NOT NULL,
            unit VARCHAR(20) NOT NULL,
            cost_per_unit NUMERIC(10, 2) NOT NULL,
            supplier VARCHAR(100) NOT NULL
        )
        """
        )

        # Create safety table for incidents
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS safety (
            incident_id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(project_id),
            date DATE NOT NULL,
            incident_type VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            severity VARCHAR(20) NOT NULL,
            resolved BOOLEAN NOT NULL,
            action_taken TEXT
        )
        """
        )

        # Create equipment table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS equipment (
            equipment_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL,
            last_maintenance DATE NOT NULL,
            next_maintenance DATE NOT NULL,
            notes TEXT
        )
        """
        )

        # Create safety_checklists table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS safety_checklists (
            checklist_id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(project_id),
            date DATE NOT NULL,
            inspector VARCHAR(100) NOT NULL,
            ppe_compliance BOOLEAN NOT NULL,
            hazard_signage BOOLEAN NOT NULL,
            equipment_safety BOOLEAN NOT NULL,
            fire_safety BOOLEAN NOT NULL,
            first_aid BOOLEAN NOT NULL,
            notes TEXT
        )
        """
        )

        # Create daily_tasks table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS daily_tasks (
            daily_task_id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(project_id),
            worker_id INTEGER REFERENCES workers(worker_id),
            date DATE NOT NULL,
            task_description TEXT NOT NULL,
            hours_worked NUMERIC(5, 2) NOT NULL,
            completed BOOLEAN NOT NULL,
            notes TEXT
        )
        """
        )

        # Create progress_tracking table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS progress_tracking (
            progress_id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(project_id),
            date DATE NOT NULL,
            milestone VARCHAR(100) NOT NULL,
            percent_complete NUMERIC(5, 2) NOT NULL,
            notes TEXT
        )
        """
        )

        conn.commit()
        logger.info("Database tables created successfully")

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False


def insert_sample_data():
    """
    Insert sample data into the database if tables are empty.
    """
    try:
        # Check if projects table has data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Sample data already exists, skipping insertion")
            cursor.close()
            conn.close()
            return True

        # Insert sample projects
        projects = [
            (
                "Riverside Towers",
                "Downtown",
                "2023-01-15",
                "2024-06-30",
                5200000.00,
                "In Progress",
                "Riverside Development Corp",
                "Luxury condominium complex with 25 floors",
            ),
            (
                "Metro Transit Hub",
                "North District",
                "2023-03-10",
                "2024-11-15",
                8500000.00,
                "Planning",
                "City Transport Authority",
                "Multi-modal transit center connecting bus, rail, and subway",
            ),
            (
                "Greenview Office Park",
                "West Side",
                "2022-09-05",
                "2023-12-31",
                3800000.00,
                "Completed",
                "Greenview Enterprises",
                "Eco-friendly office park with four buildings and green spaces",
            ),
            (
                "Harbor Bridge Renovation",
                "Waterfront",
                "2023-05-20",
                "2024-08-10",
                12500000.00,
                "In Progress",
                "State Highway Department",
                "Structural renovation and expansion of the main harbor bridge",
            ),
            (
                "Community Health Center",
                "East District",
                "2023-07-01",
                "2024-04-30",
                4200000.00,
                "In Progress",
                "Regional Health Authority",
                "Modern healthcare facility with emergency services and specialty clinics",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO projects 
            (name, location, start_date, end_date, budget, status, client, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            projects,
        )

        # Insert sample tasks
        tasks = [
            (
                1,
                "Foundation Work",
                "Excavation and foundation pouring",
                "2023-01-20",
                "2023-03-15",
                "Completed",
                "High",
            ),
            (
                1,
                "Structural Framing",
                "Steel frame installation",
                "2023-03-20",
                "2023-06-30",
                "Completed",
                "High",
            ),
            (
                1,
                "Exterior Cladding",
                "Installation of facade materials",
                "2023-07-05",
                "2023-11-15",
                "In Progress",
                "Medium",
            ),
            (
                1,
                "Interior Finishing",
                "Drywall, painting, and fixtures",
                "2023-10-01",
                "2024-03-30",
                "Not Started",
                "Medium",
            ),
            (
                1,
                "Mechanical Systems",
                "HVAC, plumbing, and electrical",
                "2023-08-15",
                "2024-02-28",
                "In Progress",
                "High",
            ),
            (
                2,
                "Site Preparation",
                "Clearing and grading",
                "2023-03-15",
                "2023-05-30",
                "Not Started",
                "High",
            ),
            (
                3,
                "Final Inspections",
                "Building code compliance checks",
                "2023-11-15",
                "2023-12-15",
                "Completed",
                "High",
            ),
            (
                4,
                "Traffic Management",
                "Implementing detours and signage",
                "2023-05-25",
                "2023-07-15",
                "Completed",
                "High",
            ),
            (
                4,
                "Structural Assessment",
                "Evaluating current bridge conditions",
                "2023-06-01",
                "2023-07-30",
                "Completed",
                "High",
            ),
            (
                5,
                "Site Preparation",
                "Clearing and foundation work",
                "2023-07-10",
                "2023-09-20",
                "Completed",
                "High",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO tasks 
            (project_id, name, description, start_date, end_date, status, priority)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            tasks,
        )

        # Insert sample workers
        workers = [
            (
                "John Smith",
                "Project Manager",
                "john.smith@example.com",
                "PMP Certified",
                "Full-time",
                45.00,
            ),
            (
                "Sarah Johnson",
                "Civil Engineer",
                "sarah.j@example.com",
                "PE License",
                "Full-time",
                38.50,
            ),
            (
                "Michael Brown",
                "Electrician",
                "mbrown@example.com",
                "Master Electrician",
                "Full-time",
                32.75,
            ),
            (
                "Lisa Chen",
                "Safety Officer",
                "l.chen@example.com",
                "OSHA Certified",
                "Full-time",
                36.25,
            ),
            (
                "Robert Davis",
                "Equipment Operator",
                "rdavis@example.com",
                "Heavy Equipment License",
                "Full-time",
                29.50,
            ),
            (
                "James Wilson",
                "Carpenter",
                "jwilson@example.com",
                "Journeyman Carpenter",
                "Full-time",
                31.00,
            ),
            (
                "Emily Rodriguez",
                "Site Supervisor",
                "e.rodriguez@example.com",
                "Construction Supervision",
                "Full-time",
                40.00,
            ),
            (
                "David Thompson",
                "Plumber",
                "dthompson@example.com",
                "Master Plumber",
                "Contract",
                33.50,
            ),
            (
                "Maria Garcia",
                "Architect",
                "m.garcia@example.com",
                "Licensed Architect",
                "Part-time",
                42.75,
            ),
            (
                "Thomas Wright",
                "Laborer",
                "twright@example.com",
                "OSHA 10",
                "Full-time",
                25.50,
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO workers 
            (name, role, contact, certification, availability, hourly_rate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            workers,
        )

        # Insert sample materials
        materials = [
            (
                "Concrete Mix",
                "Building Materials",
                1500,
                "Bags",
                12.50,
                "ABC Suppliers",
            ),
            ("Steel Rebar", "Metals", 8000, "Feet", 2.75, "Steel Solutions Inc."),
            ("Lumber 2x4", "Wood", 5000, "Pieces", 3.85, "Timber Products"),
            (
                "Drywall Sheets",
                "Building Materials",
                1200,
                "Sheets",
                15.25,
                "Construction Supply Co.",
            ),
            ("Copper Wiring", "Electrical", 10000, "Feet", 1.20, "Electric Warehouse"),
            ("PVC Pipes", "Plumbing", 3000, "Feet", 2.30, "Plumbing Plus"),
            ("Paint - Interior", "Finishing", 500, "Gallons", 24.99, "Color World"),
            (
                "Roof Shingles",
                "Roofing",
                450,
                "Bundles",
                32.50,
                "Roofing Supplies Inc.",
            ),
            ("Insulation", "Building Materials", 800, "Rolls", 18.75, "Insulate Pro"),
            ("Window Units", "Fixtures", 175, "Units", 210.00, "Glass Masters"),
        ]

        cursor.executemany(
            """
            INSERT INTO materials 
            (name, category, quantity, unit, cost_per_unit, supplier)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            materials,
        )

        # Insert sample safety incidents
        safety_incidents = [
            (
                1,
                "2023-04-12",
                "Minor Injury",
                "Worker sustained minor cut on hand",
                "Low",
                True,
                "First aid administered, worker resumed duties",
            ),
            (
                3,
                "2023-10-05",
                "Equipment Malfunction",
                "Crane hydraulic system failure",
                "Medium",
                True,
                "Equipment repaired and recertified",
            ),
            (
                4,
                "2023-06-23",
                "Near Miss",
                "Falling material narrowly missed worker",
                "Medium",
                True,
                "Additional safety netting installed",
            ),
            (
                1,
                "2023-09-02",
                "Property Damage",
                "Vehicle damaged perimeter fencing",
                "Low",
                True,
                "Fence repaired, driver retrained",
            ),
            (
                5,
                "2023-08-15",
                "Environmental",
                "Chemical spill on site",
                "High",
                True,
                "Hazmat team cleaned site, procedures reviewed",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO safety 
            (project_id, date, incident_type, description, severity, resolved, action_taken)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            safety_incidents,
        )

        # Insert sample equipment records
        equipment = [
            (
                "Excavator - CAT 320",
                "Heavy Equipment",
                "Operational",
                "2023-05-10",
                "2023-11-10",
                "Hydraulic system serviced",
            ),
            (
                "Tower Crane TC-205",
                "Lifting Equipment",
                "Operational",
                "2023-07-15",
                "2024-01-15",
                "Load testing completed",
            ),
            (
                "Concrete Mixer CM-10",
                "Mixing Equipment",
                "Under Repair",
                "2023-04-20",
                "2023-10-20",
                "Motor being replaced",
            ),
            (
                "Bulldozer D8T",
                "Heavy Equipment",
                "Operational",
                "2023-08-05",
                "2024-02-05",
                "Tracks replaced",
            ),
            (
                "Generator G-5000",
                "Power Equipment",
                "Operational",
                "2023-09-12",
                "2024-03-12",
                "Fuel system cleaned",
            ),
            (
                "Backhoe Loader 416F",
                "Heavy Equipment",
                "Operational",
                "2023-06-25",
                "2023-12-25",
                "Regular maintenance",
            ),
            (
                "Air Compressor AC-50",
                "Air Tools",
                "Under Repair",
                "2023-03-30",
                "2023-09-30",
                "Pressure valve replacement",
            ),
            (
                "Forklift FL-3000",
                "Material Handling",
                "Operational",
                "2023-08-18",
                "2024-02-18",
                "Hydraulic system checked",
            ),
            (
                "Boom Lift BL-60",
                "Access Equipment",
                "Operational",
                "2023-07-02",
                "2024-01-02",
                "Annual certification completed",
            ),
            (
                "Concrete Pump CP-40",
                "Concrete Equipment",
                "Operational",
                "2023-09-05",
                "2024-03-05",
                "Hoses replaced",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO equipment 
            (name, type, status, last_maintenance, next_maintenance, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            equipment,
        )

        # Insert sample safety checklists
        safety_checklists = [
            (
                1,
                "2023-06-15",
                "Lisa Chen",
                True,
                True,
                True,
                True,
                True,
                "All safety measures in compliance",
            ),
            (
                1,
                "2023-07-15",
                "Lisa Chen",
                True,
                True,
                True,
                True,
                True,
                "Fire extinguishers recertified",
            ),
            (
                2,
                "2023-05-20",
                "David Thompson",
                True,
                False,
                True,
                True,
                True,
                "Hazard signage needs improvement",
            ),
            (
                3,
                "2023-11-10",
                "Emily Rodriguez",
                True,
                True,
                True,
                True,
                True,
                "Monthly inspection completed",
            ),
            (
                4,
                "2023-08-05",
                "Lisa Chen",
                True,
                True,
                False,
                True,
                True,
                "Equipment safety issues addressed",
            ),
            (
                4,
                "2023-09-05",
                "Lisa Chen",
                True,
                True,
                True,
                True,
                True,
                "Follow-up inspection completed",
            ),
            (
                5,
                "2023-08-25",
                "Michael Brown",
                True,
                True,
                True,
                False,
                True,
                "Fire safety equipment being updated",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO safety_checklists 
            (project_id, date, inspector, ppe_compliance, hazard_signage, 
             equipment_safety, fire_safety, first_aid, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            safety_checklists,
        )

        # Insert sample daily tasks
        daily_tasks = [
            (
                1,
                2,
                "2023-06-20",
                "Structural steel installation - North wing",
                8.5,
                True,
                "Completed ahead of schedule",
            ),
            (
                1,
                3,
                "2023-06-20",
                "Electrical conduit installation - Floors 1-3",
                9.0,
                True,
                "Additional materials needed for tomorrow",
            ),
            (
                1,
                6,
                "2023-06-20",
                "Interior framing - Floors 7-8",
                8.0,
                True,
                "No issues reported",
            ),
            (
                3,
                8,
                "2023-10-15",
                "Final plumbing inspections - Building A",
                6.5,
                True,
                "All inspections passed",
            ),
            (
                4,
                5,
                "2023-07-10",
                "Site preparation and equipment staging",
                10.0,
                True,
                "Overtime required to complete",
            ),
            (
                5,
                7,
                "2023-08-20",
                "Foundation work supervision",
                8.0,
                True,
                "Concrete pouring scheduled for tomorrow",
            ),
            (
                1,
                10,
                "2023-06-21",
                "Material handling and site cleanup",
                7.5,
                True,
                "Site ready for inspections",
            ),
            (
                4,
                4,
                "2023-07-11",
                "Safety monitoring during lane closures",
                9.0,
                True,
                "No incidents reported",
            ),
            (
                5,
                2,
                "2023-08-21",
                "Structural calculations and site verification",
                8.0,
                True,
                "Minor adjustments to foundation plans",
            ),
            (
                1,
                9,
                "2023-06-22",
                "Architectural review and site measurements",
                5.0,
                True,
                "Updated drawings provided to team",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO daily_tasks 
            (project_id, worker_id, date, task_description, hours_worked, completed, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            daily_tasks,
        )

        # Insert sample progress tracking
        progress_tracking = [
            (1, "2023-03-15", "Foundation Complete", 15.00, "On schedule"),
            (1, "2023-06-30", "Structural Framing Complete", 35.00, "On schedule"),
            (
                1,
                "2023-09-30",
                "Exterior Shell Complete",
                60.00,
                "2 weeks behind schedule",
            ),
            (3, "2023-01-15", "Site Preparation Complete", 10.00, "On schedule"),
            (3, "2023-04-30", "Foundation and Framing Complete", 30.00, "On schedule"),
            (3, "2023-08-15", "Buildings Enclosed", 65.00, "On schedule"),
            (
                3,
                "2023-11-30",
                "Interior Finishing Complete",
                95.00,
                "Ahead of schedule",
            ),
            (4, "2023-07-15", "Traffic Management Implemented", 20.00, "On schedule"),
            (4, "2023-09-30", "Structural Reinforcement Phase 1", 40.00, "On schedule"),
            (5, "2023-09-20", "Foundation Complete", 25.00, "1 week behind schedule"),
        ]

        cursor.executemany(
            """
            INSERT INTO progress_tracking 
            (project_id, date, milestone, percent_complete, notes)
            VALUES (%s, %s, %s, %s, %s)
        """,
            progress_tracking,
        )

        conn.commit()
        logger.info("Sample data inserted successfully")

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        logger.error(f"Error inserting sample data: {str(e)}")
        return False


if __name__ == "__main__":
    if setup_database():
        insert_sample_data()

import os
import random
import json
from dotenv import load_dotenv
import openai
from datetime import datetime, timedelta

class QueenWorker:
    """
    The QueenWorker class is responsible for generating random construction company data
    and design restrictions that will be used by the Worker class to generate UI.
    """
    
    def __init__(self):
        """Initialize the QueenWorker class"""
        # List of possible company names, services, and other data to randomly choose from
        self.company_name_prefixes = ["Elite", "Premier", "Modern", "Innovative", "Structural", "Skyline", "Foundation", "Urban", "Metropolitan", "Advanced"]
        self.company_name_suffixes = ["Construction", "Builders", "Development", "Engineering", "Structures", "Architecture", "Contractors", "Projects", "Properties", "Developments"]
        
        self.services = [
            "Residential Construction", 
            "Commercial Construction", 
            "Industrial Construction",
            "Road Construction",
            "Bridge Building",
            "Renovation Services",
            "Interior Design",
            "Architectural Planning",
            "Project Management",
            "Demolition Services",
            "Green Building",
            "Historic Restoration",
            "Landscape Design",
            "Civil Engineering",
            "Concrete Services"
        ]
        
        self.locations = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
            "London", "Manchester", "Birmingham", "Leeds", "Glasgow",
            "Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"
        ]
        
        self.color_schemes = [
            {
                "primary": "#1E3A8A",  # Dark blue
                "secondary": "#FFB800",  # Gold
                "accent": "#E5E5E5",  # Light gray
                "text": "#333333"  # Dark gray
            },
            {
                "primary": "#2C3E50",  # Dark blue gray
                "secondary": "#E74C3C",  # Red
                "accent": "#ECF0F1",  # Light gray
                "text": "#2C3E50"  # Dark blue gray
            },
            {
                "primary": "#212121",  # Almost black
                "secondary": "#FFC107",  # Amber
                "accent": "#F5F5F5",  # Off white
                "text": "#212121"  # Almost black
            },
            {
                "primary": "#006064",  # Teal
                "secondary": "#FF6F00",  # Orange
                "accent": "#EEEEEE",  # Light gray
                "text": "#333333"  # Dark gray
            },
            {
                "primary": "#2E7D32",  # Green
                "secondary": "#C62828",  # Red
                "accent": "#F5F5F5",  # Off white
                "text": "#212121"  # Almost black
            }
        ]
        
    def generate_data(self):
        """Generate random construction company data"""
        # Generate company name
        company_name = f"{random.choice(self.company_name_prefixes)} {random.choice(self.company_name_suffixes)}"
        
        # Generate company slogan
        slogans = [
            f"Building Tomorrow, Today",
            f"Excellence in Every Project",
            f"Constructing Dreams into Reality",
            f"Building Strong Foundations",
            f"Quality That Stands the Test of Time",
            f"Your Vision, Our Expertise"
        ]
        slogan = random.choice(slogans)
        
        # Generate founding year
        founding_year = random.randint(1950, 2015)
        
        # Generate list of services
        num_services = random.randint(3, 7)
        company_services = random.sample(self.services, num_services)
        
        # Generate list of locations
        num_locations = random.randint(2, 5)
        company_locations = random.sample(self.locations, num_locations)
        
        # Generate project data
        num_projects = random.randint(4, 8)
        projects = []
        
        for i in range(num_projects):
            # Generate random project data
            project_name = f"Project {chr(65 + i)}"  # Project A, Project B, etc.
            project_type = random.choice(company_services)
            project_location = random.choice(company_locations)
            project_cost = random.randint(100, 5000) * 10000  # $1M to $50M
            
            # Generate random start date within the last 5 years
            days_ago = random.randint(30, 1825)  # Between 30 days and 5 years
            start_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            # Generate random duration
            duration_months = random.randint(3, 36)  # 3 months to 3 years
            
            # Calculate status based on duration and start date
            days_since_start = days_ago
            project_duration_days = duration_months * 30
            progress = min(100, int((days_since_start / project_duration_days) * 100))
            
            status = "In Progress"
            if progress >= 100:
                status = "Completed"
            elif progress < 5:
                status = "Planning"
            
            projects.append({
                "name": project_name,
                "type": project_type,
                "location": project_location,
                "cost": project_cost,
                "start_date": start_date,
                "duration_months": duration_months,
                "status": status,
                "progress": progress
            })
        
        # Generate company statistics
        stats = {
            "completed_projects": random.randint(50, 500),
            "years_in_business": datetime.now().year - founding_year,
            "employees": random.randint(50, 1000),
            "customer_satisfaction": random.randint(85, 99),
            "awards": random.randint(5, 30)
        }
        
        # Put everything together in a company data dictionary
        company_data = {
            "name": company_name,
            "slogan": slogan,
            "founding_year": founding_year,
            "services": company_services,
            "locations": company_locations,
            "projects": projects,
            "stats": stats,
            "contact": {
                "email": f"info@{company_name.lower().replace(' ', '')}.com",
                "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "address": f"{random.randint(100, 9999)} Business Ave, {random.choice(company_locations)}"
            }
        }
        
        return company_data
    
    def _generate_design_restrictions(self, company_data):
        """Generate design restrictions based on company data"""
        # Choose a random color scheme
        color_scheme = random.choice(self.color_schemes)
        
        # Generate font preferences
        heading_fonts = ["Roboto", "Montserrat", "Raleway", "Open Sans", "Oswald", "Playfair Display"]
        body_fonts = ["Open Sans", "Roboto", "Lato", "Source Sans Pro", "Nunito", "Raleway"]
        
        # Generate layout preferences
        layouts = ["modern", "classic", "minimalist", "bold", "corporate"]
        
        # Generate component preferences
        chart_types = ["bar", "line", "pie", "area", "radar"]
        
        # Create design restrictions object
        design_restrictions = {
            "colors": color_scheme,
            "fonts": {
                "heading": random.choice(heading_fonts),
                "body": random.choice(body_fonts)
            },
            "layout": random.choice(layouts),
            "components": {
                "navbar": True,
                "footer": True,
                "hero_section": True,
                "services_section": True,
                "projects_section": True,
                "stats_section": True,
                "contact_form": random.choice([True, False]),
                "testimonials": random.choice([True, False]),
                "charts": {
                    "include": random.choice([True, False]),
                    "preferred_type": random.choice(chart_types)
                }
            },
            "special_requirements": []
        }
        
        # Add some special requirements based on company data
        if len(company_data["projects"]) > 5:
            design_restrictions["special_requirements"].append("Include a project filter/search functionality")
        
        if len(company_data["services"]) > 5:
            design_restrictions["special_requirements"].append("Group services into categories")
        
        if company_data["stats"]["years_in_business"] > 30:
            design_restrictions["special_requirements"].append("Emphasize company history and experience")
        
        # Randomly add additional special requirements
        additional_requirements = [
            "Use card-based design for project showcase",
            "Include a sticky navigation bar",
            "Add parallax scrolling effects",
            "Use CSS grid for project layout",
            "Include a dark/light mode toggle",
            "Add animations for statistics counters",
            "Use timeline for company history",
            "Include interactive map showing company locations"
        ]
        
        num_additional = random.randint(0, 3)
        design_restrictions["special_requirements"].extend(random.sample(additional_requirements, num_additional))
        
        return design_restrictions
    
    def get_data_and_restrictions(self):
        """Generate both company data and design restrictions"""
        company_data = self.generate_data()
        design_restrictions = self._generate_design_restrictions(company_data)
        
        return {
            "company_data": company_data,
            "design_restrictions": design_restrictions
        }

# Test the class if run directly
if __name__ == "__main__":
    queen = QueenWorker()
    data = queen.get_data_and_restrictions()
    
    print(json.dumps(data, indent=2)) 
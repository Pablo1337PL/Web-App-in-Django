import random
from django.core.management.base import BaseCommand
from core.models import Course, ProgrammingLanguage


class Command(BaseCommand):
    help = 'Create programming languages and sample courses'

    def handle(self, *args, **kwargs):
        # Create programming languages
        self.stdout.write("Creating programming languages...")
        languages_data = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#',
            'Ruby', 'Go', 'Rust', 'PHP', 'TypeScript',
            'Swift', 'Kotlin', 'R', 'SQL', 'Scala'
        ]

        languages = []
        for lang_name in languages_data:
            lang, created = ProgrammingLanguage.objects.get_or_create(name=lang_name)
            if created:
                self.stdout.write(f"  Created: {lang_name}")
            else:
                self.stdout.write(f"  Already exists: {lang_name}")
            languages.append(lang)

        # Create courses
        self.stdout.write("\nCreating courses...")

        courses_data = [
            {
                "name": "Introduction to Python Programming",
                "description": "Learn the basics of Python programming including variables, data types, loops, and functions. Perfect for beginners with no prior programming experience.",
                "level": 1,
                "languages": ['Python']
            },
            {
                "name": "Web Development with JavaScript",
                "description": "Master modern JavaScript for web development. Learn DOM manipulation, async programming, and ES6+ features.",
                "level": 2,
                "languages": ['JavaScript', 'TypeScript']
            },
            {
                "name": "Advanced Data Structures in C++",
                "description": "Deep dive into complex data structures including trees, graphs, heaps, and advanced algorithms implementation.",
                "level": 4,
                "languages": ['C++']
            },
            {
                "name": "Full Stack Development",
                "description": "Build complete web applications from front-end to back-end. Learn React, Node.js, databases, and deployment.",
                "level": 3,
                "languages": ['JavaScript', 'TypeScript', 'SQL']
            },
            {
                "name": "Machine Learning Fundamentals",
                "description": "Introduction to machine learning concepts, algorithms, and practical implementations using Python libraries.",
                "level": 3,
                "languages": ['Python', 'R']
            },
            {
                "name": "Android App Development",
                "description": "Create native Android applications using Kotlin. Learn Android SDK, UI design, and app architecture.",
                "level": 2,
                "languages": ['Kotlin', 'Java']
            },
            {
                "name": "iOS Development with Swift",
                "description": "Build beautiful iOS applications using Swift and SwiftUI. Learn iOS frameworks and design patterns.",
                "level": 3,
                "languages": ['Swift']
            },
            {
                "name": "Database Design and SQL",
                "description": "Master relational database design, SQL queries, optimization, and database administration fundamentals.",
                "level": 2,
                "languages": ['SQL']
            },
            {
                "name": "Game Development Basics",
                "description": "Learn game development fundamentals including game loops, sprites, physics, and user input handling.",
                "level": 2,
                "languages": ['C#', 'C++']
            },
            {
                "name": "Advanced Python for Data Science",
                "description": "Advanced Python techniques for data analysis, visualization, and scientific computing. Requires solid Python foundation.",
                "level": 4,
                "languages": ['Python']
            },
            {
                "name": "RESTful API Development",
                "description": "Design and build scalable RESTful APIs. Learn authentication, versioning, documentation, and best practices.",
                "level": 3,
                "languages": ['Python', 'JavaScript', 'Go', 'Java']
            },
            {
                "name": "Rust Systems Programming",
                "description": "Master systems programming with Rust. Learn memory safety, concurrency, and low-level programming concepts.",
                "level": 5,
                "languages": ['Rust']
            },
            {
                "name": "Ruby on Rails Web Development",
                "description": "Build web applications rapidly using Ruby on Rails framework. Learn MVC architecture and Rails conventions.",
                "level": 2,
                "languages": ['Ruby', 'SQL']
            },
            {
                "name": "Cloud Computing with AWS",
                "description": "Learn cloud infrastructure, deployment, and services using Amazon Web Services. No prior cloud experience needed.",
                "level": 2,
                "languages": ['Python', 'JavaScript']
            },
            {
                "name": "Computer Graphics Programming",
                "description": "Advanced graphics programming covering shaders, rendering pipelines, and 3D mathematics. Requires strong math skills.",
                "level": 5,
                "languages": ['C++', 'C#']
            },
            {
                "name": "DevOps and CI/CD",
                "description": "Learn modern DevOps practices including containerization, orchestration, and continuous integration/deployment.",
                "level": 3,
                "languages": ['Python', 'Go', 'SQL']
            },
            {
                "name": "Blockchain Development",
                "description": "Introduction to blockchain technology and smart contract development. Learn decentralized application architecture.",
                "level": 4,
                "languages": ['JavaScript', 'Rust', 'Go']
            },
            {
                "name": "Functional Programming Concepts",
                "description": "Explore functional programming paradigms including immutability, higher-order functions, and pure functions.",
                "level": 4,
                "languages": ['Scala', 'JavaScript', 'Python']
            },
            {
                "name": "Microservices Architecture",
                "description": "Design and implement microservices-based systems. Learn service communication, API gateways, and distributed systems.",
                "level": 5,
                "languages": ['Java', 'Go', 'Python']
            },
            {
                "name": "Introduction to Programming",
                "description": "First steps in programming. Learn basic concepts that apply to all programming languages. No prerequisites.",
                "level": 1,
                "languages": ['Python', 'JavaScript']
            }
        ]

        for course_data in courses_data:
            # Check if course already exists
            course, created = Course.objects.get_or_create(
                name=course_data['name'],
                defaults={
                    'description': course_data['description'],
                    'level': course_data['level']
                }
            )

            if created:
                # Add programming languages
                for lang_name in course_data['languages']:
                    try:
                        lang = ProgrammingLanguage.objects.get(name=lang_name)
                        course.programming_languages.add(lang)
                    except ProgrammingLanguage.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"  Language not found: {lang_name}"))

                self.stdout.write(self.style.SUCCESS(f"  Created: {course.name} (Level {course.level})"))
            else:
                self.stdout.write(f"  Already exists: {course.name}")

        self.stdout.write(self.style.SUCCESS(f"\nDone! Created {len(languages_data)} languages and {len(courses_data)} courses."))

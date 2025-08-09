import pandas as pd
from fixtures import FixtureGenerator, FixtureValidator, FixtureExporter
from tabulate import tabulate

def main():
    print("ABC Premier League Fixture Generator")
    print("----------------------------------\n")
    
    try:
        # Initialize components
        generator = FixtureGenerator('data/teams.csv')
        validator = FixtureValidator()
        exporter = FixtureExporter()
        
        # Generate fixtures
        print("Generating fixtures...")
        fixtures = generator.generate_fixtures()
        
        # Display fixtures
        print("\nGenerated Fixtures:")
        print(tabulate(
            pd.DataFrame(fixtures['matches']),
            headers='keys',
            tablefmt='grid',
            showindex=False
        ))
        
        # Validate
        print("\nValidating fixtures...")
        errors = validator.validate(fixtures, generator.teams)
        if errors:
            print("\nValidation Errors:")
            for error in errors:
                print(f"- {error}")
            print("\nCannot export invalid fixtures")
            return
        
        # Export
        print("\nExporting fixtures...")
        exporter.export(fixtures)
        print("Successfully exported to:")
        print("- output/fixtures.csv")
        print("- output/fixtures.json")
        print("- output/fixtures.xlsx")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
    
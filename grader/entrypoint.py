#!/usr/bin/env python3
"""
Entrypoint for the SageMath grading container.

- Assumes student notebooks are mounted at /Submissions
- Grades all notebooks automatically
- Outputs results to /Submissions/results/grades.csv
"""

import os
import subprocess
import sys
from pathlib import Path

# Hardcoded paths inside the container
SUBMISSIONS = Path("/Submissions")        # mounted submissions folder
RESULTS = Path("/Submissions/results")    # results folder inside submissions
GRADER = Path("/grader/run_nbtests.py")  # grader script inside container

def main():
    print("=" * 70)
    print("SageMath Automatic Grader")
    print("=" * 70)
    
    # Check if submissions directory exists
    if not SUBMISSIONS.exists():
        print(f"ERROR: {SUBMISSIONS} not found!")
        print("Please mount your submissions folder:")
        print("  docker run -v /path/to/submissions:/Submissions sage-grader:latest")
        sys.exit(1)
    
    # Create results directory inside submissions
    RESULTS.mkdir(parents=True, exist_ok=True)
    
    # Find all .ipynb files (skip checkpoints and results folder)
    notebooks = sorted(
        p for p in SUBMISSIONS.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in str(p) and "/results/" not in str(p)
    )

    if not notebooks:
        print(f"\nNo .ipynb files found in {SUBMISSIONS}")
        print("Please ensure your notebook files are in the mounted directory.")
        sys.exit(0)

    print(f"\nFound {len(notebooks)} notebook(s) to grade:")
    for nb in notebooks:
        print(f"  • {nb.name}")
    
    print("\n" + "=" * 70)
    print("Starting grading process...")
    print("=" * 70 + "\n")

    # Grade each notebook
    success_count = 0
    fail_count = 0
    
    for nb in notebooks:
        print(f"{'─' * 70}")
        print(f"📝 Grading: {nb.name}")
        print(f"{'─' * 70}")
        
        try:
            # Run the grader on the notebook
            cmd = [
                "sage", "-python", str(GRADER),
                "--nb", str(nb)
            ]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            
            # Print the output from the grader
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            if result.returncode == 0:
                print(f"✓ Successfully graded {nb.name}")
                success_count += 1
            else:
                print(f"✗ Failed to grade {nb.name}")
                fail_count += 1
                
        except Exception as e:
            print(f"✗ Error grading {nb.name}: {e}")
            fail_count += 1

    # Final summary
    print("\n" + "=" * 70)
    print("GRADING COMPLETE")
    print("=" * 70)
    print(f"Successfully graded: {success_count}/{len(notebooks)}")
    if fail_count > 0:
        print(f"Failed to grade: {fail_count}/{len(notebooks)}")
    
    # Display results if grades.csv exists
    grades_file = RESULTS / "grades.csv"
    if grades_file.exists():
        print(f"\n📊 Results saved to: {grades_file}")
        print("\nGrades Summary:")
        print("─" * 70)
        try:
            with open(grades_file, 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"Could not read grades file: {e}")
    else:
        print(f"\n⚠️  Warning: No grades file generated at {grades_file}")
    
    print("=" * 70)
    sys.exit(0 if fail_count == 0 else 1)

if __name__ == "__main__":
    main()
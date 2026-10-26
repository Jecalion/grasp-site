"""
Builds every generated page, in order: exercises, About, workout plans, comparisons.

    python build/pages.py

To refresh the plans themselves first (needs the app repo):
    cd C:/dev/fitbud-viral && npx vite-node C:/dev/grasp-site-pseo/build/plans/generate.ts
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for script in ('exercises.py', 'about.py', 'plans.py', 'compare.py'):
    subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, script)], check=True)

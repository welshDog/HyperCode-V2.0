import asyncio
import argparse
import glob
import os
import sys
from framework.runner import TestRunner

async def main():
    parser = argparse.ArgumentParser(description="HyperCode Multi-Agent Testing Framework")
    parser.add_argument("--scenario", type=str, help="Path to specific scenario file")
    parser.add_argument("--dir", type=str, default="tests/framework/scenarios", help="Directory containing scenario files")
    parser.add_argument("--url", type=str, default="http://localhost:8080", help="Base URL of the Orchestrator")
    
    args = parser.parse_args()
    
    runner = TestRunner(base_url=args.url)
    
    scenarios = []
    if args.scenario:
        scenarios.append(args.scenario)
    else:
        # Find all json/yaml files in the directory
        scenarios.extend(glob.glob(os.path.join(args.dir, "*.json")))
        scenarios.extend(glob.glob(os.path.join(args.dir, "*.yaml")))
        scenarios.extend(glob.glob(os.path.join(args.dir, "*.yml")))
    
    if not scenarios:
        print("No scenarios found.")
        return

    print(f"Found {len(scenarios)} scenarios to run.")
    
    total_passed = 0
    total_failed = 0
    
    for scenario_file in scenarios:
        try:
            scenario = runner.load_scenario(scenario_file)
            result = await runner.run_scenario(scenario)
            
            total_passed += result.passed_cases
            total_failed += result.failed_cases
            
            print(f"\nScenario Result: {result.overall_score:.2f}% Score")
            print("-" * 40)
            
        except Exception as e:
            print(f"Error running scenario {scenario_file}: {e}")
            
    print("\n" + "=" * 40)
    print(f"TOTAL RESULTS: Passed: {total_passed} | Failed: {total_failed}")
    print("=" * 40)
    
    if total_failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

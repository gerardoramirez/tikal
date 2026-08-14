# Speed Improvement and Benchmarking Process

START_TOKEN = 🏎️

**ALWAYS** ask the user one question at a time and wait for a response.

**ALWAYS** confirm file names and locations if unsure.

**NEVER** make changes to Test code in this process.

This process is for making speed improvements production code.

## Steps
- For each speed improvement:
  1. Ensure all tests pass before the change.
  2. Run the benchmarking script before the change and save the results.
  3. Ensure all tests pass after the change.
  4. Run the benchmarking script after the change and save the results.
  5. Compare the results from steps 2 and 4.
  4. If the benchmark indicates a speedup, commit it with the message format: "- b <refactoring>, Speedup of x% (old benchmark - new benchmark)" (quotes must include the - b).
  5. If the benchmark does not indicate a speedup, roll back the changes and move onto the next potential speedup change.
  6. Provide a status update after each change.

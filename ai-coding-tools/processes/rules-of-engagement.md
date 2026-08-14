# Rules of Engagement

## Collaborating with Me

Please begin each reply to me with START_TOKEN (default = 🦋)
If other instructions also ask you to use a START_TOKEN, please stack them. Do not replace them.

🤝 Exercise full agency to push back on mistakes. Flag issues early, ask questions if unsure of direction instead of choosing randomly
🤲 Don't flatter me. Give me honest feedback even if I don't want to hear it
🛤️ No shortcuts or direction changes without permission. Ask with❓emoji when changing course
❓ If you need to ask me a list of questions, show me the list and then start asking one question at a time
Answer questions briefly. Provide only the information I asked for; I will request more details if I need them.

## Working in the Code Base

- **Self-Explanatory Code:**
  - When naming variables, choose descriptive names over brief names.
  - Minimize cyclomatic complexity: the bodies of loops and conditions should only go one layer deep unless parsing a multidimensional or nested data structure
  - Where possible, place all the code for a new feature in its own directory
- **Code Comments:**
  - Only add code comments for lines that do a confusing or paradoxical thing. Don't explain lines in comments where the code clearly tells me what it does.
- **Automated Tests:**
  - Begin all plans and changes with:
    - End-to-end feature tests that exercise the happy path and edge cases you anticipate
    - Unit tests exercising the individual components
    - Name tests with the pattern subject_under_test__in_situation__does_thing. Examples:
      - parse_data__valid_data_file__returns_table_representation
      - parse_data__empty_file__raises_FileEmptyException (note: class references in test names should be camelcase like the class name, not snake case like a function name)
- **Error Messages:**
  - Write clear, complete error messages that explain to the caller exactly what must change about their calls.
  - Where possible, raise exceptions from the function that the caller will need to call differently.
  - Where the caller must change a call that isn't the one raising the exception, write an error message explaining exactly what must change. Example:
    - Call #1 makes a copy of a data structure. Call #2 raises an exception when called on a copy. The exception should say "this is a copy because of call #1. If you didn't mean to make a copy, instead of making call #1, do this other thing"
- **Diagrams Illustrating System Structure:**
  - When planning features that change code organization or architecture, include in the plan:
    1. An ASCII diagram of the current organization or architecture
    2. An ASCII diagram showing what that organization or architecture will change to in this plan
- **In-Repo Documentation:**
  - When planning changes:
    1. Give the plan a name relevant to the plan we are making
    2. Put that plan in a markdown file with the name you gave the plan
    3. Save that plan in @ai-coding-tools/plans
    4. Reference that version of the plan document as we update the plan together
    5. When committing work, commit the plan document along with the changed files

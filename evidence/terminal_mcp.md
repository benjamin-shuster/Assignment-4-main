> Use the a4-tools MCP server: call its run_tests tool, then its read_file tool on discounts.py, and tell me why the failing test fails. Do not change any files.

● Explored 2 files (run_tests.json, read_file.json)
● Called 2 MCP tools (a4-tools/run_tests, a4-tools/read_file) (ctrl+o to expand)

  ### Test Results                                                                                                                                                                  
  
  Running run_tests produced the following failure:
  
    FAILED: 1 of 4 tests did not pass.
    ERROR test_lowercase_code_works: ValueError: unknown code: save10
  
  ### Why the Failing Test Fails
  
  In discounts.py:6-18:
  
  • All discount codes in the CODES dictionary are stored in uppercase (e.g., "SAVE10" and "WELCOME5").
  • apply_discount checks if code not in CODES: directly on the passed code string without converting it to uppercase (e.g., using code.upper()).
  • When test_lowercase_code_works calls the function with a lowercase code like "save10", the lookup fails to match "SAVE10", causing apply_discount to raise ValueError: unknown
  code: save10.
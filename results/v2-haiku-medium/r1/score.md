| Run | Scenario | Failed | Category | Grouping | Missing | Extra | Turns | Cost |
|---|---|---|---|---|---|---|---|---|
| run-01 | year_off_by_one | 2 | 2/2 | yes | 0 | 0 | 5 | $0.00 |
| run-02 | blank_title | 1 | 1/1 | yes | 0 | 0 | 4 | $0.00 |
| run-03 | leak_books | 2 | 2/2 | yes | 0 | 0 | 5 | $0.00 |
| run-04 | slow_list | 4 | 4/4 | yes | 0 | 0 | 5 | $0.01 |
| run-05 | db_unavailable | 26 | 26/26 | yes | 0 | 0 | 4 | $0.00 |
| run-06 | wrong_expected_value | 1 | 1/1 | yes | 0 | 0 | 5 | $0.00 |
| run-07 | wrong_locator | 2 | 2/2 | yes | 0 | 0 | 3 | $0.00 |
| run-08 | next_year_as_current | 1 | 1/1 | yes | 0 | 0 | 5 | $0.00 |
| run-09 | slow_list | 4 | 4/4 | yes | 0 | 0 | 5 | $0.01 |
| run-10 | slow_list | 2 | 2/2 | yes | 0 | 0 | 5 | $0.00 |
| run-11 | year_off_by_one+leak_books | 4 | 4/4 | yes | 0 | 0 | 5 | $0.01 |
| run-12 | leak_books+wrong_locator | 4 | 4/4 | yes | 0 | 0 | 4 | $0.01 |

- Runs fully correct (every category, grouping, nothing missing or extra): **12/12**
- Category accuracy: **100%** (53/53 failed tests)
- Grouping correct: **12/12 runs**
- Missing / extra tests in reports: 0 / 0
- Total cost: $0.04 over 55 model turns

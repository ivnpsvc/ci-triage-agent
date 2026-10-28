| Pass | Runs fully correct | Category accuracy | Grouping correct | Cost |
|---|---|---|---|---|
| r1 | 10/12 | 91% | 10/12 | $0.036 |
| r2 | 12/12 | 100% | 12/12 | $0.033 |
| r3 | 12/12 | 100% | 12/12 | $0.034 |

| Run | Scenario | Passes fully correct |
|---|---|---|
| run-01 | year_off_by_one | 3/3 |
| run-02 | blank_title | 2/3 |
| run-03 | leak_books | 3/3 |
| run-04 | slow_list | 2/3 |
| run-05 | db_unavailable | 3/3 |
| run-06 | wrong_expected_value | 3/3 |
| run-07 | wrong_locator | 3/3 |
| run-08 | next_year_as_current | 3/3 |
| run-09 | slow_list | 3/3 |
| run-10 | slow_list | 3/3 |
| run-11 | year_off_by_one+leak_books | 3/3 |
| run-12 | leak_books+wrong_locator | 3/3 |

- Same category in every pass: **91%** of failed tests (49/54)
- Total cost: $0.103

| Run | Scenario | Failed | Category | Grouping | Missing | Extra | Turns | Cost |
|---|---|---|---|---|---|---|---|---|
| run-01 | year_off_by_one | 2 | 2/2 | yes | 0 | 0 | 4 | $0.00 |
| run-02 | blank_title | 1 | 0/1 | no | 1 | 0 | 4 | $0.00 |
| run-03 | leak_books | 2 | 2/2 | yes | 0 | 0 | 4 | $0.00 |
| run-04 | slow_list | 4 | 0/4 | no | 4 | 0 | 4 | $0.00 |
| run-05 | db_unavailable | 26 | 26/26 | yes | 0 | 0 | 5 | $0.00 |
| run-06 | wrong_expected_value | 1 | 1/1 | yes | 0 | 0 | 3 | $0.00 |
| run-07 | wrong_locator | 2 | 2/2 | yes | 0 | 0 | 3 | $0.00 |
| run-08 | next_year_as_current | 1 | 1/1 | yes | 0 | 0 | 4 | $0.00 |
| run-09 | slow_list | 4 | 4/4 | yes | 0 | 0 | 4 | $0.00 |
| run-10 | slow_list | 3 | 3/3 | yes | 0 | 0 | 4 | $0.00 |
| run-11 | year_off_by_one+leak_books | 4 | 4/4 | yes | 0 | 0 | 5 | $0.00 |
| run-12 | leak_books+wrong_locator | 4 | 4/4 | yes | 0 | 0 | 4 | $0.00 |

- Runs fully correct (every category, grouping, nothing missing or extra): **10/12**
- Category accuracy: **91%** (49/54 failed tests)
- Grouping correct: **10/12 runs**
- Missing / extra tests in reports: 5 / 0
- Total cost: $0.04 over 48 model turns

Wrong categories:
- run-02 `tests.api.test_books_api::test_invalid_book_is_rejected[blank-title]`: expected product_bug, got None
- run-04 `tests.ui.test_books_ui::test_deleted_book_disappears[chromium]`: expected flaky, got None
- run-04 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected flaky, got None
- run-04 `tests.ui.test_login_ui::test_log_out_ends_the_session[chromium]`: expected flaky, got None
- run-04 `tests.ui.test_login_ui::test_new_user_lands_on_empty_bookshelf[chromium]`: expected flaky, got None

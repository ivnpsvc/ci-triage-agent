| Run | Scenario | Failed | Category | Grouping | Missing | Extra | Turns | Cost |
|---|---|---|---|---|---|---|---|---|
| run-01 | year_off_by_one | 2 | 2/2 | yes | 0 | 0 | 4 | $0.00 |
| run-02 | blank_title | 1 | 0/1 | no | 1 | 1 | 5 | $0.00 |
| run-03 | leak_books | 2 | 2/2 | yes | 0 | 0 | 5 | $0.00 |
| run-04 | slow_list | 5 | 0/5 | no | 5 | 5 | 8 | $0.01 |
| run-05 | db_unavailable | 26 | 26/26 | yes | 0 | 0 | 5 | $0.00 |
| run-06 | year_off_by_one+leak_books | 4 | 4/4 | yes | 0 | 0 | 5 | $0.01 |

- Runs fully correct (every category, grouping, nothing missing or extra): **4/6**
- Category accuracy: **85%** (34/40 failed tests)
- Grouping correct: **4/6 runs**
- Missing / extra tests in reports: 6 / 6
- Total cost: $0.02 over 32 model turns

Wrong categories:
- run-02 `tests.api.test_books_api::test_invalid_book_is_rejected[blank-title]`: expected product_bug, got None
- run-04 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected flaky, got None
- run-04 `tests.ui.test_books_ui::test_deleted_book_disappears[chromium]`: expected flaky, got None
- run-04 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected flaky, got None
- run-04 `tests.ui.test_login_ui::test_existing_user_can_log_in[chromium]`: expected flaky, got None
- run-04 `tests.ui.test_login_ui::test_log_out_ends_the_session[chromium]`: expected flaky, got None

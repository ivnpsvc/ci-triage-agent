| Run | Scenario | Failed | Category | Grouping | Missing | Extra | Turns | Cost |
|---|---|---|---|---|---|---|---|---|
| run-01 | year_off_by_one | 2 | 2/2 | no | 0 | 0 | 0 | $0.00 |
| run-02 | blank_title | 1 | 1/1 | yes | 0 | 0 | 0 | $0.00 |
| run-03 | leak_books | 2 | 2/2 | no | 0 | 0 | 0 | $0.00 |
| run-04 | slow_list | 4 | 0/4 | no | 0 | 0 | 0 | $0.00 |
| run-05 | db_unavailable | 26 | 26/26 | yes | 0 | 0 | 0 | $0.00 |
| run-06 | wrong_expected_value | 1 | 0/1 | yes | 0 | 0 | 0 | $0.00 |
| run-07 | wrong_locator | 2 | 0/2 | yes | 0 | 0 | 0 | $0.00 |
| run-08 | next_year_as_current | 1 | 0/1 | yes | 0 | 0 | 0 | $0.00 |
| run-09 | slow_list | 4 | 0/4 | no | 0 | 0 | 0 | $0.00 |
| run-10 | slow_list | 2 | 0/2 | yes | 0 | 0 | 0 | $0.00 |
| run-11 | year_off_by_one+leak_books | 4 | 4/4 | no | 0 | 0 | 0 | $0.00 |
| run-12 | leak_books+wrong_locator | 4 | 2/4 | no | 0 | 0 | 0 | $0.00 |

- Runs fully correct (every category, grouping, nothing missing or extra): **2/12**
- Category accuracy: **70%** (37/53 failed tests)
- Grouping correct: **6/12 runs**
- Missing / extra tests in reports: 0 / 0
- Total cost: $0.00 over 0 model turns

Wrong categories:
- run-04 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected flaky, got product_bug
- run-04 `tests.ui.test_books_ui::test_book_created_through_api_shows_in_ui[chromium]`: expected flaky, got product_bug
- run-04 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected flaky, got product_bug
- run-04 `tests.ui.test_login_ui::test_new_user_lands_on_empty_bookshelf[chromium]`: expected flaky, got product_bug
- run-06 `tests.api.test_books_api::test_book_can_be_updated`: expected test_bug, got product_bug
- run-07 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected test_bug, got product_bug
- run-07 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected test_bug, got product_bug
- run-08 `tests.api.test_books_api::test_current_year_is_accepted`: expected test_bug, got product_bug
- run-09 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected flaky, got product_bug
- run-09 `tests.ui.test_books_ui::test_book_created_through_api_shows_in_ui[chromium]`: expected flaky, got product_bug
- run-09 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected flaky, got product_bug
- run-09 `tests.ui.test_login_ui::test_new_user_lands_on_empty_bookshelf[chromium]`: expected flaky, got product_bug
- run-10 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected flaky, got product_bug
- run-10 `tests.ui.test_login_ui::test_log_out_ends_the_session[chromium]`: expected flaky, got product_bug
- run-12 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected test_bug, got product_bug
- run-12 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected test_bug, got product_bug

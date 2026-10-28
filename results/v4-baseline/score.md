| Run | Scenario | Failed | Category | Grouping | Missing | Extra | Turns | Cost |
|---|---|---|---|---|---|---|---|---|
| run-01 | year_off_by_one | 2 | 2/2 | no | 0 | 0 | 0 | $0.00 |
| run-02 | blank_title | 1 | 1/1 | yes | 0 | 0 | 0 | $0.00 |
| run-03 | leak_books | 2 | 2/2 | no | 0 | 0 | 0 | $0.00 |
| run-04 | slow_list | 2 | 0/2 | no | 0 | 0 | 0 | $0.00 |
| run-05 | db_unavailable | 26 | 26/26 | yes | 0 | 0 | 0 | $0.00 |
| run-06 | wrong_expected_value | 1 | 0/1 | yes | 0 | 0 | 0 | $0.00 |
| run-07 | wrong_locator | 2 | 0/2 | yes | 0 | 0 | 0 | $0.00 |
| run-08 | next_year_as_current | 1 | 0/1 | yes | 0 | 0 | 0 | $0.00 |
| run-09 | renamed_year_field | 3 | 3/3 | no | 0 | 0 | 0 | $0.00 |
| run-10 | schema_typo | 26 | 0/26 | yes | 0 | 0 | 0 | $0.00 |
| run-11 | stale_list | 1 | 0/1 | yes | 0 | 0 | 0 | $0.00 |
| run-12 | swapped_login_args | 19 | 0/19 | yes | 0 | 0 | 0 | $0.00 |
| run-13 | slow_list | 3 | 0/3 | no | 0 | 0 | 0 | $0.00 |
| run-14 | slow_list | 1 | 0/1 | yes | 0 | 0 | 0 | $0.00 |
| run-15 | stale_list | 1 | 0/1 | yes | 0 | 0 | 0 | $0.00 |
| run-16 | stale_list | 1 | 0/1 | yes | 0 | 0 | 0 | $0.00 |
| run-17 | year_off_by_one+leak_books | 3 | 3/3 | no | 0 | 0 | 0 | $0.00 |
| run-18 | leak_books+wrong_locator | 4 | 2/4 | no | 0 | 0 | 0 | $0.00 |
| run-19 | renamed_year_field+next_year_as_current | 4 | 3/4 | no | 0 | 0 | 0 | $0.00 |

- Runs fully correct (every category, grouping, nothing missing or extra): **2/19**
- Category accuracy: **41%** (42/103 failed tests)
- Grouping correct: **11/19 runs**
- Missing / extra tests in reports: 0 / 0
- Total cost: $0.00 over 0 model turns

Wrong categories:
- run-04 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected flaky, got product_bug
- run-04 `tests.ui.test_login_ui::test_log_out_ends_the_session[chromium]`: expected flaky, got product_bug
- run-06 `tests.api.test_books_api::test_book_can_be_updated`: expected test_bug, got product_bug
- run-07 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected test_bug, got product_bug
- run-07 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected test_bug, got product_bug
- run-08 `tests.api.test_books_api::test_current_year_is_accepted`: expected test_bug, got product_bug
- run-10 `tests.api.test_auth_api::test_books_require_a_token`: expected product_bug, got infrastructure
- run-10 `tests.api.test_auth_api::test_duplicate_username_is_rejected`: expected product_bug, got infrastructure
- run-10 `tests.api.test_auth_api::test_invalid_registration_is_rejected[password-too-short]`: expected product_bug, got infrastructure
- run-10 `tests.api.test_auth_api::test_invalid_registration_is_rejected[username-too-long]`: expected product_bug, got infrastructure
- run-10 `tests.api.test_auth_api::test_invalid_registration_is_rejected[username-too-short]`: expected product_bug, got infrastructure
- run-10 `tests.api.test_auth_api::test_login_returns_token`: expected product_bug, got infrastructure
- run-10 `tests.api.test_auth_api::test_login_with_wrong_password_is_rejected`: expected product_bug, got infrastructure
- run-10 `tests.api.test_auth_api::test_register_returns_created_user`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_book_can_be_updated`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_created_book_can_be_fetched`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_current_year_is_accepted`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_deleted_book_is_gone`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_invalid_book_is_rejected[blank-title]`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_invalid_book_is_rejected[empty-author]`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_invalid_book_is_rejected[next-year]`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_invalid_book_is_rejected[year-zero]`: expected product_bug, got infrastructure
- run-10 `tests.api.test_books_api::test_users_cannot_see_each_others_books`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_books_ui::test_book_created_through_api_shows_in_ui[chromium]`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_books_ui::test_deleted_book_disappears[chromium]`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_login_ui::test_books_page_requires_login[chromium]`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_login_ui::test_existing_user_can_log_in[chromium]`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_login_ui::test_log_out_ends_the_session[chromium]`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_login_ui::test_new_user_lands_on_empty_bookshelf[chromium]`: expected product_bug, got infrastructure
- run-10 `tests.ui.test_login_ui::test_wrong_password_shows_error[chromium]`: expected product_bug, got infrastructure
- run-11 `tests.ui.test_books_ui::test_deleted_book_disappears[chromium]`: expected flaky, got product_bug
- run-12 `tests.api.test_auth_api::test_duplicate_username_is_rejected`: expected test_bug, got infrastructure
- run-12 `tests.api.test_auth_api::test_login_returns_token`: expected test_bug, got infrastructure
- run-12 `tests.api.test_auth_api::test_login_with_wrong_password_is_rejected`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_book_can_be_updated`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_created_book_can_be_fetched`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_current_year_is_accepted`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_deleted_book_is_gone`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_invalid_book_is_rejected[blank-title]`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_invalid_book_is_rejected[empty-author]`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_invalid_book_is_rejected[next-year]`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_invalid_book_is_rejected[year-zero]`: expected test_bug, got infrastructure
- run-12 `tests.api.test_books_api::test_users_cannot_see_each_others_books`: expected test_bug, got infrastructure
- run-12 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected test_bug, got infrastructure
- run-12 `tests.ui.test_books_ui::test_book_created_through_api_shows_in_ui[chromium]`: expected test_bug, got infrastructure
- run-12 `tests.ui.test_books_ui::test_deleted_book_disappears[chromium]`: expected test_bug, got infrastructure
- run-12 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected test_bug, got infrastructure
- run-12 `tests.ui.test_login_ui::test_existing_user_can_log_in[chromium]`: expected test_bug, got infrastructure
- run-12 `tests.ui.test_login_ui::test_log_out_ends_the_session[chromium]`: expected test_bug, got infrastructure
- run-12 `tests.ui.test_login_ui::test_wrong_password_shows_error[chromium]`: expected test_bug, got infrastructure
- run-13 `tests.ui.test_books_ui::test_book_created_through_api_shows_in_ui[chromium]`: expected flaky, got product_bug
- run-13 `tests.ui.test_books_ui::test_deleted_book_disappears[chromium]`: expected flaky, got product_bug
- run-13 `tests.ui.test_login_ui::test_new_user_lands_on_empty_bookshelf[chromium]`: expected flaky, got product_bug
- run-14 `tests.ui.test_books_ui::test_book_created_through_api_shows_in_ui[chromium]`: expected flaky, got product_bug
- run-15 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected flaky, got product_bug
- run-16 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected flaky, got product_bug
- run-18 `tests.ui.test_books_ui::test_added_book_is_listed[chromium]`: expected test_bug, got product_bug
- run-18 `tests.ui.test_books_ui::test_future_year_shows_error_and_keeps_input[chromium]`: expected test_bug, got product_bug
- run-19 `tests.api.test_books_api::test_current_year_is_accepted`: expected test_bug, got product_bug

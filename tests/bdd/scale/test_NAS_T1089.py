# coding=utf-8
"""SCALE UI feature tests."""

import time
from function import(
    wait_on_element,
    is_element_present,
    wait_for_attribute_value,
    wait_on_element_disappear,
)
from selenium.webdriver.common.keys import (Keys)
from pytest_bdd import (
    given,
    scenario,
    then,
    when,
    parsers,
)


@scenario('features/NAS-T1089.feature', 'Add root to auxiliary group of a user')
def test_add_root_to_auxiliary_group_of_a_user():
    """Add root to auxiliary group of a user."""


@given('the browser is open, the FreeNAS URL and logged in')
def the_browser_is_open_the_freenas_url_and_logged_in(driver, nas_ip, root_password):
    """the browser is open, the FreeNAS URL and logged in."""
    if nas_ip not in driver.current_url:
        driver.get(f"http://{nas_ip}")
        assert wait_on_element(driver, 10, '//input[@data-placeholder="Username"]')
    if not is_element_present(driver, '//mat-list-item[@ix-auto="option__Dashboard"]'):
        assert wait_on_element(driver, 10, '//input[@data-placeholder="Username"]')
        driver.find_element_by_xpath('//input[@data-placeholder="Username"]').clear()
        driver.find_element_by_xpath('//input[@data-placeholder="Username"]').send_keys('root')
        driver.find_element_by_xpath('//input[@data-placeholder="Password"]').clear()
        driver.find_element_by_xpath('//input[@data-placeholder="Password"]').send_keys(root_password)
        assert wait_on_element(driver, 5, '//button[@name="signin_button"]')
        driver.find_element_by_xpath('//button[@name="signin_button"]').click()
    else:
        driver.find_element_by_xpath('//mat-list-item[@ix-auto="option__Dashboard"]').click()


@when('on the dashboard, click on the Accounts on the side menu, click on Users')
def on_the_dashboard_click_on_the_accounts_on_the_side_menu_click_on_users(driver):
    """on the dashboard, click on the Accounts on the side menu, click on Users."""
    assert wait_on_element(driver, 10, '//span[contains(.,"Dashboard")]')
    assert wait_on_element(driver, 10, '//mat-list-item[@ix-auto="option__Dashboard"]', 'clickable')
    driver.find_element_by_xpath('//mat-list-item[@ix-auto="option__Dashboard"]').click()
    time.sleep(2)
    """click on the Credentials on the side menu, click on Local Users."""
    assert wait_on_element(driver, 10, '//mat-list-item[@ix-auto="option__Credentials"]', 'clickable')
    driver.find_element_by_xpath('//mat-list-item[@ix-auto="option__Credentials"]').click()
    time.sleep(2)
    assert wait_on_element(driver, 10, '//mat-list-item[@ix-auto="option__Local Users"]', 'clickable')
    driver.find_element_by_xpath('//mat-list-item[@ix-auto="option__Local Users"]').click()


@when('the Users page should open, click the Greater-Than-Sign right of the users')
def the_users_page_should_open_click_the_greaterthansign_right_of_the_users(driver):
    """the Users page should open, click the Greater-Than-Sign right of the users."""
    assert wait_on_element(driver, 7, '//div[contains(.,"Users")]')
    assert wait_on_element(driver, 10, '//tr[@ix-auto="expander__ericbsd"]/td', 'clickable')
    driver.find_element_by_xpath('//tr[@ix-auto="expander__ericbsd"]/td').click()


@then('the User Field should expand down, click the Edit button')
def the_user_field_should_expand_down_click_the_edit_button(driver):
    """the User Field should expand down, click the Edit button."""
    time.sleep(1)
    assert wait_on_element(driver, 10, '//button[@ix-auto="button__EDIT_ericbsd"]', 'clickable')
    driver.find_element_by_xpath('//button[@ix-auto="button__EDIT_ericbsd"]').click()


@then('the User Edit Page should open, add the root group and click save')
def the_user_edit_page_should_open_add_the_root_group_and_click_save(driver):
    """the User Edit Page should open, add the root group and click save."""
    assert wait_on_element(driver, 10, '//h3[contains(.,"Edit User")]')
    time.sleep(2)
    assert wait_on_element(driver, 7, '//mat-select[@ix-auto="select__Auxiliary Groups"]', 'clickable')
    driver.find_element_by_xpath('//mat-select[@ix-auto="select__Auxiliary Groups"]').click()
    assert wait_on_element(driver, 10, '//span[contains(.,"root")]')
    driver.find_element_by_xpath('//mat-option[@ix-auto="option__Auxiliary Groups_root"]').click()
    driver.find_element_by_xpath('//mat-option[@ix-auto="option__Auxiliary Groups_root"]').send_keys(Keys.TAB)
    time.sleep(2)
    element = driver.find_element_by_xpath('//button[@ix-auto="button__SAVE"]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    wait_on_element(driver, 10, '//button[@ix-auto="button__SAVE"]', 'clickable')
    driver.find_element_by_xpath('//button[@ix-auto="button__SAVE"]').click()


@then('change should be saved, reopen the edit page, root group value should be visible')
def change_should_be_saved_reopen_the_edit_page_root_group_value_should_be_visible(driver):
    """change should be saved, reopen the edit page, root group value should be visible."""
    wait_on_element_disappear(driver, 1, '//h6[contains(.,"Please wait")]')
    time.sleep(3)
    assert wait_on_element(driver, 7, '//div[contains(.,"Users")]')
    assert wait_on_element(driver, 10, '//tr[@ix-auto="expander__ericbsd"]/td', 'clickable')
    driver.find_element_by_xpath('//tr[@ix-auto="expander__ericbsd"]/td').click()
    time.sleep(1)
    assert wait_on_element(driver, 10, '//button[@ix-auto="button__EDIT_ericbsd"]', 'clickable')
    driver.find_element_by_xpath('//button[@ix-auto="button__EDIT_ericbsd"]').click()
    assert wait_on_element(driver, 10, '//h3[contains(.,"Edit User")]')
    time.sleep(2)
    assert wait_on_element(driver, 7, '//mat-select[@ix-auto="select__Auxiliary Groups"]', 'clickable')
    driver.find_element_by_xpath('//mat-select[@ix-auto="select__Auxiliary Groups"]').click()
    assert wait_on_element(driver, 10, '//span[contains(.,"root")]')
    assert wait_on_element(driver, 10, '//mat-selected[@ix-auto="option__Auxiliary Groups_root"]')
    ## return to dashboard
    assert wait_on_element(driver, 10, '//mat-list-item[@ix-auto="option__Dashboard"]', 'clickable')
    driver.find_element_by_xpath('//mat-list-item[@ix-auto="option__Dashboard"]').click()
    time.sleep(1)

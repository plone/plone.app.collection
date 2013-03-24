*** Settings ***

Library  Selenium2Library  timeout=2  implicit_wait=0
Library  plone.app.collection.testing_keywords.Keywords

Variables  plone/app/testing/interfaces.py

Resource  collection_keywords.txt

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown

*** Variables ***

${front-page}  http://localhost:55001/plone/
${test-folder}  http://localhost:55001/plone/acceptance-test-folder

${PORT} =  55001
${ZOPE_URL} =  http://localhost:${PORT}
${PLONE_URL} =  ${ZOPE_URL}/plone
${BROWSER} =  Firefox


*** Test Cases ***

Test Type Criterion
    Log in as site owner
    Go to  ${test-folder}
    Add Page  My Document
    Go to  ${test-folder}/createObject?type_name=News+Item
    Wait Until Page Contains Element  title
    Input text  title  My News Item
    Click Button  Save
    Create Collection  My Collection

    Click Edit In Edit Bar
    Set Type Criterion

    Page should contain  My Document
    Page should not contain  My News Item
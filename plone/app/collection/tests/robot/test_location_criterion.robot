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

Test Relative Location Criterion
    Log in as site owner
    Go to  ${test-folder}
    Add Page  Document outside My Folder
    Go to  ${test-folder}
    Add folder  My Folder
    Add Page  Document inside My Folder
    Create Collection  Location Criteria Collection

    Click Edit In Edit Bar
    Set Relative Location Criterion To  ../my-folder/

    Page should contain  Document inside My Folder
    Page should not contain  Document outside My Folder

Test Absolute Location Criterion
    #
    # this currently successfully tests the absolute location criterion as it is,
    # meaning inserting the path into an input field;
    # we want to have a 'path picker' which let's us navigate to the desired
    # object and select it
    #
    Log in as site owner
    Go to  ${test-folder}
    Add folder  My Folder
    Add Page  Document inside My Folder

    Go to  ${test-folder}
    Create Collection  Location Criteria Collection

    Click Edit In Edit Bar
    Set Absolute Location Criterion To  /acceptance-test-folder/my-folder/

    Page should contain  Document inside My Folder

Test Multiple Relative Location Criterion
    #
    # test if contents of all locations that are added as criterion are shown;
    #
    Log in as site owner
    Go to  ${test-folder}
    Add Page  Document outside My Folders
    Go to  ${test-folder}
    Add folder  My Folder 1
    Add Page  Document inside My Folder 1
    Go to  ${test-folder}
    Add folder  My Folder 2
    Add Page  Document inside My Folder 2
    Go to  ${test-folder}
    Add folder  My Folder 3
    Add Page  Document inside My Folder 3

    Go to  ${test-folder}
    Create Collection  Location Criteria Collection

    Click Edit In Edit Bar
    Set Relative Location Criterion To  ../my-folder-1/
    Click Edit In Edit Bar
    Set Relative Location Criterion To  ../my-folder-2/
    Click Edit In Edit Bar
    Set Relative Location Criterion To  ../my-folder-3/

    Page should contain  Document inside My Folder 1
    Page should contain  Document inside My Folder 2
    Page should contain  Document inside My Folder 3
    Page should not contain  Document outside My Folders

Test Relative Location Without Subfolders
    Log in as site owner
    Go to  ${test-folder}
    Add folder  My Folder
    Add Page  Document inside My Folder
    Go to  ${test-folder}/my-folder
    Add folder  My SubFolder
    Add Page  Document inside My SubFolder

    Go to  ${test-folder}
    Create Collection  Location Criteria Collection

    Click Edit In Edit Bar
    Set Relative Location Without Subfolders Criterion To  ../my-folder/

    Page should contain  Document inside My Folder
    Page should not contain  Document inside My SubFolder

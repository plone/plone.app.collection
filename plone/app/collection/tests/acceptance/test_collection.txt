*** Settings ***

Library  Selenium2Library  timeout=10  implicit_wait=0.5
Library  plone.app.collection.testing_keywords.Keywords

Resource  plone/act/keywords.txt
Resource  collection_keywords.txt

Variables  plone/app/testing/interfaces.py

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

#Test Description Criterion
#    Log in as site owner
#    A document Apples with description Apples are green.
#    A document Oranges with description Oranges are orange.
#    Create Collection  Description Criterion Collection
#    Click Edit In Edit Bar
#    Set Description Criterion To  Apples are green.
#
#    Live Preview number of results should be  1
#    Live Preview should contain  Apples
#
#    Page should contain  Apples
#    Page should not contain  Oranges

#Test Searchable text Criterion
#Test Tag Criterion
#Test Title Criterion

#Test Creation date Criterion
#Test Effective date Criterion
#Test Event end date Criterion
#Test Event start date Criterion
#Test Expiration date Criterion
#Test Modification date Criterion

Test Creator Criterion
    Log in as site owner
    Go to  ${test-folder}
    Add Page  Site owner document
    Logout
    Log in as test user
    Go to  ${test-folder}
    Add Page  Test user document
    Create Collection  Creator Criterion Collection

    Click Edit In Edit Bar
    Set Creator Criterion To  ${TEST_USER_ID}

    Page should not contain  Site owner document
    Page should contain  Test user document


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

Test Review state Criterion
    Log in as site owner
    Go to  ${test-folder}
    Add Page  Published Document
    Publish Object
    Go to  ${test-folder}
    Add Page  Private Document
    Create Collection  My Collection

    Click Edit In Edit Bar
    Set Review state Criterion

    Page should contain  Published Document
    Page should not contain  Private Document

Test Short name (id) Criterion
    Log in as site owner
    Go to  ${test-folder}
    Add Page  First Document
    Go to  ${test-folder}
    Add Page  Second Document
    Create Collection  My Collection

    Click Edit In Edit Bar
    Set Short name (id) Criterion

    Page should contain  First Document
    Page should not contain  Second Document

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
    # right now only the last location is shown
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


#Test Type Criterion
#    Given a logged in user
#        And a document  My Document
#        And a news item  My News Item
#        And a collection  My Collection
#    When
#        I go to ${test-folder}/my-collection/edit
#        And set the type criterion to  Document
#    Then
#        The page should contain  My Document

# Test Sort On Sortable Title
# Test Sort On Event end date
# Test Sort On Effective date
# Test Sort On Creation date
# Test Sort On Expiration date
# Test Sort On Modification date
# Test Sort On Short name (id)
# Test Sort On Event start date
# Test Sort On Creator
# Test Sort On Review state
# Test Sort On Tag




#Scenario: Title Criterion
#    Given a logged-in administrator
#     And a collection  My Collection
#     And a document  My document
#
#    When I set the collection title criterion to  My document
#
#    Then the collection should show one result
#     And the collection should contain  My document


*** Keywords ***

Suite Setup
    Open browser  ${front-page}

Suite Teardown
    Close All Browsers

a logged-in administrator
    Log in as site owner

a document
    [Arguments]  ${title}
    Go to  ${test-folder}/createObject?type_name=Document
    Input text  name=title  ${title}
    Click Button  Save

a collection
    [Arguments]  ${title}
    Go to  ${test-folder}/createObject?type_name=Collection
    Input text  name=title  ${title}
    Click Button  Save

I set the collection title criterion to
    [Arguments]  ${title_criterion}
    Go to  ${front-page}/my-collection/edit
    Wait Until Page Contains Element  xpath=//select[@name="addindex"]
    Select From List  xpath=//select[@name="addindex"]  Title
    Wait Until Page Contains Element  xpath=//select[@class='queryoperator']
    Input Text  name=query.v:records  ${title_criterion}
    Wait Until Page Contains  1 items matching your search terms.
    Page should contain  ${title_criterion}
    Click Button  Save

the collection should show one result
    Go to  ${front-page}/my-collection
    # XXX: needs to be fixed.
    #Page should contain element  xpath=count(//span[@class="summary"])==1

the collection should contain
    [Arguments]  ${title}
    Go to  ${front-page}/my-collection
    Page should contain  ${title}

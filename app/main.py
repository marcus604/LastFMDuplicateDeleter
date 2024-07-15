# Base
import sys
import time
import os
from log import logging

from getpass import getpass

# Libraries
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
)

# App
from Classes import Scrobble, Config_Exception
from log import getLogger


PROGRAM_NAME = "LastFM Duplicate Deleter"

logger = getLogger(__name__, "logs/{}.log".format(PROGRAM_NAME))

URL_BASE = "https://last.fm/user/"
URL_PAGE = "/library?page="
URL_LOGIN = "https://www.last.fm/login"

USERNAME = os.environ.get("LASTFM_USERNAME")
PASSWORD = os.environ.get("LASTFM_PASSWORD")
TIME_THRESHOLD = os.environ.get("TIME_THRESHOLD")
DELETE_MODE = os.environ.get("DELETE_MODE")
SCAN_FROM_PAGE = os.environ.get("SCAN_FROM_PAGE")
DEBUG = os.environ.get("DEBUG")


# Log the launch of the app
def logLaunch():
    logger.info("Starting {}".center(40, "=").format(PROGRAM_NAME))


# Get selenium browser object
def getBrowser():
    opts = Options()
    if os.environ.get("SHOW_BROWSER") is None:
        opts.add_argument("--headless")
    opts.add_argument(
        "--window-size=1920,8600"
    )  # Combined with headless, sets resolution to be as tall as the whole page so all elements are viewable and interactable
    opts.add_argument("--log-level=3")  # Prevents unwanted noise in terminal
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    browser = Chrome(options=opts)
    browser.delete_all_cookies()
    return browser


# Check if scrobbles are considered duplicate based on artist, title and time difference between them
def isDuplicate(first, second, timeThreshold):
    if (second.timestamp - first.timestamp) <= timeThreshold:
        if first.title == second.title:
            if first.artist == second.artist:
                return True
    return False


# Delete scrobble
# Open more menu and click on delete button
def deleteScrobble(browser, scrobbleRow):
    parentRow = scrobbleRow.find_element("xpath", "./..")
    hover = ActionChains(browser).move_to_element(parentRow)
    browser.implicitly_wait(10)
    hover.perform()
    scrobbleRow.click()
    deleteButton = scrobbleRow.find_element("class name", "more-item--delete")
    deleteButton.click()


# Sign into last.fm with given username and USER_NAME
def signIn(browser):
    browser.get(URL_LOGIN)

    try:
        cookiePopup = browser.find_element("id", "onetrust-accept-btn-handler")
        cookiePopup.click()
    except (NoSuchElementException, ElementNotInteractableException):
        logger.debug("No cookie popup")

    userField = browser.find_element("id", "id_username_or_email")
    userField.send_keys(USERNAME)

    passwordField = browser.find_element("id", "id_password")
    passwordField.send_keys(PASSWORD)

    browser.find_element(
        "xpath", "//div[@class='form-submit']/button[@class='btn-primary']"
    ).click()


# Create scrobble object from elements on page
def generateScrobble(row):
    for i in range(0, 5):
        while True:
            try:
                artist = row.find_element(
                    "xpath", ".//form/input[@name='artist_name']"
                ).get_attribute("value")
                trackTitle = row.find_element(
                    "xpath", ".//form/input[@name='track_name']"
                ).get_attribute("value")
                timestamp = int(
                    row.find_element(
                        "xpath", ".//form/input[@name='timestamp']"
                    ).get_attribute("value")
                )
                return Scrobble(artist, trackTitle, timestamp)

            except selenium.common.exceptions.NoSuchElementException as e:
                logger.info("Failed to find element, trying again")


def dumpConfig():
    logger.debug("USERNAME: {} - Type: {}".format(USERNAME, type(USERNAME)))
    logger.debug(
        "TIME_THRESHOLD: {} - Type: {}".format(TIME_THRESHOLD, type(TIME_THRESHOLD))
    )
    logger.debug("DELETE_MODE: {} - Type: {}".format(DELETE_MODE, type(DELETE_MODE)))
    logger.debug(
        "SCAN_FROM_PAGE: {} - Type: {}".format(SCAN_FROM_PAGE, type(SCAN_FROM_PAGE))
    )
    logger.debug("DEBUG: {} - Type: {}".format(DEBUG, type(DEBUG)))


def validateConfig():
    try:
        if not USERNAME:
            raise Config_Exception("Username can't be blank")

        if not PASSWORD:
            raise Config_Exception("Password can't be blank")

        global DELETE_MODE
        if DELETE_MODE == "true":
            DELETE_MODE = True
        elif DELETE_MODE == "false":
            DELETE_MODE = False
        else:
            raise Config_Exception("Delete mode must be one of [true/false]")

        global DEBUG
        if DEBUG == "true":
            DEBUG = True
        elif DEBUG == "false":
            DEBUG = False
        else:
            raise Config_Exception("Debug must be one of [true/false]")

        try:
            global TIME_THRESHOLD
            TIME_THRESHOLD = int(TIME_THRESHOLD)  # Check its a number
        except ValueError:
            raise Config_Exception("Time threshold must be a number")

        try:
            global SCAN_FROM_PAGE
            SCAN_FROM_PAGE = int(SCAN_FROM_PAGE)  # Check its a number
        except ValueError:
            raise Config_Exception("Page to scan from must be a number")
        return True
    except Config_Exception as e:
        logger.error("Configuration Error: {}".format(e))
        return False


##################################################
#################Main Application#################
##################################################
def main():
    # Log startup
    logLaunch()

    dumpConfig()

    if DELETE_MODE:
        isDryRun = False
        logger.info("Running in delete mode; will delete duplicates")
    else:
        isDryRun = True
        logger.info("Running in read only mode; will not delete any scrobbles")

    browser = getBrowser()
    logger.debug("Created browser object")

    # Sign into users last.fm account
    signIn(browser)
    if browser.current_url == URL_LOGIN:
        raise Config_Exception("Credentials invalid")
    logger.debug("Signed in")

    # Browse to users library
    URL_USER = "{0}{1}".format(URL_BASE, USERNAME)
    browser.get("{0}{1}1".format(URL_USER, URL_PAGE))

    # Get total number of pages for user
    totalPages = int(browser.find_elements("class name", "pagination-page")[-1].text)

    # If specified page to start is given check that it is valid
    if SCAN_FROM_PAGE != 0:
        if SCAN_FROM_PAGE > totalPages or SCAN_FROM_PAGE < 0:
            raise Config_Exception(
                "Page number must be greater than 0 and less than the total number of pages"
            )
        else:
            currentPage = SCAN_FROM_PAGE
            totalPages = currentPage
    else:
        currentPage = totalPages

    browser.get("{0}{1}{2}".format(URL_USER, URL_PAGE, currentPage))
    logger.info("Starting on page: {}".format(currentPage))

    previousScrobble = ""
    elapsedTime = 0

    numToDelete = 0

    try:

        # Create .csv
        if isDryRun:
            CSV_PATH = os.path.join(os.getcwd(), "csv")
            localTime = time.localtime()
            scrobblesToDeleteFileName = "{} - ScrobblesToDelete.csv".format(
                time.strftime("%Y-%m-%d %H%M%S", localTime)
            )
            scrobblesToDeleteFullPath = os.path.join(
                CSV_PATH, scrobblesToDeleteFileName
            )
            scrobblesToDeleteFile = open(
                scrobblesToDeleteFullPath, "w", encoding="utf-8"
            )
            scrobblesToDeleteFile.write("Page,Time,Artist,Title\n")

        while currentPage > 0:
            startTime = time.time()

            percentDone = (totalPages - currentPage) / totalPages
            minutesETA = (elapsedTime * currentPage) / 60
            logger.info(
                "Checking page {} - {:.2%} - ETA {:.2f} minutes".format(
                    currentPage, percentDone, minutesETA
                )
            )
            # Grab all tracks on page

            # Grabs all scrobbles on page
            scrobbleRows = browser.find_elements(
                "xpath", "//td[@class='chartlist-more focus-control']"
            )

            scrobbles = []
            scrobbleNumber = 0

            # If no previous scrobble found than grab and consume the first one
            if previousScrobble == "":
                previousScrobble = generateScrobble(scrobbleRows[-1])
                del scrobbleRows[-1]

            # Iterate through all rows, generate scrobbles and compare to previous
            for scrobbleRow in reversed(scrobbleRows):

                scrobble = generateScrobble(scrobbleRow)

                logger.debug("Comparing {} : {}".format(previousScrobble, scrobble))
                if isDuplicate(previousScrobble, scrobble, TIME_THRESHOLD):

                    numToDelete += 1
                    logger.info(
                        "Found duplicate on page {} - {}".format(currentPage, scrobble)
                    )
                    if isDryRun:
                        scrobblesToDeleteFile.write(
                            "{},{},{},{}\n".format(
                                currentPage,
                                scrobble.timestamp,
                                scrobble.artist,
                                scrobble.title,
                            )
                        )
                    else:
                        try:
                            deleteScrobble(browser, scrobbleRow)
                            logger.info("Deleted: {}".format(scrobble))
                        except (
                            ElementNotInteractableException
                        ):  # If website is slow and element is not yet loaded this retries
                            deleteScrobble(browser, scrobbleRow)
                            logger.info("Deleted: {}".format(scrobble))

                previousScrobble = scrobble

            # Move to the next page
            currentPage -= 1
            browser.get("{0}{1}{2}".format(URL_USER, URL_PAGE, currentPage))

            elapsedTime = time.time() - startTime

        if isDryRun:
            scrobblesToDeleteFile.close()

    # Catch all in case of unexpected error to close out log file
    except Exception as e:
        logger.error("Generic Error: {}".format(e))
        if isDryRun:
            scrobblesToDeleteFile.close()

    logger.info("Found {} duplicate scrobbles".format(numToDelete))
    logger.info("Finished {}".center(40, "=").format(PROGRAM_NAME))


##################################################
#####################Launcher#####################
##################################################
if __name__ == "__main__":

    if not validateConfig():
        exit(1)

    if DEBUG:
        logLevel = logging.DEBUG
    else:
        logLevel = logging.INFO

    logger.setLevel(logLevel)
    main()

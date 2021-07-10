#Base
import sys
import time
from log import logging
from configparser import ConfigParser

#Libraries
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException

#App
from Classes import Scrobble, Config_Exception
from log import getLogger


PROGRAM_NAME = "LastFM Duplicate Deleter"

logger = getLogger(__name__, "logs/{}.log".format(PROGRAM_NAME))

MODE_VERBOSE = False

URL_BASE = "https://last.fm/user/"
URL_PAGE = "/library?page="
URL_LOGIN = "https://secure.last.fm/login"


#Log the launch of the app
def logLaunch():
    logger.info("Starting {}".center(40, "=").format(PROGRAM_NAME))
    if MODE_VERBOSE:
        logger.info("Verbose Logging".center(40, "="))

#Get selenium browser object
def getBrowser():
    opts = Options()
    #opts.add_argument("--headless")
    #opts.add_argument("--window-size=1920,8600") #Combined with headless, sets resolution to be as tall as the whole page so all elements are viewable and interactable
    opts.add_argument("--log-level=3") #Prevents unwanted noise in terminal
    browser = Chrome(options=opts)
    browser.delete_all_cookies()
    return browser

#Check if scrobbles are considered duplicate based on artist, title and time difference between them
def isDuplicate(first, second, timeThreshold):
    if (second.timestamp - first.timestamp) <= timeThreshold:
        if first.title == second.title:
            if first.artist == second.artist:
                return True
    return False

#Delete scrobble
#Open more menu and click on delete button
def deleteScrobble(browser, scrobbleRow):
    parentRow = scrobbleRow.find_element_by_xpath("./..")
    hover = ActionChains(browser).move_to_element(parentRow)
    browser.implicitly_wait(10)
    hover.perform()
    scrobbleRow.click()
    deleteButton = scrobbleRow.find_element_by_class_name("more-item--delete")
    deleteButton.click()

#Sign into last.fm with given username and password
def signIn(browser, username, password):
    browser.get(URL_LOGIN)
    
    try:
        cookiePopup = browser.find_element_by_id("onetrust-accept-btn-handler")
        cookiePopup.click()
    except (NoSuchElementException, ElementNotInteractableException):
        logger.debug("No cookie popup")

    
    userField = browser.find_element_by_id("id_username_or_email")
    userField.send_keys(username)

    passwordField = browser.find_element_by_id("id_password")
    passwordField.send_keys(password)

    browser.find_element_by_xpath("//div[@class='form-submit']/button[@class='btn-primary']").click()

#Create scrobble object from elements on page
def generateScrobble(row):
    for i in range(0,5):
        while True:
            try:
                artist = row.find_element_by_xpath(".//form/input[@name='artist_name']").get_attribute("value")
                trackTitle = row.find_element_by_xpath(".//form/input[@name='track_name']").get_attribute("value")
                timestamp = int(row.find_element_by_xpath(".//form/input[@name='timestamp']").get_attribute("value"))
                return Scrobble(artist, trackTitle, timestamp)

            except selenium.common.exceptions.NoSuchElementException as e:
                logger.info("Failed to find element, trying again")

    
##################################################
#################Main Application#################
##################################################
def main():
    #Log startup
    logLaunch()
    
    print("DISCLAIMER: This script is not guaranteed and if out of date may delete incorrect scrobbles, recommended to backup scrobbles before continuing")
    print("HIGHLY RECOMMENDED to do a dry run first to log all scrobbles to be deleted but not actually delete")
    
    #Get config file
    config = ConfigParser()

    config.read("config.ini")
    userConfig = config["USER_PREFERENCES"]

    configValid = False

    #Ask for config settings until they are valid
    while not configValid:

    
        try:
            if userConfig["username"] == "":
                userConfig["username"] = input("Enter your last.fm username: ")
            else:
                userConfig["username"] = input("Enter your last.fm username ({}): ".format(userConfig["username"])) or userConfig["username"]

            if userConfig["username"] == "":
                raise Config_Exception("Username can't be blank")
            

            password = input("Enter your last.fm password: ")
            if password == "":
                raise Config_Exception("Password can't be blank")

            dryRunPrompt = input("Dry Run {y/n} (y): ") or "y"
            if dryRunPrompt == "n" or dryRunPrompt == "N":
                isDryRun = False   
            elif dryRunPrompt == "y" or dryRunPrompt == "Y":
                isDryRun = True
            else:
                raise Config_Exception("Dry run selection must be \"y\" or \"n\"")

            #Check that input is a number
            try:
                if userConfig["time_threshold"] == "":
                    userConfig["time_threshold"] = input("Enter time threshold in seconds between scrobbles to be considered a duplicate (60): ") or "60"
                else:
                    userConfig["time_threshold"] = input("Enter time in seconds between scrobbles to be considered a duplicate ({}): ".format(userConfig["time_threshold"])) or userConfig["time_threshold"]

                timeThreshold = int(userConfig["time_threshold"])

                #Ask to start on a page number for doing batches
                scanAllScrobbles = input("Scan all scrobbles? {y/n} (y): ") or "y"
                if scanAllScrobbles == "n":
                    startOnPage = int(input("Enter page number to start scanning from : "))
                    if startOnPage <= 0:
                        raise Config_Exception("Page number must be greater than 0 and less than the total number of pages")
                elif scanAllScrobbles != "y" and scanAllScrobbles != "Y":
                    raise Config_Exception("Scan all scrobbles selection must be \"y\" or \"n\"")
                
            except ValueError: #Input was not a number for time threshold or page number 
                raise Config_Exception("Input requires a number")


            browser = getBrowser()
            logger.debug("Created browser object")

            #Sign into users last.fm account
            signIn(browser, userConfig["username"], password)
            if browser.current_url == URL_LOGIN:
                raise Config_Exception("Credentials invalid")
            logger.debug("Signed in")

            #Browse to users library
            URL_USER = "{0}{1}".format(URL_BASE, userConfig["username"])
            browser.get("{0}{1}1".format(URL_USER, URL_PAGE))

            #Get total number of pages for user
            totalPages = int(browser.find_elements_by_class_name("pagination-page")[-1].text)

            #If specified page to start is given check that it is valid
            if scanAllScrobbles == "n":
                if startOnPage > totalPages or startOnPage <= 0:
                    raise Config_Exception("Page number must be greater than 0 and less than the total number of pages")
                else:
                    currentPage = startOnPage
                    totalPages = currentPage
            else:
                currentPage = totalPages
            
            browser.get("{0}{1}{2}".format(URL_USER, URL_PAGE, currentPage))
            logger.info("Starting on page: {}".format(currentPage))

            #Config is valid so can be saved now
            configFile = open("config.ini", "w")
            config.write(configFile)
            configFile.close()

            configValid = True
        
        except Config_Exception as e:
            logger.error("Configuration Error: {}".format(e))
            continue

    

    previousScrobble = ""
    elapsedTime = 0

    numToDelete = 0

    try:

        #Create .csv 
        if isDryRun:
            localTime = time.localtime()
            scrobbleToDeleteFileName = "{} - ScrobblesToDelete.csv".format(time.strftime("%Y-%m-%d %H%M%S", localTime))
            scrobblesToDeleteFile = open(scrobbleToDeleteFileName, "w", encoding="utf-8")
            scrobblesToDeleteFile.write("Page,Time,Artist,Title\n")

        while currentPage > 0:
            startTime = time.time()
            
            percentDone = (totalPages - currentPage) / totalPages
            minutesETA = (elapsedTime * currentPage)/60
            logger.info("Checking page {} - {:.2%} - ETA {:.2f} minutes".format(currentPage, percentDone, minutesETA))
            #Grab all tracks on page
            
            #Grabs all scrobbles on page
            scrobbleRows = browser.find_elements_by_xpath("//td[@class='chartlist-more focus-control']")

            scrobbles = []
            scrobbleNumber = 0

            #If no previous scrobble found than grab and consume the first one
            if previousScrobble == "":
                previousScrobble = generateScrobble(scrobbleRows[-1])
                del scrobbleRows[-1]

            #Iterate through all rows, generate scrobbles and compare to previous
            for scrobbleRow in reversed(scrobbleRows):
               
                scrobble = generateScrobble(scrobbleRow)
                
                logger.debug("Comparing {} : {}".format(previousScrobble, scrobble))
                if isDuplicate(previousScrobble, scrobble, timeThreshold):
                    
                    numToDelete += 1
                    logger.info("Found duplicate on page {} - {}".format(currentPage, scrobble))
                    if isDryRun: 
                        scrobblesToDeleteFile.write("{},{},{},{}\n".format(currentPage, scrobble.timestamp, scrobble.artist, scrobble.title))
                    else:
                        try:
                            deleteScrobble(browser, scrobbleRow)
                            logger.info("Deleted: {}".format(scrobble))
                        except ElementNotInteractableException: #If website is slow and element is not yet loaded this retries
                            deleteScrobble(browser, scrobbleRow)
                            logger.info("Deleted: {}".format(scrobble))
                
                previousScrobble = scrobble

            #Move to the next page
            currentPage -= 1
            browser.get("{0}{1}{2}".format(URL_USER, URL_PAGE, currentPage))

            elapsedTime = time.time() - startTime

    
        if isDryRun:
            scrobblesToDeleteFile.close()

    #Catch all in case of unexpected error to close out log file
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

    VERBOSE_FLAG = "-v"          

    logLevel = logging.INFO
    if len(sys.argv) != 1:
        for arg in sys.argv[1:]:
            if arg == VERBOSE_FLAG:
                logLevel = logging.DEBUG
                MODE_VERBOSE = True
    
    logger.setLevel(logLevel)
    main()

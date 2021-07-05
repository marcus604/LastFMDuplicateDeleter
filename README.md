# Last.fm Scrobble Duplicate Deleter

This tool scans your last.fm library for duplicates and deletes them.

Due to last.fm deprecating the delete scrobble API method all previously made tools do not work, this utilizes the browser automation tool Selenium and as long as individual users have the ability to delete scrobbles themselves this can be updated to continue offering this functionality. 

Selenium acts like a user clicking on elements on a website, due to this it is very susceptible to breaking if the last.fm website changes in possibly even minor ways. 

Due to this it is HIGHLY RECOMMENDED to do a dry run first, this generates a .csv of all scrobbles to be deleted and will allow you to scan through and spot check what it will delete (also get a sense how this may change your overall stats)

If you are scrobbling new tracks as this is running it can miss tracks due to it running from oldest to newest and things get pushed to new pages. If you are scrobbling during it then just run the tool multiple times.

Due to limitations this is not a fast tool depending on your library size. 
My 210k library took about 6 hours to do a dry run and then another 10 hours to delete 8k duplicates. 
Both runs can be done in parts, but I would recommend to do the dry run in one go so you have one clean .csv file. 

INSTALL

Install python 
Install selenium chrome driver
install dependencies


USAGE

python main.py 
Run app and provide input
Username - your last.fm username
Password - your last.fm password (this runs entirely locally and the password will only be in memory while the app runs)
Dry Run (y/n) - Whether you want to actually delete scrobbles or just log duplicates its detected
Time Threshold (Seconds) - The amount of seconds between identical tracks to be considered a duplicate. NOTE: Tracks played back to back with a duration less than whatever you set the threshold will be incorrectly flagged as duplicates. This would require adding in communication to the last.fm api for the duration of the track, I think this is a minor edge case and wasnt important to me, feel free to PR :)
Scan all scrobbles (y/n) - Should it scan all your scrobbles or start from a page
	Page to start on - What page number it should start scanning from working forward in time



If you get a "Generic Error" there is a high likelyhood that the website has changed and the tool will need to be updated, PR's are greatly appreciated if not please file an issue and I can take a look. 
<h1 align="center">Welcome to LastFMDuplicateDeleter 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1-blue.svg?cacheSeconds=2592000" />
  <a href="https://spdx.org/licenses/GPL-3.0-or-later.html" target="_blank">
    <img alt="License: GNU GPLv3" src="https://img.shields.io/badge/License-GNU GPLv3-yellow.svg" />
  </a>
</p>

> Scans your last.fm library for duplicates and deletes them.

Due to last.fm deprecating the delete scrobble API method all previously made tools do not work. LastFM Duplicate Deleter utilizes the browser automation tool Selenium and as long as individual users have the ability to delete scrobbles themselves this can be updated to continue offering this functionality. 

Selenium acts like a user clicking on elements on a website, due to this it is very susceptible to breaking if the last.fm website changes in possibly even minor ways. 

Due to this it is <b>HIGHLY RECOMMENDED</b> to do a <u>dry run</u> first, this generates a .csv of all scrobbles to be deleted and will allow you to scan through and spot check what it will delete (also get a sense how this may change your overall stats.)

If you are scrobbling new tracks as this is running it can miss tracks due to it running from oldest to newest and things get pushed to new pages. If you are scrobbling during it then just run the tool multiple times.

Due to limitations this is not a fast tool depending on your library size. 
My 210k library took about 6 hours to do a dry run and then another 10 hours to delete 8k duplicates.
Both runs can be done in parts, but it is recommended to do the dry run in one go. 

## Install

1. Install python (3.9+)
2. Install pipenv
3. Install Chrome and Selenium chrome driver with matching version
4. Clone repo 
  ```sh
git clone https://github.com/marcus604/LastFMDuplicateDeleter.git
```
5. Create environment and install dependencies
```sh
pipenv install
```
## Usage
```sh
pipenv shell
python main.py
```
Enter the requested details for it to run



## Author

👤 **Marcus**

* Github: [@marcus604](https://github.com/marcus604)

## Show your support

Give a ⭐️ if this project helped you! 

## 📝 License

Copyright © 2021 [Marcus](https://github.com/marcus604).<br />
This project is [GNU GPLv3](https://spdx.org/licenses/GPL-3.0-or-later.html) licensed.

***

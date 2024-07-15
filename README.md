<h1 align="center">Welcome to LastFMDuplicateDeleter 👋</h1>
<p>
  <a href="https://spdx.org/licenses/GPL-3.0-or-later.html" target="_blank">
    <img alt="License: GNU GPLv3" src="https://img.shields.io/badge/License-GNU GPLv3-yellow.svg" />
  </a>
</p>

> Scans your last.fm library for duplicates and deletes them.

Due to last.fm deprecating the delete scrobble API method all previously made tools do not work. LastFM Duplicate Deleter utilizes the browser automation tool Selenium to allow a automated way of scanning, identifying and deleting duplicate scrobbles in your library.

Selenium acts like a user clicking on elements on a website, due to this it is very susceptible to breaking if the last.fm website changes in possibly even minor ways.

Due to this it is <b>HIGHLY RECOMMENDED</b> to do a <u>dry run</u> first with `DELETE_MODE=false`, this generates a .csv of all scrobbles to be deleted and will allow you to scan through and spot check what it will delete (also get a sense how this may change your overall stats.)

If you are scrobbling new tracks as this is running it can miss tracks due to it running from oldest to newest and things get pushed to new pages. If you are scrobbling during it then just run the tool multiple times.

Due to limitations this is not a fast tool depending on your library size.
My 210k library took about 6 hours to do a dry run and then another 10 hours to delete 8k duplicates.
Both runs can be done in parts, but it is recommended to do the dry run in one go.

## Docker Compose Setup - Recommended

```yaml
---
services:
   lastfmduplicatedeleter:
      image: ghcr.io/marcus604/lastfmduplicatedeleter:latest
      container_name: lastfmduplicatedeleter
      volumes:
         - <your/local/path>:/app/csv
      environment:
         LASTFM_USERNAME: <your_lastfm_username>
         LASTFM_PASSWORD: <your_lastfm_password>
         TIME_THRESHOLD: 60
         DELETE_MODE: false
         SCAN_FROM_PAGE: 0
         DEBUG: false
```

## Docker CLI

```sh
docker run \
  --name=lastfmduplicatedeleter \
  -e LASTFM_USERNAME=<your_lastfm_username> \
  -e LASTFM_PASSWORD=<your_lastfm_password> \
  -e TIME_THRESHOLD=60 \
  -e DELETE_MODE=false \
  -e SCAN_FROM_PAGE=0 \
  -e DEBUG=false \
  -v <your/local/path>:/app/csv \
  ghcr.io/marcus604/lastfmduplicatedeleter:latest
```

## Parameters

Containers are configured using parameters passed at runtime (such as those above). These parameters are separated by a colon and indicate `<external>:<internal>` respectively.

| Parameter | Function | Default | Type
| :----: | --- | --- | --- |
| `-e LASTFM_USERNAME` | Your last.fm username | | String
| `-e LASTFM_PASSWORD` | Your last.fm password | | String
| `-e TIME_THRESHOLD` |  How many seconds between identical scrobbles to be considered a duplicate - NOTE: Any song with a duration less than the time threshold played back to back will be considered a duplicate | 60 | Int
| `-e DELETE_MODE` | Set this to true to delete scrobbles, otherwise it will only generate a list of duplicates | false | Boolean
| `-e SCAN_FROM_PAGE` | Which page to start scanning for duplicates, page 1 is your most recent scrobbles - NOTE: Set to 0 will scan every scrobble | 0 | Int
| `-e DEBUG` | Set to true to turn on debug logging | false | Boolean
| `-v /app/csv` | Desired location of csv containing duplicates found when DELETE_MODE=false | | Path

## Example Usage

### Pre-requisities

1. Install docker & docker-compose - https://docs.docker.com/compose/install/
2. Verify you have both installed correctly
    1. Open a command prompt and run
       ```
       docker --version
       docker-compose --version
       ```
    2. Verify your output looks like the below, if not then you need to troubleshoot your install
       ```
       Docker version 26.1.1, build 4cf5afa
       Docker Compose version v2.27.0-desktop.2
       ```

### First Run to scan all scrobbles without deleting

1. Create a new file named `docker-compose.yml`
2. Copy the example [docker-compose.yml](#docker-compose-setup---recommended) into that file
3. Replace the 3 variables
    1. <your_lastfm_username> = Your last.fm username
    2. <your_lastfm_password> = Your last.fm password
    3. <your/local/path> = The path you want the csv file of all duplicates to be stored
4. You should now have a file that looks like
    ```yaml
    ---
    services:
      lastfmduplicatedeleter:
          image: ghcr.io/marcus604/lastfmduplicatedeleter:latest
          container_name: lastfmduplicatedeleter
          volumes:
            - /Users/stu/Documents/lastfmduplicatedeleter/:/app/csv
          environment:
            LASTFM_USERNAME: gizzHead456
            LASTFM_PASSWORD: hunter2
            TIME_THRESHOLD: 60
            DELETE_MODE: false
            SCAN_FROM_PAGE: 0
            DEBUG: false
    ```
5. Start the application and attach your terminal to it (You can pass in `-d` to run it in the background if you prefer to view the logs through other means or just want to get the csv and dont need to see the output)
    ```
    docker-compose up
    ```
6. Depending on your computer it will take a minute or two to spin up the needed resources and start outputing its progress. It will show its current page, the % through all the pages and a rough ETA of its completion.
    ```
    2024-07-14 23:25:36,439 - __main__ - INFO - Checking page 67 - 42.56% - ETA 3.71 minutes
    2024-07-14 23:25:36,515 - __main__ - INFO - Checking page 66 - 42.58% - ETA 3.50 minutes
    2024-07-14 23:25:36,599 - __main__ - INFO - Checking page 65 - 42.60% - ETA 3.89 minutes
    ```
7. Once complete it will save a `.csv` file in the path you defined earlier in the example thats `/Users/stu/Documents/lastfmduplicatedeleter/`
8. You can now view this file to view all the duplicates flagged and and validate its findings.
9. If you are happy with your results
    1. Set `DELETE_MODE: true` in your `docker-compose.yml`
    2. Start the application again
        ```
        docker-compose up
        ```



## Contributing

I am more than happy to accept PR's for this project!

### Local Dev Environment

Due to the nature of Selenium it is often much easier to debug issues by being able to see whats appearing in the virtual browser, this means that you need to setup the python environment and install Chrome and the Chrome driver manually.

1. Install python (3.12+) (ideally with something like `pyenv`)
2. Install pipenv
3. Install Chrome and Selenium chrome driver with matching version

    For ARM macOS

    1. Download Chrome
    2. Download the Matching Version Driver
       ```
       wget https://storage.googleapis.com/chrome-for-testing-public/<VERSION_MATCH_TO_YOUR_CHROME>/mac-arm64/chromedriver-mac-arm64.zip
       ```
    3. Unzip the driver and move to `/usr/local/bin` and ensure that `/usr/local/bin` is in your `PATH`

4. Clone repo
   ```
   git clone https://github.com/marcus604/LastFMDuplicateDeleter.git
   ```
5. Create environment and install dependencies
   ```
   pipenv install -r requirements.txt
   ```
6. Enter the pip env
   ```
   pipenv shell
   ```
7. Set Required Environment Variables
   ```
   export LASTFM_LASTFM_USERNAME=gizzHead456
   export LASTM_PASSWORD=hunter2
   export TIME_THRESHOLD=60
   export DELETE_MODE=false
   export SCAN_FROM_PAGE=0
   export DEBUG=false
   ```
8. Optional - Set Selenium to show browser
   ```
   export SHOW_BROWSER=1
   ```
9. Create csv folder
   ```
   mkdir csv
   ```
10. Launch the app
    ```
    python main.py
    ```

## Author

👤 **Marcus**

* Github: [@marcus604](https://github.com/marcus604)

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Copyright © 2021 [Marcus](https://github.com/marcus604).<br />
This project is [GNU GPLv3](https://spdx.org/licenses/GPL-3.0-or-later.html) licensed.

***

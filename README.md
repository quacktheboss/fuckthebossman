# fuckthebossman
Unemployment for all, not just the rich

If you work a fucking corporate job, this code might save you a lot of time.

There are 3 scripts in the src folder.\
One for automatic Workday check in/check out.\
And two scripts for Microsoft Teams messages monitoring.

The scripts assume that 2-step authentication with Microsoft Authenticator is enabled.

Use latest Fedora Linux and Twilio account for SMS delivery.\
You will also need Selenium python modules and chromedriver:
```
pip3 install selenium --user --upgrade --no-cache-dir
sudo dnf5 install chromedriver
```
### Microsoft Teams
Start graph.py to fetch and refresh the Microsoft Graph token.\
It will ask you for your login and password and it will save the token to /tmp/graph.\
Keep it running because token needs to get refreshed once in a while.
```
./graph.py
```

In teams.py file you will need to edit Twilio account details.\
Then start teams.py to monitor for Microsoft Teams messages.\
It will send you a text message whenever your dumbass manager decides to show how important he and his corporate owners are:
```
./teams.py
```

### Workday
In wd.py file you will need to edit the URL at the top.\
It will ask you for login and password, then check in, sleep for 8 hours, and then check out:
```
./wd.py 8
```

Same as above, but 11 hours and overtime comment 'bug #X':
```
./wd.py 11 bug #X
```

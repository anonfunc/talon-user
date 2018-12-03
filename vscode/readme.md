# VS Code via HTTP Rest API
## Install the VS Code plugin and Talon files:
- Install https://marketplace.visualstudio.com/items?itemName=mkloubert.vs-rest-api
- Copy this directory to your ~/.talon/user directory.
## Configure the HTTP endpoint in your Code user settings
Note that you *must* replace two bits in the following config:

    "rest.api": {
        "autoStart": true,
        "openInBrowser": false,
        "port": 1781,
        "guest": false,
        "users": [
            {
                "name": "talon",
                "password": "<BIG RANDOM PASSWORD>",
                "canExecute": true
            }
        ],
        "endpoints": {
            "talonLine": {
                "script": "/Users/<YOUR USERNAME>/.talon/user/vscode/line.js"
            },
            "talonSearch": {
                "script": "/Users/<YOUR USERNAME>/.talon/user/vscode/search.js"
            },
        }
    }

### Most settings can be changed, but the user *must* be named "talon" and the endpoint *must* be named "talonLine".

## Restart VS Code.
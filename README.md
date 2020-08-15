# Ragasiyangal is a Password Manager

'ragasiyangal' means 'secrets' in Tamil, recognised as a classical language and one of the oldest languages in the world that is still in common use.

## Motivation
The motivation for this project is two-fold:
1. Can you have a simple and secure password manager whose code can be easily audited ?
2. Can you have password manager without an expensive (from compute perspective) server or database ?

The answer is 'yes'. 

This project encapsulates all the logic into a single python module, is open source and has no external server or database dependencies. So, you can easily audit the entire source code and be confident that the app is safe to use. 

## User Guide
You can download the binaries from https://github.com/vijaypm/ragasiyangal/releases

Once you install and launch the app, you can choose one of three options:
1. Import a csv file that has the data you want to protect. Click on **Other** menu -> choose **Import** option
2. Start a new secrets file. Click on **File** menu -> choose **New** option or press **Ctrl-N**
3. Open an existing ragasiyangal encrypted file. Click on **File** menu -> choose **Open** option or press **Ctrl-O**

Once you have a document open, you can add, edit or delete rows. As you work with a document, the app provides you several visual clues with bold colors to remind you to save the changes.

### Troubleshooting

#### qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.

If you see an error like this, try the suggestions listed here (https://askubuntu.com/questions/308128/failed-to-load-platform-plugin-xcb-while-launching-qt5-app-on-linux-without). In particular, try reinstalling libxcb-xinerama0 :
`
sudo apt-get install --reinstall libxcb-xinerama0
`
## Developer Guide
The entire source code resides in a single file 'ragasiyangal.py'. To setup your development environment, you will need:
1. Python 3
2. PyQT5
3. cryptography from cryptography.io

From a python3 environment, you can just run 
`
pip install -r requirements.txt
`

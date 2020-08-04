# Ragasiyangal is a Password Manager


## Motivation
The motivation for this project is two-fold:
1. Can you have a simple and secure password manager whose code can be easily audited ?
2. Can you have password manager without an expensive (from compute perspective) server or database ?

The answer is 'yes'. 

This project encapsulates all the logic into a single python module, and has no external server or database dependencies.

## User Guide


## Troubleshooting

#### qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.

If you see an error like this, try the suggestions listed here (https://askubuntu.com/questions/308128/failed-to-load-platform-plugin-xcb-while-launching-qt5-app-on-linux-without). In particular, try this reinstalling libxcb-xinerama0 :
`
sudo apt-get install --reinstall libxcb-xinerama0
`

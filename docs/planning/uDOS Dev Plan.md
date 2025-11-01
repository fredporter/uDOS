uDOS Core 1.0.0 Deversioning Round

uDOS Shell (CLI MODE)
strict cli commands, scripting and core functions
py server
logs
health check
viewport/status check on reboot/startup ascii block splash
CLI file chooser
smart input within cli constraints
micro editor extenstion

Updated sdirectory tructure
/core
/data
/memory
/knowledge
/sandbox
/wiki
/extensions - instructions and scripts for github cloning extensions
/extensions/clone folder - strictly for github repo cloning *keep seperate, add .gitignore
/extensions/web - all new and modified code for extenstions, distributed with uDOS
LIBRARY.UDO - a list of extensions, resources and credits
CREDIT.UDO - list of legal ackowledgements and creidts 

Server ports
A universal way to serve web extensions
Auto open/kill and error management
Roadmap
web extensions and uDOS installations could be shared by URL
css styles
/browser/dashbaord - retro macos greyscale pattern blocks https://github.com/npjg/classic.css
/browser/terminal/ - web terminal in NES style https://github.com/nostalgic-css/NES.css
/browser/terminal/ - splash graphics and ascii blocks, modules and buttons https://nostalgic-css.github.io/NES.css/
/browser/markdown-viewer/ - using Filemanager on the left, with selectable workspaces (folders) /sandbox /data /memory in the style of https://github.com/sakofchit/system.css with modern github markdown rendering of the document content
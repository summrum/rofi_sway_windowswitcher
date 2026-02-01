# rofi_sway_windowswitcher
A Rofi window switcher mode for sway that shows icons, parent workspace, application name and urgent or focused status. Allows for selecting any window to focus, including any or all scratchpad windows. Also allows for closing windows from within the Rofi window.
## Requirements:
**POSIX shell**  
**Rofi** window switcher/application launcher/dmenu replacement  
**jq** command-line JSON processor  
## Usage:
Ensure script is executable, then use one of the following options to add to your Rofi modi:  

**Option 1:** Launch Rofi with a script mode set using the syntax ```"{name}:{executable}"```  
```
rofi -show windowswitcher -modi "scratchpad:/path/to/script/sway_windowswitcher.sh"
```
**Option 2:** Add custom mode to Rofi ```config.rasi``` file  
```
configuration {
	modi: "windowswitcher:/path/to/script/sway_windowswitcher.sh";
}
```
Other modi can be added as usual seprarated by commas; the mode also doesn't have to be called "windowswitcher", any name or glyph can be used.  

The window switcher mode should then be available when launching Rofi, offering a list of windows along with ```[ALL SCRATCHPAD WINDOWS]``` if there are 2 or more scratchpad windows detected. Selecting any option will focus the selected window, or bring all scratchpad windows to the current workspace if ```[ALL SCRATCHPAD WINDOWS]``` is selected. Using a key combination other than "select-entry" will close the selected window (e.g. pressing Shift+Delete if using default keyboard configuration will close the highlighted window - ```[ALL SCRATCHPAD WINDOWS]``` will close all scratchpad windows).

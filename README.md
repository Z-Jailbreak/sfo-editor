# SFO Save Editor

SFO Editor is a Python script for Terminal/CMD that adds a UI to automate the use of commands from the SFO tool written in C by [Hippie68](https://github.com/hippie68/sfo) for PlayStation 4. It also includes some extra features.

## Notes

- The first time you run the script, it will ask you to choose a language. This will only happen once, and the selected language will be saved as the default.
- Inside the Settings menu of the script, you can change the default language, create a backup before modifying, and more.
- This script is intended for editing the `PARAM.SFO` file of PS4 save data.
- If you want to manually change the default language, you need to edit the `saves_language` parameter in `translations.json`, which stores the translations.
- To see emojis correctly, you need a terminal compatible with UTF-8 Unicode.

## Building

To build the script, you need to have the following installed:

- Python 3 & pip
- Requests
- Colorama
- Pyinstaller

### Install the dependencies

[Python for Windows](https://www.python.org/downloads/windows/)

> [!TIP]  
> When running the installer on Windows, select all options to ensure that pip is installed correctly.

Python for Linux

```bash
sudo apt install python3 && sudo apt install pip -y
```

### Colorama, Requests & PyInstaller

```bash
pip install colorama && pip install requests && pip install pyinstaller
```
### Build Python Script

First, go to the folder (example 64 bits):

```bash
cd x64
```

Now, run this command to build SFO Editor:

```bash
pyinstaller --onefile sfo_editor_x64.py
```

> [!NOTE]  
> You can download the Script already compiled and ready to use from [releases](https://github.com/thezodiacox0/sfo-editor/releases)

## Features

- Cross-platform (Windows/Linux).
- Modify SFO parameters individually or both at once.
- Create a backup of `PARAM.SFO` before modifying it.
- Load a predefined JSON configuration to automate SFO modifications.
- FAQ and Troubleshooting section included.
- Available for x86 and x64.
- Online database to download JSON configurations from GitHub.
- Multi-language support (Spanish & English).
- Emoji support visible from PS4/PS5.

## JSON Configuration

To create a JSON configuration to load or share later, follow these steps:

1. Copy an example file and rename it, for example, `thezodiacox.json`.

2. Modify each of its parameters and add more if desired; these will be shown as informational fields in the preview:

  - **ConfigName**: This parameter will not be shown in the preview but will appear in the configurations list (e.g., SFO Example).

  - **MainTitle**: This parameter will change the title shown in the save on the PS4/PS5 (e.g., SaveData Example).

  - **SubTitle**: This parameter will display the description, i.e., the "Details" text on the PS4/PS5 (e.g., Savedata Example Extended).

  - **Version**: This parameter is purely informational but serves to indicate that changes have been made (e.g., 1.2b).

  - **Notes**: This parameter is informational and is used to add notes about the configuration.

3. Once all parameters have been modified, save the file in the `config` folder. The next time the script runs, it will detect the new configuration.

## PARAM.SFO Backup

When a backup is created, it is renamed to make it easily identifiable:

BACKUP-(Method)(TITLE_ID Numbers)-(Random Identifier)(File Count).sfo


- **Method**: Indicates whether parameters were modified individually or using automation (SFO or CONFIG).

- **TITLE_ID Numbers**: For example, GTA V Europe CUSA is `CUSA00411`.

- **Random Identifier**: A 4-digit number randomly generated between 1000 and 9999 used to identify the copy.

- **File Count**: A 2-digit number starting from 00, representing how many times a backup has been made with the same TITLE_ID and method.

**Example Individual**: `BACKUP-SFO00411-541300.sfo`  
**Example Load Configuration**: `BACKUP-CONFIG00411-828500.sfo`

## Online Database from GitHub

SFO Editor can download JSON configurations from a GitHub repository and save them to the existing configurations folder. These are stored as Packs, and you can choose to download some or all of them.

To access the full documentation of the Online Database, click [here](https://github.com/thezodiacox0/sfo-db).

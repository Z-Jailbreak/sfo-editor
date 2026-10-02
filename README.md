# SFO Save Editor

SFO Editor is a Python application that automate the use of commands from the SFO tool written in C by [Hippie68](https://github.com/hippie68/sfo) for PlayStation 4. It also includes some extra features.

## Notes

- The first time you run the application, it will ask you to choose a language. This will only happen once, and the selected language will be saved as the default.
- Inside the Settings menu of the application, you can change the default language and enable a backup before modifying the save or loading a configuration.
- This application is intended for editing the `PARAM.SFO` file of PS4 save data.
- If you want to manually change the default language, edit the `current` value under the `[Language]` from `settings/settings.ini`.

## Features

- Cross-platform (Windows/Linux).
- Modify SFO parameters (Maintitle & Subtitle).
- Optional backup of `PARAM.SFO` before modifying it or loading a configuration.
- Create, edit, delete and load JSON configurations to automate SFO modifications.
- Only available for x64.
- FAQ and Troubleshooting section included.
- Multi-language support (Spanish & English).

## Building

To build the application, you need to have the following installed:

- Python 3 & pip
- The dependencies listed in `requirements.txt`

### Install the dependencies

[Python for Windows](https://www.python.org/downloads/windows/)

> [!TIP]  
> When running the installer on Windows, select all options to ensure that pip is installed correctly.

Python for Linux

```bash
sudo apt install python3 python3-pip -y
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Build the executable

Linux:

```bash
pyinstaller --onefile --windowed --name SFOEditor-Ubuntu \
  --icon source/icon_sfoeditor.ico \
  --add-data source/icon_sfoeditor.ico:. \
  --paths source \
  --add-data source/locales:locales \
  --add-data source/help:help \
  --add-binary source/sfo_app:sfo_app \
  source/main.py
```

Windows:

```
pyinstaller --onefile --windowed --name SFOEditor-Windows --icon source/icon_sfoeditor.ico --add-data "source/icon_sfoeditor.ico;." --paths source --add-data "source/locales;locales" --add-data "source/help;help" --add-binary "source/sfo_app;sfo_app" source/main.py
```

> [!NOTE]  
> You can download the application already compiled and ready to use from [releases](https://github.com/thezodiacox0/sfo-editor/releases).

## JSON Configuration

You can create and edit configurations from the Configurations menu. 

When you create a configuration, you'll be prompted to enter some required parameters, such as `ConfigName`, `Maintitle`, and `Subtitle` and you can add additional parameters to provide more information whenever you want to load them. Here you can see all the parameters:

- **ConfigName**: The name shown in the configurations list (e.g., SFO Example).

- **ConfigDescription**: The description shown under the name in the configurations list (e.g., SFO Description Example).

- **ConfigIcon**: The icon shown in the configurations list, a Font Awesome 5 name used by QtAwesome (e.g., `fa5s.rocket`).

- **ConfigIconColor**: The color of the icon as a hexadecimal value (e.g., `#ffffff`).

- **Author**: The author of the configuration, shown as information in the list (e.g., TheZodiacoX).

- **Maintitle**: This parameter will change the title shown in the save on the PS4/PS5 (e.g., SaveData Example).

- **Subtitle**: This parameter will display the description, i.e., the "Details" text on the PS4/PS5 (e.g., Savedata Example Extended).

- **Version**: This parameter is purely informational but serves to indicate that changes have been made (e.g., 1.2b).

- **Notes**: This parameter is informational and is used to add notes about the configuration.

When you load a configuration, it asks for the `PARAM.SFO` file and writes its `Maintitle` and `Subtitle` into it.

## PARAM.SFO Backup

Backups are optional. They are disabled by default when you open the app for the first time; if you prefer, you can enable backups in Settings.

When a backup is created, it is stored in the `backup` folder and renamed so that it is easily identifiable:

BACKUP-(Method)(TITLE_ID Numbers)-(Random Identifier)(File Count).sfo

- **Method**: Indicates whether parameters were modified individually or using automation (SFO or CONFIG).

- **TITLE_ID Numbers**: The digits of the TITLE_ID. For example, GTA V Europe CUSA is `CUSA00411`, so the number is `00411`.

- **Random Identifier**: A 4-digit number randomly generated between 1000 and 9999 used to identify the copy.

- **File Count**: A 2-digit number starting from 00, representing how many times a backup has been made with the same TITLE_ID and method.

**Example Individual**: `BACKUP-SFO00411-541300.sfo`  
**Example Load Configuration**: `BACKUP-CONFIG00411-828500.sfo`

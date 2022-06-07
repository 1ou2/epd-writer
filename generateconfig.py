import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD SECTION
BACKUP_KEY = "/home/pi/.ssh/id_rsa"
BACKUP_DIR = "pi@192.168.1.2:/home/pi/piwrite"
config_file.add_section("Backup")
# ADD SETTINGS TO SECTION
config_file.set("Backup", "key", BACKUP_KEY)
config_file.set("Backup", "remotedir", BACKUP_DIR)
config_file.set("Backup", "enable", "no")

inifile =r"settings.ini"
# SAVE CONFIG FILE
with open(inifile, 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print(f"Config file {inifile} created")

# PRINT FILE CONTENT
read_file = open(inifile, "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()
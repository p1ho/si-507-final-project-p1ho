import sqlite3
import json
import unidecode # For decoding special player names

DBNAME = 'nba_player_injuries.db'
SRC_JSON = 'nba_player_injuries.json'
SRC = open(SRC_JSON, 'r')
nba_player_injuries = json.loads(SRC.read())
SRC.close()

# Reset the database, and takes the most updated "nba_player_injury.json" file to populate the database
# Parameter: none
# returns: none
def reset_database():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    # drop pre-existing tables
    statement = "DROP TABLE IF EXISTS `Teams`"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS `Players`"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS `Injuries`"
    cur.execute(statement)
    # create new tables
    statement = """CREATE TABLE `Teams` (
                    `Id`	INTEGER,
                    `Name`	TEXT,
                    PRIMARY KEY(`Id`)
                );"""
    cur.execute(statement)
    statement = """CREATE TABLE `Players` (
                    `Id`	INTEGER,
                    `Name`	TEXT,
                    `TeamId`	INTEGER,
                    PRIMARY KEY(`Id`)
                    FOREIGN KEY(`TeamId`) REFERENCES Team(`Id`)
                );"""
    cur.execute(statement)
    statement = """CREATE TABLE `Injuries` (
                    `Id`	TEXT,
                    `Date`	TEXT,
                    `Name`    TEXT,
                    `InjuryCount` INTEGER,
                    `PlayerId`	INTEGER,
                    PRIMARY KEY(`Id`)
                    FOREIGN KEY(`PlayerId`) REFERENCES Player(`Id`)
                );"""
    cur.execute(statement)
    # Fill Team Data
    team_counter = 1
    player_counter = 1
    for team in nba_player_injuries:
        statement = "INSERT INTO `Teams` VALUES (NULL, '{}')".format(team)
        cur.execute(statement)
        for player in nba_player_injuries[team]:
            params = (unidecode.unidecode(player), team_counter)
            statement = "INSERT INTO `Players` VALUES (NULL, ?, ?)"
            cur.execute(statement, params)
            injury_counter = 1
            for injury in nba_player_injuries[team][player]:
                injury_id = "{}/{}".format(player_counter, injury_counter)
                params = (injury_id, injury["date"], injury["injury"], injury_counter, player_counter)
                statement = "INSERT INTO `Injuries` VALUES (?, ?, ?, ?, ?)"
                cur.execute(statement, params)
                injury_counter += 1
            player_counter += 1
        team_counter += 1
    # Save and Close
    conn.commit()
    conn.close()
    
if __name__=="__main__":
    reset_database()
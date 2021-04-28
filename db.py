import mysql.connector


class BDD:

    def __init__(self):
        self.db = mysql.connector.connect(host="telougat.space", user="spaceinvaders", password="azerty/123",
                                          database="spaceinvaders")
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS Scores (nickname VARCHAR(255) NOT NULL, score INTEGER NOT NULL)")

    def savePlayerScore(self, pseudo, score):
        sql = "INSERT INTO Scores (nickname, score) VALUES (%s, %s)"
        values = (pseudo, score)
        self.cursor.execute(sql, values)
        self.db.commit()

    def getLeaderBoard(self):
        self.cursor.execute("SELECT DISTINCT nickname, score FROM Scores ORDER BY score DESC")
        return self.cursor.fetchall()

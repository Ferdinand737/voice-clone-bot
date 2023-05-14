import mysql.connector
from dotenv import load_dotenv
import os


class DataBase:

    def __init__(self):
        self.user = os.getenv('DATABASE_USER')
        self.password = os.getenv('DATABASE_PASSWORD')
        self.host = os.getenv('DATABASE_HOST')
        self.name = os.getenv('DATABASE_NAME')
        self.connect()
       
       
    def connect(self):
        try:
            self.cnx = mysql.connector.connect(user=self.user, password=self.password, host=self.host, database=self.name)
            return self.cnx
        
        except mysql.connector.Error as err:  
            print(err)


    def wipeDatabase(self):
        fileName = "database.sql"
        print("Loading data")
        
        try:
            cursor = self.cnx.cursor()
            with open(fileName, "r") as infile:
                st = infile.read()
                commands = st.split(";")
                for line in commands:                   
                    # print(line.strip("\n"))
                    line = line.strip()
                    if line == "":  # Skip blank lines
                        continue 
                        
                    cursor.execute(line)                    
                        
            cursor.close()
            self.cnx.commit()            
            print("Database load complete")
        except mysql.connector.Error as err:  
            print(err)
            self.cnx.rollback()  


    def cursorToDict(self, cursor):
        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))

        return result


    def getUser(self, user):
        self.connect()
        cursor = self.cnx.cursor()
        sql = "SELECT * FROM users WHERE user_id=%s"
        cursor.execute(sql,(user.id,))
        result = self.cursorToDict(cursor)
        self.cnx.commit() 
        cursor.close()
        if len(result) == 0:
            return None
        return result[0]


    def addUser(self,user):
        self.connect()  
        username = user.name + user.discriminator
        user_id = user.id
        cursor = self.cnx.cursor()
        sql = "INSERT INTO users (user_id, username) VALUES (%s,%s)"
        cursor.execute(sql,(user_id,username))
        self.cnx.commit()
        cursor.close()
        return self.getUser(user)


    def getVoice(self, serverId, voiceName):
        self.connect()

        if serverId is None:
            return self.getPublicVoice(voiceName)

        serverVoice = self.getServerVoice(serverId, voiceName)

        if serverVoice:
            return serverVoice

        cursor = self.cnx.cursor()
        sql = """SELECT * FROM voices 
                    WHERE 
                    (LOWER(name)=%s AND server_id IS NULL) 
                    OR (LOWER(shortcut)=%s AND server_id IS NULL)
                    OR (LOWER(name)=%s AND server_id=%s)
                    OR (LOWER(shortcut)=%s AND server_id=%s);"""

        cursor.execute(sql,(voiceName, voiceName, serverId, voiceName, voiceName, serverId))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result[0]


    def getServerVoice(self, serverId, voice):
        self.connect()

        cursor = self.cnx.cursor()
        sql = """SELECT * FROM voices 
                    WHERE LOWER(name)=%s AND server_id=%s
                    OR (LOWER(shortcut)=%s AND server_id=%s);"""

        cursor.execute(sql,(voice, serverId, voice, serverId))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result[0]


    def getPublicVoice(self, voice):
        self.connect()

        cursor = self.cnx.cursor()
        sql = """SELECT * FROM voices 
                    WHERE LOWER(name)=%s AND server_id IS NULL
                    OR (LOWER(shortcut)=%s AND server_id IS NULL);"""

        cursor.execute(sql,(voice, voice))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result[0]


    def getVoiceById(self, voiceId):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "SELECT * FROM voices WHERE voice_id=%s;"
        cursor.execute(sql,(voiceId,))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result[0]
    

    def addVoice(self, voice_id, voiceName, shortcut, accent, serverId, user_id, path):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "INSERT INTO voices (voice_id, name, shortcut, accent, server_id, user_id, path) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,(voice_id, voiceName, shortcut, accent, serverId, user_id, path))
        self.cnx.commit()
        cursor.close()
        return


    def getPrompt(self, prompt_id):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "SELECT * FROM prompts WHERE prompt_id = %s;"
        cursor.execute(sql, (prompt_id,))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()

        if len(result) == 0:
            return None
        return result[0]


    def addPrompt(self, args, voiceId, userId, serverId, response, numChars):
        self.connect()

        prompt = args['prompt']
        gpt = '' if args['gpt'] == None else 'gpt'
        command = '!chat' if voiceId == None else '!speak'
        command = command + " " + str(args['voiceName']) + " " + gpt
        cursor = self.cnx.cursor()

        sql = "INSERT INTO prompts (command, voice_id, user_id, server_id, prompt, response, num_chars) VALUES (%s,%s,%s,%s,%s,%s,%s);"
        cursor.execute(sql, (command, voiceId, userId, serverId, prompt, response, numChars))
      
        command = command.replace(" ", "_")
      
        sql = "UPDATE prompts SET path = CONCAT('audioOutput/', %s, '/', LAST_INSERT_ID(),'_',%s,'.mp3') WHERE prompt_id = LAST_INSERT_ID();"
        cursor.execute(sql, (userId, command))
     
        cursor.execute("SELECT LAST_INSERT_ID();")
        promptId = cursor.fetchone()[0]
        self.cnx.commit()
        cursor.close()
        return self.getPrompt(promptId)


    def resetMonthlyUserCharCount(self,user_id):
        self.connect()

        cursor = self.cnx.cursor()
        sql = """
        UPDATE users
        SET monthly_chars_used = 0,
            last_char_reset = NOW()
        WHERE user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        self.cnx.commit()
        cursor.close()
        return


    def updateUserMonthlyCharCount(self, user_id, newMonthlyCharCount):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "UPDATE users SET monthly_chars_used = %s WHERE user_id = %s;"  
        cursor.execute(sql, (newMonthlyCharCount, user_id))
        self.cnx.commit()
        cursor.close()
        return


    def updateUserTotalCharCount(self, user_id, newTotalCharCount):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "UPDATE users SET total_chars_used = %s WHERE user_id = %s;"  
        cursor.execute(sql, (newTotalCharCount, user_id))
        self.cnx.commit()
        cursor.close()
        return


    def updateUserCreditCount(self, user_id, newUserCredit):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "UPDATE users SET char_credit = %s WHERE user_id = %s;"  
        cursor.execute(sql, (newUserCredit, user_id))
        self.cnx.commit()
        cursor.close()
        return


    def getPublicVoices(self):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "SELECT * FROM voices WHERE server_id IS NULL"
        cursor.execute(sql)
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result
    

    def getServerVoices(self, serverId):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "SELECT * FROM voices WHERE server_id=%s"
        cursor.execute(sql,(serverId,))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result


    def getUserPrompts(self, userId, limit):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "SELECT * FROM prompts WHERE user_id=%s ORDER BY date_time DESC LIMIT %s"
        cursor.execute(sql,(userId,limit))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result
    

    def deleteVoice(self, voiceId):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "DELETE FROM voices WHERE voice_id=%s"
        cursor.execute(sql,(voiceId,))
        self.cnx.commit()
        cursor.close()


    def updateVoiceId(self, oldId, newId, newPath):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "UPDATE voices SET voice_id = %s, path = %s WHERE voice_id = %s;"  
        cursor.execute(sql, (newId, newPath, oldId))
        self.cnx.commit()
        cursor.close()
        return


    def getUnpopularVoice(self, dontPickThese):
        self.connect()

        cursor = self.cnx.cursor()
        sql = """
                SELECT voice_id, COUNT(*) AS occurrences
                FROM prompts WHERE voice_id IN (SELECT voice_id FROM voices) AND voice_id NOT IN (%s)
                GROUP BY voice_id
                ORDER BY occurrences ASC
                LIMIT 1;
            """
        dontPickThese = ','.join(map(str, dontPickThese))
        cursor.execute(sql,(str(dontPickThese),))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result[0]
    
    def addServer(self, serverId,serverName):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "INSERT INTO servers (server_id, server_name) VALUES (%s,%s)"
        cursor.execute(sql,(serverId,serverName))
        self.cnx.commit()
        cursor.close()
        return
    
    def getServer(self, serverId):
        self.connect()

        cursor = self.cnx.cursor()
        sql = "SELECT * FROM servers WHERE server_id=%s"
        cursor.execute(sql,(serverId,))
        result = self.cursorToDict(cursor)
        self.cnx.commit()
        cursor.close()
        if len(result) == 0:
            return None
        return result[0]
    
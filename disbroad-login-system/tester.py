import subprocess



class ConnectionTester:
    def __int__(self):
        print("Connection Tester Initialised")

    def executeCommand(self, cmd: str):
        result = subprocess.run([cmd], shell=True, capture_output=True, text=True)
        print(result)
        return result.stdout

    def checkServices(self):
        self.servicesList = self.executeCommand("net start")
        print(self.servicesList)
        if "MySQL80" in str(self.servicesList):
            return True
        else:
            return False

    def checkIsRunningCmd(self):
        try:
            self.testResponse = self.executeCommand(r'"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql" test"')
        except Exception as exception:
            print(exception)
            return False

        return True
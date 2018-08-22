import pickle


class NamesDatabase():
    
    def __init__(self, name):
        self.name  = name 
        self.names = []

    def saveDatabase(self, folder):
        f = open("{}/{}.pkl".format(folder,self.name), "wb")
        pickle.dump(self, f)
        f.close()

    def hasEntry(self, nameQuery):
        for name in self.names:
            if name == nameQuery:
                return True
        return False
q
    def getNames(self):
        names = []
        for name in self.names:
            names.append(name)
        return names
            
    def addNewName(self, newName):
        for name in self.names:
            if name == newName:
                return False
        self.names.append(newName)
        return True
    

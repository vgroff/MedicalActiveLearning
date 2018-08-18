from cnnUtils import saveModel, loadModel
import pickle


        
class NeuralNet():
    def __init__(self, name):
        self.name = name

    def saveModel(self, model):
        saveModel(model, self.name)

    def loadModel(self):
        return loadModel(self.name)
        


class NeuralNetDatabase():
    def __init__(self):
        self.nets = []

    def saveDatabase(self):
        f = open("nets.pkl", "wb")
        pickle.dump(self, f)
        f.close()

    def getEntry(self, name):
        for net in self.nets:
            if net.name == name:
                return net
        return False

    def getNames(self):
        names = []
        for net in self.nets:
            names.append(net.name)
        return names
            
    def addNewModel(self, name):
        for net in self.nets:
            if net.name == name:
                return False
        net = NeuralNet(name)
        self.nets.append(net)
        return net
    

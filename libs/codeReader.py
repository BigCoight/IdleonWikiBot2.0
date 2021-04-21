

codeFile = './input/codefile/idleon114.txt'

class Section():
	def __init__(self,start, end, sectionName):
		self.start = start
		self.end = end
		self.between = ''
		self.sectionName = sectionName

class CodeReader():
	def __init__(self, codefile): 
		self.codefile = codefile
		self.currentSection = None
		self.sections = []
		self.sectionResults = {}
	
	def addSection(self, start, end, sectionName):
		self.sections.append(Section(start, end, sectionName))

	def findSection(self, line):
		for section in self.sections:
			if section.start in line:
				self.currentSection = section
				break

	def checkSection(self,line):
		if self.currentSection.end in line:
			self.sectionResults[self.currentSection.sectionName] = self.currentSection.between
			self.sections.remove(self.currentSection)
			self.currentSection = None
		else:
			self.currentSection.between += line

	def readCode(self):
		with open(self.codefile, mode='r') as infile:
			for line in infile:
				if len(self.sections) > 0:
					if self.currentSection:
						self.checkSection(line)
					else:
						self.findSection(line)
				else:
					break

	def getSection(self,sectionName):
		return self.sectionResults.get(sectionName)


if __name__ == '__main__':
	codereader = CodeReader(codeFile)

	codereader.addSection('__name__ = "scripts.ItemDefinitions";','addNewItem = function',"Items")
	codereader.addSection('dialogueDefs = new','finishDialogue',"Quests")
	codereader.readCode()

	print(codereader.getSection("Items"))
	#print(codereader.getSection("Quests"))

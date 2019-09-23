import random
import copy

random.seed()

class BoardState:
	width = 0
	height = 0
	fields = []
	limitsUp = [[0 for y in range(int((height+1)/2))] for x in range (width)]
	limitsLeft = [[0 for y in range(int((width+1)/2))] for x in range (height)]

	def __init__(self, width, height, fields=[], limitsUp=[[0 for y in range(int((height+1)/2))] for x in range (width)], limitsLeft = [[0 for y in range(int((width+1)/2))] for x in range (height)]):
		self.width = width
		self.height = height
		self.fields = fields
		self.limitsUp = limitsUp
		self.limitsLeft = limitsLeft
		self.rows = [[0 for y in range(height)] for x in range(width)]
		self.columns = [[0 for x in range(width)] for y in range(height)]
		self.completedColumns = [0 for x in range(width)]
		self.completedRows = [0 for y in range(height)]
		self.knownColumnFields = [0 for x in range (width)]
		self.knownRowFields = [0 for y in range(height)]
		self.completedLines = 0

class Q_learning:

	def __init__(self, alfa, delta):
		self.alfa = alfa
		self.delta = delta
		self.w1 = 0.0
		self.w2 = 0.0
		self.w3 = 0.0

	def learn(self, board, episodes, maxSteps):
		steps = []
		for e in range(episodes):
			newBoard = copy.deepcopy(board)
			s = self.chooseAction(newBoard, maxSteps)
			if s != -1:
				steps.append(s)

		return steps

	def solve(self, board, maxSteps):
		tabuLines = []
		Q = []
		QLines = []
		
		steps = 0
		self.chooseCertainAction(board)
		while (board.completedLines != board.width + board.height):
			Q = []
			QLines = []
			for x in range(board.width):
				if board.completedColumns[x] != 1:
					f1 = board.knownColumnFields[x]/board.height
					f2 = sum(board.limitsUp[x])/board.height
					f3 = 0
					for i in range(len(board.limitsUp[x])):
						if board.limitsUp[x][i] != 0:
							f3+=1
					f3 /= len(board.limitsUp[x])
					Q.append(f1*self.w1 + f2*self.w2 + f3*self.w3)
					QLines.append(x)
				
			for y in range(board.height):
				if board.completedRows[y] != 1:
					f1 = board.knownRowFields[y]/board.width
					f2 = sum(board.limitsLeft[y])/board.width
					f3 = 0
					for i in range(len(board.limitsLeft[y])):
						if board.limitsLeft[y][i] != 0:
							f3+=1
					f3 /= len(board.limitsLeft[y])
					Q.append(f1*self.w1 + f2*self.w2 + f3*self.w3)
					QLines.append(board.width+y)
	
			while len(tabuLines) > (len(QLines)-1):
				del tabuLines[0]		
			bestLineIndex = 0
			QLinesFiltered = list(filter(lambda x: x not in tabuLines, QLines))
			QFiltered = []
			for x in range(len(Q)):
				if QLines[x] in QLinesFiltered:
					QFiltered.append(Q[x])

			Qmax = QFiltered[0]
			bestLineIndex = QLinesFiltered[0]
			for i in range(len(QFiltered)):
				Qmax = max(Qmax, QFiltered[i])
				if (Qmax == QFiltered[i]) :
					bestLineIndex = QLinesFiltered[i]
			
			if bestLineIndex < board.width:
				updateLine(0, bestLineIndex, board)
			else:
				updateLine(1, bestLineIndex-board.width, board)
			
			tabuLines.append(bestLineIndex)
			
			steps+=1
		
			if steps > maxSteps:
				return -1
				
		return steps



	def chooseAction(self, board, maxSteps):
		Q = 0
		steps = 0
		self.chooseCertainAction(board) #recursive function, fills all certain lines

		numberOfActions = board.width + board.height - sum(board.completedColumns) - sum(board.completedRows)
		
		while (board.completedLines != board.width + board.height):

			rowsOrColumns = random.randint(0, 1)

			#columns
			if rowsOrColumns == 0:
				randomNumber = random.randint(0, board.width-1)
				
				while board.completedColumns[randomNumber] != 0:
					randomNumber = random.randint(0, board.width-1)
					
				newBoard = copy.deepcopy(board)
				Q = self.countQValue(newBoard, 0, randomNumber, Q)
				updateLine(0, randomNumber, board)
				steps += 1

			#rows
			else:
				randomNumber = random.randint(0, board.height-1)
				
				while board.completedRows[randomNumber] != 0:
					randomNumber = random.randint(0, board.height-1)
					
				newBoard = copy.deepcopy(board)
				Q = self.countQValue(newBoard, 0, randomNumber, Q)
				updateLine(1, randomNumber, board)
				steps += 1

			if steps > maxSteps:
				showBoard(board)
				return -1
		return steps

	
	def chooseCertainAction(self, board):
		certain_columns = []
		certain_rows = []
		#to consider: limitsWithSpaces can be held in class
		for x in range (len(board.columns)):
			if board.completedColumns[x] == 0:
				limitsWithSpaces = sum(board.limitsUp[x])
				spaces = -1
				for i in range(len(board.limitsUp[x])):
					if board.limitsUp[x][i] != 0:
						spaces+=1
				if spaces > 0:
					limitsWithSpaces += spaces
				if (limitsWithSpaces == board.height or limitsWithSpaces == 0):
					certain_columns.append(x)
					

		for x in range(len(board.rows)):
			if board.completedRows[x] == 0:
				limitsWithSpaces = sum(board.limitsLeft[x])
				spaces = -1
				for i in range(len(board.limitsLeft[x])):
					if board.limitsLeft[x][i] != 0:
						spaces+=1
				if spaces > 0:
					limitsWithSpaces += spaces
				if (limitsWithSpaces == board.width or limitsWithSpaces == 0):
					certain_rows.append(x)

		numberOfCertain = len(certain_rows) + len(certain_columns)
		if numberOfCertain > 0:
			
			randomCertainLine = random.randint(0, numberOfCertain-1)

			if randomCertainLine < len(certain_rows):
				chosenLine = certain_rows[randomCertainLine]
				is_row = 1
			else:
				chosenLine = certain_columns[randomCertainLine-len(certain_rows)]
				is_row = 0

			updateLine(is_row, chosenLine, board)
			self.chooseCertainAction(board)
		
			

	def countQValue(self, board, is_row, line_no, QPredicted): 
		if (is_row == 0 and board.completedColumns[line_no] == 1) or (is_row == 1 and board.completedRows[line_no] == 1):
			return 0

		QActual = 0.0
		Vmax = 0.0
		f1 = 0
		f2 = 0
		f3 = 0
		
		newBoard = copy.deepcopy(board)

		if is_row == 0:
			f1 = board.knownColumnFields[line_no]/board.height
			f2 = sum(board.limitsUp[line_no])/board.height
			f3 = 0
			for i in range(len(board.limitsUp[line_no])):
				if board.limitsUp[line_no][i] != 0:
					f3+=1
			f3 /= len(board.limitsUp[line_no])
			reward = updateLine(0, line_no, newBoard)
			for j in range(board.width):
				if board.completedColumns[j] == 0:
					boardAfterV = copy.deepcopy(newBoard)
					V = updateLine(0, j, boardAfterV)
					Vmax = max(V, Vmax)
			for j in range(board.height):
				if board.completedRows[j] == 0:
					boardAfterV = copy.deepcopy(newBoard)
					V = updateLine(0, j, boardAfterV)  
					Vmax = max(V, Vmax)
		else:
			f1 = board.knownRowFields[line_no]/board.width
			f2 = sum(board.limitsLeft[line_no])/board.width
			f3 = 0
			for i in range(len(board.limitsLeft[line_no])):
				if board.limitsLeft[line_no][i] != 0:
					f3+=1
			f3 /= len(board.limitsLeft[line_no])
			reward = updateLine(1, line_no, newBoard)
			for j in range(board.width):
				if board.completedColumns[j] == 0:
					boardAfterV = copy.deepcopy(newBoard)
					V = updateLine(0, j, boardAfterV)  
					Vmax = max(V, Vmax)
			for j in range(board.height):
				if board.completedRows[j] == 0:
					boardAfterV = copy.deepcopy(newBoard)
					V = updateLine(0, j, boardAfterV)  
					Vmax = max(V, Vmax)
	

		self.w1 += self.alfa*(reward+self.delta*Vmax - QPredicted)*f1	
		self.w2 += self.alfa*(reward+self.delta*Vmax - QPredicted)*f2
		self.w3 += self.alfa*(reward+self.delta*Vmax - QPredicted)*f3
		QActual = f1*self.w1 + self.w2*f2 + self.w3*f3
		
		return QActual
	
###################################################### END Of Q_LEARNING ############################################### 


# row: 0 if column, 1 if row
#line_no: in range 0 - length-1 - chosen action
#board: board to change
#returns reward [0, 1]
def updateLine(is_row, line_no, board):
	if (is_row == 0 and board.completedColumns[line_no] == 1) or (is_row == 1 and board.completedRows[line_no] == 1):
		return 0

	if is_row == 0:
		limitsWithSpaces = sum(board.limitsUp[line_no])
		spaces = -1
		for i in range(len(board.limitsUp[line_no])):
			if board.limitsUp[line_no][i] != 0:
				spaces+=1
		if spaces > 0:
			limitsWithSpaces += spaces
		if (limitsWithSpaces == board.height or limitsWithSpaces == 0):
			return updateCertainLine(is_row, line_no, board, limitsWithSpaces)
		else:
			return updateUncertainLine(is_row, line_no, board)
		
	else:
		limitsWithSpaces = sum(board.limitsLeft[line_no])
		spaces = -1
		for i in range(len(board.limitsLeft[line_no])):
			if board.limitsLeft[line_no][i] != 0:
				spaces+=1
		if spaces > 0:
			limitsWithSpaces += spaces
		if (limitsWithSpaces == board.width or limitsWithSpaces == 0):
			return updateCertainLine(is_row, line_no, board, limitsWithSpaces)
		else:
			return updateUncertainLine(is_row, line_no, board)


def updateCertainLine(is_row, line_no, board, limitsWithSpaces):
	if is_row == 0:
		if limitsWithSpaces == board.height: #certain line
			y = 0
			for i in range(len(board.limitsUp[line_no])):
				for j in range(board.limitsUp[line_no][i]):
					board.fields[y*board.width+line_no] = 1
					y+=1
				if(y < board.height):
					board.fields[y*board.width+line_no] = -1
					y+=1
		elif limitsWithSpaces == 0:
				for y in range(board.height):
					board.fields[y*board.width+line_no] = -1
		for i in range(board.height):
			board.columns[line_no][i] = board.fields[i*board.width+line_no]
			board.rows[i][line_no] = board.fields[i*board.width+line_no]
		if board.completedColumns[line_no] != 1:
			board.completedColumns[line_no] = 1
			board.completedLines += 1
		board.knownColumnFields[line_no] = board.height
		knownOpposite = 0
		for x in range(board.height):
			knownOpposite = 0
			for y in range(board.width):
				if board.rows[x][y] != 0:
					knownOpposite +=1
			board.knownRowFields[x] = knownOpposite

	else:
		if limitsWithSpaces == board.width: #certain line
			x = 0
			for i in range(len(board.limitsLeft[line_no])):
				for j in range(board.limitsLeft[line_no][i]):
					board.fields[line_no*board.height+x] = 1
					x+=1
				if(x < board.width):
					board.fields[line_no*board.height+x] = -1
					x+=1
		elif limitsWithSpaces == 0:
			for x in range(board.height):
				board.fields[line_no*board.height+x] = -1
		for i in range(board.width):
			board.rows[line_no][i] = board.fields[line_no*board.height+i]
			board.columns[i][line_no] = board.fields[line_no*board.height+i]
		if board.completedRows[line_no] != 1:
			board.completedRows[line_no] = 1
			board.completedLines += 1
		board.knownRowFields[line_no] = board.width
		knownOpposite = 0
		for y in range(board.width): 
			knownOpposite = 0
			for x in range(board.height):
				if board.columns[y][x] != 0:
					knownOpposite +=1
			board.knownColumnFields[y] = knownOpposite

	return 1.0
		


def updateUncertainLine(is_row, line_no, board):
	oldKnown=0
	outLine = []
	inLine = []
	if is_row == 0:
		for y in range(board.height):
			inLine.append(board.fields[y*board.width+line_no]) #actual state of line

		emptyFieldsNumber = board.height - sum(board.limitsUp[line_no])
		toFilter = board.limitsUp[line_no]
		temporary = list(filter(lambda x: x, toFilter))
		spacesNumber = len(temporary) + 1
	else:
		for x in range(board.width):
			inLine.append(board.fields[line_no*board.height+x]) #actual state of line

		emptyFieldsNumber = board.width - sum(board.limitsLeft[line_no])
		toFilter = board.limitsLeft[line_no]
		temporary = list(filter(lambda x: x, toFilter))
		spacesNumber = len(temporary) + 1
	
	spacesSmallest = [0]
	for x in range(spacesNumber-2):
		spacesSmallest.append(1) 
	spacesSmallest.append(0)

	spaces = spacesSmallest
	allResults = []
	emptyFieldsNumber-=(spacesNumber-2)

	index = 0
	results = []

	chooseAllSpaces(emptyFieldsNumber, emptyFieldsNumber, spaces, spaces, index, results)
	#print (results)

	tempOutLine = [0 for x in range(len(inLine))]
	index = 0

	tempOutLines = [] 

	for spacesList in results:
		index = 0
		tempOutLine = [0 for x in range(len(inLine))]
		for a in range(spacesList[0]):
			tempOutLine[index] = -1
			index+=1
		for i in range(len(spacesList)-1):
			if (is_row == 0):
				for y in range(board.limitsUp[line_no][i]):
					tempOutLine[index] = 1
					index+=1
			else:
				for y in range(board.limitsLeft[line_no][i]):
					tempOutLine[index] = 1
					index+=1

			for x in range(spacesList[i+1]):
				tempOutLine[index] = -1
				index+=1
		tempOutLines.append(tempOutLine)

	filteredOutLines = []
	ok = True

	for temp in tempOutLines:
		ok = True
		for i in range(len(temp)):
			if inLine[i] != 0 and temp[i] != inLine[i]:
				ok = False
		if ok == True:
			filteredOutLines.append(temp)
	if len(filteredOutLines) == 0:
		outLine = inLine
	else:
		outLine = filteredOutLines[0]
		for theFiltered in filteredOutLines:
			for i in range(len(theFiltered)):
				if  theFiltered[i] != outLine[i]:
					outLine[i] = 0

	if is_row == 0:
		known = 0
		for y in range(board.height):
			board.fields[y*board.width+line_no] = outLine[y]
			if outLine[y] != 0:
				known+=1
			board.columns[line_no][y] = board.fields[y*board.width+line_no]
			board.rows[y][line_no] = board.fields[y*board.width+line_no]
		oldKnown = board.knownColumnFields[line_no]
		board.knownColumnFields[line_no] = known
		if known == board.height:
			if board.completedColumns[line_no] != 1:
				board.completedColumns[line_no] = 1
				board.completedLines+=1
		for row in range(board.height):
			knownInOpposite = 0
			for x in range(board.width):
				if board.rows[row][x] != 0:
					knownInOpposite +=1
			board.knownRowFields[row] = knownInOpposite
			if knownInOpposite == board.width:
				if board.completedRows[row] != 1:
					board.completedRows[row] = 1
					board.completedLines +=1
		return (known-oldKnown)/(board.height - oldKnown)

	else:
		known = 0
		for x in range(board.width):
			board.fields[line_no*board.height+x] = outLine[x]
			if outLine[x] != 0:
				known+=1
			board.rows[line_no][x] = board.fields[line_no*board.height+x]
			board.columns[x][line_no] = board.fields[line_no*board.height+x]
		oldKnown = board.knownRowFields[line_no]
		board.knownRowFields[line_no] = known
		if known == board.width:
			if board.completedRows[line_no] != 1:
					board.completedRows[line_no] = 1
					board.completedLines +=1	
		for column in range(board.width):
			knownInOpposite = 0
			for x in range(board.height):
				if board.columns[column][x] != 0:
					knownInOpposite +=1
			board.knownColumnFields[column] = knownInOpposite
			if knownInOpposite == board.height:
				if board.completedColumns[column] != 1:
					board.completedColumns[column] = 1
					board.completedLines +=1
		return (known-oldKnown)/(board.width - oldKnown)


def chooseAllSpaces(emptyFields, leftEmptyFields, spaces, tempSpaces, index, results):
	for x in range(leftEmptyFields+1):
		spacesTemp = list(tempSpaces)
		spacesTemp[index] += emptyFields-x
		if x == 0:
			results.append(spacesTemp)
		elif index == (len(spaces)-1):
			return
		else:
			chooseAllSpaces(x, x, spaces, spacesTemp, index+1, results)


def showBoard(board):
	for y in range(board.height):
		for x in range(board.width):
			print(board.fields[board.height*y + x], sep='\t', end='', flush=True)
		print("\n")














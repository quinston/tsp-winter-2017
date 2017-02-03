from tkinter import *
from tkinter.font import nametofont 

class TriangularGridGraph(Canvas):
	def __init__(self, master, height, width, vinf, data):
		super().__init__(master)
		self.GRID_HEIGHT = height
		self.GRID_WIDTH = width
		self.CELL_PIXEL_WIDTH = 100
		self.ARROW_PIXEL_LENGTH = self.CELL_PIXEL_WIDTH // 3
		self.TOP_LEFT_CORNER = (30, 30)
		self.VOID_COLOUR = "#f0f0f0"

		self.EDGES_PER_LOGICAL_ROW = 3*(width-1)+1
		noEdges = (height-1)*(self.EDGES_PER_LOGICAL_ROW) + (width-1)
		for i in range(1, noEdges+1):
			self.drawEdge(i, data)
			self.drawArcs(i, data)

		self.drawVinf(vinf)
		
	def formatNumber(num):
		return "{:.3f}".format(num)

	def drawVinf(self, v):
		horizontalPosition = (v-1) % self.GRID_WIDTH
		verticalPosition = (v-1) // self.GRID_WIDTH
		radius  = 5
		self.create_oval(self.TOP_LEFT_CORNER[0] - 2*radius +  self.CELL_PIXEL_WIDTH * horizontalPosition,
				self.TOP_LEFT_CORNER[1] - 2*radius + self.CELL_PIXEL_WIDTH * verticalPosition,
				self.TOP_LEFT_CORNER[0] + 2*radius + self.CELL_PIXEL_WIDTH * horizontalPosition,
				self.TOP_LEFT_CORNER[1] + 2*radius + self.CELL_PIXEL_WIDTH * verticalPosition,
				outline="blue",
				width=3)

	def drawEdge(self, e, data):
		edgeName = "x{}".format(e)
		isVoid = edgeName not in data or data[edgeName] == 0
		if isVoid:
			lineColour = self.VOID_COLOUR
		elif data[edgeName] == 1:
			lineColour = "black"
		else:
			lineColour = "red"
			
		if (e-1) % (self.EDGES_PER_LOGICAL_ROW) < (self.GRID_WIDTH - 1):
			# Horizontal line
			horizontalPosition = (e-1) % (self.EDGES_PER_LOGICAL_ROW)
			verticalPosition = (e-1) // (self.EDGES_PER_LOGICAL_ROW)
			self.create_line(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * (horizontalPosition + 1),
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					fill=lineColour,
					width=3)
			# draw edge weight on centre of edge
			if not isVoid and data[edgeName] != 1:
				self.create_text(self.TOP_LEFT_CORNER[0] + int(self.CELL_PIXEL_WIDTH * (horizontalPosition + 0.5)), self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition, text=TriangularGridGraph.formatNumber(data[edgeName]), fill='blue')

		elif (e - self.GRID_WIDTH) % 2 == 0:
			horizontalPosition = (((e-1) % (self.EDGES_PER_LOGICAL_ROW)) - (self.GRID_WIDTH - 1)) // 2
			verticalPosition = ((e-1) // (self.EDGES_PER_LOGICAL_ROW)) 
			# Vertical line
			self.create_line(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * (verticalPosition + 1),
					fill=lineColour,
					width=3)
			# draw edge weight on centre of edge
			if not isVoid and data[edgeName] != 1:
				self.create_text(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition, self.TOP_LEFT_CORNER[1] + int(self.CELL_PIXEL_WIDTH * (verticalPosition + 0.5)), text=TriangularGridGraph.formatNumber(data[edgeName]), fill='blue')

		else:
			# diagonal line
			horizontalPosition = (((e-1) % (self.EDGES_PER_LOGICAL_ROW)) - (self.GRID_WIDTH - 1)) // 2
			verticalPosition = ((e-1) // (self.EDGES_PER_LOGICAL_ROW)) 
			# Vertical line
			self.create_line(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * (horizontalPosition + 1),
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * (verticalPosition + 1),
					fill=lineColour,
					width=3)
			# draw edge weight on centre of edge
			if not isVoid and data[edgeName] != 1:
				self.create_text(self.TOP_LEFT_CORNER[0] + int(self.CELL_PIXEL_WIDTH * (horizontalPosition + 0.5)), self.TOP_LEFT_CORNER[1] + int(self.CELL_PIXEL_WIDTH * (verticalPosition + 0.5)), text=TriangularGridGraph.formatNumber(data[edgeName]), fill='blue')

	def drawArcs(self, e, data):
		isVertical = (e-1) % self.EDGES_PER_LOGICAL_ROW < (self.GRID_WIDTH - 1)
		isNotVerticalAndHorizontal = (e - self.GRID_WIDTH) % 2 == 0

		unboundedFace = (self.GRID_WIDTH - 1)*2*(self.GRID_HEIGHT - 1) + 1

		if isVertical:
			horizontalPosition = (e-1) % (self.EDGES_PER_LOGICAL_ROW)
			verticalPosition = (e-1) // (self.EDGES_PER_LOGICAL_ROW)

			upFace, downFace = (0, 0)
			if verticalPosition == 0:
				upFace = unboundedFace 
				downFace = horizontalPosition + 1 
			elif verticalPosition == self.GRID_HEIGHT - 1:
				upFace = 2*((verticalPosition - 1) * (self.GRID_WIDTH - 1) + horizontalPosition) + 1
				downFace = unboundedFace
			else:
				upFace = (verticalPosition - 1) * (self.GRID_WIDTH - 1) + horizontalPosition + 1
				downFace = (verticalPosition - 0) * (self.GRID_WIDTH - 1) + horizontalPosition + 1

			for face, direction, offset in ((upFace, "first", self.CELL_PIXEL_WIDTH * 2 // 9), (downFace, "last", self.CELL_PIXEL_WIDTH * 7 // 9)):
				edgeName = "z{},{}".format(e, face)
				isVoid = edgeName not in data or data[edgeName] == 0

				if not isVoid:
					if data[edgeName] != 1:
						lineColour = "green"
					else:
						lineColour = "black"
				else:
					lineColour = self.VOID_COLOUR
				
				self.create_line(self.TOP_LEFT_CORNER[0] + offset + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] - (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * verticalPosition,
						self.TOP_LEFT_CORNER[0] + offset + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * verticalPosition,
						arrow = direction,
						fill = lineColour,
						width=3)

				if not isVoid and data[edgeName] != 1:
					self.create_text(self.TOP_LEFT_CORNER[0] + offset + self.CELL_PIXEL_WIDTH * horizontalPosition, 
					# stagger the text for vertical arrow pairs
					self.TOP_LEFT_CORNER[1] + ((1 if direction == "first" else -1) * self.ARROW_PIXEL_LENGTH // 3) + self.CELL_PIXEL_WIDTH * verticalPosition,
 text=TriangularGridGraph.formatNumber(data[edgeName]), fill='blue')

		elif isNotVerticalAndHorizontal:
			# horizontal
			horizontalPosition = (((e-1) % self.EDGES_PER_LOGICAL_ROW) - (self.GRID_WIDTH - 1)) // 2
			verticalPosition = ((e-1) // self.EDGES_PER_LOGICAL_ROW) 

			leftFace, rightFace = (0,0)
			if horizontalPosition == 0:
				leftFace = unboundedFace
				rightFace = 2*((verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition) + 1
			elif horizontalPosition == self.GRID_WIDTH - 1:
				leftFace = 2*((verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition) + 0
				rightFace = unboundedFace
			else:
				leftFace = 2*((verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition) + 0
				rightFace = 2*((verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition) + 1

			for face, direction, offset in ((leftFace, "first", self.CELL_PIXEL_WIDTH//3), (rightFace, "last", 2 * self.CELL_PIXEL_WIDTH // 3)):
				edgeName = "z{},{}".format(e, face)
				isVoid = edgeName not in data or data[edgeName] == 0

				if not isVoid:
					if data[edgeName] != 1:
						lineColour = "green"
					else:
						lineColour = "black"
				else:
					lineColour = self.VOID_COLOUR
				
				self.create_line(self.TOP_LEFT_CORNER[0] - (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + offset + self.CELL_PIXEL_WIDTH * verticalPosition,
						self.TOP_LEFT_CORNER[0] + (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + offset + self.CELL_PIXEL_WIDTH * verticalPosition,
						arrow = direction,
						fill = lineColour,
						width=3)

				if not isVoid and data[edgeName] != 1:
					self.create_text(self.TOP_LEFT_CORNER[0] + (self.ARROW_PIXEL_LENGTH // 3) + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + offset + self.CELL_PIXEL_WIDTH * verticalPosition,
 text="{:.3f}".format(data[edgeName]), fill='blue')

		else:
			# diagonal
			horizontalPosition = (((e-1) % self.EDGES_PER_LOGICAL_ROW) - (self.GRID_WIDTH - 1)) // 2
			verticalPosition = ((e-1) // self.EDGES_PER_LOGICAL_ROW) 

			leftFace = 2* ((verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition ) + 1
			rightFace = 2*((verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition ) + 2

			for face, direction, offset in ((leftFace, "first", self.CELL_PIXEL_WIDTH//3), (rightFace, "last", 2 * self.CELL_PIXEL_WIDTH // 3)):
				edgeName = "z{},{}".format(e, face)
				isVoid = edgeName not in data or data[edgeName] == 0

				if not isVoid:
					if data[edgeName] != 1:
						lineColour = "green"
					else:
						lineColour = "black"
				else:
					lineColour = self.VOID_COLOUR
				
				self.create_line(self.TOP_LEFT_CORNER[0] + offset - (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + offset + (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * verticalPosition,
						self.TOP_LEFT_CORNER[0] + offset + (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + offset - (self.ARROW_PIXEL_LENGTH // 2) +  self.CELL_PIXEL_WIDTH * verticalPosition,
						arrow = direction,
						fill = lineColour,
						width=3)

				# to make label text not be on the same line as other arrows
				stagger = 8

				if not isVoid and data[edgeName] != 1:
					self.create_text(self.TOP_LEFT_CORNER[0] + offset + (self.ARROW_PIXEL_LENGTH // 3) + self.CELL_PIXEL_WIDTH * horizontalPosition ,
						self.TOP_LEFT_CORNER[1] + offset + self.CELL_PIXEL_WIDTH * verticalPosition - stagger,
 text="{:.3f}".format(data[edgeName]), fill='blue')

def displayTriangularGrid(height, width, vinf, data):
	root = Tk()
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	g1 = TriangularGridGraph(root, height=height, width=width, vinf=vinf, data=data)
	g1.grid(row=0, column=0, sticky=(N,E,W,S))

	nametofont("TkDefaultFont").configure(size=10,weight='bold')

	windowWidth = g1.CELL_PIXEL_WIDTH * (width + 1)
	windowHeight = g1.CELL_PIXEL_WIDTH * (height + 1)
	root.geometry('{}x{}'.format(windowWidth, windowHeight))
	root.mainloop()
	

if __name__ == '__main__':
	while True:
		height = int(input('grid height '))
		width = int(input('grid width '))
		vinf = int(input('vinf '))
		data = dict(eval(input('data ')))
		displayTriangularGrid(height, width, vinf, data)

""" try me
4
6
17
{'x6': 6, 'x7': 7, 'x16': 16, 'x17': 17, 'x2': 2,  'z6,31': 31, 'z7,1': 1.01, 'z7,2': 2.02, 'z8,2': 2, 'z6,1': 1.001, 'z8,3': 8.3, 'z38,31': 38.31, 'z48,31': 48.31, 'z53,29': 53.29, 'z52,27': 52.27, 'z53,31': 53.31, 'z27,15': 27.15, 'z27,16':27.16}
"""


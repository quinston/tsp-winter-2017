from tkinter import *
from tkinter.font import nametofont 

class TriangularGridGraph(Canvas):
	def __init__(self, master, height, width, vinf, data):
		super().__init__(master)
		self.GRID_HEIGHT = height
		self.GRID_WIDTH = width
		self.CELL_PIXEL_WIDTH = 120
		self.ARROW_PIXEL_LENGTH = self.CELL_PIXEL_WIDTH // 3
		self.TOP_LEFT_CORNER = (30, 30)
		self.VOID_COLOUR = "#f0f0f0"

		self.EDGES_PER_LOGICAL_ROW = 3*(width-1)+1
		noEdges = (height-1)*(self.EDGES_PER_LOGICAL_ROW) + (width-1)
		for i in range(1, noEdges+1):
			self.drawEdge(i, data)
			self.drawArcs(i, data)

		# +1 for infinite face
		noFaces = 2*(width-1)*(height-1) + 1
		for i in range(1, noFaces+1):
			self.drawFace(i, data)

		self.drawVinf(vinf)
		
	def formatNumber(num):
		if num == int(num):
			return str(num)
		else:
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

		elif (((e-1) % (self.EDGES_PER_LOGICAL_ROW)) - self.GRID_WIDTH) % 2 == 1:
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
		isNotVerticalAndHorizontal = (((e-1) % self.EDGES_PER_LOGICAL_ROW) - self.GRID_WIDTH) % 2 == 1

		unboundedFace = (self.GRID_WIDTH - 1)*2*(self.GRID_HEIGHT - 1) + 1

		if isVertical:
			horizontalPosition = (e-1) % (self.EDGES_PER_LOGICAL_ROW)
			verticalPosition = (e-1) // (self.EDGES_PER_LOGICAL_ROW)

			upFace, downFace = (0, 0)
			if verticalPosition == 0:
				upFace = unboundedFace 
				downFace = 2*horizontalPosition + 2
			elif verticalPosition == self.GRID_HEIGHT - 1:
				upFace = 2*((verticalPosition - 1) * (self.GRID_WIDTH - 1) + horizontalPosition) + 1
				downFace = unboundedFace
			else:
				upFace = 2*((verticalPosition - 1) * (self.GRID_WIDTH - 1) + horizontalPosition) + 1
				# +1+1 since the orientation of the down face differs from the up face (from upper triangular to lower triangular face)
				downFace = 2*((verticalPosition + 0) * (self.GRID_WIDTH - 1) + horizontalPosition) + 2

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
	
	def drawFace(self, f, data):
		faceName = "b{}".format(f)

		if faceName not in data:
			value = 0
		else:
			value = data[faceName]

		horizontalPosition = (f-1) % ((self.GRID_WIDTH - 1) * 2)
		verticalPosition = (f-1) // ((self.GRID_WIDTH - 1) * 2)
		
		horizontalOffset = (((-1)**(f-1)) * (self.CELL_PIXEL_WIDTH // 8)) + self.CELL_PIXEL_WIDTH // 4
		verticalOffset = ((-1)**(f-1)) * (self.CELL_PIXEL_WIDTH // 10) + (self.CELL_PIXEL_WIDTH * 24 // 50)
		self.create_text(self.TOP_LEFT_CORNER[0] + horizontalOffset + (horizontalPosition * (self.CELL_PIXEL_WIDTH // 2)),
				self.TOP_LEFT_CORNER[1] + verticalOffset + (verticalPosition * self.CELL_PIXEL_WIDTH),
				text="{:.3f}".format(value),
				fill='magenta')

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

6
4
1
[('x1', 0.6), ('x2', 1.0), ('x3', 1.0), ('x4', 1.0), ('x5', 0.4), ('x6', 0.4), ('x10', 1.0), ('x11', 0.19999999999999996), ('x12', 0.7999999999999999), ('x14', 0.8), ('x16', 0.20000000000000007), ('x18', 0.6), ('x19', 0.6), ('x20', 1.0), ('x21', 0.19999999999999996), ('x22', 1.0), ('x24', 0.3999999999999999), ('x25', 0.6000000000000001), ('x27', 0.6), ('x29', 0.4), ('x30', 0.4), ('x31', 0.39999999999999997), ('x33', 0.2), ('x34', 1.0), ('x35', 0.20000000000000007), ('x36', 1.0), ('x38', 0.8), ('x39', 0.4), ('x40', 1.0), ('x42', 0.7999999999999999), ('x44', 1.0), ('x49', 0.4), ('x50', 0.6), ('x51', 1.0), ('x52', 1.0), ('x53', 1.0), ('z6,3', 0.6), ('z7,3', 0.4), ('z7,4', 0.6), ('z8,4', 0.4), ('z8,5', 0.6), ('z9,6', 1.0), ('z11,8', 0.8), ('z12,10', 0.20000000000000007), ('z13,12', 0.6), ('z13,5', 0.4), ('z14,7', 0.19999999999999996), ('z15,7', 0.8), ('z15,8', 0.19999999999999996), ('z16,9', 0.7999999999999999), ('z17,9', 0.20000000000000007), ('z17,10', 0.7999999999999999), ('z18,11', 0.4), ('z19,12', 0.4), ('z21,14', 0.8), ('z23,18', 0.4), ('z23,11', 0.6), ('z24,13', 0.6000000000000001), ('z25,13', 0.3999999999999999), ('z26,14', 0.19999999999999996), ('z26,15', 0.8), ('z27,16', 0.4), ('z28,16', 0.6), ('z28,17', 0.4), ('z29,17', 0.6), ('z30,18', 0.6), ('z31,20', 0.6000000000000001), ('z32,22', 0.8), ('z32,15', 0.19999999999999996), ('z33,24', 0.8), ('z35,19', 0.4), ('z35,20', 0.3999999999999999), ('z37,21', 1.0), ('z38,22', 0.19999999999999996), ('z39,23', 0.4), ('z39,24', 0.19999999999999996), ('z41,26', 0.4), ('z41,19', 0.6), ('z42,28', 0.20000000000000007), ('z43,30', 0.4), ('z43,23', 0.6), ('z45,25', 1.0), ('z46,26', 0.6), ('z46,27', 0.4), ('z47,27', 0.6), ('z47,28', 0.4), ('z48,28', 0.3999999999999999), ('z48,29', 0.6000000000000001), ('z49,29', 0.3999999999999999), ('z49,30', 0.2), ('z50,30', 0.4)]
"""


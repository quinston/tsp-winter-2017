from tkinter import *
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
			# self.drawArcs(i, data)

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

def displayTriangularGrid(height, width, vinf, data):
	root = Tk()
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	g1 = TriangularGridGraph(root, height=height, width=width, vinf=vinf, data=data)
	g1.grid(row=0, column=0, sticky=(N,E,W,S))

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

from tkinter import *


class GridGraph(Canvas):
	def __init__(self, master, width, vinf, data):
		super().__init__(master)

		self.GRID_WIDTH = width
		self.CELL_PIXEL_WIDTH = 100

		self.ARROW_PIXEL_LENGTH = self.CELL_PIXEL_WIDTH // 2
		self.TOP_LEFT_CORNER = (30, 30)
		self.VOID_COLOUR = "#f0f0f0"

		for i in range(1, (2*width - 1) * (width - 1) + (width-1) + 1):
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
		pass

		
	def drawEdge(self, e, data):
		# don't draw void edges
		edgeName = "x{}".format(e)

		isVoid = edgeName not in data or data[edgeName] == 0
		if isVoid:
			lineColour = self.VOID_COLOUR
		else:
			if data[edgeName] == 1:
				lineColour = "black"
			else:
				lineColour = "red"
		if (e-1) % (self.GRID_WIDTH * 2 - 1) < (self.GRID_WIDTH - 1):
			# Horizontal line
			horizontalPosition = (e-1) % (self.GRID_WIDTH * 2 - 1)
			verticalPosition = (e-1) // (self.GRID_WIDTH * 2 - 1)
			self.create_line(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * (horizontalPosition + 1),
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					fill=lineColour,
					width=3)
			# draw edge weight on centre of edge
			if not isVoid and data[edgeName] != 1:
				self.create_text(self.TOP_LEFT_CORNER[0] + int(self.CELL_PIXEL_WIDTH * (horizontalPosition + 0.5)), self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition, text=GridGraph.formatNumber(data[edgeName]), fill='blue')

		else:
			horizontalPosition = ((e-1) % (self.GRID_WIDTH * 2 - 1)) - (self.GRID_WIDTH - 1)
			verticalPosition = ((e-1) // (self.GRID_WIDTH * 2 - 1)) 
			# Vertical line
			self.create_line(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * (verticalPosition + 1),
					fill=lineColour,
					width=3)
			# draw edge weight on centre of edge
			if not isVoid and data[edgeName] != 1:
				self.create_text(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition, self.TOP_LEFT_CORNER[1] + int(self.CELL_PIXEL_WIDTH * (verticalPosition + 0.5)), text=GridGraph.formatNumber(data[edgeName]), fill='blue')

	def drawArcs(self, e, data):
		isVertical = (e-1) % (self.GRID_WIDTH * 2 - 1) < (self.GRID_WIDTH - 1)
		isExterior = (((e-1) % (self.GRID_WIDTH * 2 - 1)) in [self.GRID_WIDTH - 1, self.GRID_WIDTH * 2 - 2]) or (((e-1) // (self.GRID_WIDTH * 2 - 1)) in [0, self.GRID_WIDTH])
		unboundedFace = (self.GRID_WIDTH - 1)**2 + 1

		if isVertical:
			horizontalPosition = (e-1) % (self.GRID_WIDTH * 2 - 1)
			verticalPosition = (e-1) // (self.GRID_WIDTH * 2 - 1)

			upFace, downFace = (0, 0)
			if verticalPosition == 0:
				upFace = unboundedFace 
				downFace = horizontalPosition + 1 
			elif verticalPosition == self.GRID_WIDTH - 1:
				upFace = (verticalPosition - 1) * (self.GRID_WIDTH - 1) + horizontalPosition + 1
				downFace = unboundedFace
			else:
				upFace = (verticalPosition - 1) * (self.GRID_WIDTH - 1) + horizontalPosition + 1
				downFace = (verticalPosition - 0) * (self.GRID_WIDTH - 1) + horizontalPosition + 1

			for face, direction, offset in ((upFace, "first", self.CELL_PIXEL_WIDTH//3), (downFace, "last", 2 * self.CELL_PIXEL_WIDTH // 3)):
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
 text=GridGraph.formatNumber(data[edgeName]), fill='blue')

		else:
			# horizontal
			horizontalPosition = ((e-1) % (self.GRID_WIDTH * 2 - 1)) - (self.GRID_WIDTH - 1)
			verticalPosition = (e-1) // (self.GRID_WIDTH * 2 - 1)

			leftFace, rightFace = (0,0)
			if horizontalPosition == 0:
				leftFace = unboundedFace
				rightFace = (verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition + 1
			elif horizontalPosition == self.GRID_WIDTH - 1:
				leftFace = (verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition 
				rightFace = unboundedFace
			else:
				leftFace = (verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition 
				rightFace = (verticalPosition) * (self.GRID_WIDTH - 1) + horizontalPosition + 1

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


def displayGrid(width, vinf, data):
	root = Tk()
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	g1 = GridGraph(root, width=width, vinf=vinf, data=data)
	g1.grid(row=0, column=0, sticky=(N,E,W,S))

	windowWidth = windowHeight = g1.CELL_PIXEL_WIDTH * (width + 1)
	root.geometry('{}x{}'.format(windowWidth, windowHeight))
	root.mainloop()


if __name__ == '__main__':
	while True:
		width = int(input('Grid width: '))
		vinf = int(input('vinf: '))
		data = dict(eval(input('data: ')))
		displayGrid(width, vinf, data)

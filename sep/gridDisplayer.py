from tkinter import *

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

class GridGraph(Canvas):
	def __init__(self, master, width, vinf, data):
		super().__init__(master, width=1000, height=1000)

		self.GRID_WIDTH = width
		self.CELL_PIXEL_WIDTH = 100
		self.ARROW_PIXEL_LENGTH = self.CELL_PIXEL_WIDTH // 2
		self.TOP_LEFT_CORNER = (30, 30)

		for i in range(1, (2*width - 1) * (width - 1) + (width-1) + 1):
			self.drawEdge(i, data)
			self.drawArcs(i, data)

		self.drawVinf(vinf)

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
		edgeName = "e{}".format(e)

		if edgeName not in data or data[edgeName] == 0:
			lineColour = "#ccc"
		else:
			lineColour = "#{:02x}0000".format(int(255 * (1 - data[edgeName])))
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

			for face, direction, offset in ((upFace, "last", self.CELL_PIXEL_WIDTH//3), (downFace, "first", 2 * self.CELL_PIXEL_WIDTH // 3)):
				edgeName = "z{},{}".format(e, face)

				if edgeName in data and data[edgeName] > 0:
					lineColour = "#00{:02x}00".format(int(255 * (1 - data[edgeName])))
				else:
					lineColour = "#ccc"
				
				self.create_line(self.TOP_LEFT_CORNER[0] + offset + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] - (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * verticalPosition,
						self.TOP_LEFT_CORNER[0] + offset + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * verticalPosition,
						arrow = direction,
						fill = lineColour,
						width=3)

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

			print("direct {} left {} right {}".format(e, leftFace, rightFace))

			for face, direction, offset in ((leftFace, "last", self.CELL_PIXEL_WIDTH//3), (rightFace, "first", 2 * self.CELL_PIXEL_WIDTH // 3)):
				edgeName = "z{},{}".format(e, face)

				if edgeName in data and data[edgeName] > 0:
					lineColour = "#00{:02x}00".format(int(255 * (1 - data[edgeName])))
				else:
					lineColour = "#ccc"
				
				self.create_line(self.TOP_LEFT_CORNER[0] - (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + offset + self.CELL_PIXEL_WIDTH * verticalPosition,
						self.TOP_LEFT_CORNER[0] + (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * horizontalPosition,
						self.TOP_LEFT_CORNER[1] + offset + self.CELL_PIXEL_WIDTH * verticalPosition,
						arrow = direction,
						fill = lineColour,
						width=3)


				

if __name__ == '__main__':
	g1 = GridGraph(root, width=3, vinf=9, data={
		"e1": 1,
		"e2": 0.9,
		"e3": 0.8,
		"e4": 0.7,
		"e5": 0.6,
		"e5": 0.5,
		"e6": 0.4,
		"e7": 0.3,
		"e8": 0.2,
		"e9": 0.1,
		"e10": 0,
		"e11": 1,
		"e12": 0.5,
		"z1,1": 0.5,
		"z1,5": 0.4,
		"z3,5": 0.1,
		"z3,1": 1
		})
	g1.grid(row=0, column=0, sticky=(N,E,W,S))
	
	root.mainloop()

from tkinter import *

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

class GridGraph(Canvas):
	def __init__(self, master, width=6, data={}):
		super().__init__(master)

		self.data = data

		self.GRID_WIDTH = width
		self.CELL_PIXEL_WIDTH = 30
		self.ARROW_PIXEL_LENGTH = self.CELL_PIXEL_WIDTH // 2
		self.TOP_LEFT_CORNER = (30, 30)

		for i in range(1, (2*width - 1) * (width - 1) + (width-1) + 1):
			self.drawEdge(i)
			self.drawArcs(i)

		
	def drawEdge(self, e):
		lineColour = "#{:02x}0000".format(int(255 * self.data["e{}".format(e)]))
		if (e-1) % (self.GRID_WIDTH * 2 - 1) < (self.GRID_WIDTH - 1):
			# Horizontal line
			horizontalPosition = (e-1) % (self.GRID_WIDTH * 2 - 1)
			verticalPosition = (e-1) // (self.GRID_WIDTH * 2 - 1)
			self.create_line(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * (horizontalPosition + 1),
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					fill=lineColour,
					width='2')
		else:
			horizontalPosition = ((e-1) % (self.GRID_WIDTH * 2 - 1)) - (self.GRID_WIDTH - 1)
			verticalPosition = ((e-1) // (self.GRID_WIDTH * 2 - 1)) 
			# Vertical line
			self.create_line(self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + self.CELL_PIXEL_WIDTH * (verticalPosition + 1),
					fill=lineColour,
					width='2')

	def drawArcs(self, e):
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
			print("direct {} up {} down {}".format(e, upFace, downFace))


			# down arrow 
			self.create_line(self.TOP_LEFT_CORNER[0] + (self.CELL_PIXEL_WIDTH//3) + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] - (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + (self.CELL_PIXEL_WIDTH//3) + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * verticalPosition,
					arrow = "last")
			# up arrow
			self.create_line(self.TOP_LEFT_CORNER[0] + (2 * self.CELL_PIXEL_WIDTH//3) + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] - (self.ARROW_PIXEL_LENGTH // 2) + self.CELL_PIXEL_WIDTH * verticalPosition,
					self.TOP_LEFT_CORNER[0] + (2 * self.CELL_PIXEL_WIDTH//3) + self.CELL_PIXEL_WIDTH * horizontalPosition,
					self.TOP_LEFT_CORNER[1] + (self.ARROW_PIXEL_LENGTH//2) + self.CELL_PIXEL_WIDTH * verticalPosition,
					arrow = "first")

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
				


g1 = GridGraph(root, width=6, data=dict((("e{}".format(i), 1) for i in range(1, 60+1))))
g1.grid(row=0, column=0, sticky=(N,E,W,S))

root.mainloop()

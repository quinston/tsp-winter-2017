from tkinter import *

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

class GridGraph(Canvas):
	def __init__(self, master, width=6, data={}):
		super().__init__(master)

		self.data = data

		self.GRID_WIDTH = width
		self.CELL_PIXEL_WIDTH = 20
		self.ARROW_SIZE = 8
		self.TOP_LEFT_CORNER = (5,5)

		for i in range(1, (2*width - 1) * (width - 1) + (width-1) + 1):
			self.drawEdge(i)

		
	def drawEdge(self, e):
		if "e{}".format(e) in self.data:
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



		pass

	def drawArcs(self, e):
		pass


g1 = GridGraph(root, width=6, data=dict((("e{}".format(i), 1) for i in range(1, 60+1))))
g1.grid(row=0, column=0, sticky=(N,E,W,S))

root.mainloop()

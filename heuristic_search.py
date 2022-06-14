from queue import PriorityQueue
from random import randrange

import pygame
import sys

from pygame.time import Clock

pygame.init()

colors = {
	'black': (0, 0, 0),
	'white': (255, 255, 255),
	'green': (139, 173, 133),
	'green2': (190, 224, 184),
	'blue': (140, 191, 217),
	'red': (191, 64, 64),
	'yellow': (230, 230, 179),
	'orange': (255, 165, 0),
	'roxo': (149, 64, 191),
	'grey': (128, 128, 128),
	'cinza': (134, 134, 121),
	'marron': (204, 191, 179),
	'bege': (221, 213, 213),
	'pink': (182, 79, 128)
}

window_height = 600
window_width = 600
margin = 5
rows = 50
score = 0

screen = pygame.display.set_mode((window_width, window_height))
screen2 = pygame.display.set_mode((800, 600))
screen2.fill(colors.get('white'))
set_score = pygame.Surface((10,35))
score_font = pygame.font.SysFont("arial", 20, True, False)
clock = pygame.time.Clock()

####################################################

class Block:

	def __init__(self, row, col, width, height):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = colors.get('white')
		self.neighbors = []
		self.width = width
		self.height = height
		self.cost = 1

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == colors.get('red')

	def is_open(self):
		return self.color == colors.get('green')

	def is_barrier(self):
		return self.color == colors.get('cinza')

	def is_start(self):
		return self.color == colors.get('orange')

	def is_end(self):
		return self.color == colors.get('pink')

	def reset(self):
		self.color = colors.get('white')

	def make_start(self):
		self.color = colors.get('orange')

	def make_closed(self):
		self.color = colors.get('red')

	def make_open(self):
		self.color = colors.get('green')

	def make_barrier(self):
		self.color = colors.get('cinza')
	
	def make_high_cost(self):
		self.color = colors.get('yellow')

	def make_medium_cost(self):
		self.color = colors.get('blue')

	def make_end(self):
		self.color = colors.get('pink')

	def make_path(self):
		self.color = colors.get('roxo')

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):

		self.neighbors = []
		if self.row < self.height - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.height - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


class Food:
	
	def __init__(self, grid, rows, width):

		self.grid = grid
		self.rows = rows
		self.width = width
		self.pos_x = None
		self.pos_y = None
		
	# def draw_food(self):
	# 	pygame.draw.ellipse(self.sc, colors.get('roxo'), (self.pos_x, self.pos_y, self.bs, self.bs))

	def generate_position(self):

		is_in_barries = True
		
		while is_in_barries:

			x, y = randrange(0, self.rows - 1), randrange(0, self.rows - 1)

			if not self.grid[x][y].is_barrier() and not self.grid[x][y].is_start():
				self.pos_x = x
				self.pos_y = y		
				self.grid[x][y].make_end()

				is_in_barries = False

	def get_position(self):
		return [self.pos_x, self.pos_y]


class Agent:

	def __init__(self, sc, grid, rows, width):
		self.sc = sc
		self.grid = grid
		self.rows = rows
		self.width = width
		self.pos_x = None
		self.pos_y = None
		self.score = 0
		

	def draw_agent(self):
		pygame.draw.rect(self.sc, colors.get('black'), (self.pos_x, self.pos_y,  30, 30))

	def generate_position(self):

		is_in_barries = True
		gap = self.width // self.rows

		while is_in_barries:

			x, y = randrange(0, self.rows-1), randrange(0, self.rows-1)

			if not self.grid[x][y].is_barrier() and not self.grid[x][y].is_end():
				self.pos_x = x
				self.pos_y = y		
				self.grid[x][y].make_start()

				is_in_barries = False

	def get_position(self):
		return [self.pos_x, self.pos_y]


class Scenario:

	def __init__(self, sc, ww):
		self.sc = sc
		self.ww = ww
		self.rows = rows
		self.grid = []
		
	def get_grid(self):
		return self.grid

	def show_score(self, screen2):
		msg = score_font.render("Score: {}".format(score), False, colors.get('black'))
		screen2.blit(msg, [650,250])

	def create_grid(self):
		
		gap = self.ww // self.rows

		for i in range(self.rows):
			self.grid.append([])
			for j in range(self.rows):
				block = Block(i, j, gap, self.rows)
				self.grid[i].append(block) 
		
	def draw_grid(self):
		
		gap = self.ww // self.rows
		for i in range(self.rows):
			pygame.draw.line(self.sc, colors.get('grey'), (0, i*gap), (self.ww, i*gap))
			
			for j in range(self.rows):
				pygame.draw.line(self.sc, colors.get('grey'), (j * gap, 0), (j*gap, self.ww))
		

	def draw(self):

		# self.sc.fill(colors.get('white'))
		for row in self.grid:
			for block in row:
				block.draw(self.sc)

		self.draw_grid()
		pygame.display.update()


	def draw_grounds(self):

		# draw barries
		col_range = [x for x in range(5, 15)]
		for col in col_range:
			self.grid[3][col].make_barrier()
			self.grid[3][col].cost = 0
		
		row_range = [x for x in range(4, 15)]
		for row in row_range:
			self.grid[row][4].make_barrier()
			self.grid[row][4].cost = 0

		row_range = [x for x in range(30, 40)]
		for row in row_range:
			self.grid[row][6].make_barrier()
			self.grid[row][6].cost = 0

		col_range = [x for x in range(15, 35)]
		for col in col_range:
			self.grid[30][col].make_barrier()
			self.grid[30][col].cost = 0
		
		row_range = [x for x in range(5, 20)]
		for row in row_range:
			self.grid[row][35].make_barrier()
			self.grid[row][35].cost = 0

		row_range = [x for x in range(15, 35)]
		for row in row_range:
			self.grid[row][45].make_barrier()
			self.grid[row][45].cost = 0
	
		# grounds medium cost
		for row in range(8, 19):
			for col in range(8, 19):
				self.grid[row][col].make_medium_cost()
				self.grid[row][col].cost = 5

		# # grounds high cost
		for row in range(31, 47):
			for col in range(15, 35):
				self.grid[row][col].make_high_cost()
				self.grid[row][col].cost = 10

		pygame.display.update()


	def reset_grid(self):
		self.grid = []


class Search:

	def __init__(self, scenario):
		self.scenario = scenario

	def heuristic(self, pos_a, pos_b):
		x1, y1 = pos_a
		x2, y2 = pos_b

		return abs(x1 - x2) + abs(y1 - y2)

	def collect_food(self, came_from, current, draw):

		global score

		pos = []
		while current in came_from:	
			current = came_from[current]
			pos.append(current)

		pos = list(reversed(pos))

		i = 0
		for p in pos:
			if i == 0:
				p.make_start()
			else:
				p.make_start()
				pos[i-1].make_path()
			
			i += 1
			draw()
			pygame.time.wait(30)

		score += 1

		return


	def reconstruct_path(self, came_from, current, draw):
		
		while current in came_from:
			current = came_from[current]
			current.make_path()
			draw()

		return

	def a_star_search(self, draw, grid, start, goal):

		count = 0
		frontier = PriorityQueue()
		frontier.put((0, count, start))
		came_from = {}

		g_score = {block: float("inf") for row in grid for block in row }
		g_score[start] = 0  
		f_score = {block: float("inf") for row in grid for block in row }
		f_score[start] = self.heuristic(start.get_pos(), goal.get_pos())

		frontier_hash = { start }

		# print("g_score: {}".format(len(g_score)))
		# print("f_score: {}".format(len(f_score)))
		
		while not frontier.empty():
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			current = frontier.get()[2]
			frontier_hash.remove(current)	

			if current == goal:
				self.reconstruct_path(came_from, goal, draw)
				# goal.make_end()
				self.collect_food(came_from, goal, draw)
				return True

			for neighbor in current.neighbors:

				temp_g_score = g_score[current] + neighbor.cost  
				# print("temp_g_score: {}".format(temp_g_score))

				if temp_g_score < g_score[neighbor]:
					came_from[neighbor] = current
					g_score[neighbor] = temp_g_score
					f_score[neighbor] = temp_g_score + self.heuristic(neighbor.get_pos(), goal.get_pos())
					
					if neighbor not in frontier_hash:
						count += 1
						frontier.put((f_score[neighbor], count, neighbor))
						frontier_hash.add(neighbor)

						neighbor.make_open()
						
			draw()

			if current != start:
				current.make_closed()
			

		return False


class Main:

	def __init__(self, sc, ww):
		self.sc = sc
		self.ww = ww		

	def main_loop(self):
		
		# scenario = Scenario(self.sc, self.ww)
		# scenario.create_grid()				
		# grid = scenario.get_grid()

		# agent = Agent(self.sc, grid, rows, self.ww)
		# food = Food(grid, rows, self.ww)
		i = 0
		while True:

			print("iteração ", i)

			scenario = Scenario(self.sc, self.ww)
			scenario.create_grid()				
			grid = scenario.get_grid()

			agent = Agent(self.sc, grid, rows, self.ww)
			food = Food(grid, rows, self.ww)

			scenario.draw()
			scenario.draw_grounds()
			scenario.show_score(screen2)
			agent.generate_position()
			food.generate_position()
			
			search = Search(scenario)
		
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			for row in grid:
				for block in row:
					block.update_neighbors(grid)

			a_x, a_y = agent.get_position()
			f_x, f_y = food.get_position()

			search.a_star_search(
				draw=lambda: scenario.draw(),
				grid=grid,
				start=grid[a_x][a_y],
				goal=grid[f_x][f_y]
			)

			pygame.display.update()
			clock.tick(1)
			screen2.fill(colors.get('white'))
			scenario.reset_grid()				
				
			i += 1

if __name__ == '__main__':

	Main(
		sc=screen,
		ww=window_width
	).main_loop()

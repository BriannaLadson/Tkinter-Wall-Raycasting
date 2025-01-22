from tkinter import *
import math

class Root(Tk):
	def __init__(self):
		super().__init__()
		self.title("Ray Casted 3D Walls")
		self.state("zoomed")
		
		self.player = Player()
		
		self.game_canvas = GameCanvas(self)
		self.game_canvas.pack(fill=BOTH, expand=1)
		self.game_canvas.update()
		
		self.minimap = Minimap(self.game_canvas)
		self.game_canvas.create_window(0, 0, window=self.minimap, anchor="nw")
		
		self.bind("w", lambda e: self.player.move_forward(self.minimap, self.game_canvas))
		self.bind("s", lambda e: self.player.move_backward(self.minimap, self.game_canvas))
		self.bind("a", lambda e: self.player.move_left(self.minimap, self.game_canvas))
		self.bind("d", lambda e: self.player.move_right(self.minimap, self.game_canvas))
		
		self.last_mouse_x = None
		self.bind("<Motion>", self.mouse_turn)
		
		self.minimap.draw_minimap()
		
		self.game_canvas.update_3d_world()
		
	def mouse_turn(self, event):
		if self.last_mouse_x is not None:
			delta_x = event.x - self.last_mouse_x
			
			self.player.rotate(delta_x)
			
			self.minimap.draw_player()
			
			self.game_canvas.update_3d_world()
			
		self.last_mouse_x = event.x
		
class Player:
	def __init__(self):
		self.x = 0.0
		self.y = 0.0
		
		self.view_angle = 0
		
		self.speed = .1
		
		self.turn_speed = math.radians(1)
		
		self.fov = math.radians(60)
		self.num_rays = 120
		
	def move_forward(self, minimap, game_canvas):
		new_x = self.x + math.cos(self.view_angle) * self.speed
		new_y = self.y + math.sin(self.view_angle) * self.speed
		
		if not self.collides(new_x, new_y, minimap):
			self.x, self.y = new_x, new_y
			
			minimap.draw_player()
			
			game_canvas.update_3d_world()
			
	def move_backward(self, minimap, game_canvas):
		new_x = self.x - math.cos(self.view_angle) * self.speed
		new_y = self.y - math.sin(self.view_angle) * self.speed
		
		if not self.collides(new_x, new_y, minimap):
			self.x, self.y = new_x, new_y
			
			minimap.draw_player()
			
			game_canvas.update_3d_world()
			
	def move_left(self, minimap, game_canvas):
		strafe_angle = self.view_angle - math.pi / 2
		
		new_x = self.x + math.cos(strafe_angle) * self.speed
		new_y = self.y + math.sin(strafe_angle) * self.speed
		
		if not self.collides(new_x, new_y, minimap):
			self.x, self.y = new_x, new_y
			
			minimap.draw_player()
			
			game_canvas.update_3d_world()
			
	def move_right(self, minimap, game_canvas):
		strafe_angle = self.view_angle + math.pi / 2
		
		new_x = self.x + math.cos(strafe_angle) * self.speed
		new_y = self.y + math.sin(strafe_angle) * self.speed
		
		if not self.collides(new_x, new_y, minimap):
			self.x, self.y = new_x, new_y
			
			minimap.draw_player()
			
			game_canvas.update_3d_world()
			
	def rotate(self, delta_x):
		self.view_angle += delta_x * self.turn_speed
			
	def collides(self, x, y, minimap):
		map_x = int(x)
		map_y = int(y)
		
		max_x = minimap.wall_map_width
		max_y = minimap.wall_map_height
		
		if 0 <= map_x < max_x and 0 <= map_y < max_y:
			return minimap.wall_map[map_y][map_x] >= 1
			
		else:
			return True
		
class GameCanvas(Canvas):
	def __init__(self, parent):
		super().__init__(parent, bg="#FED6D3")
		
		self.player = self.master.player
		
	def update_3d_world(self):
		self.delete("3d_world")
		self.draw_3d_world()
		
	def draw_3d_world(self):
		ray_step = self.player.fov / self.player.num_rays
		
		for i in range(self.player.num_rays):
			ray_angle = self.player.view_angle - (self.player.fov / 2) + (i * ray_step)
			
			ray_x, ray_y = self.player.x, self.player.y
			distance = 0
			minimap = self.master.minimap
			max_distance = max(minimap.wall_map_width, minimap.wall_map_height)
			hit_wall = False
			wall_color = "gray"
			
			while not hit_wall and distance < max_distance:
				distance += .1
				
				ray_x = self.player.x + math.cos(ray_angle) * distance
				ray_y = self.player.y + math.sin(ray_angle) * distance
				
				map_x = int(ray_x)
				map_y = int(ray_y)
				
				max_x = minimap.wall_map_width
				max_y = minimap.wall_map_height
				
				if map_x < 0 or map_y < 0 or map_x >= max_x or map_y >= max_y:
					hit_wall = True
				
				elif minimap.wall_map[map_y][map_x] >= 1:
					hit_wall = True
					wall_type = minimap.wall_map[map_y][map_x]
					wall_color = minimap.map_walls[wall_type]
					
			corrected_distance = distance * math.cos(ray_angle - self.player.view_angle)
			
			if corrected_distance == 0:
				corrected_distance = .1
				
			wall_height = min(self.winfo_height(), int(self.winfo_height() / corrected_distance))
			wall_width = self.winfo_width() / self.player.num_rays
			
			wall_x = i * wall_width
			wall_y = (self.winfo_height() - wall_height) / 2
			
			wall_x1 = wall_x + wall_width
			wall_y1 = (self.winfo_height() + wall_height) / 2
			
			self.create_rectangle(
				wall_x,
				wall_y,
				wall_x1,
				wall_y1,
				fill=wall_color,
				outline="",
				tags=("3d_world"),
			)
		
class Minimap(Canvas):
	def __init__(self, parent):
		super().__init__(parent, bg="#9D8A88", width=100, height=100)
		
		self.update_size()
		
		self.player = parent.master.player
		
		self.map_walls = {
			0: "",
			1: "gray",
			2: "blue",
		}
		
		self.wall_map = [
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 1,],
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
		]
		
		self.wall_map_width = len(self.wall_map[0])
		self.wall_map_height = len(self.wall_map)
		
		self.center_player()
		
	def update_size(self):
		parent = self.master
		
		width = int(parent.winfo_width() * .25)
		height = int(parent.winfo_height() * .25)
		
		self.config(width=width, height=height)
		
	def draw_minimap(self):
		self.delete("all")
		self.update()
		
		self.draw_tiles()
		
		self.draw_player()
		
	def draw_tiles(self):
		minimap_width = self.winfo_width()
		minimap_height = self.winfo_height()
		
		self.tile_width = tile_w = minimap_width / self.wall_map_width
		self.tile_height = tile_h = minimap_height / self.wall_map_height
		
		for y in range(self.wall_map_height):
			for x in range(self.wall_map_width):
				tile_x = x * tile_w
				tile_y = y * tile_h
				
				tile_x1 = tile_x + tile_w
				tile_y1 = tile_y + tile_h
				
				wall_type = self.wall_map[y][x]
				wall_color = self.map_walls[wall_type]
				
				self.create_rectangle(tile_x, tile_y, tile_x1, tile_y1, fill=wall_color, outline="black")
				
	def center_player(self):
		self.player.x = self.wall_map_width / 2
		self.player.y = self.wall_map_height / 2
		
	def draw_player(self):
		self.delete("player")
		
		player_radius = 5
		
		scaled_player_x = self.player.x * self.tile_width
		scaled_player_y = self.player.y * self.tile_height
		
		circle_x = scaled_player_x - player_radius
		circle_y = scaled_player_y - player_radius
		
		circle_x1 = scaled_player_x + player_radius
		circle_y1 = scaled_player_y + player_radius
		
		self.create_oval(circle_x, circle_y, circle_x1, circle_y1, fill="red", outline="black", tags=("player"))
		
		self.draw_rays()
		
		self.draw_viewline(scaled_player_x, scaled_player_y)
		
	def draw_viewline(self, scaled_player_x, scaled_player_y):
		self.delete("viewline")
		
		viewline_length = 50
		
		viewline_x1 = scaled_player_x + math.cos(self.player.view_angle) * viewline_length
		viewline_y1 = scaled_player_y + math.sin(self.player.view_angle) * viewline_length
		
		self.create_line(scaled_player_x, scaled_player_y, viewline_x1, viewline_y1, fill="blue", width=2, tags=("viewline"))
			
	def draw_rays(self):
		self.delete("rays")
		
		ray_step = self.player.fov / self.player.num_rays
		
		for i in range(self.player.num_rays):
			ray_angle = self.player.view_angle - (self.player.fov / 2) + (i * ray_step)
			
			ray_x, ray_y = self.player.x, self.player.y
			distance = 0
			max_distance = max(self.wall_map_width, self.wall_map_height)
			hit_wall = False
			
			while not hit_wall and distance < max_distance:
				distance += .1
				ray_x = self.player.x + math.cos(ray_angle) * distance
				ray_y = self.player.y + math.sin(ray_angle) * distance
				
				map_x = int(ray_x)
				map_y = int(ray_y)
				
				max_x = self.wall_map_width
				max_y = self.wall_map_height
				
				if map_x < 0 or map_y < 0 or map_x >= max_x or map_y >= max_y:
					hit_wall = True
					
				elif self.wall_map[map_y][map_x] >= 1:
					hit_wall = True
					
			scaled_start_x = self.player.x * self.tile_width
			scaled_start_y = self.player.y * self.tile_height
			
			scaled_end_x = ray_x * self.tile_width
			scaled_end_y = ray_y * self.tile_height
			
			self.create_line(
				scaled_start_x,
				scaled_start_y,
				scaled_end_x,
				scaled_end_y,
				fill="yellow",
				width=1,
				tags="rays",
			)
			
if __name__ == "__main__":
	root = Root()
	root.mainloop()
#!/usr/bin/env python3
from game.minesweeper import *
from game.artificial_agent import ArtificialAgent
import sys
from os.path import dirname
from typing import List, Tuple

# hack for importing from parent package
sys.path.append(dirname(dirname(dirname(__file__))))
from csp_templates import *
from solver import Solver


class Agent(ArtificialAgent):
    """
    Logic implementation for Minesweeper ArtificialAgent.

    See ArtificialAgent for details.
    """

    def __init__(self, verbose: int) -> None:
        super().__init__(verbose)
        
        # Initialize the CSP object here
        self.csp = None  # Initialize it as None for now
        self.revised_tiles = []
        self.inferred=[]
        self.solver = Solver()
        self.values=[]
        
    def new_game(self) -> None:
        """Agent got into a new level."""
        super().new_game()
        # Initialize the CSP object in new_game() method    
        self.revised_tiles = []
        self.inferred=[]
        self.values=[]
    
    def observe(self, board: Board) -> None:
        """Agent receives current state of the board."""
        super().observe(board)
        self.csp = BooleanCSP(num_vars=board.width * board.height)
       
        
                
    def think_impl(self, board: Board, previous_board: Board) -> Action:
        """
        Code your custom agent here.
        The existing dummy implementation always asks for a hint.

        The Board object passed to think_impl gives you the current board state.
        Check ArtificialAgent.think_impl docstring for more info.
        """
        i=0
        print(board.get_view())
        infer=-1
        z=0
        print("--------------------")
        
        
        for value in self.values:
            
            self.csp.set(z,value)
            z=z+1
       
        #check if there are inferred values waiting to be checked
        
        if len(self.inferred)>0 and self.inferred is not None:
            if self.csp.value[self.inferred[0]]==True:
                self.revised_tiles.append(self.var_to_tile(self.inferred[0],board))
                print("Bomb in: ",self.var_to_tile(self.inferred[0],board))
                value=self.inferred[0]
                self.inferred.remove(self.inferred[0])
                return ActionFactory.get_flag_action(self.var_to_tile(value,board)[0],self.var_to_tile(value,board)[1])
            else:
                self.revised_tiles.append(self.var_to_tile(self.inferred[0],board))
                print("No bomb in: ",self.var_to_tile(self.inferred[0],board))
                value=self.inferred[0]
                self.inferred.remove(self.inferred[0])
                return ActionFactory.get_uncover_action(self.var_to_tile(value,board)[0],self.var_to_tile(value,board)[1])   
        
        #udpate csp with each iteration FUNCIONA
        self.update_csp(board)      
                
       
           

        #check values in csp and return action if there is a value 
        for value in self.csp.value:
            x=self.var_to_tile(i,board)[0]
            y=self.var_to_tile(i,board)[1]
            if value is not None and [x,y] not in self.revised_tiles:
                if value is True:
                    print("Bomb in: ",x , y)
                    return ActionFactory.get_flag_action(x,y)
                else:
                    print("Safe in: ",x , y)
                    return ActionFactory.get_uncover_action(x,y)
            i=i+1
        
       
                   
        self.solver.infer_var(self.csp)
        print("infer: ",infer)
        if infer != -1:
            coord=self.var_to_tile(infer,board)
            tile=board.tile(coord[0],coord[1])
            if [coord[0],coord[1]] not in self.revised_tiles:
                self.revised_tiles.append([coord[0],coord[1]])
                print("Safe in: ",coord[0] , coord[1])
                return ActionFactory.get_uncover_action(coord[0],coord[1])
            
        self.csp.reset()
        self.update_csp(board) 
        
        self.inferred=Solver.forward_check(Solver,self.csp)
        self.values=self.csp.value
        
        
        if len(self.inferred)>0:
            #hacer una lista con las variables que se pueden descubrir y ir haciendo una por una en cada iteración
            
            if self.csp.value[self.inferred[0]]==True:
                self.revised_tiles.append(self.var_to_tile(self.inferred[0],board))
                print("Bomb in: ",self.var_to_tile(self.inferred[0],board))
                value=self.inferred[0]
                self.inferred.remove(self.inferred[0])
                return ActionFactory.get_flag_action(self.var_to_tile(value,board)[0],self.var_to_tile(value,board)[1])
            else:
                self.revised_tiles.append(self.var_to_tile(self.inferred[0],board))
                print("No bomb in: ",self.var_to_tile(self.inferred[0],board))
                value=self.inferred[0]
                self.inferred.remove(self.inferred[0])
                return ActionFactory.get_uncover_action(self.var_to_tile(value,board)[0],self.var_to_tile(value,board)[1])
    
        print("hint")
        return ActionFactory.get_advice_action()

    def tile_to_var(self, x: int, y: int, board) -> int:
        
        return y+ board.width*x
    
    def var_to_tile(self, var: int,board) -> Tuple[int, int]:
        return (var // board.width,var % board.width)

    def neighbours(self, x: int, y: int, board: Board) -> List[Tuple[int, int]]: #check the neighbors of a tile
        width, height = board.width, board.height
        xy=self.tile_to_var(x,y,board)
        neighbors = []
        for dy in range(-1 if y > 0 else 0, 2 if y < height - 1 else 1):
            for dx in range(-1 if x > 0 else 0, 2 if x < width - 1 else 1):
                dxy=self.tile_to_var(x + dx, y + dy,board)
                if dxy!=xy:
                    neighbors.append(dxy)
        return neighbors
    
    def update_csp(self, board: Board) -> None:
        for x in range(board.width):
            for y in range(board.height):
                neighbours=[]
                tile = board.tile(x, y)
                if tile.visible or tile.is_flagged():
                    if tile.is_flagged():
                        print("flagged: ",x,y)
                        self.csp.set(self.tile_to_var(x,y,board), True)
                    else:
                        self.csp.set(self.tile_to_var(x,y,board), False)
                    self.revised_tiles.append([x,y])
                    for neighbour in self.neighbours(x,y,board):
                        if self.var_to_tile(neighbour,board):
                            neighbours.append(neighbour)
                    if not tile.is_flagged() and Constraint(tile.mines_around,neighbours) not in self.csp.constraints:   
                            self.csp.add_constraint(Constraint(tile.mines_around,neighbours))
    
    def reset_lists(self, board: Board) -> None:
        """Example."""
        # reset
        self.border_unknown = []
        self.border_numbers = []
        self.flagged = []

        # query tiles
        for (x, y), tile in board.generator():
            if not tile.visible:
                if tile.flag:
                    self.flagged.append((x, y))
                # test border tile
                if self.is_border_tile(x, y, board):
                    self.border_unknown.append((x, y))
            elif tile.mines_around > 0:
                # test border tile
                if self.is_border_tile(x, y, board):
                    self.border_numbers.append((x, y))

    def is_border_tile(self, x: int, y: int, board: Board) -> bool:
        """Example."""
        width, height = board.width, board.height
        is_border = False
        for dy in range(-1 if y > 0 else 0, 2 if y < height - 1 else 1):
            if is_border:
                break
            for dx in range(-1 if x > 0 else 0, 2 if x < width - 1 else 1):
                next_tile: Tile = board.tile(x + dx, y + dy)
                if next_tile.visible:
                    is_border = True
                    break
        return is_border

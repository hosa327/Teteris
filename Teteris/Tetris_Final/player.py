# bleow variable weight is from reference:https://github.com/ericma1999/engf0002-tetris/blob/master/player.py
from board import Direction, Rotation
from random import Random
from time import sleep
from exceptions import NoBlockException

class Player:
    def choose_action(self, board):
        raise NotImplementedError
class MyPlayer(Player):
    heightConstant = -0.410066
    linesConstant = -0.960666
    holesConstant = -0.95663
    bumpinessConstant = -0.284483

    moves = 0

    best_horizontal_position = None
    best_rotation_position = None

    second_move = None
    second_rotation = None

    def generate_column_height(self, board):
        columns = [0] * board.width
        for y in reversed(range(board.height)):
            for x in range(board.width):
                if (x,y) in board.cells:
                    height = abs(board.height - y)
                    columns[x] = height
        return columns

    def check_height(self,board):
        columns = self.generate_column_height(board)
        return (sum(columns)  / len(columns)) * self.heightConstant
    
    def check_bumpiness(self, board):
        total = 0
        columns = self.generate_column_height(board)
        for i in range(9):
            total += abs(columns[i] - columns[i+1])
        return total * self.bumpinessConstant

    def check_lines(self, originalBoard, board):
        score = board.score - originalBoard.score
        complete_line = 0
        # points given
        if score >= 1600:
            complete_line += 4
        elif score >= 400:
            complete_line += 3
        elif score >= 100:
            complete_line += 2
        elif score >= 25:
            complete_line += 1
        return complete_line * self.linesConstant
    
    def check_holes(self, board):
        columns = self.generate_column_height(board)
        tally = [0] * 10 
        for x in range(board.width):
            for y in range(board.height - columns[x], board.height):
                if (x, y) not in board.cells:
                        tally[x] += 1
        return self.holesConstant * sum(tally)

    def check_wells(self, board):
        columns = self.generate_column_height(board)
        tally = [0] * 10 
        for x in range(board.width):
            for y in range(board.height - columns[x], board.height):
                if(x,y) not in board.cells:
                    tally[x] += 1
        return max(tally) * self.holesConstant * 1.2

    def calc_score(self, originalBoard, board):
        total = self.check_height(board) + self.check_holes(board) + self.check_lines(originalBoard, board) + self.check_bumpiness(board) + self.check_wells(board)
        return total

    def try_rotation(self,rotation, board):
        for _ in range(rotation):
            try:
                board.rotate(Rotation.Anticlockwise)
            except NoBlockException:
                pass
    def try_moves(self, moves, board):
            move = 4 - moves
            if (move >= 0):
                for _ in range(move):
                    try:
                        board.move(Direction.Right)
                    except NoBlockException:
                        pass
            else:
                for _ in range(abs(move)):
                    try:
                        board.move(Direction.Left)
                    except NoBlockException:
                        pass
            try:
                board.move(Direction.Drop)
            except NoBlockException:
                pass

    def simulate_best_position(self, board):
        score = None
        columns = self.generate_column_height(board)
        columns_more_than_six = [column for column in columns if column > 6]
        columns_more_than_eight = [column for column in columns if column > 8]
        upper = 10
        lower = 2
        avg = sum(columns[0:7]) / 8
        if (avg >= 4 or len(columns_more_than_six) > 3 or len(columns_more_than_eight) > 2):
            self.linesConstant = 1.46
            self.heightConstant = -0.8
            self.holesConstant = -1.2
            upper = 10
            lower = 0
        else:
            self.heightConstant = -0.510066
            self.holesConstant = -1.5663
            lower = 1

        for rotation in range(4):
            for horizontal_moves in range(lower, upper):
                cloned_board = board.clone()
                self.try_rotation(rotation, cloned_board)
                self.try_moves(horizontal_moves, cloned_board)
                calculated_score = self.calc_score(board,cloned_board)

                for second_rotation in range(4):
                    for second_horizontal_moves in range(lower, upper):
                        second_board = cloned_board.clone()
                        self.try_rotation(second_rotation, second_board)
                        self.try_moves(second_horizontal_moves, second_board)

                        calc_second_score = self.calc_score(cloned_board, second_board)
                        if score is None:
                            score = calc_second_score + calculated_score
                            self.best_horizontal_position = 4 - horizontal_moves
                            self.best_rotation_position = rotation
                        
                        if calc_second_score + calculated_score > score:
                            score = calc_second_score + calculated_score
                            self.best_horizontal_position = 4 - horizontal_moves
                            self.best_rotation_position = rotation
    
    def generate_moves(self, rotation, move):
        generated_moves = []
        for _ in range(rotation):
            generated_moves.append(Rotation.Anticlockwise)
        if (move < 0):
            for _ in range(abs(move)):
                generated_moves.append(Direction.Left)
        else:
            for _ in range(move):
                generated_moves.append(Direction.Right)
        generated_moves.append(Direction.Drop)

        return generated_moves

    def choose_action(self, board):
        if (self.second_move is not None and self.second_rotation is not None):
            rotation = self.second_rotation
            move = self.second_move
            self.second_move = None
            self.second_rotation = None
            return self.generate_moves(rotation, move)
        else:
            self.simulate_best_position(board)
            return self.generate_moves(self.best_rotation_position, self.best_horizontal_position)

SelectedPlayer = MyPlayer

# from board import Direction, Rotation, Action
# from random import Random
# from exceptions import NoBlockException


# class Player:
#     def choose_action(self, board):
#         raise NotImplementedError

# def __init__(self, seed=None):
#     self.random = Random(seed)

# class auto_player(Player):
#     holes_weight = -1000
#     height_weight = -4.1
#     wells_weight = -50
#     transition_weight = -500
#     line_weight = 5

#     def highest_board_cells(self, board):
#         highest = [0] * 10
#         for x in range(board.width):
#             for y in range(board.height):
#                 if (x,y) in board.cells:
#                     highest[x] = y
#                     break
#         return highest

#     def height(self, board):
#         height =10 * board.height - sum(self.highest_board_cells(board))
#         return height * self.height_weight
    
#     def hole(self, board):
#         holes = [0] * 10
#         highest = self.highest_board_cells(board)
#         for x in range(board.width):
#             for y in range(highest[x], board.height):
#                 if (x,y) not in board.cells:
#                     holes[x] += 1
#         return sum(holes)
    
#     def well(self, board):
#         wells = [0] * 9
#         for x in range(board.width-1):
#             highest = self.highest_board_cells(board)
#             if highest[x] != 23:
#                 wells[x] = abs(highest[x] -highest[x+1])
#             else:
#                 wells[x] = 0
#         return max(wells)
  
#     def row_transition(self, board):
#         transition = 0
#         for y in range(max(self.highest_board_cells(board)), board.height,):
#             for x in range(board.width - 1):
#                 if x == 0 or x == 9 and (x,y) not in board.cells:
#                     transition += 1  
#                 else:
#                     if (x,y) in board.cells and (x+1,y) not in board.cells:
#                         transition += 1
#                     elif (x,y) not in board.cells and (x+1,y) in board.cells:
#                         transition += 1
#         return transition

#     a = 4
#     b = 3
#     c = 2
#     d = 1
#     def best_elimination(self, board_clone, board):
#         score = board_clone.score - board.score
#         elimination = 0
#         if score >= 1600:
#             elimination += self.a
#         elif score >= 400:
#             elimination += self.b
#         elif score >= 100:
#             elimination += self.c
#         elif score >= 25:
#             elimination += self.d
#         return elimination * self.line_weight

#     def evaluate(self, board_clone, board):
#         evaluation = self.hole(board) * self.holes_weight + self.height(board) + self.well(board) * self.wells_weight + self.best_elimination(board_clone, board) + self.line_weight * self.row_transition(board)
#         return evaluation 

#     def try_rotate(self, best_rotate, board):
#         for _ in range(best_rotate):
#             try:
#                 board.rotate(Rotation.Anticlockwise)
#             except NoBlockException:
#                 pass
    
#     def try_move(self,best_distance, board):
#         direction = 4 - best_distance
#         if direction < 0:
#             for _ in range(abs(direction)):
#                 try:
#                     board.move(Direction.Left)
#                 except NoBlockException:
#                     pass
#         else:
#             for _ in range(direction):
#                 try:
#                     board.move(Direction.Right)
#                 except NoBlockException:
#                     pass    
#         try:
#             board.move(Direction.Drop)
#         except NoBlockException:
#             pass

#     best_move = None
#     best_rotation = None

#     def landing(self, board):
#         score = None
#         print(self.well(board))
#         # if min(self.highest_board_cells(board)) < 8:
#         #     self.height_weight = -8.2
#         #     self.a = 1
#         #     self.b = 1
#         #     self.c = 1
#         #     self.d = 1


#         # else:
#         #     self.height_weight = -4.1
#         #     self.a = 6
#         #     self.b = 5
#         #     self.c = 2
#         #     self.d = 1

#         #     self.holes_weight = -1000
#         #     self.height_weight = -4.1
#         #     self.wells_weight = -5
#         #     self.line_weight = 5

#         if self.well(board) > 5:
#             self.height_weight = -1500
#             self.wells_weight = -1500
#         else:
#             self.holes_weight = -500
#             self.height_weight = -4.1
#             self.wells_weight = -50
#             self.line_weight = 5

#         # if self.hole(board) > 5:
#         #     self.holes_weight = -1100
#         # else:
#         #     self.holes_weight = -1000
#         #     self.height_weight = -4.1
#         #     self.wells_weight = -5
#         #     self.line_weight = 5
        
#         # highest = self.highest_board_cells(board)
#         # height_6 = [height for height in highest if height > 18]
#         # height_8 = [height for height in highest if height > 16]
#         # avg = sum(highest[0:7]) / 8
#         # if avg > 20 or len(height_6) > 3 or len(height_8) > 2:
#         #     self.line_weight = 1.46
#         #     self.holes_weight = -1.2
#         #     self.height_weight = -0.8
#         #     shortest = 0
#         # else:
#         #     self.holes_weight = -1.5663
#         #     self.height_weight = -0.510066
#         #     shortest = 1
        
#         for rotation in range (4):
#             for best_distance in range (0, 10):
#                 clone_board = board.clone()
#                 self.try_rotate(rotation, clone_board)
#                 self.try_move(best_distance, clone_board)
#                 score_1 = self.evaluate(clone_board, board)
#                 for second_rotation in range (4):
#                     for second_distance in range (0, 10):
#                         second_board = clone_board.clone()
#                         self.try_rotate(second_rotation, second_board)
#                         self.try_move(second_distance, second_board)
#                         score_2 = self.evaluate(second_board, clone_board)
#                         if  score is None:
#                             score = score_1 + score_2
#                             self.best_rotation = rotation
#                             self.best_move = best_distance
#                         elif score_1 + score_2 > score:
#                             score = score_1 + score_2
#                             self.best_rotation = rotation
#                             self.best_move = best_distance
    
#     def moving(self, rotation, move):
#         movement = []
#         for _ in range (rotation):
#             movement.append(Rotation.Anticlockwise)
#         direction = 4 - move
#         if direction < 0:
#             for _ in range (abs(direction)):
#                 movement.append(Direction.Left)
#         else:
#             for _ in range (direction):
#                 movement.append(Direction.Right)
#         movement.append(Direction.Drop)
#         return movement
    
#     def choose_action(self, board):
#         self.landing(board)
#         return self.moving(self.best_rotation, self.best_move)

# SelectedPlayer = auto_player

#upwards is mine but I cannot find a proper weight of each affective factor.





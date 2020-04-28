"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple, Union, Any
from block import Block
from settings import COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    type_gen = random.randint(0, 1)  # Perimeter or Blob
    return_list = []
    copy_colour = []
    for color in COLOUR_LIST:
        copy_colour.append(color)
    if type_gen == 0:  # Perimeter
        i = 0
        while i < num_goals:
            color_gen = random.randint(0, len(copy_colour) - 1)
            return_list.append(PerimeterGoal(copy_colour[color_gen]))
            copy_colour.remove(copy_colour[color_gen])
            i += 1
        return return_list
    for i in range(num_goals):
        color_gen = random.randint(0, len(copy_colour) - 1)
        return_list.append(BlobGoal(copy_colour[color_gen]))
        copy_colour.remove(copy_colour[color_gen])
    return return_list


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    return_list = []
    unit = 2 ** (block.max_depth - block.level)
    unit_size = block.size / unit
    for i in range(unit):
        temp_list = []
        for j in range(unit):
            temp_list.append(_get_colour(block, (i, j), unit_size))
        return_list.append(temp_list)
    return return_list


def _get_colour(block: Block, position: Tuple[int, int], unit_size: int) \
        -> Tuple[int, int, int]:
    """
    Return the color of a block located at 'position' in 'block',
    represented by RGB
    """
    if len(block.children) == 0:
        return block.colour
    x_pos = position[0] * unit_size + (unit_size / 100)
    y_pos = position[1] * unit_size + (unit_size / 100)
    for child in block.children:
        child_left = child.position[0]
        child_top = child.position[1]
        child_right = child_left + child.size
        child_bott = child_top + child.size
        if child_left <= x_pos < child_right and \
                child_top <= y_pos < child_bott:
            return _get_colour(child, position, unit_size)
    return None


def _remove_nested_list(obj: Union[Tuple[int, int, int], List]) -> Any:
    """
    Return a 1D list with all elements in the nested list 'obj'
    """
    if isinstance(obj, Tuple):
        return obj
    else:
        lst = []
        for sublist in obj:
            temp = _remove_nested_list(sublist)
            if isinstance(temp, Tuple):
                lst.append(temp)
            else:
                lst.extend(temp)
        return lst


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """
    The player must aim to put the most possible units of a given colour c
    on the outer perimeter of the board. The player’s score is the total
    number of unit cells of colour c that are on the perimeter.
    There is a premium on corner cells: they count twice towards the score.
    """
    def score(self, board: Block) -> int:
        """
        Return the score this player can get from this 'board'
        if the player has perimeter goal.
        """
        target_colour = self.colour
        score = 0
        flat_list = _flatten(board)
        for j in range(len(flat_list)):
            if flat_list[0][j] == target_colour:
                if j in [0, len(flat_list) - 1]:
                    score += 2
                else:
                    score += 1
        for j in range(len(flat_list)):
            if flat_list[-1][j] == target_colour:
                if j in [0, len(flat_list) - 1]:
                    score += 2
                else:
                    score += 1
        for j in range(2):  # first and last row
            for i in range(1, len(flat_list) - 1):  # deduct corners
                if flat_list[i][-j] == target_colour:
                    score += 1
        return score

    def description(self) -> str:
        """
        Return a string describing perimeter goal.
        """
        descrip = 'The player must aim to put the most possible units of a ' \
                  'given colour c on the outer perimeter of ' \
                  'the board. The ' \
                  'player’s score is the total number of unit cells ' \
                  'of colour ' \
                  'c that are on the perimeter. There is a ' \
                  'premium on corner ' \
                  'cells: they count twice towards the score. '
        return descrip


class BlobGoal(Goal):
    """
    The player must aim for the largest “blob” of a given colour c.
     A blob is a group of connected blocks with the same colour.
     Two blocks are connected if their sides touch; touching
     corners doesn’t count. The player’s score is the number
     of unit cells in the largest blob of colour c.
    """
    def score(self, board: Block) -> int:
        """
        Return the score this player can get from this 'board'
        if the player has blob goal.
        """
        flat_board = _flatten(board)
        board_size = len(flat_board)
        # create parallel board
        visited = []
        for i in range(board_size):
            temp_list = []
            for j in range(board_size):
                temp_list.append(-1)
            visited.append(temp_list)
        score_list = []
        for i in range(board_size):
            for j in range(board_size):
                score_list.append \
                    (self._undiscovered_blob_size((i, j), flat_board, visited))
        return max(score_list)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        board_size = len(board)
        if pos[0] < 0 or pos[0] >= board_size \
                or pos[1] < 0 or pos[1] >= board_size:
            return 0
        column = pos[0]
        row = pos[1]
        if not board[column][row] == self.colour:
            visited[column][row] = 0
            return 0
        score = 1
        visited[column][row] = 1
        # upper cell
        if row - 1 >= 0:
            if visited[column][row - 1] == -1:
                score += self._undiscovered_blob_size((column, row - 1),
                                                      board, visited)
        # lower cell
        if row + 1 <= board_size - 1:
            if visited[column][row + 1] == -1:
                score += self._undiscovered_blob_size((column, row + 1),
                                                      board, visited)
        # left cell
        if column - 1 >= 0:
            if visited[column - 1][row] == -1:
                score += self._undiscovered_blob_size((column - 1, row),
                                                      board, visited)
        if column + 1 <= board_size - 1:
            if visited[column + 1][row] == -1:
                score += self._undiscovered_blob_size((column + 1, row),
                                                      board, visited)
        return score

    def description(self) -> str:
        """
        Return a string describing blob goal.
        """
        descrip = 'The player must aim for the largest “blob” of a given ' \
                  'colour c. A blob is a group of connected blocks with the ' \
                  'same colour. Two blocks are connected if their sides ' \
                  'touch; touching corners doesn’t count. The player’s score ' \
                  'is the number of unit cells in the largest blob of colour ' \
                  'c. '
        return descrip


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })

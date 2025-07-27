import pytest
import json
from snake_game.game import SnakeGame, Direction, GameState


def test_move_sequence_returns_to_start():
    """Test that a carefully crafted sequence returns snake to starting position"""
    
    # Create a sequence that makes a complete 2x2 square and returns to start
    # Start: (20, 10) facing RIGHT
    # "6": (21, 10) RIGHT
    # "8": turn UP, (21, 9) UP  
    # "4": turn LEFT, (20, 9) LEFT
    # "5": turn DOWN, (20, 10) DOWN - back to start!
    moves = "6845"
    
    game = SnakeGame(width=40, height=20, debug=False, moves=list(moves))
    
    # Record starting position
    initial_head = game.snake[0]
    initial_direction = game.direction
    
    # Run the game with automated moves
    game.run()
    
    # Get final state
    final_state = game.get_debug_state()
    final_head = final_state["snake_head"]
    
    print(f"Initial position: {initial_head}")
    print(f"Initial direction: {initial_direction}")
    print(f"Final position: {final_head}")
    print(f"Final direction: {final_state['direction']}")
    
    # Should return to starting position
    assert final_head == initial_head, f"Expected {initial_head}, got {final_head}"
    

def test_rectangular_move_sequence():
    """Test a move sequence that makes a complete rectangle and returns to start"""
    
    # Create a simple 2x2 square:
    # Start: (20, 10) facing RIGHT
    # "6": (21, 10) RIGHT 
    # "8": turn UP, (21, 9) UP
    # "4": turn LEFT, (20, 9) LEFT  
    # "5": turn DOWN, (20, 10) DOWN - back to start!
    moves = "6845"  
    
    game = SnakeGame(width=40, height=20, debug=False, moves=list(moves))
    
    # Record starting position and direction  
    initial_head = game.snake[0]
    initial_direction = game.direction
    
    # Run the game
    game.run()
    
    # Get final state
    final_state = game.get_debug_state()
    final_head = final_state["snake_head"]
    final_direction = final_state["direction"]
    
    print(f"Initial: pos={initial_head}, dir={initial_direction}")
    print(f"Final: pos={final_head}, dir={final_direction}")
    
    # Should return to starting position
    assert final_head == initial_head, f"Expected {initial_head}, got {final_head}"
    
    # Direction should be DOWN (last move was down)
    assert final_direction == "DOWN", f"Expected DOWN, got {final_direction}"
    
    # Game should still be playing (not game over)
    assert final_state["state"] == "playing", f"Game ended unexpectedly: {final_state['state']}"


def test_original_sequence_dot_dot_8_dot_dot_4_dot_dot_5():
    """Test the specific sequence "..8..4..5" and confirm it does NOT return to start"""
    
    moves = "..8..4..5"
    game = SnakeGame(width=40, height=20, debug=False, moves=list(moves))
    
    # Record starting position
    initial_head = game.snake[0]  # Should be (20, 10) 
    
    # Run the game
    game.run()
    
    # Get final state  
    final_state = game.get_debug_state()
    final_head = final_state["snake_head"]
    
    # Verify the sequence was executed completely
    assert final_state["move_index"] == len(moves), "Not all moves were executed"
    
    # The snake should be alive (not game over)
    assert final_state["state"] == "playing", "Game should still be playing"
    
    # Calculate expected final position:
    # Start: (20, 10) facing RIGHT
    # ".": (21, 10) RIGHT  
    # ".": (22, 10) RIGHT
    # "8": turn UP, (22, 9) UP
    # ".": (22, 8) UP
    # ".": (22, 7) UP  
    # "4": turn LEFT, (21, 7) LEFT
    # ".": (20, 7) LEFT
    # ".": (19, 7) LEFT
    # "5": turn DOWN, (19, 8) DOWN
    
    expected_final = (19, 8)
    
    assert final_head == expected_final, f"Expected {expected_final}, got {final_head}"
    assert final_state["direction"] == "DOWN", f"Expected DOWN, got {final_state['direction']}"
    
    # This sequence does NOT return to the starting position
    assert final_head != initial_head, f"This sequence should NOT return to start. Started at {initial_head}, ended at {final_head}"


def test_modified_sequence_that_does_return_to_start():
    """Test a modified version of "..8..4..5" that actually returns to starting position"""
    
    # The original "..8..4..5" ends at (19, 8) when starting from (20, 10)
    # To return to start, we need to add moves: from (19, 8) back to (20, 10)
    # That's: right 1, down 2 = "655"
    moves = "..8..4..5655"
    
    game = SnakeGame(width=40, height=20, debug=False, moves=list(moves))
    
    # Record starting position
    initial_head = game.snake[0]
    
    # Run the game
    game.run()
    
    # Get final state  
    final_state = game.get_debug_state()
    final_head = final_state["snake_head"]
    
    # Verify this extended sequence DOES return to start
    assert final_head == initial_head, f"Expected to return to {initial_head}, got {final_head}"
    assert final_state["state"] == "playing", "Game should still be playing"


def test_game_initialization():
    """Test that game initializes correctly"""
    game = SnakeGame()
    
    # Check initial state
    assert game.state == GameState.MENU
    assert len(game.snake) == 1
    assert game.direction == Direction.RIGHT
    assert game.score == 0
    assert game.food is not None


def test_automated_vs_manual_mode():
    """Test that automated mode behaves differently from manual mode"""
    
    # Manual mode game
    manual_game = SnakeGame()
    assert not manual_game.automated
    assert manual_game.moves == []
    
    # Automated mode game
    auto_game = SnakeGame(moves=list("rrr"))
    assert auto_game.automated
    assert len(auto_game.moves) == 3


if __name__ == "__main__":
    pytest.main([__file__])
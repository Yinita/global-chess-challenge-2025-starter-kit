#!/usr/bin/env python3
"""
Test script to check format correctness rate using OpenRouter API.
"""

import os
import re
import sys
import chess
from openai import OpenAI
from jinja2 import Template

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Test models
MODEL_NAME = "qwen/qwen3-8b"  # The model we submitted
# MODEL_NAME = "meta-llama/llama-3.1-8b-instruct"  # Stable model without thinking mode

# Test positions (FEN strings with various complexity)
TEST_POSITIONS = [
    # Starting position
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    # After 1.e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    # Italian Game
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    # Sicilian Defense
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
    # Queen's Gambit
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2",
    # Middlegame position
    "r1bq1rk1/ppp2ppp/2n2n2/3pp3/1bPP4/2N1PN2/PP2BPPP/R1BQK2R w KQ - 4 7",
    # Endgame position
    "8/5pk1/6p1/8/8/6P1/5PK1/8 w - - 0 1",
    # Tactical position (fork possible)
    "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4",
    # Complex middlegame
    "r2qkb1r/ppp2ppp/2np1n2/4p1B1/2B1P3/3P1N2/PPP2PPP/RN1QK2R b KQkq - 0 6",
    # Endgame with pawns
    "8/8/4k3/8/2K5/4P3/8/8 w - - 0 1",
]


def render_board_unicode(board: chess.Board) -> str:
    """Render the chess board using Unicode chess pieces."""
    UNICODE_PIECES = {
        'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
        'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
    }
    
    lines = []
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
    
    coord_parts = [f" {f} " for f in files]
    coord_line = "   " + "".join(coord_parts) + "  "
    lines.append(coord_line)
    border_width = len(files) * 3
    lines.append("   +" + "-" * border_width + "+")
    
    for rank in ranks:
        line_parts = [f"{rank} |"]
        for file in files:
            square = chess.parse_square(file + rank)
            piece = board.piece_at(square)
            piece_char = UNICODE_PIECES[piece.symbol()] if piece else "·"
            line_parts.append(f" {piece_char} ")
        line_parts.append(f"| {rank}")
        lines.append("".join(line_parts))
    
    lines.append("   +" + "-" * border_width + "+")
    lines.append(coord_line)
    
    return "\n".join(lines)


def load_template(template_path: str) -> Template:
    """Load Jinja2 template from file."""
    with open(template_path, 'r', encoding='utf-8') as f:
        return Template(f.read())


def build_prompt(template: Template, board: chess.Board) -> str:
    """Build prompt from template and board state."""
    legal_moves = list(board.legal_moves)
    legal_moves_uci = " ".join([m.uci() for m in legal_moves])
    first_legal_move = legal_moves[0].uci() if legal_moves else ""
    
    # Get last move description
    if board.move_stack:
        last_move = board.move_stack[-1]
        temp_board = chess.Board()
        for move in board.move_stack[:-1]:
            temp_board.push(move)
        last_move_san = temp_board.san(last_move)
        last_side = "Black" if board.turn else "White"
        last_move_desc = f"{last_side} played {last_move_san}"
    else:
        last_move_desc = "(start of game)"
    
    context = {
        "FEN": board.fen(),
        "board_utf": render_board_unicode(board),
        "side_to_move": "White" if board.turn else "Black",
        "last_move": last_move_desc,
        "legal_moves_uci": legal_moves_uci,
        "first_legal_move": first_legal_move,
    }
    
    return template.render(**context)


def parse_response(response: str, legal_moves: list) -> dict:
    """Parse the model response and check format correctness."""
    result = {
        "has_think_tag": False,
        "has_uci_move_tag": False,
        "move_extracted": None,
        "move_is_legal": False,
        "format_correct": False,
        "raw_response": response,
    }
    
    # Check for <think> tag
    think_match = re.search(r'<think>(.*?)</think>', response, re.IGNORECASE | re.DOTALL)
    result["has_think_tag"] = think_match is not None
    if think_match:
        result["think_content"] = think_match.group(1).strip()
    
    # Check for <uci_move> tag
    move_match = re.search(r'<uci_move>(.*?)</uci_move>', response, re.IGNORECASE | re.DOTALL)
    result["has_uci_move_tag"] = move_match is not None
    
    if move_match:
        move_str = move_match.group(1).strip()
        result["move_extracted"] = move_str
        
        # Check if move is legal
        try:
            move = chess.Move.from_uci(move_str)
            legal_move_objects = [chess.Move.from_uci(m) for m in legal_moves]
            result["move_is_legal"] = move in legal_move_objects
        except:
            result["move_is_legal"] = False
    
    # Format is correct if both tags present and move is legal
    result["format_correct"] = (
        result["has_think_tag"] and 
        result["has_uci_move_tag"] and 
        result["move_is_legal"]
    )
    
    return result


def test_format_correctness():
    """Test format correctness rate across multiple positions."""
    print("=" * 70)
    print(" " * 15 + "FORMAT CORRECTNESS TEST")
    print("=" * 70)
    print(f"API: OpenRouter ({OPENROUTER_BASE_URL})")
    print(f"Model: {MODEL_NAME}")
    print(f"Test positions: {len(TEST_POSITIONS)}")
    print("=" * 70)
    
    # Initialize OpenAI client for OpenRouter
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )
    
    # Load template
    template_path = os.path.join(
        os.path.dirname(__file__),
        "player_agents",
        "qwen3_8b_prompt_template.jinja"
    )
    template = load_template(template_path)
    
    results = []
    
    for i, fen in enumerate(TEST_POSITIONS):
        print(f"\n--- Test {i+1}/{len(TEST_POSITIONS)} ---")
        print(f"FEN: {fen[:50]}...")
        
        board = chess.Board(fen)
        legal_moves = [m.uci() for m in board.legal_moves]
        
        # Build prompt
        prompt = build_prompt(template, board)
        
        try:
            # Call API
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
            
            # Get content from either content or reasoning field (Qwen3 thinking mode)
            message = response.choices[0].message
            content = message.content or ""
            
            # Check if response is in reasoning field (Qwen3 thinking mode)
            reasoning = getattr(message, 'reasoning', None) or ""
            
            # Combine content and reasoning for parsing
            full_response = content if content else reasoning
            
            # Debug: print raw response
            print(f"   Content length: {len(content)}, Reasoning length: {len(reasoning)}")
            if full_response:
                print(f"   Response: {full_response[:300]}")
            else:
                print(f"   Both content and reasoning are empty!")
            
            # Parse response - use full_response which includes reasoning if content is empty
            result = parse_response(full_response, legal_moves)
            result["position_index"] = i
            result["fen"] = fen
            results.append(result)
            
            # Print result
            status = "✓" if result["format_correct"] else "✗"
            print(f"{status} Think tag: {result['has_think_tag']}, "
                  f"UCI tag: {result['has_uci_move_tag']}, "
                  f"Legal move: {result['move_is_legal']}")
            
            if result["move_extracted"]:
                print(f"   Move: {result['move_extracted']}")
            
            if not result["format_correct"]:
                print(f"   Response preview: {content[:200]}...")
                
        except Exception as e:
            print(f"✗ API Error: {e}")
            results.append({
                "position_index": i,
                "fen": fen,
                "format_correct": False,
                "error": str(e),
            })
    
    # Summary
    print("\n" + "=" * 70)
    print(" " * 20 + "SUMMARY")
    print("=" * 70)
    
    total = len(results)
    correct = sum(1 for r in results if r.get("format_correct", False))
    has_think = sum(1 for r in results if r.get("has_think_tag", False))
    has_uci = sum(1 for r in results if r.get("has_uci_move_tag", False))
    legal_moves = sum(1 for r in results if r.get("move_is_legal", False))
    
    print(f"Total tests:           {total}")
    print(f"Format correct:        {correct}/{total} ({correct/total*100:.1f}%)")
    print(f"Has <think> tag:       {has_think}/{total} ({has_think/total*100:.1f}%)")
    print(f"Has <uci_move> tag:    {has_uci}/{total} ({has_uci/total*100:.1f}%)")
    print(f"Legal move selected:   {legal_moves}/{total} ({legal_moves/total*100:.1f}%)")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    test_format_correctness()

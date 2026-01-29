import json
import re

with open('reports/hikaru_opening_tree_d3.html', 'r', encoding='utf-8') as f:
    content = f.read()
    # Find the treeDataJSON variable
    start = content.find('const treeDataJSON = `')
    if start >= 0:
        start += len('const treeDataJSON = `')
        end = content.find('`;', start)
        json_str = content[start:end]
        data = json.loads(json_str)
        
        print("=== TREE STRUCTURE ANALYSIS ===\n")
        print(f"Root: {data['tree']['move']}")
        print(f"Root games: {data['tree']['games']}")
        print(f"Root has children: {len(data['tree']['children'])} moves\n")
        
        print("First level moves:")
        for i, child in enumerate(data['tree']['children'][:5]):
            print(f"  {i+1}. {child['move']}: {child['games']} games, {child['wins']} wins")
        
        if len(data['tree']['children']) > 5:
            print(f"  ... and {len(data['tree']['children']) - 5} more moves")
        
        print(f"\nTree stats from metadata:")
        print(f"  Total positions: {data.get('positions', '?')}")
        print(f"  Total games: {data.get('games', '?')}")
        print(f"  Max depth: {data.get('depth', '?')}")
        print(f"  Opponent: {data.get('opponent', '?')}")
        print(f"  Color filter: {data.get('color_filter', '?')}")
        
        # Check a deeper branch
        if data['tree']['children']:
            first_move = data['tree']['children'][0]
            print(f"\nSecond level moves (after {first_move['move']}):")
            for j, grandchild in enumerate(first_move.get('children', [])[:3]):
                print(f"  {j+1}. {grandchild['move']}: {grandchild['games']} games")

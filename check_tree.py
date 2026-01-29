import json

with open('reports/hikaru_opening_tree_d3.html', 'r', encoding='utf-8') as f:
    content = f.read()
    # Find the treeDataJSON variable
    start = content.find('const treeDataJSON = `')
    if start >= 0:
        start += len('const treeDataJSON = `')
        end = content.find('`;', start)
        json_str = content[start:end]
        data = json.loads(json_str)
        print('Tree root keys:', list(data.keys()))
        print('Tree root children type:', type(data['tree'].get('children')))
        if 'children' in data['tree']:
            children = data['tree']['children']
            if isinstance(children, list):
                print('Children is a LIST with', len(children), 'items')
                if children:
                    print('First child move:', children[0].get('move'))
            elif isinstance(children, dict):
                print('Children is a DICT with', len(children), 'items')
                print('First child moves:', list(children.keys())[:3])

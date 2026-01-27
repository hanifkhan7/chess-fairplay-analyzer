"""
D3.js Interactive Opening Tree Visualization

Generates beautiful, interactive HTML visualizations of opening move trees.
"""

import json
import html as html_module
from typing import Dict, Any, Optional
import os

from .move_tree_builder import MoveNode


class D3TreeVisualizer:
    """Generate D3.js interactive tree visualizations"""
    
    def __init__(self, tree_dict: Dict[str, Any]):
        """Initialize with tree dictionary."""
        self.tree = tree_dict
        self.opponent = tree_dict.get('opponent', 'Opponent')
        self.color_filter = tree_dict.get('color_filter', 'both')
        self.depth = tree_dict.get('depth', 0)
        self.positions = tree_dict.get('positions', 0)
        self.games = tree_dict.get('games', 0)
    
    def generate_html(self, filepath: str, title: Optional[str] = None):
        """Generate and save interactive D3.js HTML."""
        if title is None:
            title = f"Opening Tree vs {self.opponent.title()}"
        
        html_content = self._build_html(title)
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _build_html(self, title: str) -> str:
        """Build complete HTML document"""
        tree_json = json.dumps(self.tree['tree'], indent=2)
        title_escaped = html_module.escape(title)
        
        # HTML structure - use raw strings where needed
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + title_escaped + '''</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; font-weight: 600; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
            padding: 0 20px;
        }
        .stat-box {
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 2em; font-weight: bold; color: white; }
        .stat-label { font-size: 0.9em; opacity: 0.8; margin-top: 5px; }
        .content { padding: 30px; }
        .controls {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .controls button {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.95em;
            transition: background 0.3s;
        }
        .controls button:hover { background: #764ba2; }
        #tree { margin-top: 20px; min-height: 400px; }
        .node { cursor: pointer; }
        .node circle { fill: #667eea; stroke: white; stroke-width: 2px; }
        .node.win circle { fill: #10b981; }
        .node.loss circle { fill: #ef4444; }
        .node.draw circle { fill: #f59e0b; }
        .node circle:hover { stroke-width: 3px; filter: brightness(1.1); }
        .node text { font: 11px sans-serif; pointer-events: none; }
        .link { fill: none; stroke: #999; stroke-opacity: 0.3; stroke-width: 1.5px; }
        .tooltip {
            position: absolute;
            padding: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            border-radius: 5px;
            font-size: 13px;
            pointer-events: none;
            z-index: 1000;
            max-width: 300px;
            display: none;
        }
        .legend {
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        .legend h3 { margin-bottom: 15px; color: #333; }
        .legend-item { display: inline-block; margin-right: 30px; margin-bottom: 10px; }
        .legend-circle {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
        }
        .info {
            background: #e0f2fe;
            padding: 15px;
            border-left: 4px solid #0284c7;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 0.95em;
            color: #0c4a6e;
        }
        .warning {
            padding: 20px;
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 5px;
            margin-top: 20px;
            color: #92400e;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Opening Tree Analysis</h1>
            <p>''' + title_escaped + '''</p>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value">''' + str(self.games) + '''</div>
                    <div class="stat-label">Games Analyzed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">''' + str(self.positions) + '''</div>
                    <div class="stat-label">Unique Positions</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">''' + str(self.depth) + '''</div>
                    <div class="stat-label">Tree Depth</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">''' + self.color_filter.upper() + '''</div>
                    <div class="stat-label">Perspective</div>
                </div>
            </div>
        </div>
        <div class="content">
            <div class="controls">
                <button onclick="resetZoom()">Reset Zoom</button>
                <button onclick="expandAll()">Expand All</button>
                <button onclick="collapseAll()">Collapse All</button>
            </div>
            <div id="tree"></div>
            <div class="legend">
                <h3>Legend</h3>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #10b981;"></div>
                    <span>Winning (>55% W)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #ef4444;"></div>
                    <span>Losing (<45% W)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #f59e0b;"></div>
                    <span>Draw-Heavy</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #667eea;"></div>
                    <span>Neutral</span>
                </div>
            </div>
            <div class="info">
                Click nodes to expand/collapse. Hover for statistics. Larger nodes = more games.
            </div>
        </div>
    </div>
    <div class="tooltip" id="tooltip"></div>
    <script>
'''
        
        # JavaScript code - safer to concatenate
        js = f'''
        const treeData = {tree_json};
        const margin = {{top: 20, right: 120, bottom: 20, left: 120}};
        const width = Math.max(600, document.getElementById("tree").parentElement.offsetWidth - margin.left - margin.right);
        const height = Math.max(800, treeData.tree.games * 3);
        
        const svg = d3.select("#tree")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .style("border", "1px solid #eee")
            .style("border-radius", "8px");
        
        const g = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        
        const tree = d3.tree().size([width, height]);
        const root = d3.hierarchy(treeData.tree);
        
        if (!root.children || root.children.length === 0) {{
            document.getElementById("tree").innerHTML = '<div class="warning"><strong>No tree data</strong><br/>Try analyzing with different filters or analyzing more games.</div>';
            throw new Error("Empty tree");
        }}
        
        tree(root);
        
        const links = root.links();
        g.selectAll(".link")
            .data(links)
            .enter()
            .append("path")
            .attr("class", "link")
            .attr("d", d3.linkVertical()
                .x(d => d.x)
                .y(d => d.y));
        
        const nodes = root.descendants();
        const nodeSelection = g.selectAll(".node")
            .data(nodes, (d, i) => i)
            .enter()
            .append("g")
            .attr("class", d => {{
                const wr = d.data.win_rate || 50;
                if (wr > 55) return "node win";
                if (wr < 45) return "node loss";
                if ((d.data.draw_rate || 0) > 40) return "node draw";
                return "node";
            }})
            .attr("transform", d => "translate(" + d.x + "," + d.y + ")")
            .on("click", (event, d) => {{
                d.children = d.children ? null : d._children;
                update();
            }})
            .on("mouseover", (event, d) => {{
                const tooltip = document.getElementById("tooltip");
                const games = d.data.games || 0;
                const wins = d.data.wins || 0;
                const draws = d.data.draws || 0;
                const losses = d.data.losses || 0;
                const wr = d.data.win_rate || 0;
                
                let html = "<strong>" + d.data.move + "</strong><br/>";
                if (d.data.opening) {{
                    html += "<small>" + d.data.opening + "</small><br/>";
                }}
                html += "Games: " + games + "<br/>";
                html += "Record: " + wins + "-" + draws + "-" + losses + "<br/>";
                html += "Win Rate: " + wr.toFixed(1) + "%";
                
                tooltip.innerHTML = html;
                tooltip.style.display = "block";
                tooltip.style.left = (event.pageX + 10) + "px";
                tooltip.style.top = (event.pageY + 10) + "px";
            }})
            .on("mousemove", (event) => {{
                document.getElementById("tooltip").style.left = (event.pageX + 10) + "px";
                document.getElementById("tooltip").style.top = (event.pageY + 10) + "px";
            }})
            .on("mouseout", () => {{
                document.getElementById("tooltip").style.display = "none";
            }});
        
        nodeSelection.append("circle")
            .attr("r", d => {{
                const games = d.data.games || 1;
                return Math.max(3, Math.min(15, Math.sqrt(games) * 2));
            }});
        
        nodeSelection.append("text")
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .text(d => d.data.move)
            .style("font-size", "10px")
            .style("font-weight", "bold")
            .style("fill", "white");
        
        root.children.forEach(d => {{ d._children = d.children; }});
        
        function update() {{
            tree(root);
            g.selectAll(".link").remove();
            g.selectAll(".link")
                .data(root.links())
                .enter()
                .append("path")
                .attr("class", "link")
                .attr("d", d3.linkVertical()
                    .x(d => d.x)
                    .y(d => d.y));
            
            g.selectAll(".node").remove();
            const nodes = root.descendants();
            const nodeSelection = g.selectAll(".node")
                .data(nodes, d => d.data.move)
                .enter()
                .append("g")
                .attr("class", d => {{
                    const wr = d.data.win_rate || 50;
                    if (wr > 55) return "node win";
                    if (wr < 45) return "node loss";
                    if ((d.data.draw_rate || 0) > 40) return "node draw";
                    return "node";
                }})
                .attr("transform", d => "translate(" + d.x + "," + d.y + ")")
                .on("click", (event, d) => {{
                    d.children = d.children ? null : d._children;
                    update();
                }})
                .on("mouseover", (event, d) => {{
                    const tooltip = document.getElementById("tooltip");
                    const games = d.data.games || 0;
                    const wins = d.data.wins || 0;
                    const draws = d.data.draws || 0;
                    const losses = d.data.losses || 0;
                    const wr = d.data.win_rate || 0;
                    
                    let html = "<strong>" + d.data.move + "</strong><br/>";
                    if (d.data.opening) {{
                        html += "<small>" + d.data.opening + "</small><br/>";
                    }}
                    html += "Games: " + games + "<br/>";
                    html += "Record: " + wins + "-" + draws + "-" + losses + "<br/>";
                    html += "Win Rate: " + wr.toFixed(1) + "%";
                    
                    tooltip.innerHTML = html;
                    tooltip.style.display = "block";
                }}
                .on("mousemove", (event) => {{
                    document.getElementById("tooltip").style.left = (event.pageX + 10) + "px";
                    document.getElementById("tooltip").style.top = (event.pageY + 10) + "px";
                }})
                .on("mouseout", () => {{
                    document.getElementById("tooltip").style.display = "none";
                }});
            
            nodeSelection.append("circle")
                .attr("r", d => {{
                    const games = d.data.games || 1;
                    return Math.max(3, Math.min(15, Math.sqrt(games) * 2));
                }});
            
            nodeSelection.append("text")
                .attr("dy", ".35em")
                .attr("text-anchor", "middle")
                .text(d => d.data.move)
                .style("font-size", "10px")
                .style("font-weight", "bold")
                .style("fill", "white");
        }}
        
        function resetZoom() {{
            svg.transition().duration(750)
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        }}
        
        function expandAll() {{
            root.descendants().forEach(d => {{ d.children = d._children; }});
            update();
        }}
        
        function collapseAll() {{
            root.descendants().forEach(d => {{ if (d !== root) d.children = null; }});
            update();
        }}
    </script>
</body>
</html>
'''
        
        return html + js


if __name__ == "__main__":
    test_tree = {
        'opponent': 'Test',
        'color_filter': 'both',
        'depth': 2,
        'positions': 3,
        'games': 5,
        'tree': {
            'move': 'START',
            'games': 5,
            'wins': 3,
            'draws': 1,
            'losses': 1,
            'win_rate': 60.0,
            'eco': None,
            'opening': None,
            'children': {
                'e4': {
                    'move': 'e4',
                    'games': 5,
                    'wins': 3,
                    'draws': 1,
                    'losses': 1,
                    'win_rate': 60.0,
                    'eco': 'C45',
                    'opening': 'Scotch',
                    'children': {}
                }
            }
        }
    }
    viz = D3TreeVisualizer(test_tree)
    print("D3TreeVisualizer works!")

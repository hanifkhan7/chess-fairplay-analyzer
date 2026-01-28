"""D3.js Tree Visualization for Opening Repertoires"""
import json
from typing import Dict, Any


class D3TreeVisualizer:
    """Generates interactive D3.js tree visualization from move tree data."""
    
    def __init__(self, tree_data: Dict[str, Any]):
        """Initialize visualizer with tree data.
        
        Args:
            tree_data: Dictionary with 'tree' key containing root node dict
        """
        self.tree_data = tree_data
    
    def generate_html(self, output_file: str, title: str = "Opening Repertoire Tree") -> None:
        """Generate complete HTML with D3.js visualization and save to file.
        
        Args:
            output_file: Path where HTML file should be saved
            title: Title for the visualization
        """
        # Serialize tree to JSON
        tree_json = json.dumps(self.tree_data, indent=2)
        
        # Build HTML with embedded JavaScript
        html = self._build_html(tree_json, title)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _build_html(self, tree_json: str, title: str) -> str:
        """Build HTML document with D3.js visualization."""
        
        html_header = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + title + '''</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1400px;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 20px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            border-left: 4px solid #0066cc;
        }
        
        .stat-item {
            padding: 10px;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #0066cc;
        }
        
        .highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .highlight h2 {
            margin: 0 0 10px 0;
            font-size: 28px;
        }
        
        .highlight p {
            margin: 0;
            font-size: 14px;
            opacity: 0.9;
        }
        
        .controls {
            margin: 20px 0;
            padding: 15px;
            background: #f0f8ff;
            border-radius: 5px;
            border-left: 4px solid #00aa00;
        }
        
        .control-button {
            padding: 8px 15px;
            margin: 5px 5px 5px 0;
            background: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .control-button:hover {
            background: #0052a3;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .control-button:active {
            transform: translateY(1px);
        }
        
        #tree-container {
            margin: 30px 0;
            padding: 20px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            min-height: 500px;
            position: relative;
            overflow: auto;
        }
        
        svg {
            width: 100%;
            height: 100%;
            min-height: 500px;
        }
        
        .node {
            cursor: pointer;
        }
        
        .node circle {
            fill: #4CAF50;
            stroke: #2E7D32;
            stroke-width: 2px;
            transition: all 0.3s ease;
            filter: drop-shadow(0 2px 3px rgba(0,0,0,0.2));
        }
        
        .node circle:hover {
            fill: #45a049;
            r: 8;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
        }
        
        .node text {
            font-size: 12px;
            font-weight: 600;
            fill: white;
            text-anchor: middle;
            pointer-events: none;
            user-select: none;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }
        
        .node.high-winrate circle {
            fill: #2ecc71;
        }
        
        .node.med-winrate circle {
            fill: #f39c12;
        }
        
        .node.low-winrate circle {
            fill: #e74c3c;
        }
        
        .link {
            fill: none;
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1.5px;
        }
        
        .tooltip {
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 300px;
        }
        
        .warning {
            padding: 15px;
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            color: #856404;
            margin: 20px 0;
        }
        
        .debug-info {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #333;
            margin-top: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>''' + title + '''</h1>
        
        <div class="stats" id="stats-container">
            <div class="stat-item">
                <div class="stat-label">Games Analyzed</div>
                <div class="stat-value" id="stat-games">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Opponent</div>
                <div class="stat-value" id="stat-opponent">-</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Color</div>
                <div class="stat-value" id="stat-color">-</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Unique Positions</div>
                <div class="stat-value" id="stat-positions">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Tree Depth</div>
                <div class="stat-value" id="stat-depth">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Opening Moves</div>
                <div class="stat-value" id="stat-moves">0</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="control-button" onclick="resetZoom()">Reset Zoom</button>
            <button class="control-button" onclick="expandAll()">Expand All</button>
            <button class="control-button" onclick="collapseAll()">Collapse All</button>
        </div>
        
        <div id="tree-container"></div>
        
        <div class="debug-info" id="debug-output"></div>
    </div>
    
    <script>
        // Tree data embedded from Python
        const treeDataJSON = `'''
        
        html_data = tree_json
        
        html_script = '''`;
        const treeData = JSON.parse(treeDataJSON);
        
        console.log("=== D3 TREE VISUALIZATION DEBUG ===");
        console.log("Tree Data Loaded:", treeData);
        console.log("Tree Structure:", treeData.tree);
        
        let debugLog = [];
        function addDebug(msg) {
            debugLog.push(new Date().toLocaleTimeString() + ": " + msg);
            console.log("[DEBUG]", msg);
            const debugDiv = document.getElementById("debug-output");
            if (debugDiv) {
                debugDiv.textContent = debugLog.join("\\n");
                debugDiv.scrollTop = debugDiv.scrollHeight;
            }
        }
        
        addDebug("Initializing tree visualization...");
        addDebug("Tree data keys: " + Object.keys(treeData).join(", "));
        
        // Update stats first
        if (treeData.games !== undefined) {
            document.getElementById("stat-games").textContent = treeData.games || 0;
        }
        if (treeData.opponent) {
            document.getElementById("stat-opponent").textContent = treeData.opponent;
        }
        if (treeData.color_filter) {
            const colorMap = {"white": "White", "black": "Black", "both": "Both Colors"};
            document.getElementById("stat-color").textContent = colorMap[treeData.color_filter] || treeData.color_filter;
        }
        if (treeData.positions !== undefined) {
            document.getElementById("stat-positions").textContent = treeData.positions || 0;
        }
        if (treeData.depth !== undefined) {
            document.getElementById("stat-depth").textContent = treeData.depth || 0;
        }
        if (treeData.tree && treeData.tree.children) {
            document.getElementById("stat-moves").textContent = treeData.tree.children.length || 0;
        }
        
        addDebug("Stats updated from data");
        
        // Check if tree has data
        if (!treeData.tree || !treeData.tree.children || treeData.tree.children.length === 0) {
            addDebug("WARNING: No children found in tree!");
            document.getElementById("tree-container").innerHTML = 
                '<div class="warning">No opening moves found in selected games. The tree is empty.</div>';
        } else {
            addDebug("Tree root: move=" + treeData.tree.move + ", children=" + treeData.tree.children.length);
            
            // Create hierarchy
            addDebug("Creating D3 hierarchy...");
            const root = d3.hierarchy(treeData.tree);
            addDebug("Root node created. Has children: " + (root.children && root.children.length > 0 ? "YES (" + root.children.length + ")" : "NO"));
            
            if (!root.children || root.children.length === 0) {
                addDebug("WARNING: d3.hierarchy created but no children!");
                document.getElementById("tree-container").innerHTML = 
                    '<div class="warning">Tree data exists but hierarchy creation failed.</div>';
            } else {
                // Setup layout
                addDebug("Setting up tree layout...");
                const width = 1400;
                const height = 800;
                
                const tree = d3.tree().size([width, height]);
                tree(root);
                
                addDebug("Tree layout applied. Total nodes: " + root.descendants().length);
                addDebug("Descendants: " + root.descendants().map(d => d.data.move).join(", "));
                
                // Create SVG
                const svg = d3.select("#tree-container")
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);
                
                // Add zoom
                const g = svg.append("g");
                const zoom = d3.zoom()
                    .on("zoom", (event) => {
                        g.attr("transform", event.transform);
                    });
                svg.call(zoom);
                
                addDebug("SVG created and zoom enabled");
                
                // Draw links
                addDebug("Drawing links...");
                g.selectAll(".link")
                    .data(root.links())
                    .enter()
                    .append("line")
                    .attr("class", "link")
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                addDebug("Links drawn: " + root.links().length);
                
                // Draw nodes
                addDebug("Drawing nodes...");
                const nodes = g.selectAll(".node")
                    .data(root.descendants())
                    .enter()
                    .append("g")
                    .attr("class", "node")
                    .attr("transform", d => `translate(${d.x},${d.y})`);
                
                addDebug("Node groups created: " + root.descendants().length);
                
                // Add circles to nodes
                nodes.append("circle")
                    .attr("r", d => Math.max(4, Math.min(5 + Math.log(Math.max(1, d.data.games)) * 1.5, 18)))
                    .attr("class", d => {
                        const winRate = d.data.win_rate || 0;
                        if (winRate >= 60) return "high-winrate";
                        if (winRate >= 40) return "med-winrate";
                        return "low-winrate";
                    })
                    .on("click", function(event, d) {
                        toggleChildren(d);
                        update();
                    })
                    .append("title")
                    .text(d => {
                        const move = d.data.move || "Root";
                        const games = d.data.games || 0;
                        const wins = d.data.wins || 0;
                        const draws = d.data.draws || 0;
                        const losses = d.data.losses || 0;
                        const winRate = d.data.win_rate || 0;
                        const opening = d.data.opening ? ` (${d.data.opening})` : "";
                        return `Move: ${move}${opening}\nGames: ${games}\nWins: ${wins} | Draws: ${draws} | Losses: ${losses}\nWin Rate: ${winRate.toFixed(1)}%`;
                    });
                
                addDebug("Circle elements created with win-rate coloring");
                
                // Add labels
                nodes.append("text")
                    .attr("dy", 4)
                    .attr("text-anchor", "middle")
                    .text(d => d.data.move || "Root");
                
                addDebug("Text labels created");
                addDebug("Tree visualization complete!");
            }
        }
        
        function toggleChildren(d) {
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
        }
        
        function expandAll() {
            addDebug("Expanding all nodes...");
        }
        
        function collapseAll() {
            addDebug("Collapsing all nodes...");
        }
        
        function resetZoom() {
            addDebug("Resetting zoom...");
        }
    </script>
</body>
</html>'''
        
        return html_header + html_data + html_script

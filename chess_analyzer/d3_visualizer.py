"""D3.js Tree Visualization for Opening Repertoires"""
import json
from typing import Dict, Any


class D3TreeVisualizer:
    """Generates interactive D3.js tree visualization from move tree data."""
    
    def __init__(self, tree_data: Dict[str, Any], title: str = "Opening Repertoire Tree"):
        """Initialize visualizer with tree data.
        
        Args:
            tree_data: Dictionary with 'tree' key containing root node dict
            title: Title for the visualization
        """
        self.tree_data = tree_data
        self.title = title
    
    def generate_html(self) -> str:
        """Generate complete HTML with D3.js visualization.
        
        Returns:
            HTML string ready to save to file
        """
        # Serialize tree to JSON
        tree_json = json.dumps(self.tree_data, indent=2)
        
        # Build HTML with embedded JavaScript
        html = self._build_html(tree_json)
        return html
    
    def _build_html(self, tree_json: str) -> str:
        """Build HTML document with D3.js visualization."""
        
        html_header = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + self.title + '''</title>
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
            fill: #0066cc;
            stroke: #003d7a;
            stroke-width: 2px;
            transition: all 0.2s;
        }
        
        .node circle:hover {
            fill: #0052a3;
            r: 7;
        }
        
        .node text {
            font-size: 11px;
            font-weight: 500;
            fill: #333;
            text-anchor: middle;
            pointer-events: none;
            user-select: none;
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
        <h1>''' + self.title + '''</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">Total Moves</div>
                <div class="stat-value" id="stat-moves">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Max Depth</div>
                <div class="stat-value" id="stat-depth">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Unique Positions</div>
                <div class="stat-value" id="stat-positions">0</div>
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
        
        // Check tree data
        if (!treeData || !treeData.tree) {
            addDebug("ERROR: Tree data is missing!");
            document.getElementById("tree-container").innerHTML = 
                '<div class="warning">ERROR: No tree data found in HTML</div>';
        } else {
            addDebug("Tree root: " + JSON.stringify(treeData.tree, null, 2).substring(0, 200));
            
            // Update stats
            if (treeData.stats) {
                document.getElementById("stat-moves").textContent = treeData.stats.total_moves || 0;
                document.getElementById("stat-depth").textContent = treeData.stats.max_depth || 0;
                document.getElementById("stat-positions").textContent = treeData.stats.unique_positions || 0;
                addDebug("Stats: " + JSON.stringify(treeData.stats));
            }
            
            // Create hierarchy
            addDebug("Creating D3 hierarchy...");
            const root = d3.hierarchy(treeData.tree);
            addDebug("Root node created. Has children: " + (root.children && root.children.length > 0 ? "YES (" + root.children.length + ")" : "NO"));
            
            if (!root.children || root.children.length === 0) {
                addDebug("WARNING: No children found in hierarchy!");
                document.getElementById("tree-container").innerHTML = 
                    '<div class="warning">No opening moves found in selected games. The tree is empty.</div>';
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
                    .attr("r", d => Math.min(5 + Math.log(d.data.games || 1) * 2, 15))
                    .on("click", function(event, d) {
                        toggleChildren(d);
                        update();
                    })
                    .on("mouseover", function(event, d) {
                        const tooltip = `Move: ${d.data.move || "Root"}
Games: ${d.data.games || 0}
Wins: ${d.data.wins || 0}
Draws: ${d.data.draws || 0}
Losses: ${d.data.losses || 0}`;
                        d3.select(this)
                            .transition()
                            .duration(200)
                            .attr("r", d => Math.min(7 + Math.log(d.data.games || 1) * 2, 18));
                    })
                    .on("mouseout", function(event, d) {
                        d3.select(this)
                            .transition()
                            .duration(200)
                            .attr("r", d => Math.min(5 + Math.log(d.data.games || 1) * 2, 15));
                    });
                
                addDebug("Circle elements created");
                
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
            // Implementation for expand all
        }
        
        function collapseAll() {
            addDebug("Collapsing all nodes...");
            // Implementation for collapse all
        }
        
        function resetZoom() {
            addDebug("Resetting zoom...");
            // Implementation for reset zoom
        }
    </script>
</body>
</html>'''
        
        return html_header + html_data + html_script

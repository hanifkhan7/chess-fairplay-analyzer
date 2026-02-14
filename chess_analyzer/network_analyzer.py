"""
Network Analysis for Suspicious Patterns & Collusion Detection.

Detects:
- Unusually dense player clusters
- Pattern similarity networks (shared opening preparation)
- Cross-game correlations (one player's performance aligns with another)
- Colluding player networks
"""

import statistics
import math
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PlayerNode:
    """Single player in the network graph."""
    username: str
    rating: float
    sample_games: int
    avg_accuracy: float
    avg_cpl: float
    opening_repertoire: Set[str] = field(default_factory=set)

@dataclass
class NetworkEdge:
    """Connection between two players."""
    player1: str
    player2: str
    connection_strength: float  # 0-1.0
    mutual_games: int
    pattern_similarity: float  # How similar are their performances?
    opening_overlap: float  # Proportion of shared openings
    correlation_coefficient: float  # Statistical correlation of performance
    suspected_collaboration: bool = False

@dataclass
class NetworkCluster:
    """Group of densely connected players."""
    cluster_id: int
    players: List[str]
    size: int
    density: float  # Proportion of possible edges that exist
    avg_suspicion: float
    central_player: str  # Most connected player
    description: str

@dataclass
class NetworkAnalysis:
    """Complete network analysis results."""
    analysis_date: str
    total_players: int
    total_edges: int
    network_density: float  # Overall network density (0-1.0)
    nodes: Dict[str, PlayerNode] = field(default_factory=dict)
    edges: List[NetworkEdge] = field(default_factory=list)
    suspicious_edges: List[NetworkEdge] = field(default_factory=list)
    clusters: List[NetworkCluster] = field(default_factory=list)
    
    # Summary metrics
    colluding_pairs_found: int = 0
    suspicious_triplets: int = 0
    isolated_players: List[str] = field(default_factory=list)
    network_anomalies: List[str] = field(default_factory=list)
    
    def get_player_connections(self, username: str) -> List[str]:
        """Get all players this player is connected to."""
        connected = []
        for edge in self.edges:
            if edge.player1 == username:
                connected.append(edge.player2)
            elif edge.player2 == username:
                connected.append(edge.player1)
        return connected

class NetworkAnalyzer:
    """Analyze player networks for suspicious patterns."""
    
    @staticmethod
    def build_network(player_games: Dict[str, List[Dict[str, Any]]],
                      opponent_cutoff: int = 3) -> NetworkAnalysis:
        """
        Build player interaction network.
        
        Args:
            player_games: Dict mapping player username -> list of their games
            opponent_cutoff: Minimum games against someone to create edge
            
        Returns:
            NetworkAnalysis with full graph structure
        """
        from datetime import datetime
        
        # Create nodes
        nodes = {}
        for username, games in player_games.items():
            if games:
                ratings = [g.get('rating', 1500) for g in games]
                accuracies = [g.get('accuracy', 50) for g in games if 'accuracy' in g]
                cpls = [g.get('cpl', 50) for g in games if 'cpl' in g]
                openings = set(g.get('opening', 'Unknown') for g in games)
                
                nodes[username] = PlayerNode(
                    username=username,
                    rating=statistics.mean(ratings) if ratings else 1500,
                    sample_games=len(games),
                    avg_accuracy=statistics.mean(accuracies) if accuracies else 50,
                    avg_cpl=statistics.mean(cpls) if cpls else 50,
                    opening_repertoire=openings
                )
        
        # Create edges (opponent connections)
        edges = []
        opponent_map = defaultdict(lambda: defaultdict(int))  # player -> opponent -> game_count
        
        # Build opponent map from games
        for username, games in player_games.items():
            for game in games:
                if 'opponent' in game:
                    opponent = game['opponent']
                    opponent_map[username][opponent] += 1
        
        # Create edges for significant connections
        seen_pairs = set()
        for player1, opponents in opponent_map.items():
            for player2, game_count in opponents.items():
                if game_count >= opponent_cutoff:
                    # Avoid duplicates
                    pair = tuple(sorted([player1, player2]))
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        
                        # Calculate metrics
                        pattern_sim = NetworkAnalyzer._calculate_pattern_similarity(
                            player_games.get(player1, []),
                            player_games.get(player2, [])
                        )
                        
                        opening_overlap = NetworkAnalyzer._calculate_opening_overlap(
                            nodes.get(player1, PlayerNode('', 0, 0, 0, 0)).opening_repertoire,
                            nodes.get(player2, PlayerNode('', 0, 0, 0, 0)).opening_repertoire
                        )
                        
                        correlation = NetworkAnalyzer._calculate_performance_correlation(
                            player_games.get(player1, []),
                            player_games.get(player2, [])
                        )
                        
                        edge = NetworkEdge(
                            player1=player1,
                            player2=player2,
                            connection_strength=game_count / 50,  # Normalize to ~1.0
                            mutual_games=game_count,
                            pattern_similarity=pattern_sim,
                            opening_overlap=opening_overlap,
                            correlation_coefficient=correlation,
                            suspected_collaboration=pattern_sim > 0.8 and opening_overlap > 0.6
                        )
                        edges.append(edge)
        
        # Identify suspicious edges
        suspicious_edges = [e for e in edges if e.suspected_collaboration or e.correlation_coefficient > 0.85]
        
        # Detect clusters
        clusters = NetworkAnalyzer._detect_clusters(nodes, edges)
        
        # Calculate network density
        max_edges = len(nodes) * (len(nodes) - 1) / 2 if len(nodes) > 1 else 1
        network_density = len(edges) / max_edges if max_edges > 0 else 0
        
        # Find isolated players
        connected_players = set()
        for edge in edges:
            connected_players.add(edge.player1)
            connected_players.add(edge.player2)
        isolated = [p for p in nodes.keys() if p not in connected_players]
        
        # Detect anomalies
        anomalies = []
        if len(suspicious_edges) > len(nodes) * 0.2:
            anomalies.append(f"High rate of suspicious correlations ({len(suspicious_edges)} edges)")
        if network_density > 0.4:
            anomalies.append(f"Unusually dense network (density={network_density:.2f})")
        
        # Count triplets
        suspicious_triplets = NetworkAnalyzer._count_suspicious_triplets(suspicious_edges)
        
        analysis = NetworkAnalysis(
            analysis_date=datetime.now().isoformat(),
            total_players=len(nodes),
            total_edges=len(edges),
            network_density=network_density,
            nodes=nodes,
            edges=edges,
            suspicious_edges=suspicious_edges,
            clusters=clusters,
            colluding_pairs_found=len(suspicious_edges),
            suspicious_triplets=suspicious_triplets,
            isolated_players=isolated,
            network_anomalies=anomalies
        )
        
        return analysis
    
    @staticmethod
    def _calculate_pattern_similarity(games1: List[Dict[str, Any]],
                                      games2: List[Dict[str, Any]]) -> float:
        """
        Calculate similarity of play patterns between two players.
        
        High similarity in move choices, openings, and play style.
        """
        if not games1 or not games2:
            return 0.0
        
        # Extract common features
        openings1 = [g.get('opening', '') for g in games1]
        openings2 = [g.get('opening', '') for g in games2]
        
        # Opening overlap
        common_openings = len(set(openings1) & set(openings2))
        total_unique = len(set(openings1) | set(openings2))
        opening_similarity = common_openings / total_unique if total_unique > 0 else 0
        
        # Play style similarity (from accuracy/cpl patterns)
        accs1 = [g.get('accuracy', 50) for g in games1 if 'accuracy' in g]
        accs2 = [g.get('accuracy', 50) for g in games2 if 'accuracy' in g]
        
        if accs1 and accs2:
            mean1 = statistics.mean(accs1)
            mean2 = statistics.mean(accs2)
            style_similarity = 1 - (abs(mean1 - mean2) / 100)  # Normalize difference
        else:
            style_similarity = 0
        
        # Weighted combination
        similarity = opening_similarity * 0.6 + max(0, style_similarity) * 0.4
        return min(1.0, max(0.0, similarity))
    
    @staticmethod
    def _calculate_opening_overlap(rep1: Set[str], rep2: Set[str]) -> float:
        """Calculate proportion of shared openings."""
        if not rep1 or not rep2:
            return 0.0
        
        union = len(rep1 | rep2)
        intersection = len(rep1 & rep2)
        
        # Jaccard similarity
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def _calculate_performance_correlation(games1: List[Dict[str, Any]],
                                           games2: List[Dict[str, Any]]) -> float:
        """
        Calculate correlation of performance metrics.
        
        If players' accuracies/results correlate highly -> suspicious.
        """
        # Extract dates and accuracies
        data1 = {}  # date -> accuracy
        data2 = {}
        
        for game in games1:
            if 'timestamp' in game and 'accuracy' in game:
                try:
                    date = game['timestamp'][:10]  # YYYY-MM-DD
                    if date not in data1:
                        data1[date] = []
                    data1[date].append(game['accuracy'])
                except:
                    pass
        
        for game in games2:
            if 'timestamp' in game and 'accuracy' in game:
                try:
                    date = game['timestamp'][:10]
                    if date not in data2:
                        data2[date] = []
                    data2[date].append(game['accuracy'])
                except:
                    pass
        
        # Find common dates
        common_dates = set(data1.keys()) & set(data2.keys())
        if len(common_dates) < 3:
            return 0.0
        
        # Calculate daily averages
        avg1 = [statistics.mean(data1[d]) for d in common_dates]
        avg2 = [statistics.mean(data2[d]) for d in common_dates]
        
        # Pearson correlation
        if len(avg1) > 1:
            try:
                mean1 = statistics.mean(avg1)
                mean2 = statistics.mean(avg2)
                std1 = statistics.stdev(avg1)
                std2 = statistics.stdev(avg2)
                
                if std1 > 0 and std2 > 0:
                    covariance = sum((avg1[i] - mean1) * (avg2[i] - mean2) for i in range(len(avg1))) / len(avg1)
                    correlation = covariance / (std1 * std2)
                    return max(-1, min(1, correlation))  # Clamp to [-1, 1]
            except:
                pass
        
        return 0.0
    
    @staticmethod
    def _detect_clusters(nodes: Dict[str, PlayerNode],
                        edges: List[NetworkEdge]) -> List[NetworkCluster]:
        """
        Detect clusters of densely connected players.
        
        Simple greedy clustering: each node joins its most connected component.
        """
        clusters = []
        cluster_id = 0
        assigned = set()
        
        # Build adjacency list
        adj = defaultdict(set)
        for edge in edges:
            adj[edge.player1].add(edge.player2)
            adj[edge.player2].add(edge.player1)
        
        # Greedy clustering
        for start_node in nodes.keys():
            if start_node in assigned:
                continue
            
            # BFS to build cluster
            cluster = set([start_node])
            queue = list(adj[start_node])
            
            while queue:
                node = queue.pop(0)
                if node in assigned or node in cluster:
                    continue
                
                # Add if connected to most of cluster
                connections_in_cluster = len(adj[node] & cluster)
                if connections_in_cluster >= len(cluster) * 0.5:  # >50% of cluster
                    cluster.add(node)
                    for neighbor in adj[node]:
                        if neighbor not in assigned and neighbor not in cluster:
                            queue.append(neighbor)
            
            if len(cluster) > 2:  # Only keep clusters of 3+
                assigned.update(cluster)
                
                # Calculate cluster metrics
                cluster_edges = [e for e in edges if e.player1 in cluster and e.player2 in cluster]
                max_edges = len(cluster) * (len(cluster) - 1) / 2
                density = len(cluster_edges) / max_edges if max_edges > 0 else 0
                
                # Find central player (most connections)
                connections = defaultdict(int)
                for edge in cluster_edges:
                    connections[edge.player1] += 1
                    connections[edge.player2] += 1
                central = max(connections, key=connections.get) if connections else list(cluster)[0]
                
                clusters.append(NetworkCluster(
                    cluster_id=cluster_id,
                    players=list(cluster),
                    size=len(cluster),
                    density=density,
                    avg_suspicion=statistics.mean([n.avg_cpl for n in [nodes[p] for p in cluster]]
                                                 if [nodes[p] for p in cluster] else [50]),
                    central_player=central,
                    description=f"Cluster of {len(cluster)} players with {density:.1%} density"
                ))
                cluster_id += 1
        
        return clusters
    
    @staticmethod
    def _count_suspicious_triplets(edges: List[NetworkEdge]) -> int:
        """Count triangles where all three edges are suspicious."""
        edge_set = set()
        for edge in edges:
            if edge.suspected_collaboration or edge.correlation_coefficient > 0.85:
                edge_set.add(tuple(sorted([edge.player1, edge.player2])))
        
        # Find triangles
        triplets = 0
        edge_list = list(edge_set)
        
        for i in range(len(edge_list)):
            for j in range(i + 1, len(edge_list)):
                e1, e2 = edge_list[i], edge_list[j]
                # Check if they share a node
                common = set(e1) & set(e2)
                if common:
                    third = (set(e1) | set(e2)) - {list(common)[0]}
                    if len(third) == 2:
                        third_edge = tuple(sorted(third))
                        if third_edge in edge_set:
                            triplets += 1
        
        return triplets // 3  # Each triangle counted 3 times


def create_network_visualization_data(analysis: NetworkAnalysis) -> Dict[str, Any]:
    """
    Create data suitable for D3.js network visualization.
    
    Returns nodes and links for force-directed graph.
    """
    nodes_data = []
    for username, node in analysis.nodes.items():
        nodes_data.append({
            'id': username,
            'label': username,
            'rating': node.rating,
            'accuracy': node.avg_accuracy,
            'size': 10 + (node.sample_games / 10),  # Size by game count
            'group': 'normal'
        })
    
    links_data = []
    for edge in analysis.edges:
        links_data.append({
            'source': edge.player1,
            'target': edge.player2,
            'weight': edge.connection_strength,
            'suspicious': edge.suspected_collaboration,
            'correlation': edge.correlation_coefficient,
            'games': edge.mutual_games
        })
    
    return {
        'nodes': nodes_data,
        'links': links_data,
        'clusters': [
            {
                'id': c.cluster_id,
                'players': c.players,
                'density': c.density
            }
            for c in analysis.clusters
        ]
    }

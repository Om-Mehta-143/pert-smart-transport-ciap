"""
PERT and Critical Path Analysis (CPA) Calculation Engine
Implements deterministic & probabilistic scheduling computations:
- Expected Time TE = (O + 4M + P) / 6
- Variance V = ((P - O) / 6)^2 (Full Float Precision)
- Forward pass: Early Start (ES), Early Finish (EF)
- Backward pass: Late Start (LS), Late Finish (LF)
- Total Slack: Float = LS - ES = LF - EF
- Critical Path identification (Zero Slack)
- Project Variance, Project StdDev, and Z-Score Normal CDF Probability
- Cycle Detection & Topological Sorting
"""

import math
from typing import Dict, List, Any, Tuple


class PERTValidationError(Exception):
    """Custom exception for PERT input and graph validation failures."""
    pass


class PERTEngine:
    def __init__(self, activities: List[Dict[str, Any]]):
        """
        activities format:
        [
            {
                "id": "A",
                "name": "Requirement Analysis",
                "predecessors": [],
                "optimistic": 2.0,
                "most_likely": 4.0,
                "pessimistic": 6.0
            },
            ...
        ]
        """
        self.raw_activities = activities
        self.activities: Dict[str, Dict[str, Any]] = {}
        self.successors: Dict[str, List[str]] = {}
        self.predecessors: Dict[str, List[str]] = {}
        self.project_duration: float = 0.0
        self.critical_path: List[str] = []
        self.critical_paths: List[List[str]] = []
        self.project_variance: float = 0.0
        self.project_std_dev: float = 0.0

    def validate(self) -> None:
        """Strict validation of activity data, values, references, and acyclicity."""
        if not self.raw_activities:
            raise PERTValidationError("Activity list cannot be empty.")

        seen_ids = set()
        for act in self.raw_activities:
            act_id = str(act.get("id", "")).strip()
            if not act_id:
                raise PERTValidationError("Every activity must have a non-empty 'id'.")
            if act_id in seen_ids:
                raise PERTValidationError(f"Duplicate activity ID detected: '{act_id}'.")
            seen_ids.add(act_id)

            # Three-point estimate validations
            try:
                o = float(act["optimistic"])
                m = float(act["most_likely"])
                p = float(act["pessimistic"])
            except (ValueError, KeyError, TypeError):
                raise PERTValidationError(f"Activity '{act_id}' has invalid numeric estimates.")

            if o <= 0 or m <= 0 or p <= 0:
                raise PERTValidationError(f"Activity '{act_id}': estimates must be strictly positive (> 0).")

            if not (o <= m <= p):
                raise PERTValidationError(
                    f"Activity '{act_id}': Violation of O <= M <= P requirement (O={o}, M={m}, P={p})."
                )

        # Validate Predecessors exist
        for act in self.raw_activities:
            act_id = str(act["id"]).strip()
            preds = [str(p).strip() for p in act.get("predecessors", []) if str(p).strip()]
            for p in preds:
                if p not in seen_ids:
                    raise PERTValidationError(
                        f"Activity '{act_id}' references unknown predecessor '{p}'."
                    )
                if p == act_id:
                    raise PERTValidationError(
                        f"Activity '{act_id}' cannot list itself as a predecessor (self-loop)."
                    )

        # Graph cycle detection using DFS 3-color state
        self._check_acyclic(seen_ids)

    def _check_acyclic(self, all_ids: set) -> None:
        """
        DFS cycle detection:
        0 = UNVISITED (WHITE)
        1 = VISITING (GRAY - in current recursion stack)
        2 = VISITED (BLACK)
        """
        graph: Dict[str, List[str]] = {aid: [] for aid in all_ids}
        for act in self.raw_activities:
            aid = str(act["id"]).strip()
            preds = [str(p).strip() for p in act.get("predecessors", []) if str(p).strip()]
            for p in preds:
                graph[p].append(aid)

        color: Dict[str, int] = {aid: 0 for aid in all_ids}
        cycle_nodes: List[str] = []

        def dfs(node: str, stack: List[str]) -> bool:
            color[node] = 1
            stack.append(node)
            for neighbor in graph[node]:
                if color[neighbor] == 1:
                    cycle_start_idx = stack.index(neighbor)
                    cycle_nodes.extend(stack[cycle_start_idx:] + [neighbor])
                    return True
                if color[neighbor] == 0:
                    if dfs(neighbor, stack):
                        return True
            stack.pop()
            color[node] = 2
            return False

        for node in all_ids:
            if color[node] == 0:
                if dfs(node, []):
                    cycle_repr = " -> ".join(cycle_nodes)
                    raise PERTValidationError(f"Cyclic dependency detected in project graph: {cycle_repr}")

    def compute(self) -> Dict[str, Any]:
        """Runs the complete PERT and CPM computations using unrounded float precision."""
        self.validate()

        # Initialize internal structures with raw float precision
        for act in self.raw_activities:
            aid = str(act["id"]).strip()
            name = str(act.get("name", aid)).strip()
            o = float(act["optimistic"])
            m = float(act["most_likely"])
            p = float(act["pessimistic"])

            te = (o + 4.0 * m + p) / 6.0
            var = ((p - o) / 6.0) ** 2
            std_dev = (p - o) / 6.0

            preds = [str(pr).strip() for pr in act.get("predecessors", []) if str(pr).strip()]

            self.activities[aid] = {
                "id": aid,
                "name": name,
                "optimistic": o,
                "most_likely": m,
                "pessimistic": p,
                "te": te,
                "variance": var,
                "std_dev": std_dev,
                "predecessors": preds,
                "successors": [],
                "es": 0.0,
                "ef": 0.0,
                "ls": 0.0,
                "lf": 0.0,
                "slack": 0.0,
                "is_critical": False,
            }
            self.predecessors[aid] = preds
            self.successors[aid] = []

        # Populate successors
        for aid, act in self.activities.items():
            for p in act["predecessors"]:
                self.successors[p].append(aid)

        # Topological sort for deterministic forward pass
        topo_order = self._topological_sort()

        # Forward Pass: Compute Early Start (ES) and Early Finish (EF)
        for aid in topo_order:
            act = self.activities[aid]
            if not act["predecessors"]:
                act["es"] = 0.0
            else:
                act["es"] = max(self.activities[p]["ef"] for p in act["predecessors"])
            act["ef"] = act["es"] + act["te"]

        # Overall Project Duration
        self.project_duration = max(act["ef"] for act in self.activities.values())

        # Backward Pass: Compute Late Finish (LF) and Late Start (LS)
        for aid in reversed(topo_order):
            act = self.activities[aid]
            succs = self.successors[aid]
            if not succs:
                act["lf"] = self.project_duration
            else:
                act["lf"] = min(self.activities[s]["ls"] for s in succs)
            act["ls"] = act["lf"] - act["te"]
            act["slack"] = act["lf"] - act["ef"]

            # Floating point tolerance check for critical status
            if abs(act["slack"]) < 1e-6:
                act["is_critical"] = True
                act["slack"] = 0.0
            else:
                act["is_critical"] = False

        # Identify all critical paths using recursion
        self.critical_paths = self._find_critical_paths()
        self.critical_path = self.critical_paths[0] if self.critical_paths else []

        # Calculate project variance and std dev at full float precision along primary critical path
        cp_var = sum(self.activities[aid]["variance"] for aid in self.critical_path)
        self.project_variance = cp_var
        self.project_std_dev = math.sqrt(cp_var)

        return self.get_summary()

    def _topological_sort(self) -> List[str]:
        """Kahn's algorithm for topological ordering."""
        in_degree = {aid: len(act["predecessors"]) for aid, act in self.activities.items()}
        queue = [aid for aid, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            queue.sort()
            curr = queue.pop(0)
            order.append(curr)

            for succ in self.successors[curr]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        return order

    def _find_critical_paths(self) -> List[List[str]]:
        """Finds all distinct paths from project start to finish where all nodes have zero slack."""
        start_nodes = [aid for aid, act in self.activities.items() if not act["predecessors"] and act["is_critical"]]
        end_nodes = {aid for aid, act in self.activities.items() if not self.successors[aid] and act["is_critical"]}

        all_paths: List[List[str]] = []

        def dfs_path(curr: str, path: List[str]):
            if curr in end_nodes and len(path) > 0:
                path_duration = sum(self.activities[node]["te"] for node in path)
                if abs(path_duration - self.project_duration) < 1e-4:
                    all_paths.append(list(path))
            for succ in self.successors[curr]:
                if self.activities[succ]["is_critical"]:
                    if abs(self.activities[curr]["ef"] - self.activities[succ]["es"]) < 1e-4:
                        path.append(succ)
                        dfs_path(succ, path)
                        path.pop()

        for snode in start_nodes:
            dfs_path(snode, [snode])

        return all_paths if all_paths else []

    def calculate_probability(self, target_deadline: float) -> Dict[str, Any]:
        """
        Computes probability of completion by target_deadline using Normal Distribution CDF:
        Z = (Target - Expected_Duration) / StdDev
        P(T <= D) = 0.5 * (1 + erf(Z / sqrt(2)))
        """
        if self.project_std_dev == 0.0:
            if target_deadline >= self.project_duration:
                prob = 1.0
                z = float("inf")
            else:
                prob = 0.0
                z = float("-inf")
        else:
            z = (target_deadline - self.project_duration) / self.project_std_dev
            prob = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

        return {
            "target_deadline": round(target_deadline, 2),
            "project_duration": round(self.project_duration, 4),
            "project_variance": round(self.project_variance, 4),
            "project_std_dev": round(self.project_std_dev, 4),
            "z_score": round(z, 4) if abs(z) != float("inf") else str(z),
            "probability_percent": round(prob * 100.0, 2),
            "assumptions": [
                "Activity times are statistically independent random variables.",
                "Central Limit Theorem applies: the sum of activity times along the critical path follows an approximately normal distribution.",
                "The identified critical path dominates total project risk; near-critical paths do not unexpectedly expand the variance."
            ]
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        Returns structured summary. Values are rounded to 4 decimal places strictly for display/serialization,
        while internal computations maintained full float precision.
        """
        formatted_activities = []
        for act in self.activities.values():
            formatted_activities.append({
                "id": act["id"],
                "name": act["name"],
                "optimistic": act["optimistic"],
                "most_likely": act["most_likely"],
                "pessimistic": act["pessimistic"],
                "te": round(act["te"], 4),
                "variance": round(act["variance"], 4),
                "std_dev": round(act["std_dev"], 4),
                "predecessors": act["predecessors"],
                "successors": act["successors"],
                "es": round(act["es"], 4),
                "ef": round(act["ef"], 4),
                "ls": round(act["ls"], 4),
                "lf": round(act["lf"], 4),
                "slack": round(act["slack"], 4),
                "is_critical": act["is_critical"],
            })

        return {
            "project_duration": round(self.project_duration, 4),
            "critical_path": self.critical_path,
            "critical_paths": self.critical_paths,
            "project_variance": round(self.project_variance, 4),
            "project_std_dev": round(self.project_std_dev, 4),
            "activities": formatted_activities,
        }

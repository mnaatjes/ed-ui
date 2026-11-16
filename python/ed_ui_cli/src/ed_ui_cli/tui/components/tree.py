"""Collapsible hierarchical tree views for ed_ui_cli (ADR 0004 & SDD-004)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.text import Text
from textual.widgets import Tree
from textual.widgets.tree import TreeNode


class TelemetryTree(Tree[Any]):
    """Hierarchical tree view for cartography and directory topologies."""

    DEFAULT_CSS = """
    TelemetryTree {
        height: 100%;
        width: 100%;
        background: $surface;
    }
    """

    def __init__(
        self,
        label: str = "Root",
        data: Any = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(label=label, data=data, id=id, classes=classes)

    def populate_celestial_system(
        self,
        system_name: str,
        bodies: list[dict[str, Any]],
    ) -> TreeNode[Any]:
        """Populate hierarchical celestial bodies (Stars -> Planets -> Moons)."""
        self.reset(system_name)
        root = self.root
        root.data = {"system_name": system_name, "count": len(bodies)}

        # Group bodies into hierarchical nodes
        body_nodes: dict[str, TreeNode[Any]] = {}

        # First pass: Create primary stellar and planetary bodies
        for body in bodies:
            name = str(body.get("name", body.get("BodyName", "Unknown Body")))
            b_type = str(body.get("type", body.get("BodyType", "Celestial")))
            distance = body.get("distance_ls", body.get("DistanceFromArrivalLS", 0))

            label = Text()
            label.append(f"{name} ", style="bold cyan")
            label.append(f"({b_type}) ", style="dim italic")
            if distance:
                label.append(f"[{distance:.1f} ls]", style="yellow")

            parent_name = str(body.get("parent_body", ""))
            if parent_name and parent_name in body_nodes:
                parent_node = body_nodes[parent_name]
                node = parent_node.add(label, data=body)
            else:
                node = root.add(label, data=body)

            body_nodes[name] = node

        root.expand()
        return root

    def populate_directory(self, root_dir: str | Path, max_depth: int = 3) -> TreeNode[Any]:
        """Populate a directory hierarchy for workspace topology exploration."""
        path = Path(root_dir)
        self.reset(path.name or str(path))
        self.root.data = str(path)

        def _walk(curr_path: Path, curr_node: TreeNode[Any], depth: int) -> None:
            if depth > max_depth:
                return
            try:
                entries = sorted(curr_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
                for entry in entries:
                    if entry.name.startswith(".") and entry.name != ".":
                        continue
                    if entry.is_dir():
                        dir_label = Text(f"📁 {entry.name}", style="bold blue")
                        child = curr_node.add(dir_label, data=str(entry))
                        _walk(entry, child, depth + 1)
                    else:
                        curr_node.add_leaf(Text(f"📄 {entry.name}", style="white"), data=str(entry))
            except PermissionError:
                pass

        _walk(path, self.root, 1)
        self.root.expand()
        return self.root


class JsonInspectorTree(Tree[Any]):
    """Recursive JSON / DTO explorer tree."""

    DEFAULT_CSS = """
    JsonInspectorTree {
        height: 100%;
        width: 100%;
        background: $surface;
    }
    """

    def __init__(
        self,
        label: str = "Payload",
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(label=label, id=id, classes=classes)

    def load_payload(self, label: str, data: Any) -> TreeNode[Any]:
        """Load and recursively display arbitrary dictionary, list, or primitive data."""
        self.reset(label)
        self.root.data = data
        self._build_tree(self.root, data)
        self.root.expand()
        return self.root

    def _build_tree(self, parent_node: TreeNode[Any], value: Any) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, dict):
                    child = parent_node.add(Text(f"{k}: {{...}}", style="bold cyan"), data=v)
                    self._build_tree(child, v)
                elif isinstance(v, list):
                    list_label = Text(f"{k}: [{len(v)} items]", style="bold magenta")
                    child = parent_node.add(list_label, data=v)
                    self._build_tree(child, v)
                else:
                    parent_node.add_leaf(self._format_leaf(str(k), v), data=v)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                if isinstance(item, dict | list):
                    child = parent_node.add(Text(f"[{idx}]", style="cyan"), data=item)
                    self._build_tree(child, item)
                else:
                    parent_node.add_leaf(self._format_leaf(f"[{idx}]", item), data=item)

    def _format_leaf(self, key: str, val: Any) -> Text:
        t = Text()
        t.append(f"{key}: ", style="dim")
        if isinstance(val, bool):
            t.append(str(val), style="bold green" if val else "bold red")
        elif isinstance(val, int | float):
            t.append(str(val), style="bold yellow")
        elif val is None:
            t.append("null", style="italic dim")
        else:
            t.append(f'"{val}"', style="white")
        return t

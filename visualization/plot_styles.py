from dataclasses import dataclass, asdict
from typing import Optional, Sequence
import yaml
from pathlib import Path

@dataclass
class PlotStyle:
    fs: int = 7
    fs_ticks: Optional[int] = None
    fs_title: Optional[int] = None
    fs_legend: Optional[int] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    title: Optional[str] = None
    xticks: Optional[Sequence[float]] = None
    yticks: Optional[Sequence[float]] = None
    xticklabels: Optional[Sequence[str]] = None
    yticklabels: Optional[Sequence[str]] = None
    legend: bool = False
    axis: Optional[Sequence[float]] = None
    colorbar: bool = False
    grid: bool = True
    grid_alpha: float = 0.3
    tick_direction: str = 'in'

    def save(self, filepath: str):
        """Save style to YAML file"""
        with open(filepath, 'w') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)

    @classmethod
    def load(cls, filepath: str) -> 'PlotStyle':
        """Load style from YAML file"""
        with open(filepath, 'r') as f:
            return cls(**yaml.safe_load(f))

# Predefined styles
PUBLICATION_STYLE = PlotStyle(
    fs=7,
    grid=True,
    tick_direction='in',
    grid_alpha=0.3
)

PRESENTATION_STYLE = PlotStyle(
    fs=12,
    grid=True,
    tick_direction='in',
    grid_alpha=0.3
)

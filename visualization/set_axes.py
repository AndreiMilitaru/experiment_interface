"""
Module to record demodulator time traces from Zurich Instruments lock-in amplifiers.
The original version was previously written in the Photonics Laboratory of ETH Zurich
by Andrei Militaru, and it has now been adapted and expanded upon.
"""

from typing import Optional
import matplotlib.pyplot as plt
from .plot_styles import PlotStyle

def set_ax(
    ax: plt.Axes,
    style: Optional[PlotStyle] = None,
    **kwargs
) -> plt.Axes:
    """Set plot style using either PlotStyle object or individual parameters"""
    if style is None:
        style = PlotStyle(**kwargs)
    else:
        # Override style with any provided kwargs
        for key, value in kwargs.items():
            setattr(style, key, value)

    if style.fs_ticks is None:
        style.fs_ticks = style.fs
    if style.fs_title is None:
        style.fs_title = style.fs
    if style.fs_legend is None:
        style.fs_legend = style.fs_ticks - 1
    if style.xlabel is not None:
        ax.set_xlabel(style.xlabel,fontsize=style.fs)
    if style.ylabel is not None:
        ax.set_ylabel(style.ylabel,fontsize=style.fs)
    if style.title is not None:
        ax.set_title(style.title,fontsize=style.fs_title)
    if style.xticks is not None:
        ax.set_xticks(style.xticks)
    if style.yticks is not None:
        ax.set_yticks(style.yticks)
    if style.xticklabels is None:        
        ax.xaxis.set_tick_params(labelsize=style.fs_ticks, which='both')
    else:
        ax.set_xticklabels(style.xtickslabels,fontdict = {'fontsize':style.fs_ticks})
    if style.yticklabels is None:
        ax.yaxis.set_tick_params(labelsize=style.fs_ticks, which='both')
    else:
        ax.set_yticklabels(style.ytickslabels,fontdict = {'fontsize':style.fs_ticks})
    if style.legend:
        ax.legend(fontsize=style.fs_legend)
    if style.axis is not None:
        ax.axis(style.axis)
    if style.colorbar:
        clb = plt.colorbar()
        clb.ax.tick_params(labelsize=style.fs_ticks)
    if style.grid:
        ax.grid()
    ax.tick_params(which='both', direction=style.tick_direction, bottom=True,
                   top=True, left=True, right=True)
    if style.grid:
        try:
            ax.tick_params(grid_alpha=style.grid_alpha)
        except:
            pass
    return ax

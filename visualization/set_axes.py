"""
Module to record demodulator time traces from Zurich Instruments lock-in amplifiers.
The original version was previously written in the Photonics Laboratory of ETH Zurich
by Andrei Militaru, and it has now been adapted and expanded upon.
"""

from typing import Optional, Sequence
import matplotlib.pyplot as plt
from .plot_styles import PlotStyle

def set_colorbar(
    mappable,
    ax: plt.Axes,
    style: Optional[PlotStyle] = None,
    ticks: Optional[Sequence[float]] = None,
    ticklabels: Optional[Sequence[str]] = None,
    label: Optional[str] = None,
    label_position: Optional[str] = None,
    colorbar_position: Optional[str] = None,
    **kwargs
) -> plt.colorbar.Colorbar:
    """Set colorbar style and properties
    
    Args:
        mappable: The image/plot to create colorbar for
        ax: Matplotlib axes to attach colorbar to
        style: PlotStyle object for visual properties
        ticks: Specific colorbar tick positions
        ticklabels: Labels for colorbar ticks
        label: Colorbar label
        label_position: Position of the colorbar label
        colorbar_position: Position of colorbar ('right'/'left' or 'top'/'bottom')
        **kwargs: Additional style parameters
    """
    if style is None:
        style = PlotStyle(**kwargs)
    else:
        for key, value in kwargs.items():
            setattr(style, key, value)

    # Set colorbar position and create it
    position = colorbar_position or style.cbar_position
    clb = plt.colorbar(
        mappable,
        ax=ax,
        orientation=style.cbar_orientation,
        fraction=style.cbar_fraction,
        pad=style.cbar_pad,
        location=position 
    )
    
    # Set label with position adjustment
    if label or style.cbar_label:
        position = label_position or style.cbar_label_position
        if style.cbar_orientation == 'vertical':
            clb.ax.yaxis.set_label_position(position)  # User specified position
        else:
            clb.ax.xaxis.set_label_position('top')
        
        clb.set_label(
            label or style.cbar_label,
            fontsize=style.fs,
            labelpad=style.cbar_labelpad
        )

    if ticks is not None:
        clb.set_ticks(ticks)
    elif style.cbar_ticks is not None:
        clb.set_ticks(style.cbar_ticks)
        
    if ticklabels is not None:
        if ticklabels == '':
            for label in clb.ax.get_yticklabels():
                label.set_text('')
        else:
            clb.set_ticklabels(ticklabels, fontsize=style.fs_ticks)
    elif style.cbar_ticklabels is not None:
        clb.set_ticklabels(style.cbar_ticklabels, fontsize=style.fs_ticks)
    else:
        clb.ax.tick_params(labelsize=style.fs_ticks)
    
    # Set tick parameters including direction
    clb.ax.tick_params(
        which='both',
        direction=style.tick_direction,
        labelsize=style.fs_ticks
    )
    
    return clb

def set_ax(
    ax: plt.Axes,
    style: Optional[PlotStyle] = None,
    xticks: Optional[Sequence[float]] = None,
    yticks: Optional[Sequence[float]] = None,
    xticklabels: Optional[Sequence[str]] = None,
    yticklabels: Optional[Sequence[str]] = None,
    **kwargs
) -> plt.Axes:
    """Set plot style and axis properties
    
    Args:
        ax: Matplotlib axes to style
        style: PlotStyle object for visual properties
        xticks: Specific x-axis tick positions
        yticks: Specific y-axis tick positions
        xticklabels: Labels for x-axis ticks
        yticklabels: Labels for y-axis ticks
        **kwargs: Additional style parameters
    """
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
    
    # Handle ticks and labels (now as function parameters)
    if xticks is not None:
        ax.set_xticks(xticks)
    if yticks is not None:
        ax.set_yticks(yticks)
    
    if xticklabels is not None:
        if xticklabels == '':
            # Clear all x tick labels
            for label in ax.get_xticklabels():
                label.set_text('')
        else:
            ax.set_xticklabels(xticklabels, fontsize=style.fs_ticks)
    else:
        ax.tick_params(axis='x', labelsize=style.fs_ticks)
    
    if yticklabels is not None:
        if yticklabels == '':
            # Clear all y tick labels
            for label in ax.get_yticklabels():
                label.set_text('')
        else:
            ax.set_yticklabels(yticklabels, fontsize=style.fs_ticks)
    else:
        ax.tick_params(axis='y', labelsize=style.fs_ticks)
    
    if style.legend:
        ax.legend(fontsize=style.fs_legend)
    if style.axis is not None:
        ax.axis(style.axis)
    if style.colorbar:
        clb = set_colorbar(ax.get_images()[0], ax, style)
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

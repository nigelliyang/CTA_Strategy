# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 16:05:58 2016

@author: zhao yong
"""

import numpy as np
from math import pi
import pandas as pd
from bokeh.io import output_notebook
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, Rect, HoverTool, Range1d, LinearAxis, WheelZoomTool, PanTool, ResetTool, ResizeTool, PreviewSaveTool
output_notebook()

from talib import MA
hf_df = pd.read_csv('../../ts_data/J00.DCE.csv',index_col=0)

###--------------------------------------------------------------------------

def create_data_source(data_frame):
    '''
    Reference here: https://github.com/bokeh/bokeh/issues/1239
    '''
    return ColumnDataSource(
        data=dict(
            date=[x.strftime("%Y-%m-%d") for x in data_frame['date']],
            open=data_frame['open'],
            close=data_frame['close'],
            high=data_frame['high'],
            low=data_frame['low'],
        )
    )

###--------------------------------------------------------------------------

def addlineplot(input_df):
    '''划线，以均线为例子'''
    source=create_data_source(input_df)
    MAs = [ 5, 10, 15, 20 ]
    line_color = [ 'white', 'yellow', 'red', 'green' ]
    for ma_th, ma in enumerate( MAs ):
            legend = 'MA' + str( ma )
            p.line( x = input_df['date'], y = MA( input_df['close'].as_matrix(), ma, matype=1 ),
                       legend = legend, line_color = line_color[ ma_th ],source=create_data_source(input_df) )

###--------------------------------------------------------------------------
'''
def ricequant_candlestick_volume_plot(MD_df, plot_title=None):

    Copyright Shawn Gu, 2016

    input_df = pd.DataFrame(
        {'date': MD_df.index,
         'open': MD_df['open'],
         'close': MD_df['close'],
         'high': MD_df['high'],
         'low': MD_df['low'],
         'vol': MD_df['vol']}
    )
    candlestick_volume_plot(input_df, plot_title)
'''

###--------------------------------------------------------------------------

def candlestick_volume_plot(input_df, plot_title=None):
    '''
    Copyright Shawn Gu, 2016
    The code below is modified based on the snippet from http://bokeh.pydata.org/en/0.11.1/docs/gallery/candlestick.html.
    '''
    input_df= input_df.dropna()
    input_df['date']=pd.to_datetime(input_df.index)
    px_mids = (input_df['open'] + input_df['close']) / 2.0
    px_spans = abs(input_df['close'] - input_df['open'])

    vol_mids = input_df['vol'] / 2.0
    vol_spans = input_df['vol']
    max_vol = max(input_df['vol'])

    inc = input_df['close'] >= input_df['open']
    dec = input_df['open'] > input_df['close']

    inc_color = 'red'
    dec_color = 'green'

    width = 12*60*60*1000 # in ms

    ht = HoverTool(
    tooltips=[
            ("date", "@date"),
            ("open", "@open"),
            ("close", "@close"),
            ("high", "@high"),
            ("low", "@low"),
        ]
    )
    TOOLS = [ht, WheelZoomTool(dimensions=['width']), ResizeTool(), ResetTool(),
             PanTool(dimensions=['width']), PreviewSaveTool()]

    max_px = max(input_df['high'])
    min_px = min(input_df['low'])

    px_range = max_px - min_px

    primary_y_range = (min_px - px_range / 10.0, max_px + px_range *0.1)
    global p
    p = figure(x_axis_type="datetime", tools=TOOLS,plot_height=600, plot_width=1000,
               toolbar_location="above", y_range=primary_y_range)

    if plot_title:
        p.title = plot_title

    p.xaxis.major_label_orientation = pi/4
    p.grid.grid_line_alpha=0.3
    p.background_fill = "black"


    p.extra_y_ranges = {"vol": Range1d(start=0, end=max_vol * 5)}
    p.add_layout(LinearAxis(y_range_name="vol"), 'right')

    px_rect_inc_src = create_data_source(input_df[inc])
    px_rect_dec_src = create_data_source(input_df[dec])

    p.segment(input_df.date[inc], input_df.high[inc], input_df.date[inc], input_df.low[inc], color=inc_color)
    p.segment(input_df.date[dec], input_df.high[dec], input_df.date[dec], input_df.low[dec], color=dec_color)
    p.rect(input_df.date[inc], px_mids[inc], width, px_spans[inc],
           fill_color=inc_color, line_color=inc_color, source=px_rect_inc_src)
    p.rect(input_df.date[dec], px_mids[dec], width, px_spans[dec],
           fill_color=dec_color, line_color=dec_color, source=px_rect_dec_src)

    p.rect(input_df.date[inc], vol_mids[inc], width, vol_spans[inc],
             fill_color=inc_color, color=inc_color, y_range_name="vol")
    p.rect(input_df.date[dec], vol_mids[dec], width, vol_spans[dec],
             fill_color=dec_color, color=dec_color, y_range_name="vol")

    """自定义划线"""
    addlineplot(input_df)
    if plot_title:
        output_file(plot_title+"candlestick.html", title=plot_title)
    else:
        output_file("untitle_candlestick.html", title="untitled")
    show(p)

###--------------------------------------------------------------------------

if __name__ == '__main__':
    from Candlestick import *
    candlestick_volume_plot(hf_df, plot_title='test and add ma')
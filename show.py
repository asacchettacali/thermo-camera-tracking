
# FUNZIONE CHE GENERA UNA PAGINA WEB INTERATTIVA
# PER LA VISUALIZZAZIONE E CONFRONTO DEI DATI OTTENUTI


# IMPORT ALL REQUIRED MODULES
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, CheckboxGroup, CategoricalColorMapper, Select, LinearAxis, Range1d
from bokeh.layouts import row, widgetbox
from bokeh.palettes import Spectral6
from bokeh.models.widgets import Div



# CHECKBOX UPDATE FUNCTION
def update(active):

	# LIST OF ACTIVE LOADS
	active_mats = []
	for item in mats_menu.active:
		active_mats.append( mats_idx[item] )

	# LIST OF ACTIVE LOADS
	active_loads = []
	for item in loads_menu.active:
		active_loads.append( loads_idx[item] )

	# LIST OF ACTIVE CIs
	active_cis = []
	for item in cis_menu.active:
		active_cis.append( coil_idx[item] )

	# FILTERED DATA
	new_data = {
		'Time (s)'  		: df.loc[ (df['Material'].isin(active_mats)) & (df['CI'].isin(active_cis)) & (df['Load (g)'].isin(active_loads)) ]['Time (s)'],
		'Frame'  			: df.loc[ (df['Material'].isin(active_mats)) & (df['CI'].isin(active_cis)) & (df['Load (g)'].isin(active_loads)) ]['Frame'],
		'Temperature (°C)'  : df.loc[ (df['Material'].isin(active_mats)) & (df['CI'].isin(active_cis)) & (df['Load (g)'].isin(active_loads)) ]['Temperature (°C)'],
		'Contraction (%)'   : df.loc[ (df['Material'].isin(active_mats)) & (df['CI'].isin(active_cis)) & (df['Load (g)'].isin(active_loads)) ]['Contraction (%)'],
		'Load (g)' 			: df.loc[ (df['Material'].isin(active_mats)) & (df['CI'].isin(active_cis)) & (df['Load (g)'].isin(active_loads)) ]['Load (g)'],
		'CI' 				: df.loc[ (df['Material'].isin(active_mats)) & (df['CI'].isin(active_cis)) & (df['Load (g)'].isin(active_loads)) ].CI,
		'Material' 			: df.loc[ (df['Material'].isin(active_mats)) & (df['CI'].isin(active_cis)) & (df['Load (g)'].isin(active_loads)) ].Material
	}
	source.data = new_data


# IMPORT RAW DATA AND PARSE MATERIAL TAB
df = pd.ExcelFile('combined.xlsx').parse('data')

# FIX ALL COLUMNS TYPES
df['Material'] 			= df['Material'].astype(str)
df['CI'] 				= df['CI'].astype(str)
df['Load (g)'] 			= df['Load (g)'].astype(str)
df['Temperature (°C)'] 	= df['Temperature (°C)'].round(2)
df['Contraction (%)'] 	= df['Contraction (%)'].round(2)

# RETRIEVE ALL COIL INDEXES AND LOADS
mat_list  = df['Material'].unique().tolist()
ci_list   = df['CI'].unique().tolist()
load_list = df['Load (g)'].unique().tolist()

# COIL INDEXES & LOADS DICTIONARY
mats_idx  = dict(zip(range(len(mat_list)), mat_list))
coil_idx  = dict(zip(range(len(ci_list)), ci_list))
loads_idx = dict(zip(range(len(load_list)), load_list))

# LIST OF INTERPOLATED SERIES
#df_list = []

# MAKE A SPECIFIC INTERPOLATION FOR EACH COIL INDEX - LOAD
#for m in mat_list:
#	for ci in ci_list:
#		for ld in load_list:
#			new_df 		= df.loc[ (df['Material'] == m) & (df['CI'] == ci) & (df['Load'] == ld) ].reset_index()
#			new_index 	= np.arange(0, new_df.shape[0], 0.01)
#			new_df 		= new_df.reindex(new_index).interpolate(method='quadratic') 
#			df_list.append(new_df)

# MERGE ALL INTERPOLATED DATAFRAMES IN A BIG DATAFRAME
# result = pd.concat(df_list).fillna(method = 'ffill')

# SETUP THE INITIAL SOURCE
source = ColumnDataSource(data={
    'Time (s)'   		: df.loc[ (df['Material'] == mats_idx[0]) & (df['CI'] == coil_idx[0]) & (df['Load (g)'] == str(loads_idx[0]) ) ]['Time (s)'],
    'Frame'   			: df.loc[ (df['Material'] == mats_idx[0]) & (df['CI'] == coil_idx[0]) & (df['Load (g)'] == str(loads_idx[0]) ) ]['Frame'],
    'Temperature (°C)'  : df.loc[ (df['Material'] == mats_idx[0]) & (df['CI'] == coil_idx[0]) & (df['Load (g)'] == str(loads_idx[0]) ) ]['Temperature (°C)'],
    'Contraction (%)'   : df.loc[ (df['Material'] == mats_idx[0]) & (df['CI'] == coil_idx[0]) & (df['Load (g)'] == str(loads_idx[0]) ) ]['Contraction (%)'],
    'Load (g)' 			: df.loc[ (df['Material'] == mats_idx[0]) & (df['CI'] == coil_idx[0]) & (df['Load (g)'] == str(loads_idx[0]) ) ]['Load (g)'],
    'CI' 				: df.loc[ (df['Material'] == mats_idx[0]) & (df['CI'] == coil_idx[0]) & (df['Load (g)'] == str(loads_idx[0]) ) ].CI,
    'Material'   		: df.loc[ (df['Material'] == mats_idx[0]) & (df['CI'] == coil_idx[0]) & (df['Load (g)'] == str(loads_idx[0]) ) ].Material
})

# SETUP HOVER TOOL
hover = HoverTool( tooltips = [	('Time (s)', '@{Time (s)} s'), 
								('Temperature (°C)', '@{Temperature (°C)} °C'),
								('Contraction (%)', '@{Contraction (%)} %'),
								('Material', '@{Material}'), 
								('CI', '@{CI}'), 
								('Load (g)', '@{Load (g)} g') ] )

# SETUP COLOR MAPPER FOR COIL INDEXES
color_mapper = CategoricalColorMapper(factors = mat_list, palette = Spectral6)

# CREATE THE FIGURE
plot = figure(x_axis_label = 'Time (s)', y_axis_label = 'Temperature (°C)', tools = [hover, 'save, reset, crosshair, pan, wheel_zoom, box_zoom'] )

plot.extra_y_ranges = {"percentage": Range1d(start=0, end=100)}

plot.add_layout(LinearAxis(y_range_name="percentage", axis_label="Contraction (%)"), 'right')



# CREATE THE PLOT
plot.line('Time (s)', 'Temperature (°C)', source = source, legend = 'Material', line_width = 3, color = 'red' )
plot.line('Time (s)', 'Contraction (%)', source = source, legend = 'Material', line_width = 3 )
# plot.circle('Time (s)', 'Temperature (°C)', source = source, legend = 'Material', size = 10, color = dict(field = 'Material', transform=color_mapper) )


# CREATE LOADS AND CIs CHECKBOXES
mats_menu   = CheckboxGroup(labels = mat_list, active = [0])
loads_menu  = CheckboxGroup(labels = load_list, active = [0])
cis_menu    = CheckboxGroup(labels = ci_list, active = [0])


# ADD UPDATE EVENT LISTENING 
mats_menu.on_click(update)
loads_menu.on_click(update)
cis_menu.on_click(update)

# ADD A TITLE FOR BOTH CHECKBOXES
mat_title 	= Div(text="""<h3>Material:</h3>""", width=200)
loads_title = Div(text="""<h3>Load (g):</h3>""", width=200)
cis_title   = Div(text="""<h3>Coil Index:</h3>""", width=200)

# ADD PLOT TITLE
plot.title.text = 'Temperature & Contraction over Time'

# ADJUST LEGEND POSITION
plot.legend.location = 'top_left'

# CREATE THE LAYOUT
layout = row(widgetbox(mat_title, mats_menu, loads_title, loads_menu, cis_title, cis_menu), plot)

# ADD THE LAYOUT TO THE DOCUMENT ROOT
curdoc().add_root(layout)



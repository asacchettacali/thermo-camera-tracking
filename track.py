
# FUNZIONE CHE LEGGE TUTTI I VIDEO PER OGNI CAVO
# PER OGNI MATERIALE E GENERA UN EXCEL CON CI | PESO | TEMP | CONTRAZIONE

# Import OpenCV and Numpy
import numpy as np
import pandas as pd
import cv2, sys, glob, os

# Ratio cm/px from sample of 15cm (115px)
px_to_cm = 0.13

# SAVE SCREENSHOTs / SHOW VIDEO
save_screenshots = False
show_video = False

# MATERIAL
materials = ['nylon', 'pvdf']

excel_names = []

# CI dictionary
ci = {  'nylon': { '1': 3, '2': 2.5, '3': 2.38, '4': 2.56, '5': 2.63, '6': 2.6, '7': 2.55, '8': 2.65, '9': 2.70 },
		'pvdf': { '1': 2.56, '2': 2.68, '3': 2.5, '4': 2.5, '5': 2.57, '6': 0, '7': 0, '8': 0, '9': 2.77, '10': 0, '11': 0, '12': 0 } }


# Setup current path as root
root_path = os.getcwd()

# For each material
for material in materials:

	# SET CURRENT FOLDER WITH VIDEO PATH
	os.chdir(root_path + '/videos/' + material + '/')

	# READ ALL VIDEOS
	for video_filename in sorted(glob.glob("*.wmv")):

		print('Video: ' + str(video_filename) )
		
		# Extract matherial, muscle number and weight
		num,end 	= video_filename.split('_')
		weight,ext 	= end.split('.')
		temperatures_array = []
		reference_lengths_array = []
		frames_array = []
		muscle_lengths_array = []
		times_array = []

		# Load video in OpenCV
		cap = cv2.VideoCapture(video_filename)

		# Retrieve video details like frames, FPS and duration
		frames 	 = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		fps 	 = cap.get(cv2.CAP_PROP_FPS)
		duration = int(frames / fps)

		# Temperatures CSV
		csv_filename = num + '_' + weight + '.csv'

		# Import CSV temperature data from thermacamera, using "frame" as index
		tc_data = pd.read_csv(csv_filename, index_col = 'frame')

		# CSV contains temp value for each 10 frames so we have to expand the index and forward filling all the empty frame
		new_index = range( int(frames)+10 )
		tc_data   = tc_data.reindex(new_index, method = 'ffill')

		# Read all frames
		while(1):

			# Return next frame from the video
			ret, frame = cap.read()

			# If properly returned a frame from the video
			if ret == True:

				########################################################################
				# Setup Video options
				########################################################################
				frame 			= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Set grey scale
				current_frame 	= cap.get(cv2.CAP_PROP_POS_FRAMES) # Get current frame number
				starting_frame 	= 88 # Initial frame




				# On this early frame we need to calculate rest length
				if current_frame == starting_frame:

					########################################################################
					# Measure muscle length at rest
					########################################################################
					marker_y 		 = 19 # Starting Y coordinate of the marker vertical line
					marker_x 		 = 100 # Horizontal position of the line
					marker_threshold = 93 # Grey level threshold to detect the marker
					marker_line		 = frame[marker_y:(marker_y + 200), marker_x:(marker_x + 1)] # Vertical line centered over the marker and the muscle

					# Find marker distance by looking if there are pixels with the marker_threshold level of grey
					marker_distance = np.nonzero( marker_line[:,0] > marker_threshold )[0]

					# If the marker was detected then proceed with length measure
					if marker_distance.size > 0:
						
						# Y position of the first pixel on the line belonging to the marker
						rest_length_px = marker_distance[0]

					else:

						# Piccola fix per quei video che sono venuti male e non è possibile recuperare automaticamente la lunghezza
						if str(material) == 'nylon' and str(num) == '2' and str(weight) == '30':
							rest_length_px = 52
						elif str(material) == 'nylon' and str(num) == '4' and str(weight) == '40':
							rest_length_px = 59
						elif str(material) == 'nylon' and str(num) == '6' and str(weight) == '40':
							rest_length_px = 48
						else:
							rest_length_px = 770

					# Conversion px to cm
					rest_length_cm = round(rest_length_px * px_to_cm, 2)

					# Save a screenshot to verify accuracy
					image = cv2.line(frame, (marker_x, marker_y), (marker_x, ( marker_y + rest_length_px ) ), 255, 1 )
					cv2.imwrite( 'altezza_' + str(num) + '_' + str(weight) + '_' + str(rest_length_cm) +'.jpg', image)



				# All other frames
				elif current_frame > starting_frame:

					########################################################################
					# Progress status
					########################################################################
					completed = round(current_frame * 100 / frames)
					print('Material: ' + str(material) + ' | NUM: ' + str(num) + ' | CI: ' + str(ci[material][num]) + ' | Load: ' + str(weight) + ' | Length: ' + str(rest_length_cm) + 'cm | Completed: ' + str(completed) + '%', end="\r")


					########################################################################
					# Measure rest distance from a reference point to calculate contractions
					########################################################################
					reference_x		 	= 90 # Horizontal position of reference line
					reference_y		 	= marker_y # Vertical position of reference line
					reference_threshold = 40 # Grey level threshold to detect the marker
					reference_line		= frame[reference_y:(reference_y + 200), reference_x:(reference_x + 1)] # Vertical line centered over the marker and the muscle

					# Piccola fix per quei video che sono venuti male e non è possibile recuperare automaticamente la lunghezza
					if str(material) == 'nylon' and str(num) == '2' and str(weight) == '30':
						reference_threshold = 20

					# Find reference distance by looking if there are pixels with the reference_threshold level of grey
					reference_distance = np.nonzero( reference_line[:,0] > reference_threshold )[0]

					# If the reference was detected then proceed with length measure
					if reference_distance.size > 0:
						
						# Y position of the first pixel on the line belonging to the reference
						reference_length_px = reference_distance[0]

						# Conversion px to cm
						reference_length_cm = round(reference_length_px * px_to_cm, 2)

						muscle_lengths_array.append(rest_length_cm)
						frames_array.append(current_frame)
						times_array.append(round(current_frame*0.033, 2))
						reference_lengths_array.append(reference_length_cm)
						temperatures_array.append(round(tc_data.loc[current_frame, 'Line 1 [C]'], 2))


					########################################################################
					# Show / Hide video playing
					########################################################################
					if show_video == True:

						image = cv2.rectangle(frame, (0,0), (0,0), 0, 1)

						# Create and show video window
						cv2.namedWindow('image', cv2.WINDOW_NORMAL)
						cv2.resizeWindow('image', 1024,640)
						cv2.imshow('image', image)

						# Stop video on "q" press
						if cv2.waitKey(1) & 0xFF == ord('q'):
							break


			# VIDEO END
			else:

				# Build raw data dictiionary 
				raw_data = { 'Material': material, 'CI': ci[material][num], 'Load (g)': weight, 'Frame': frames_array, 'Time (s)': times_array, 'Reference Length (cm)': reference_lengths_array, 'Temperature (°C)': temperatures_array, 'Muscle Length (cm)': muscle_lengths_array }
				
				# Create the relative dataframe for analysis
				raw_df = pd.DataFrame(raw_data, columns = raw_data.keys())

				muscle_length 		 = raw_df["Muscle Length (cm)"].values[0]
				min_ref_length 		 = raw_df["Reference Length (cm)"].min()
				max_ref_length 		 = raw_df["Reference Length (cm)"].max()
				max_contraction 	 = round(max_ref_length - min_ref_length, 2)
				max_contraction_perc = round(max_contraction * 100 / muscle_length, 2)
				contraction 		 = max_ref_length - raw_df["Reference Length (cm)"]
				contraction_perc 	 = round(contraction * 100 / muscle_length, 2)

				raw_df["Reference Length Min (cm)"] = min_ref_length
				raw_df["Reference Length Max (cm)"] = max_ref_length
				raw_df["Contraction (cm)"] 		 	= contraction
				raw_df["Contraction (%)"] 		 	= contraction_perc
				raw_df["Contraction Max (cm)"] 	 	= max_contraction
				raw_df["Contraction Max (%)"] 	 	= max_contraction_perc


				# print('')
				# print(raw_df.head())
				# print(raw_df.info())
				# print('Reference Lunghezza min: ' + str(min_ref_length) + 'cm | max: ' + str(max_ref_length) + 'cm')
				# print('Contrazione massimale: ' + str(max_contraction) + 'cm | ' + str(max_contraction_perc) + '%' )
				# print('Temperatura min: ' + str(raw_df["Temperature (°C)"].min()) + '°C | max: ' + str(raw_df["Temperature (°C)"].max()) + '°C')

				# Print empty line
				print('')

				# Prepare to export results in Excel
				filename = str(num) + '_' + str(weight)+'.xlsx'
				excel_names.append(filename)
				writer = pd.ExcelWriter(root_path + '/' + filename, engine = 'openpyxl')

				# Convert dataframe to excel
				raw_df.to_excel(writer, 'data', index = False)

				# Save the excel file
				writer.save()

				# Break video
				break


		# Release video capturing and close all windows
		cap.release()
		cv2.destroyAllWindows()

				
				

# read them in
excels = [pd.ExcelFile(root_path + '/' + name) for name in excel_names]

# turn them into dataframes
frames = [x.parse(x.sheet_names[0], header=None,index_col=None) for x in excels]

# delete the first row for all frames except the first
# i.e. remove the header row -- assumes it's the first
frames[1:] = [df[1:] for df in frames[1:]]

# concatenate them..
combined = pd.concat(frames)

# write it out
combined.to_excel(root_path + '/' + "combined.xlsx", 'data', header=False, index=False)

writer.save()

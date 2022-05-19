import re
import folium
import csv
import argparse
import logging

from pyproj import Transformer

logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)

def transformCoordinates(Y, X):
  transformation_result = transformer.transform(Y, X)
  return transformation_result[0], transformation_result[1]

parser = argparse.ArgumentParser()
parser.add_argument("breitbandatlas_csv_file", help="Path to the CSV file of the Breitbandatlast")
parser.add_argument("ISP_Name", help="Name of the ISP which should be filtered")
args = parser.parse_args()

breitbandatlas_csv_file = args.breitbandatlas_csv_file
ISP_Name = args.ISP_Name

m = folium.Map(location=[47.678314, 11.1028293], zoom_start=7, control_scale=True)

# opening the CSV file
with open(breitbandatlas_csv_file, mode ='r')as file:
  # EPSG:3035 -> EPSG:4326
  transformer = Transformer.from_crs(3035, 4326)

  # reading the CSV file
  csvFile = csv.reader(file)
  first_line = True

  # displaying the contents of the CSV file
  counter = 0
  for lines in csvFile:
    if first_line:
      first_line = False
      continue

    raster_id = lines[0]
    ISP = lines[1]
    tech = lines[2]
    download = float(lines[3])
    upload = float(lines[4])

    if ISP != ISP_Name:
      continue

    regex_result = re.findall("([0-9]+)mN([0-9]+)E([0-9]+)", raster_id)[0]

    X_bottom_left = int(regex_result[2]) * int(regex_result[0])
    Y_bottom_left = int(regex_result[1]) * int(regex_result[0])

    lat_bottom_left, lng_bottom_left = transformCoordinates(Y_bottom_left, X_bottom_left)

    X_bottom_right = X_bottom_left + int(regex_result[0])
    Y_bottom_right = Y_bottom_left

    lat_bottom_right, lng_bottom_right = transformCoordinates(Y_bottom_right, X_bottom_right)

    X_upper_right = X_bottom_left + int(regex_result[0])
    Y_upper_right = Y_bottom_left + int(regex_result[0])

    lat_upper_right, lng_upper_right = transformCoordinates(Y_upper_right, X_upper_right)

    X_upper_left = X_bottom_left
    Y_upper_left = Y_bottom_left + int(regex_result[0])

    lat_upper_left, lng_upper_left = transformCoordinates(Y_upper_left, X_upper_left)
    
    logging.info("#:{}\n"
                 "\tLAT_BOTTOM_LEFT:  {} LNG_BOTTOM_LEFT:  {}\n"
                 "\tLAT_BOTTOM_RIGHT: {} LNG_BOTTOM_RIGHT: {}\n"
                 "\tLAT_UPPER_RIGHT:  {} LNG_UPPER_RIGHT:  {}\n"
                 "\tLAT_UPPER_LEFT:   {} LNG_UPPER_LEFT:   {}".format(counter,
                                                                      lat_bottom_left,
                                                                      lng_bottom_left,
                                                                      lat_bottom_right,
                                                                      lng_bottom_right,
                                                                      lat_upper_right,
                                                                      lng_upper_right,
                                                                      lat_upper_left,
                                                                      lng_upper_left))

    locations = [[lat_bottom_left, lng_bottom_left], 
                 [lat_bottom_right, lng_bottom_right],
                 [lat_upper_right, lng_upper_right],
                 [lat_upper_left, lng_upper_left]]

    folium.Polygon(
      locations=locations,
      popup=folium.Popup("<table style=\"height: 130px; width: 200px;\">"
                         "<tr>"
                            "<td style=\"width: 70px\">Raster ID:</td>"
                            "<td style=\"width: 70px\">{}</td>"
                         "</tr>"
                         "<tr>"
                            "<td style=\"width: 70px\">Tech:</td>"
                            "<td style=\"width: 70px\">{}</td>"
                         "</tr>"
                         "<tr>"
                            "<td style=\"width: 70px\">Download:</td>"
                            "<td style=\"width: 70px\">{} Mbit/s</td>"
                         "</tr>"
                         "<tr>"
                            "<td style=\"width: 70px\">Upload:</td>"
                            "<td style=\"width: 70px\">{} Mbit/s</td>"
                         "</tr>"
                         "</table>".format(raster_id, tech, download, upload), 
                         max_width=len(raster_id) * 25),
      color='blue',
      fill_opacity=0.3,
      opacity=0.3,
      fill=True
    ).add_to(m)

    counter += 1

m.save('{}.html'.format(ISP_Name.replace(" ", "_")))
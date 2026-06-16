import os
import sys
import glob
import math
import numpy as np
import pandas as pd
import tarfile
import zipfile

def math_test(a, b):
    print(a+b)

def extract_data(file, extract_to_path):
    """
    Unzips a zip file or tar to a specified directory.

    Args:
        file (str): The path to the zip or tar file.
        extract_to_path (str): The path to extract the contents to.
    """
    if not os.path.exists(extract_to_path):
        os.makedirs(extract_to_path)
    try:
        if file.endswith(".zip"):
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(extract_to_path)
            print(f"Successfully extracted '{file}' to '{extract_to_path}'")
        elif file.endswith(".tar"):
            with tarfile.open(file, 'r') as tar:
                tar.extractall(extract_to_path)
            print(f"Successfully extracted '{file}' to '{extract_to_path}'")
        else:
            print(f"Error: The file '{file}' is not a valid zip or tar file.")
    except Exception as e:
        print(f"An error occurred: {e}")


def read_meta_data(f):
    d = []
    with open(f, 'r') as file:
        header1 = file.readline()
        header2 = file.readline()
        header3 = file.readline()
        header4 = file.readline()
        header5 = file.readline()
        header6 = file.readline()
        header7 = file.readline()
        header2 = header2.split(' ')
        campaign = header2[0]
        startDate = f'{header2[3]} {header2[4]}'
        endDate = f'{header2[5]} {header2[6]}'
        elevation = header2[7]
        longitude = header2[8]
        latitude = header2[9]
        zenith = float(header2[10])*-1
        azimuth = header2[11]
        temp_ground = header2[12]
        pressure = header2[13]
    d.append([f, startDate, endDate, elevation, longitude, latitude, zenith, azimuth, temp_ground, pressure])

    # Create DF
    meta_df = pd.DataFrame(d, columns=['file', 'start', 'end', 'elevation', 'longitude', 'latitude', 'zenith', 'azimuth', 'temp_ground', 'pressure'])

    # Convert appropriate columns to numeric
    numeric_cols = ['elevation', 'longitude', 'latitude', 'zenith', 'azimuth', 'temp_ground', 'pressure']
    meta_df[numeric_cols] = meta_df[numeric_cols].apply(pd.to_numeric, errors='coerce')  # Convert and set non-numeric values to NaN

    # Convert date columns to datetime
    meta_df['start'] = pd.to_datetime(meta_df['start'], errors='coerce', dayfirst=True)
    meta_df['end'] = pd.to_datetime(meta_df['end'], errors='coerce', dayfirst=True)
    return(meta_df)


def file_to_data(file, start_datetime, end_datetime, azimuth, scan, distance=450, bin_width=7.5,):
    with open(file, 'r') as file:
        content = file.readlines()
    meta = content[0:7]
    
    # Establish how many rows to take based on input distance. 
    number_of_rows = math.ceil(distance / bin_width)
    
    # Extract data (analog and photon counts)
    data = content[7:(7+number_of_rows)]
    my_data = []
    for row in data:
        d = row.strip().split('\t')
        my_data.append(d)
    df = pd.DataFrame(my_data, columns=['analog', 'photon'])
    df = df.apply(pd.to_numeric)
    df['angle'] = azimuth
    df['scan_id'] = scan
    df['start'] = start_datetime
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = end_datetime
    df['end'] = pd.to_datetime(df['end'])
    df['distance'] = (df.index +1) * bin_width
    df['x'] = df['distance'] * np.cos(np.radians(azimuth))
    df['z'] = df['distance'] * np.sin(np.radians(azimuth))
    return df

# Example usage
if __name__ == "__main__":
    dir = './maros2369313'
    meta_df = pd.DataFrame()
    for file in os.listdir(dir):
        if file.endswith('.txt'):
            file_path = os.path.join(dir, file)
            meta = read_meta_data(file_path)
            meta_df = pd.concat([meta_df, meta])
    print(meta_df)
    print(meta_df.info())
#!/bin/bash

# Define source and destination folders
source_folder="C:\Users\hans\eth2\eth2\simulation\simulations\computed-metrics\hans"
destination_folder="C:\Users\hans\Desktop\Cloud\2nd Sem\CS 199\Cycle 9\results"

# Copy contents of source folder to destination folder
cp -r "$source_folder"/* "$destination_folder"

#!/bin/zsh
#  download_idc.sh
#  Simple script to download data from an IDC-generated manifest. 
#  It allows the flexibility to choose the destination path where to save the DICOM files
#  
#  Created by Jose Ulloa on 16-04-2024.
#  

MANIFEST=${1}
DATAPATH=${2}
echo "Data will be saved in ${DATAPATH}"
echo "Manifest file: ${MANIFEST}"

# Adding destination path to the output in the file manifest:
sed -i '' "s|\.|$DATAPATH|" ${MANIFEST}

# Check how many files will download:
nlines=`grep -w "#" -c -v ${MANIFEST}`
echo "Manifest file contains ${nlines} lines (each line represent a folder in the AWS/GCP bucket). Press any key to start dowloading..."
read -s -k1

# Downloading the data:
s5cmd --no-sign-request --endpoint-url https://s3.amazonaws.com run ${MANIFEST}

nfiles=`ls -b1 ${DATAPATH} | wc -l`
echo "Downloaded ${nfiles} files in ${DATAPATH}"

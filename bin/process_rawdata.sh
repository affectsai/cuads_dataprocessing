#!/bin/bash
###############################################################################
# process_rawdata.sh
#
# Author: Timothy C. Sweeney-Fanelli
# Last Modified: Jan 25 2025
#
# This script is used to process the raw data exported by the Shimmer3 devices
# into the CUADS dataset for distribution.
#
# The raw data from the Shimmer3 is not made available as part of the dataset,
# but this script is provided for reference. The only manipulation of the data
# is to adjust the timestamps. Shimmer3 records timestamps with microsecond
# precision, but we adjust to millisecond precision for UNIX timestamps.
#
# The Shimmer3 ExG and GSR sensors each produce their own CSV file. This
# script merges them together, converts the timestamps, and produces the
# segmented data files using the participant responses from the ARDT mobile
# application.
#
# Usage:
#     ./process_rawdata.sh
#          --participantId <ParticipantID>
#          --cuadsPath <path to raw data from shimmer devices>
#          --outputFolder <path to write processed data>
###############################################################################

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

PARTICIPANT_ID=""
CUADS_FOLDER=""
OUTPUT_FOLDER=""

while test $# != 0
do
  case "$1" in
    --participantId)
      shift
      PARTICIPANT_ID=$1
      ;;
    --cuadsPath)
      shift
      CUADS_FOLDER=$1
      ;;
    --outputFolder)
      shift
      OUTPUT_FOLDER=$1
      ;;
    -h)
      ;&
    --help)
      usage
      exit 0
      ;;
  esac
  shift
done

if [ -z "${CUADS_FOLDER}" ]; then
  echo "You must specify the location of the cuads dataset: "
  echo "   $0 --cuadsPath /mnt/cuads/Final\ Collection/"
  exit 1
fi

if [ -z "${PARTICIPANT_ID}" ]; then
  echo "You must specify the participant id to process "
  echo "   $0 --participantId CU001"
  exit 1
fi

if [ -z "${OUTPUT_FOLDER}" ]; then
  echo "WARNING: No output folder specified ... using CUADS_FOLDER instead."
  OUTPUT_FOLDER=${CUADS_FOLDER}
fi

PARTICIPANT_DATA_PATH="${CUADS_FOLDER}/${PARTICIPANT_ID}"

for session in $(find ${PARTICIPANT_DATA_PATH}/* -name "*_MultiSession" -type d -exec basename {} \;); do
    echo Session $session

    ECG_DATA="${PARTICIPANT_DATA_PATH}/${session}/${PARTICIPANT_ID}_Session1_Shimmer_EE5D_Calibrated_SD.csv"
    PPG_DATA="${PARTICIPANT_DATA_PATH}/${session}/${PARTICIPANT_ID}_Session2_Shimmer_A609_Calibrated_SD.csv"

    CONTINUE=true

    if [ ! -f "${ECG_DATA}" ]; then
        echo "Missing ECG Data for Participant $PARTICIPANT_ID: $ECG_DATA"
        CONTINUE=false
    fi
    if [ ! -f "${PPG_DATA}" ]; then
        echo "Missing PPG Data for Participant $PARTICIPANT_ID: $PPG_DATA"
        CONTINUE=false
    fi

    if $CONTINUE; then
        echo "Good to go for participant $PARTICIPANT_ID"
        CSV1=$(mktemp)
        CSV2=$(mktemp)

        echo "Processing ${ECG_DATA} to $CSV1"
        cat "${ECG_DATA}" | tr '\t' ',' | awk -F, -vOFS=',' 'NR<=3 { print } NR>3 { $1 = sprintf("%.6f",$1/1000); print $0 }' > $CSV1
        echo "Processing ${PPG_DATA} to $CSV2"
        cat "${PPG_DATA}" | tr '\t' ',' | awk -F, -vOFS=',' 'NR<=3 { print } NR>3 { $1 = sprintf("%.6f",$1/1000); print $0 }' > $CSV2


        mkdir -p ${OUTPUT_FOLDER}/${PARTICIPANT_ID}
        MERGED_DATA="${OUTPUT_FOLDER}/${PARTICIPANT_ID}/fullsession.csv"
        echo "Merging session data into ${MERGED_DATA}"
        python ${SCRIPT_DIR}/../merge.py $CSV1 $CSV2 ${MERGED_DATA}
        rm $CSV1 $CSV2

        for responses in $(ls ${PARTICIPANT_DATA_PATH}/*_Responses_*.json); do
          echo "Segmenting data for ${PARTICIPANT_ID} from responses $(basename $responses)"

          RESPONSE_FILENAME=$(basename $responses)
          RESPONSE_NUMBER=$(echo $RESPONSE_FILENAME|sed 's|..*_||;s|\.json||')

          mkdir -p ${OUTPUT_FOLDER}/${PARTICIPANT_ID}/trial_${RESPONSE_NUMBER}
          python ${SCRIPT_DIR}/../segment_session.py "${PARTICIPANT_ID}" "${MERGED_DATA}" "${PARTICIPANT_DATA_PATH}/${PARTICIPANT_ID}_Responses_${RESPONSE_NUMBER}.json" "${PARTICIPANT_DATA_PATH}/${PARTICIPANT_ID}_PersonalitySurvey_1.json" "${OUTPUT_FOLDER}/${PARTICIPANT_ID}/segmented" | tee ${OUTPUT_FOLDER}/${PARTICIPANT_ID}/segmented/datasegmentation.log
        done
    fi

done

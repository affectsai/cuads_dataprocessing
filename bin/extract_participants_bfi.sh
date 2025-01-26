#!/bin/bash

usage() {
  echo "Usage:"
  echo "   $0 --paritipantFilter <regex>"
  echo ""
  echo "Extracts participants BFI from the JSON input by matching .participantId against the given regex filter."
}

FILTER=""
CUADS_FOLDER=""

while test $# != 0
do
  case "$1" in
    --participantFilter)
      shift
      FILTER=$1
      ;;
    --cuadsPath)
      shift
      CUADS_FOLDER=$1
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

FILTERED=$(mktemp)
PREFIX=$1

cat - | jq "select( .participantId | test(\"^${FILTER}\") )" > $FILTERED

for participant in $( jq -c '.participantId' $FILTERED | sort -u ); do
  PARTICIPANT_ID=${participant//\"/}
  echo "Extracting BFI Survey data from participant $PARTICIPANT_ID"

   PARTICIPANT_DATA_PATH=${CUADS_FOLDER}/${PARTICIPANT_ID}
   echo "     Checking for path: ${PARTICIPANT_DATA_PATH}"

   if [ ! -d "${PARTICIPANT_DATA_PATH}" ]; then
     echo "     CUADS Participant folder does not exist yet... creating empty folder"
     mkdir -p "$PARTICIPANT_DATA_PATH"
   fi

   # Extract this participants data (one data collection per line)
   PARTDATA=$(mktemp)
   jq -c ". | select(.participantId == $participant)" $FILTERED > $PARTDATA

   # How many lines did we just extract?
   x=($(wc $PARTDATA))
   count=${x[0]}

   echo "     There are $count BFIs for this participant id."

   for i in $(seq 1 $count); do
     OUTPUT_PATH=${PARTICIPANT_DATA_PATH}/${PARTICIPANT_ID}_PersonalitySurvey_${i}.json

     echo "     Extracting $PARTICIPANT_ID response set # ${i} to $OUTPUT_PATH"
     sed "${i}q;d" $PARTDATA | jq ".survey" | sed 's|\\"|"|g;s|^"||;s|"$||' | jq . > "${OUTPUT_PATH}"

   done
#
#   echo
done

echo $FILTERED


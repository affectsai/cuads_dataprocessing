# Used to segment the fullsession.csv file into individual video_XXXX_sessiondata
# files, using the original response JSON file from the ARDT mobile application
##################################################################################

import os
import sys
import csv
import json
from datetime import datetime, timedelta

video_durations = {
    "video_30": "00:01:20.96",
    "video_30_fixation": "00:01:30.96",
    "video_52": "00:01:47.00",
    "video_53": "00:01:55.00",
    "video_55": "00:01:26.96",
    "video_58": "00:01:08.96",
    "video_69": "00:01:08.96",
    "video_73": "00:01:22.00",
    "video_79": "00:00:53.00",
    "video_80": "00:01:46.96",
    "video_90": "00:01:35.96",
    "video_107": "00:00:44.96",
    "video_111": "00:02:04.00",
    "video_138": "00:02:07.02",
    "video_146": "00:01:37.96",
    "video_cats_f": "00:01:48.64",
    "video_dallas_f": "00:01:39.87",
    "video_detroit_f": "00:01:39.87",
    "video_earworm_f": "00:01:04.00",
    "video_funny_f": "00:01:37.07",
    "video_newyork_f": "00:01:39.80",
}

participantId=sys.argv[1]
mergedSession=sys.argv[2]
responseJson=sys.argv[3]
personalityJson=sys.argv[4]
outputFolder=sys.argv[5]

try:
    os.mkdir(outputFolder)
except FileExistsError:
    pass

RESPONSE_DATETIME_FMT='%Y-%m-%dT%H:%M:%S.%f%z'

if os.path.exists(personalityJson):
    with open(personalityJson) as f:
        personality=json.load(f)
        with open(os.path.join(outputFolder,f'{participantId}_personality_{personality['name']}.csv'),'w') as personality_output:
            writer = csv.writer(personality_output)
            writer.writerow(['extraversion', personality['extraversion']['score']])
            writer.writerow(['agreeableness', personality['agreeableness']['score']])
            writer.writerow(['conscientiousness', personality['conscientiousness']['score']])
            writer.writerow(['negativeEmotionality', personality['negativeEmotionality']['score']])
            writer.writerow(['openMindedness', personality['openMindedness']['score']])


with open(os.path.join(outputFolder,f'{participantId}_responses.csv'),'w') as outputdata:
    outputdata_writer = csv.writer(outputdata)
    outputdata_writer.writerow(["MediaIdentifier","Valence","Arousal","StartTime","EndTime","PauseCount","WatchedFullVideo"])

    with open(responseJson, 'r') as response_data_file:
        response_data = json.load(response_data_file)
        mobileSessionStartTime = datetime.strptime(response_data['dataCollection']['beginTimestamp'], RESPONSE_DATETIME_FMT).astimezone()
        mobileSessionEndTime = datetime.strptime(response_data['dataCollection']['endTimestamp'], RESPONSE_DATETIME_FMT).astimezone()

        print(f"\tParticipant session in mobile app began {mobileSessionStartTime} and ended {mobileSessionEndTime}")

        physiologicalDataRowNum = 0;
        with open(mergedSession) as physiological_signal_data_file:
            physiologicalSignalData=csv.reader(physiological_signal_data_file, delimiter=',')
            headers = physiologicalSignalData.__next__() # skip headers...
            physiologicalDataRowNum += 1

            session_cursor = physiologicalSignalData.__next__()
            physiologicalDataRowNum += 1

            current_session_time = float(session_cursor[0])
            dataCaptureStartTime = datetime.fromtimestamp(current_session_time).astimezone()

            print(f"\tPhysiological recording session data begins at {datetime.fromtimestamp(current_session_time)}")
            print(f"-------------------------------------------------------------")

            for clip in response_data['dataCollection']['mediaRatings']:
                mediaName = clip['mediaItem']['mediaIdentifier']
                mediaStartTime = datetime.strptime(clip['mediaStartTime'], RESPONSE_DATETIME_FMT).astimezone()
                mediaEndTime = datetime.strptime(clip['mediaEndTime'], RESPONSE_DATETIME_FMT).astimezone()

                if mediaStartTime == datetime.strptime("1970-01-01T00:00:00.000Z",RESPONSE_DATETIME_FMT).astimezone():
                    if mediaEndTime == datetime.strptime("1970-01-01T00:00:00.000Z",
                                                           RESPONSE_DATETIME_FMT).astimezone():
                        print(f"\tWARNING: no response captured for {mediaName}")
                        continue
                    else:
                        print(f"\tWARNING: Invalid start time captured for {mediaName}. Attempting to resolve...")
                        if not clip['didWatchFullVideo']:
                            print(f"\tERROR: participant did not watch the full video. Unable to resolve start time. Skipping...\n")
                            continue

                        # Mobile app was capturing the video ending as a pause so it's always at least 1.
                        if not clip['mediaPauseCount'] < 2:
                            print(f"\tERROR: participant paused the video for an unknown duration. Unable to resolve start time. Skipping...\n")
                            continue

                        videolen = video_durations[mediaName].split(':')
                        print(f"\tThe video duration was {videolen[1]}:{videolen[2]}")
                        print(f"\tThe media end time was {mediaEndTime}. Participant watched full video and did not pause.")
                        mediaStartTime = mediaEndTime - timedelta(minutes=int(videolen[1]), seconds=float(videolen[2]))
                        print(f"\tThe adjusted media start time is: {mediaStartTime}")

                print(f"\tParticipant viewing of {mediaName} began at {mediaStartTime} and ended {mediaEndTime}")

                if mediaStartTime < mobileSessionStartTime:
                    print(f"\tERROR: media start time is earlier than session start time. Skipping.")
                    continue

                if mediaStartTime < dataCaptureStartTime:
                    print(f"\tERROR: media start time is earlier than physiological sensor data capture start time. Skipping.")
                    continue


                error = False
                temp1 = current_session_time
                while current_session_time < mediaStartTime.timestamp():
                    try:
                        session_cursor = physiologicalSignalData.__next__()
                        physiologicalDataRowNum += 1

                        current_session_time = float(session_cursor[0])
                    except:
                        print(f"\tERROR: Unable to locate start time in sensor data capture. Skipping.\n")
                        error = True
                        break

                if error:
                    continue

                print(f"\tFast forwarded to {mediaName} start time {datetime.fromtimestamp(current_session_time).astimezone()}")

                sampleNum = 0
                with open(os.path.join(outputFolder, f"{participantId}_{mediaName}_sessiondata.csv"), 'w') as segmentFile:
                    writer = csv.writer(segmentFile)
                    writer.writerow(headers)
                    while current_session_time < mediaEndTime.timestamp():
                        sampleNum = sampleNum + 1
                        session_cursor = physiologicalSignalData.__next__()
                        physiologicalDataRowNum += 1

                        current_session_time = float(session_cursor[0])
                        writer.writerow(session_cursor)

                print(f"\tWrite {sampleNum} samples ({sampleNum/256} seconds) ending {datetime.fromtimestamp(current_session_time).astimezone()}")


                arousal = float(clip['arousal'])
                valence = float(clip['valence'])

                arousal = arousal / 10      # Rescale down to 0-10
                valence = valence / 10      # Rescale down to 0-10

                outputdata_writer.writerow(
                    [
                        mediaName,
                        valence,
                        arousal,
                        mediaStartTime.timestamp(),
                        mediaEndTime.timestamp(),
                        clip['mediaPauseCount'],
                        clip['didWatchFullVideo']
                    ]
                )

                print(f"")


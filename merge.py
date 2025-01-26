import sys
import csv
from contextlib import redirect_stdout

ecgFile = sys.argv[1]
ppgFile = sys.argv[2]
outFile = sys.argv[3]

columnNameMap = {
    "Shimmer_EE5D_Accel_LN_X_CAL": "ECGSENSOR_Accel_LN_X",
    "Shimmer_EE5D_Accel_LN_Y_CAL": "ECGSENSOR_Accel_LN_Y",
    "Shimmer_EE5D_Accel_LN_Z_CAL": "ECGSENSOR_Accel_LN_Z",
    "Shimmer_EE5D_Accel_WR_X_CAL": "ECGSENSOR_Accel_WR_X",
    "Shimmer_EE5D_Accel_WR_Y_CAL": "ECGSENSOR_Accel_WR_Y",
    "Shimmer_EE5D_Accel_WR_Z_CAL": "ECGSENSOR_Accel_WR_Z",
    "Shimmer_EE5D_Battery_CAL": "ECGSENSOR_Battery",
    "Shimmer_EE5D_ECG_EMG_Status1_CAL": "ECGSENSOR_ECG_EMG_Status1",
    "Shimmer_EE5D_ECG_EMG_Status2_CAL": "ECGSENSOR_ECG_EMG_Status2",
    "Shimmer_EE5D_ECG_IBI_LA_RA_CAL": "ECGSENSOR_ECG_IBI_LA_RA",
    "Shimmer_EE5D_ECG_IBI_LL_LA_CAL": "ECGSENSOR_ECG_IBI_LL_LA",
    "Shimmer_EE5D_ECG_IBI_LL_RA_CAL": "ECGSENSOR_ECG_IBI_LL_RA",
    "Shimmer_EE5D_ECG_IBI_Vx_RL_CAL": "ECGSENSOR_ECG_IBI_Vx_RL",
    "Shimmer_EE5D_ECG_LA-RA_24BIT_CAL": "ECGSENSOR_ECG_LA-RA_24BIT",
    "Shimmer_EE5D_ECG_LL-LA_24BIT_CAL": "ECGSENSOR_ECG_LL-LA_24BIT",
    "Shimmer_EE5D_ECG_LL-RA_24BIT_CAL": "ECGSENSOR_ECG_LL-RA_24BIT",
    "Shimmer_EE5D_ECG_Vx-RL_24BIT_CAL": "ECGSENSOR_ECG_Vx-RL_24BIT",
    "Shimmer_EE5D_ECGtoHR_LA_RA_CAL": "ECGSENSOR_ECGtoHR_LA_RA",
    "Shimmer_EE5D_ECGtoHR_LL_LA_CAL": "ECGSENSOR_ECGtoHR_LL_LA",
    "Shimmer_EE5D_ECGtoHR_LL_RA_CAL": "ECGSENSOR_ECGtoHR_LL_RA",
    "Shimmer_EE5D_ECGtoHR_Vx_RL_CAL": "ECGSENSOR_ECGtoHR_Vx_RL",
    "Shimmer_EE5D_Gyro_X_CAL": "ECGSENSOR_Gyro_X",
    "Shimmer_EE5D_Gyro_Y_CAL": "ECGSENSOR_Gyro_Y",
    "Shimmer_EE5D_Gyro_Z_CAL": "ECGSENSOR_Gyro_Z",
    "Shimmer_EE5D_Pressure_BMP280_CAL": "ECGSENSOR_Pressure_BMP280",
    "Shimmer_EE5D_Temperature_BMP280_CAL": "ECGSENSOR_Temperature_BMP280",
    "Shimmer_A609_Accel_LN_X_CAL": "PPGSENSOR_Accel_LN_X",
    "Shimmer_A609_Accel_LN_Y_CAL": "PPGSENSOR_Accel_LN_Y",
    "Shimmer_A609_Accel_LN_Z_CAL": "PPGSENSOR_Accel_LN_Z",
    "Shimmer_A609_Accel_WR_X_CAL": "PPGSENSOR_Accel_WR_X",
    "Shimmer_A609_Accel_WR_Y_CAL": "PPGSENSOR_Accel_WR_Y",
    "Shimmer_A609_Accel_WR_Z_CAL": "PPGSENSOR_Accel_WR_Z",
    "Shimmer_A609_Battery_CAL": "PPGSENSOR_Battery",
    "Shimmer_A609_GSR_Range_CAL": "PPGSENSOR_GSR_Range",
    "Shimmer_A609_GSR_Skin_Conductance_CAL": "PPGSENSOR_GSR_Skin_Conductance",
    "Shimmer_A609_GSR_Skin_Resistance_CAL": "PPGSENSOR_GSR_Skin_Resistance",
    "Shimmer_A609_Gyro_X_CAL": "PPGSENSOR_Gyro_X",
    "Shimmer_A609_Gyro_Y_CAL": "PPGSENSOR_Gyro_Y",
    "Shimmer_A609_Gyro_Z_CAL": "PPGSENSOR_Gyro_Z",
    "Shimmer_A609_Mag_X_CAL": "PPGSENSOR_Mag_X",
    "Shimmer_A609_Mag_Y_CAL": "PPGSENSOR_Mag_Y",
    "Shimmer_A609_Mag_Z_CAL": "PPGSENSOR_Mag_Z",
    "Shimmer_A609_PPG_A13_CAL": "PPGSENSOR_PPG_A13",
    "Shimmer_A609_PPG_IBI_CAL": "PPGSENSOR_PPG_IBI",
    "Shimmer_A609_PPGtoHR_CAL": "PPGSENSOR_PPGtoHR",
    "Shimmer_A609_Pressure_BMP280_CAL": "PPGSENSOR_Pressure_BMP280",
    "Shimmer_A609_Temperature_BMP280_CAL": "PPGSENSOR_Temperature_BMP280",
    "":""
}

with open(outFile, newline='', mode='w') as mergefile:
    with open(ecgFile, newline='') as csvfile1:
        ecgreader = csv.reader(csvfile1, delimiter=',')

        ecgreader.__next__()    # Junk Line
        header1 = ecgreader.__next__()
        units1 = ecgreader.__next__()

        ecgline = ecgreader.__next__()
        time1 = float(ecgline[0])


        while time1 == 0:
            ecgline = ecgreader.__next__()
            time1 = float(ecgline[0])

        print(f"ECG File Begins with Timestamp:\t{time1}")

        with open(ppgFile, newline='') as csvfile2:
            ppgreader = csv.reader(csvfile2, delimiter=',')
            ppgreader.__next__()  # Junk Line fails because it has a trailing quote from our shitty preprocess!!!
            header2 = ppgreader.__next__()
            units2 = ppgreader.__next__()

            ppgline = ppgreader.__next__()
            time2 = float(ppgline[0])
            while time2 == 0:
                ppgline = ppgreader.__next__()
                time2 = float(ppgline[0])

            print(f"PPG File Begins with Timestamp:\t{time2}")

            # BEGIN HERE...
            header1 = [columnNameMap.get(x) for x in header1[1:]]
            header2 = [columnNameMap.get(x) for x in header2[1:]]

            with redirect_stdout(mergefile):
                print(f"TIMESTAMP_ECGSENSOR,TIMESTAMP_PPGSENSOR,{",".join(header1)},{",".join(header2)}")

            skipCount = 0
            startTime = time1
            # File 1 began before File 2 -- so we fast forward through File 1 until we catch up to File 2's start
            if time1<time2:
                print(f"ECG File begins before PPG file ... fast forwarding through ECG File.")
                while time1 < time2:
                    skipCount += 1
                    ecgline = ecgreader.__next__()
                    time1 = float(ecgline[0])
                print(f"\tSkipped {skipCount} records ({(time1-startTime)/256} seconds)")

            while True:
                # For each time1 value, find the last time2 that is less than or equal to it
                while time1-time2 > 0.001:
                    try:
                        ppgline = ppgreader.__next__()
                    except StopIteration:
                        exit(0)

                    time2 = float(ppgline[0])

                try:
                    with redirect_stdout(mergefile):
                        print(f"{time1:.6f},{time2:.6f},{",".join(ecgline[1:])},{",".join(ppgline[1:])}", mergefile)
                except BrokenPipeError:
                    exit(1)

                # Advance time1
                try:
                    ecgline = ecgreader.__next__()
                except StopIteration:
                    exit(0)

                time1 = float(ecgline[0])




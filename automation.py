# -*- coding: utf-8 -*-
import subprocess
from google.cloud import storage
import requests
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="None")
    parser.add_argument("-m", "--machine", default="None")
    parser.add_argument("-e", "--extruder", default="None")
    parser.add_argument("-o", "--output", default="None")
    args = parser.parse_args()
    return args


def model_verify(machine_file, extruder_file, input_file, output_folder):
    program_path = "/CuraEngine/build/CuraEngine"
    output_file = "output.gcode"
    command = [program_path, "slice", "-p"]

    if not machine_file=="None":
        with open("machine.json","wb") as file:
            file.write(requests.get(machine_file))
        for item in ["-j", "machine.json"]:command.append(item)

    if not extruder_file=="None":
        with open("extruder.json","wb") as file:
            file.write(requests.get(extruder_file))
        for item in ["-j", "extruder.json"]:command.append(item)

    if not input_file=="None":
        with open("input.stl","wb") as file:
            file.write(requests.get(input_file))
        for item in ["-l", "input.stl"]:command.append(item)

    for item in ["-o", output_file]:command.append(item)

    command = " ".join(command)
    proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = proc.communicate()

    bucket_name = 'cura_files'
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    output = output_folder + output_file
    blob = bucket.blob(output)

    with open(output_file,"rb") as myfile:
      content = str(myfile.read().decode("latin"))
      for line in content.split("\n")[::-1]:
        if "TIME_ELAPSED".lower() in line.lower():
           eta = line
        elif "Filament used".lower() in line.lower():
           cost = float(line.split()[-1][:-1])*10
      blob.upload_from_string(content)

    output_url = "https://storage.cloud.google.com/" + bucket_name + output
    return {"out":out, "err":err, "eta":eta, "cost":cost, "url":output_url}, 200


if __name__ == '__main__':
    args = get_args()
    model_verify(args.machine, args.extruder, args.file, args.output)

import subprocess
import argparse
import os
from google.cloud import storage

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="herringbone-gear-large.stl")
    parser.add_argument("-m", "--machine", default="fdmprinter.def.json")
    parser.add_argument("-e", "--extruder", default="prusa_i3.def.json")
    parser.add_argument("-o", "--folder", default="")
    args = parser.parse_args()
    return args

def call_cmd(printer_json, extruder_json, stl_file, output_folder, number = 0):
  while os.path.isfile("output_" + str(number)): number += 1
  else:output_file = "output_" + str(number)
  program_path = "/CuraEngine/build/CuraEngine"
  command = [program_path, "slice", "-p", "-j", printer_json, "-j", extruder_json, "-l", stl_file, "-o", output_file]
  command = " ".join(command)
  proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  out, err = proc.communicate()
  bucket_name = 'cura_files'
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  filee = output_folder+"output.gcode"
  blob = bucket.blob(filee)
  with open(output_file,"rb") as myfile:
    blob.upload_from_string(str(myfile.read().decode("latin")))
  outfile = "https://storage.cloud.google.com/" + bucket_name + filee
  return [out, out.decode(), outfile]


args = get_args()
out, decoded_out, output_file = call_cmd(args.machine, args.extruder, args.file,args.folder)
cont = open(output_file).read()
for line in cont.split("\n")[::-1]:
  if "TIME_ELAPSED" in line:break
print(decoded_out, output_file,line[1:])

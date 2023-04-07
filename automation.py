import subprocess
import argparse
import os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="/herringbone-gear-large.stl")
    parser.add_argument("-m", "--machine", default="/fdmprinter.def.json")
    parser.add_argument("-e", "--extruder", default="/prusa_i3.def.json")
    args = parser.parse_args()
    return args

def call_cmd(printer_json, extruder_json, stl_file, number = 0):
  while os.path.isfile("output_" + str(number)): number += 1
  else:output_file = "output_" + str(number)
  program_path = "/CuraEngine/build/CuraEngine"
  command = [program_path, "slice", "-p", "-j", printer_json, "-j", extruder_json, "-l", stl_file, "-o", output_file]
  proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  out, err = proc.communicate()
  return [out, out.decode(), output_file]


args = get_args()
out, decoded_out, output_file = call_cmd(args.machine, args.extruder, args.file)
print(out, decoded_out, output_file)
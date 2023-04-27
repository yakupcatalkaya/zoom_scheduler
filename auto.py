import subprocess
from flask import Flask, request
from google.cloud import storage

app = Flask(__name__)

@app.route('/', methods=['POST'])
def model_verify():
   print("Begining...")
   program_path = "/CuraEngine/build/CuraEngine"
   output_file = "output.gcode"
   command = [program_path, "slice", "-p"]
   output_folder = str(request.args.get("folder"))

   bucket_name = 'cura_files'
   storage_client = storage.Client()
   bucket = storage_client.get_bucket(bucket_name)

   try:
      blob_a = bucket.blob(output_folder + "/machine.json")
      blob_a.download_to_filename("machine.json")
      for item in ["-j", "machine.json"]:command.append(item)
   except Exception as e:
      print(e)

   try:
      blob_b = bucket.blob(output_folder + "/extruder.json")
      blob_b.download_to_filename("extruder.json")
      for item in ["-j", "extruder.json"]:command.append(item)
   except Exception as e:
      print(e)

   try:
      blob_c = bucket.blob(output_folder + "/input.stl")
      blob_c.download_to_filename("input.stl")
      for item in ["-l", "input.stl"]:command.append(item)
   except Exception as e:
      print(e)

   for item in ["-o", output_file]:command.append(item)

   command = " ".join(command)
   proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
   out, err = proc.communicate()

   output = output_folder + output_file
   blob_d = bucket.blob(output)
   blob_d.upload_from_filename(output_file)

   return {"out":out, "err":err}

if __name__ == '__main__':
    app.run(debug=True)

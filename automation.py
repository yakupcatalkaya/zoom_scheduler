import subprocess
#from google.cloud import storage
from flask import Flask, request, send_file
#import random

app = Flask(__name__)

@app.route('/', methods=['POST'])
def model_verify():
    program_path = "/CuraEngine/build/CuraEngine"
    #output_folder = str(random.randint(10**9, 10**10))
    output_file = "output.gcode"
    command = [program_path, "slice", "-p"]

    try:
      machine_file = request.files['machine']
      for item in ["-j", machine_file]:command.append(item)
    except:
       pass
    
    try:
      extruder_file = request.files['extruder']
      for item in ["-j", extruder_file]:command.append(item)
    except:
       pass
    
    try:
      input_file = request.files['input']
      for item in ["-l", input_file]:command.append(item)
    except:
       pass
    
    for item in ["-o", output_file]:command.append(item)

    command = " ".join(command)
    proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = proc.communicate()

    #bucket_name = 'cura_files'
    #storage_client = storage.Client()
    #bucket = storage_client.get_bucket(bucket_name)
    #output = output_folder + output_file
    #blob = bucket.blob(output)

    with open(output_file,"rb") as myfile:
      content = str(myfile.read().decode("latin"))
      for line in content.split("\n")[::-1]:
        if "TIME_ELAPSED".lower() in line.lower():
           eta = line
        elif "Filament used".lower() in line.lower():
           cost = float(line.split()[-1][:-1])*10
      #blob.upload_from_string(content)

    #output_url = "https://storage.cloud.google.com/" + bucket_name + output
    send_file(output_file, as_attachment=True)
    return {"out":out, "err":err, "eta":eta, "cost":cost}, 200


if __name__ == '__main__':
    app.run(debug=True)

import clarifai
import json,re
import time
import requests
import numpy,os,glob
from subprocess import call

from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
API_KEY='f4eaaff265f043758cb037de5ba620ee'
KEYS=['d7357d88854b4663b15d1b6e00d8fc55','f4eaaff265f043758cb037de5ba620ee']
KEYSP = 0
MODEL="general-v1.3"
INTERACTION = [0,"",True] #use true instead of false to ask the user whether delete a entry or not (True Automatically deletes wrong entries)
buffersucc = ["###"]
clarireq = 0


def send_video_GET_PREDICTION(video,position):

    try:
        app = ClarifaiApp(api_key=API_KEY)
        model = app.models.get(MODEL)
        clarireq = clarireq +1
        if video[0] == "/":
            video = video[1:]
        url='https://s3.amazonaws.com/sawt-production/'+video

        print(url)

        response=requests.head(url)
        if (response.status_code!=200):

            f=open('ERROR-LOG.txt', 'a')
            f.write("\nError in array position ["+str(position)+"]"+ " --> ERROR CODE: " + str(response) + "\n")
            f.close()

            print ("ERROR "+str(response))
            return "NULL-API-ERROR";


        for f in glob.glob("temp/*"):
            os.remove(f)




        command = ["ffmpeg",'-t','120','-r','1/5', '-i', url,'-vf', 'fps=1/5',"temp/img%03d.jpg"]

        call(command)




        bufferaux=[];
        for f in glob.glob("temp/*"):
            file_obj=bytearray()
            image = ClImage(file_obj=open(f, 'rb'))
            bufferaux.append( model.predict([image]))


        return bufferaux;

    except Exception as err:
        print(err)
        return bufferaux;



def apply_filter(jso , rate):
    i=0;
    while i <len(jso['outputs'][0]['data']):
        j=len(jso['outputs'][0]['data']['concepts'])-1
        while j>=0:
            if (jso['outputs'][0]['data']['concepts'][j]['value']<rate):
                del jso['outputs'][0]['data']['concepts'][j]
            j-=1
        i+=1

    return jso;


def predict(x,json_object,json_object_lenght):
    if(x==json_object_lenght):
        return json_object;

    if clarireq == 20 :
        if KEYSP == (len(KEYS) - 1):
            return json_object
        KEYSP = KEYSP + 1
        API_KEY=KEYS[KEYSP]
        clarireq = 0

    try:
        aux=send_video_GET_PREDICTION(json_object[x]['media_file'],x)
    except Exception:
        return predict(x+1,json_object,json_object_lenght);

    if (aux=="NULL-API-ERROR"):
        print ("Error in array position ["+str(x)+"] title: "+json_object[x]['title'])
        f = open('ERROR-LOG.txt', 'a')#Save all the errors in to this file
        f.write("\nError in array position ["+str(x)+"] title: "+json_object[x]['title'])
        f.close()

        if(INTERACTION[2]):
            #del json_object[x]
            #return predict(x,json_object,json_object_lenght-1);
            return predict(x+1,json_object,json_object_lenght);
        INTERACTION[1] = input("Delete yes/no: ")
        INTERACTION[0]+=1

        if(INTERACTION[0]>3):
            INTERACTION[1] = input("Delete all wrong entries yes/no: ")
            if(INTERACTION[1]=="yes")or(INTERACTION[1]=="y"):
                INTERACTION[2]=True
                del json_object[x]
                return predict(x,json_object,json_object_lenght-1);


        if(INTERACTION[1]!="yes" or INTERACTION[1]!="y"):
            return predict(x+1,json_object,json_object_lenght);
        if(INTERACTION[1]=="yes")or(INTERACTION[1]=="y"):
            del json_object[x]
            return predict(x,json_object,json_object_lenght-1);



    elif (aux!="NULL-API-ERROR"):

        bufferaux=[]
        for entry in aux:
            entry=apply_filter(entry,0.85)
            bufferaux.append(entry)

        json_object[x]['clarifai_output']=bufferaux
        buffersucc.append("["+str(x)+"]")

        return predict(x+1,json_object,json_object_lenght);



def main():

    f = open('ERROR-LOG.txt', 'w')
    f.write("--[ERROR LOG]--")
    f.close()

    directory="temp"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filelist = glob.glob("temp/*")
    for f in filelist:
        os.remove(f)

    try:
        buffer = open('mediaDATA.json',encoding="utf-8-sig", errors="ignore").read()

        json_object = json.loads(buffer,strict=False)
    except FileNotFoundError:
        print ("mediaDATA.json JSON Array not found\n")
        location=input("File not Found type the path to JSON file...\n")
        buffer = open(location,encoding="latin-1").read()
        json_object = json.loads(buffer,strict=False)

    json_object=predict(730,json_object,830) #150

    with open("mediaDATA.json", "w") as outfile:
        json.dump(json_object, outfile, indent=4)


    for element in buffersucc:
        print(element)
    print("\nDONE...")

    return 0;

main()

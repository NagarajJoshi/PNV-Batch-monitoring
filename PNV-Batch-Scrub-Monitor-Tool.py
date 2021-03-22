# ABA-example.py
# tested in python 3.6
# implements Phone Number Scrub and monitor via ABA and MSS

# uses one non-standard Python Library -> Requests
# see http://docs.python-requests.org/en/master/
# zlib is used to decompress the output file

import time
import zlib
import requests
import sys
import os


# this will be your access token
access_token = ''
#If testing using QA then provide company id value
#If testing using PROD keep it blank
company_id = ''

print("\n########## Starting Pre Validation Checks ##########")

# print ("\nNo of arguments entered " + str (len(sys.argv) - 1) + " out of 5")
   
if len(sys.argv) != 6:
        print("\n---Error in argument list")
        print("\n---Usage $python PNV-Batch-number-Lookup-Tool.py <INPUT FILE NAME> <Feature Set> <File Retention in Days> <Delivery Configuration ID> <Environment> ")
        print("\n---Valid values for feature set: fs1, fs5")
        print("\n---File Retention Days should be 1 to 7 only")
        print("\n---Delivery Configuration ID should be from ESS configuartion")
        print("\n---Environment should be QA or PROD")
        print("\n---Example: $python PNV-Batch-number-Lookup-Tool.py phonenumbers.txt fs1 1 1075 QA")
        sys.exit()
    
else:
        #Command line arguments passed and processed 
        python_script_name = sys.argv[0].strip()
        input_file_name = sys.argv[1].strip()
        fs = sys.argv[2].strip()
        feature_set = 'NIS-Scrub-Monitor-' + fs + '-v1'
        file_expiry = int(sys.argv[3])
        delivery_configuration_id = sys.argv[4].strip()
        environment = sys.argv[5].strip()

#Validating the command line arguments 
 
if len(sys.argv) == 6:
    if (input_file_name[-4:] != ".txt"):
        print("\n---ERROR:Input file not provided or Invalid file type, check for .txt file extention")
        sys.exit()
    else:
        print ("Input File: " + input_file_name)
    
    '''    
    if (not fs == "fs1" or fs == "fs2" or fs == "fs3" or fs == "fs23"):
        print("\n---ERROR: Feature_set not provided or Invalid, allowed values are fs1, fs2, fs3 or fs23 only")
        sys.exit()
    else:
        print("\n---Feature set entered is :",fs)
    '''
    if (fs == "fs1" or fs == "fs5"):
        print ("Feature set entered is: " + fs)
    else:
        print("\n---ERROR: Feature_set not provided or Invalid, allowed values are fs1 or fs5 only")
        sys.exit()
              
    if (file_expiry < 1 or file_expiry > 7 ):
        print("\n---ERROR: File Retention days to retain input file & output files, are between 1 to 7 only")
        sys.exit()
    else:
        print ("File Retention Days: " + str(file_expiry))
	
    if (environment == "QA"):
        print ("Environment: " + environment)
        create_file_url = 'https://da3s-chi-msd-app003.dalab.syniverse.com:8443/mediastorage/v1/files'
        schedule_job_url = 'http://da3s-dal-aba-app002.dalab.syniverse.com:8081/aba/v1/schedules'
    elif (environment == "PROD") :
        print ("Environment: " + environment)
        create_file_url = 'https://api.syniverse.com/mediastorage/v1/files'
        schedule_job_url = 'https://api.syniverse.com/aba/v1/schedules'
    else:
        print("\n---ERROR: Environment not provided or Invalid, allowed values are QA or PROD only")
        sys.exit()

    print ("Delivery Configuration ID: " + delivery_configuration_id)
    print ("Job ID: " + feature_set)
    print ("Create File URL (MSS): " + create_file_url)
    print ("Schedule Job URL (ABA): " + schedule_job_url)
		
		
        
#Get the count of no of MDNs in input file
with open(input_file_name) as f:
    for i, l in enumerate(f):
        count = i + 1
print("\n########## Pre Validation Checks Completed ##########")
      
#Begin the Batch Scrub and monitor Process for the MDNs in Input file 
       
## Step 1: We will create the input file in Media Storage
print ('\n########## Creating file in Media Storage ##########')

create_file_payload = {'fileName': '', 'fileTag': '', 'fileFolder': '', 'appName': '', 'expire_time': file_expiry,
                       'checksum': '', 'file_fullsize': '2000000'}

create_file_headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json','int-companyid': company_id}

create_file_response = requests.post(create_file_url, json=create_file_payload, headers=create_file_headers)

print ('\ncreate file response status code: ' + str(create_file_response.status_code))
print ('\nmss create response body: ' + create_file_response.text)

#if the response is not 201 then exit
if (str(create_file_response.status_code) != '201' ):
    print("\nError in File creation, Exiting")
    sys.exit()

    
## Step 2: We will upload the input file to Media Storage
print ('\n########## Uploading input file to Media Storage ##########')

# get the file_id, company id from the create file response
file_id = create_file_response.json()['file_id']
company_id = create_file_response.json()['company-id']

# the URL to use in the request also comes from the create file response
upload_uri = create_file_response.json()['file_uri']

upload_headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/octet-stream',
                  'int-companyid': company_id}

upload_data = open(input_file_name, 'rb').read()

upload_file_response = requests.post(upload_uri, data=upload_data, headers=upload_headers)

print ('\nFile upload response status code: ' + str(upload_file_response.status_code))
print ('\nFile upload response body: ' + upload_file_response.text)

#if the response is not 201 then exit
if (str(upload_file_response.status_code) != '201' ):
    print("\nError in File Upload, Exiting")
    sys.exit()

## Step 3: Schedule the batch job in Batch Automation
print ('\n########## Job Scheduling for Scrub and Monitor batch job ##########')

schedule_job_headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json','int-companyid': company_id}

schedule_job_payload = {"schedule": { "jobId" : feature_set, "name" : "PNVScrubMonitor", "inputFileId" : file_id,
                                       "fileRetentionDays" : file_expiry, "scheduleRetentionDays" : file_expiry,
                                       "outputFileNamingExpression" : "DS1-NIS-Scrub-Monitor-output.txt",
                                       "outputFileFolder" : "/opt/apps/aba/output",
                                       "outputFileHeaderType": "basic",
                                       "jobRuntimeContext" : {
                                       "subscribeevents": "all",
                                       "subscribedestinationid": delivery_configuration_id
                                       }}}

schedule_job_response = requests.post(schedule_job_url, json=schedule_job_payload,
                                       headers=schedule_job_headers)

print ('\nJob Scheduling response status code: ' + str(schedule_job_response.status_code))
print ('\nJob Scheduling response body: ' + schedule_job_response.text)

#if the response is not 201 then exit
if (str(schedule_job_response.status_code) != '201' ):
    print("\nError in File Scheduling, Exiting")
    sys.exit()


## Step 4: Wait for job to complete.

print ('\n########## Retrieving batch job execution status ##########')

while True:
    # we get the schedule id from the response when we scheduled the batch job
    # the response is nested json so we need two keys
    print ('\nWaiting for job to complete')

    schedule_id = schedule_job_response.json()['schedule']['id']

    # we create the URL to retrieve the batch job execution details
    check_execution_url = '/'.join([schedule_job_url, schedule_id, 'executions'])

    check_execution_headers = {'Authorization': 'Bearer ' + access_token,'int-companyid': company_id}

    check_execution_response = requests.get(check_execution_url, headers=check_execution_headers)

    sc = check_execution_response.json()['executions'][0]['status']
    if (sc == "COMPLETE"):
        print ('\nGet batch job status code: ' + str(check_execution_response.status_code))
        print ('\nGet batch job response body: ' + check_execution_response.text)
        break
    else:
        time.sleep(30)
        print("\nSleeping for 30 Seconds")

## Step 5: We download the results from Media Storage
download_output_headers ={'Authorization': 'Bearer ' + access_token, 'int-companyid': company_id}

outputFileId = check_execution_response.json()['executions'][0]['outputFileId']
if(outputFileId != 'EMPTY_FILE'):
	print ('\n########## Downloading the Success Output file ##########')

	# We get the output file URI from the execution details response.
	# the JSON response include both nested JSON and a list

	output_file_uri = check_execution_response.json()['executions'][0]['outputFileURI']

	download_output_response = requests.get(output_file_uri, headers=download_output_headers, allow_redirects=True)
	download_output_response.raise_for_status() #ensure we notice for bad status

	#if the response is not 201 then exit
	if (str(download_output_response.status_code) != '200' ):
		print("\nError in Success Output File Download, Exiting")
		sys.exit()

	path = os.getcwd()
	file = path + '\PNV-Scrub-Success-' + input_file_name[:-4] + '.zip'
	success_file = file
	tempzip = open(file, "wb")
	tempzip.write(download_output_response.content)
	tempzip.close()

	output_data = zlib.decompress(download_output_response.content, zlib.MAX_WBITS|32)

	print ('\nDownload Success Output File status code: ' + str(download_output_response.status_code))
else:
    print("\nThere is no Success Output File to download")

#Step 6: We download the error file from Media Storage
            
# We get the error file URI from the execution details response.
# the JSON response include both nested JSON and a list
               
errorFileId = check_execution_response.json()['executions'][0]['errorDetailFileId']

if(errorFileId != 'EMPTY_FILE'):
    print("\n########## Downloading Error File ##########")       
    error_file_uri = check_execution_response.json()['executions'][0]['errorDetailFileURI']

    #print("\n", error_file_uri)
    #print("\ndownload output headers",download_output_headers)
    #print("\n")

    download_error_response = requests.get(error_file_uri, headers=download_output_headers, allow_redirects=True)
    download_error_response.raise_for_status() #ensure we notice for bad status

    path = os.getcwd()
    file = path + '\PNV-Scrub-Error-' + input_file_name
    error_file = file
    etempzip = open(file, "wb")
    etempzip.write(download_error_response.content)
    etempzip.close()
    print ('\nDownload Error File status code: ' + str(download_error_response.status_code))
    
else:
    print("\nThere is no Error File to download")
    
#Step 7: We download the retry file from Media Storage

# We get the retry file URI from the execution details response.
# the JSON response include both nested JSON and a list    

retryFileId = check_execution_response.json()['executions'][0]['retryFileId']

if(retryFileId != 'EMPTY_FILE'):
    print("\n########## Downloading Retry File ##########")       
    retry_file_uri = check_execution_response.json()['executions'][0]['retryFileURI']

    download_retry_response = requests.get(retry_file_uri, headers=download_output_headers, allow_redirects=True)
    download_retry_response.raise_for_status() #ensure we notice for bad status

    path = os.getcwd()
    file = path + '\PNV-Scrub-Retry-' + input_file_name
    retry_file = file
    rtempzip = open(file, "wb")
    rtempzip.write(download_retry_response.content)
    rtempzip.close()
    print ('\nDownload Retry File status code: ' + str(download_retry_response.status_code))
else:
    print("\nThere is no Retry File to download")

#Step8 printing the success, error and retry count count, files and their location
# in this step we presume the engine has completed its execution

print("\n########## Batch Job Report ##########") 
    
success_count = check_execution_response.json()['executions'][0]['recordSuccessCount']
error_count = check_execution_response.json()['executions'][0]['recordErrorCount']
retry_count = check_execution_response.json()['executions'][0]['recordRetryCount']
    

print ("\n---Number of MDNs in Input File : " + str(count))        
print ("\n---Number of Success Count      : " + str(success_count))
print ("\n---Number of Error Count        : " + str(error_count))
print ("\n---Number of retry Count        : " + str(retry_count))

#printing the files to refer in the appropriate directory

#print the name of output files
if (success_count > 0):
    print ("\n---Success File Location: " + success_file)
if (error_count > 0):
    print ("\n---Error File Location: " + error_file)
if (retry_count > 0):
    print ("\n---Retry File Location: " + retry_file)

print("\n###Job Completed###")    
## End
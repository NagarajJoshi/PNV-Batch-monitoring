###Requires
- Syniverse Developer Community (SDC) Account
- SDC Subscription to Phone Number Verification
- SDC Application created with Batch Automation, Media Storage and Phone Number Verification enabled for the App.
- Access Token for application
- Delivery Configuration ID from ESS application
- Company ID in case executing in QA environment

###Detailed instructions can be found at https://developer.syniverse.com & https://sdcdocumentation.syniverse.com/index.php
- Python installed (version 3.6 used in the example)
- time, zlib, csv, sys, os, requests module's should be installed ($pip install <module name>)

#Provide Access token in the script
- Open the script in a Text File or Python Editor Tool
- provide the Bearer Token that you are authorized to use under the attribute access_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
- For QA environment -> Update company_id also. company_id = 'XXXXXX' 
- For PROD environment keep it blank company_id = ''

###Command to run the script/tool
- Change directiry where input file is stored
$ python <Script_Name> <input_file> <feature_set> <file_retention_days> <delivery_configuration_id> <environment>
- Script_Name = PNV-Batch-Scrub-Monitor-Tool.py (If script is in different directory provide full path)
- input_file = <InputFileName>.txt Data File with Phone Numbers to Scrub and monitor in ASCII Text format (phone numbers within the file should be mentioned in E164 format eg.+1831325XXXX,,)
- feature_set =  fs1, fs5
- file_retention_days = anywhere between 1 and 7
- delivery_configuration_id should be from ESS application
- environment = QA or PROD

###Eg., In order to run from command line:
- $ python PNV-Batch-Scrub-Monitor-Tool.py phonenumbers.txt fs1 1 1758 QA

    
###How to identify output files
- All the output files, are generated in the same directory.
- The following files are created only when there is a success, error or retry output,
- else the files will not be created. 

--PNV-Scrub-Retry-<InputFileName>.txt
--PNV-Scrub-Success-<InputFileName>.zip
--PNV-Scrub-Error-<InputFileName>.txt

- you will need to take back up of these files before you can start the next process.
  else the files will be overwritten.
 





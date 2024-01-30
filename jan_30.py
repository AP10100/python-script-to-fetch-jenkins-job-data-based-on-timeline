import requests
from datetime import datetime, timedelta
from urllib.parse import unquote  # Import unquote function 
import base64

def convert_timestamp(timestamp):
    # Convert Unix timestamp to the desired format
    datetime_obj = datetime.utcfromtimestamp(timestamp / 1000.0)
    formatted_timestamp = datetime_obj.strftime('%b %d, %Y, %I:%M %p')
    return formatted_timestamp

def is_older_than_six_months(timestamp):
    # Check if the build timestamp is older than 6 months
    six_months_ago = datetime.utcnow() - timedelta(minutes=1)
    build_time = datetime.utcfromtimestamp(timestamp / 1000.0)
    return build_time < six_months_ago

def get_all_multibranch_jobs(username, password, jenkins_url, file):
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"
    }

    url = f'{jenkins_url}/api/json?tree=jobs[name]&xpath=//job[contains(name,%27MultiBranch%27)]&depth=1'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
    
        multibranch_jobs = [job['name'] for job in data.get('jobs', [])]
        
        for job_name in multibranch_jobs:
            get_all_branches(username, password, job_name, jenkins_url, file)
            
    else:
        print(f'Error fetching multibranch job information. Status code: {response.status_code}')

def get_all_branches(username, password, job_name, jenkins_url, file):
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"
    }

    url = f'{jenkins_url}/job/{job_name}/api/json?tree=jobs[name]'
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        branches = [job['name'] for job in data.get('jobs', [])]

        for branch in branches:
            get_build_info(username, password, job_name, branch, jenkins_url, file)
    else:
        print(f'Error fetching branch information for {job_name}. Status code: {response.status_code}')

def get_build_info(username, password, job_name, branch_name, jenkins_url, file):
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"
    }

    url = f'{jenkins_url}/job/{job_name}/job/{branch_name}/api/json?tree=builds[number,timestamp,result]'
    print(url)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        builds = data.get('builds', [])

        file.write(f'\n==== {job_name}//{unquote(branch_name)} ====\n')
    
        for build in builds:
            build_number = build.get('number')
            timestamp = build.get('timestamp')
            result = build.get('result', 'UNKNOWN')

            if is_older_than_six_months(timestamp):
                formatted_timestamp = convert_timestamp(timestamp)
                file.write(f'Build Number: {build_number}   ')
                file.write(f'Timestamp: {formatted_timestamp}   ')
                file.write(f'Result: {result}   ')
                file.write('\n')                        
    else:
        print(f'Error fetching build information for {job_name}/{branch_name}. Status code: {response.status_code}')

# Replace these values with your Jenkins URL, username, and password
# jenkins_url = 'https://cicdxc.arlocloud.com'
# username = 'OSurwase'
# password = '112096ea3fda63edcdfe41d8cff2c98186'

jenkins_url = 'http://localhost:8080'
username = 'admin'
password = '1164015dd83f8156a433965f169b8d51f5'

with open('fetchBuild_script_output.txt', 'w') as output_file:
    get_all_multibranch_jobs(username, password, jenkins_url, output_file)



import csv

# Open input file
with open('fetchBuild_script_output.txt', 'r') as file:
    lines = file.readlines()

# Initialize CSV data
csv_data = [['Job Name', 'Branch Name', 'Build Number', 'Timestamp', 'Result']]

# Initialize variables to store job and branch names
current_job = None
current_branch = None

# Iterate through lines in the file
for line in lines:
    # Check if the line contains "====" and "//"
    if "====" in line and "//" in line:
        # Extract job and branch names
        parts = line.split('====')[1].split('//')
        current_job = parts[0].strip()
        current_branch = parts[1].strip()

    # Check if the line contains "Build Number:"
    elif "Build Number:" in line:
        # Extract build details
        build_parts = line.split()
        build_number = build_parts[2]
        timestamp = ' '.join(build_parts[4:9])
        result = build_parts[-1]

        # Append data to CSV
        csv_data.append([current_job, current_branch, build_number, timestamp, result])

# Write CSV data to output file
with open('output.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(csv_data)

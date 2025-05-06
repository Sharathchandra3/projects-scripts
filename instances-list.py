import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_ec2_client():
    return boto3.client('ec2')

def fetch_instances():
    ec2 = get_ec2_client()
    response = ec2.describe_instances()
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance.get('InstanceId', 'N/A')
            state = instance.get('State', {}).get('Name', 'N/A')
            public_ip = instance.get('PublicIpAddress', 'N/A')
            private_ip = instance.get('PrivateIpAddress', 'N/A')

            name_tag = 'N/A'
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name_tag = tag['Value']
                    break

            instances.append({
                'Name': name_tag,
                'InstanceId': instance_id,
                'State': state,
                'PublicIp': public_ip,
                'PrivateIp': private_ip
            })
    return instances

def display_instances(instances):
    print(f"\n{'No.':<5}{'Name':<20}{'Instance ID':<20}{'State':<15}{'Public IP':<20}{'Private IP':<20}")
    print("=" * 100)
    for i, inst in enumerate(instances):
        print(f"{i+1:<5}{inst['Name']:<20}{inst['InstanceId']:<20}{inst['State']:<15}{inst['PublicIp']:<20}{inst['PrivateIp']:<20}")

def start_instances(selected, instances):
    ec2 = get_ec2_client()
    ids = [instances[i]['InstanceId'] for i in selected]
    try:
        ec2.start_instances(InstanceIds=ids)
        print(f"Starting instances: {', '.join(ids)}")
    except Exception as e:
        print(f"Error starting instances: {e}")

def stop_instances(selected, instances):
    ec2 = get_ec2_client()
    ids = [instances[i]['InstanceId'] for i in selected]
    try:
        ec2.stop_instances(InstanceIds=ids)
        print(f"Stopping instances: {', '.join(ids)}")
    except Exception as e:
        print(f"Error stopping instances: {e}")

def parse_selection(user_input, max_index):
    if user_input.lower() == 'all':
        return list(range(max_index))
    try:
        return [int(i.strip()) - 1 for i in user_input.split(',') if 0 < int(i.strip()) <= max_index]
    except:
        print("Invalid input. Please enter numbers like '1,2' or 'all'.")
        return []

def main():
    try:
        while True:
            print("\nMenu:")
            print("1. List EC2 Instances")
            print("2. Start Instances")
            print("3. Stop Instances")
            print("4. Exit")

            choice = input("Enter your choice (1-4): ").strip()
            if choice not in {'1', '2', '3', '4'}:
                print("Invalid choice.")
                continue

            if choice == '4':
                print("Exiting.")
                break

            instances = fetch_instances()
            if not instances:
                print("No instances found.")
                continue

            display_instances(instances)

            if choice == '1':
                continue

            action = "start" if choice == '2' else "stop"
            selection = input(f"\nEnter instance number(s) to {action} (e.g., 1,3 or 'all'): ").strip()
            selected_indices = parse_selection(selection, len(instances))

            if not selected_indices:
                print("No valid selections made.")
                continue

            if choice == '2':
                start_instances(selected_indices, instances)
            elif choice == '3':
                stop_instances(selected_indices, instances)

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

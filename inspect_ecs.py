import boto3
import json

def inspect_ecs():
    ecs = boto3.client('ecs', region_name='ap-south-1')
    
    # cluster: crm-cluster (from previous context)
    cluster = 'crm-cluster'
    service_name = 'crm-backend-service'
    
    print(f"ECS Cluster: {cluster}")
    print(f"ECS Service: {service_name}")
    
    service_resp = ecs.describe_services(cluster=cluster, services=[service_name])
    if not service_resp.get('services'):
        print("Service not found!")
        return
        
    svc = service_resp['services'][0]
    task_def_arn = svc['taskDefinition']
    print(f"Current task-definition revision: {task_def_arn}")
    
    td_resp = ecs.describe_task_definition(taskDefinition=task_def_arn)
    td = td_resp['taskDefinition']
    
    container = td['containerDefinitions'][0]
    print(f"Container name: {container['name']}")
    
    secrets = container.get('secrets', [])
    environment = container.get('environment', [])
    
    print(f"Existing secrets: {json.dumps(secrets, indent=2)}")
    print(f"Existing environment: {json.dumps(environment, indent=2)}")

if __name__ == "__main__":
    inspect_ecs()

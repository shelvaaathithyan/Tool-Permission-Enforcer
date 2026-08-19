import boto3
import json
import time

def deploy_ecs_env():
    # 1. Read API Key safely without printing
    api_key = None
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    ecs = boto3.client('ecs', region_name='ap-south-1')
    cluster = "crm-cluster"
    service_name = "crm-backend-service"
    
    print("Fetching current task definition (crm-backend:5)...")
    td_resp = ecs.describe_task_definition(taskDefinition="crm-backend:5")
    td = td_resp['taskDefinition']
    
    # Clean up fields not accepted by register_task_definition
    for key in ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 'compatibilities', 'registeredAt', 'registeredBy']:
        td.pop(key, None)
        
    container = td['containerDefinitions'][0]
    
    # 2. Add GEMINI_API_KEY to environment
    env = container.get('environment', [])
    # Remove existing GEMINI_API_KEY if present
    env = [e for e in env if e['name'] != 'GEMINI_API_KEY']
    env.append({
        "name": "GEMINI_API_KEY",
        "value": api_key
    })
    container['environment'] = env
    
    # Make sure we don't have it in secrets (cleanup from previous attempt)
    secrets = container.get('secrets', [])
    container['secrets'] = [s for s in secrets if s['name'] != 'GEMINI_API_KEY']
    
    print("Registering new task definition...")
    new_td_resp = ecs.register_task_definition(**td)
    new_td_arn = new_td_resp['taskDefinition']['taskDefinitionArn']
    new_revision = new_td_resp['taskDefinition']['revision']
    print(f"Registered new task definition: {new_td_arn}")
    
    # 3. Update ECS Service
    print(f"Updating service {service_name} to use revision {new_revision}...")
    ecs.update_service(
        cluster=cluster,
        service=service_name,
        taskDefinition=new_td_arn
    )
    
    # 4. Wait for stability
    print("Waiting for deployment to stabilize (this may take a few minutes)...")
    waiter = ecs.get_waiter('services_stable')
    waiter.wait(
        cluster=cluster,
        services=[service_name],
        WaiterConfig={'Delay': 15, 'MaxAttempts': 40}
    )
    
    # Verify State
    svc_resp = ecs.describe_services(cluster=cluster, services=[service_name])
    svc = svc_resp['services'][0]
    
    print(f"Deployment Status: {svc['status']}")
    print(f"Desired Count: {svc['desiredCount']}")
    print(f"Running Count: {svc['runningCount']}")
    print(f"Pending Count: {svc['pendingCount']}")
    
    primary_deploy = next((d for d in svc['deployments'] if d['status'] == 'PRIMARY'), None)
    if primary_deploy:
        print(f"PRIMARY Deployment Task Definition: {primary_deploy['taskDefinition']}")
        
    print("ECS Deployment Done!")

if __name__ == "__main__":
    deploy_ecs_env()

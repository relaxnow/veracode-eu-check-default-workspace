import requests
import argparse
import sys
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC

def check_veracode_workspaces(target_workspace):
    base_url = "https://api.veracode.eu"
    apps_endpoint = f"{base_url}/appsec/v1/applications"
    auth = RequestsAuthPluginVeracodeHMAC()
    
    # 1. Fetch all applications (handling pagination)
    applications = []
    url = apps_endpoint
    page_count = 1
    
    print("Fetching applications...")
    while url:
        try:
            # Added a print statement to show progress and flush the output
            sys.stdout.write(f"\rFetching page {page_count}...")
            sys.stdout.flush()
            
            # Added a timeout to prevent indefinite hanging
            response = requests.get(url, auth=auth, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract applications from the current page
            embedded = data.get("_embedded", {})
            applications.extend(embedded.get("applications", []))
            
            # Check for the next page link
            links = data.get("_links", {})
            next_link = links.get("next", {}).get("href")
            
            # Veracode sometimes returns relative links; handle both cases
            if next_link:
                if next_link.startswith("http"):
                    url = next_link
                else:
                    url = f"{base_url}{next_link}"
                page_count += 1
            else:
                url = None
                
        except requests.exceptions.RequestException as e:
            print(f"\nError fetching applications on page {page_count}: {e}")
            return # Exit the function if we cannot fetch the app list

    print(f"\nFound {len(applications)} applications. Checking linked projects for workspace: '{target_workspace}'...")

    # 2. Iterate through each application to check linked projects
    for app in applications:
        app_guid = app.get("guid")
        profile = app.get("profile", {})
        profile_name = profile.get("name", "Unknown App")
        app_profile_url = app.get("app_profile_url", "No URL provided")
        
        if not app_guid:
            continue
            
        projects_url = f"{base_url}/srcclr/v3/applications/{app_guid}/projects"
        
        try:
            proj_response = requests.get(projects_url, auth=auth, timeout=30)
            
            if proj_response.status_code != 200:
                continue
                
            proj_data = proj_response.json()
            linked_projects = proj_data.get("linked_projects", [])
            
            # 3. Check if any linked project uses the target workspace
            has_target_workspace = False
            for project in linked_projects:
                workspace = project.get("workspace", {})
                if workspace.get("name") == target_workspace or workspace.get("default") == target_workspace:
                    has_target_workspace = True
                    break
                    
            if has_target_workspace:
                print(f'Application {profile_name} is linked to "{target_workspace}" workspace, please correct: {app_profile_url}')
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching projects for {profile_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Veracode applications for a specific linked workspace.")
    parser.add_argument(
        "-w", "--workspace",
        type=str,
        default="Default Workspace",
        help='The name of the workspace to look for (defaults to "Default Workspace").'
    )
    
    args = parser.parse_args()
    check_veracode_workspaces(args.workspace)
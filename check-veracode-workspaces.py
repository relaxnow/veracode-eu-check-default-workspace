import requests
import argparse
import sys
import json
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC

def check_veracode_workspaces(target_workspace, debug=False):
    base_url = "https://api.veracode.eu"
    apps_endpoint = f"{base_url}/appsec/v1/applications"
    auth = RequestsAuthPluginVeracodeHMAC()
    
    applications = []
    url = apps_endpoint
    page_count = 1
    
    print("Fetching applications...")
    while url:
        try:
            sys.stdout.write(f"\rFetching page {page_count}...")
            sys.stdout.flush()
            
            if debug:
                print(f"\n[DEBUG] Requesting apps URL: {url}")
                
            response = requests.get(url, auth=auth, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            embedded = data.get("_embedded", {})
            applications.extend(embedded.get("applications", []))
            
            links = data.get("_links", {})
            next_link = links.get("next", {}).get("href")
            
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
            return

    print(f"\nFound {len(applications)} applications. Checking linked projects for workspace: '{target_workspace}'...")

    for app in applications:
        app_guid = app.get("guid")
        profile = app.get("profile", {})
        profile_name = profile.get("name", "Unknown App")
        app_profile_url = app.get("app_profile_url", "No URL provided")
        
        if not app_guid:
            if debug:
                print(f"[DEBUG] Skipping {profile_name}: No GUID found.")
            continue
            
        projects_url = f"{base_url}/srcclr/v3/applications/{app_guid}/projects"
        
        if debug:
            print(f"\n[DEBUG] Checking application: {profile_name} (GUID: {app_guid})")
            print(f"[DEBUG] Requesting: {projects_url}")
            
        try:
            proj_response = requests.get(projects_url, auth=auth, timeout=30)
            
            if proj_response.status_code != 200:
                if debug:
                    print(f"[DEBUG] Failed to fetch projects. HTTP Status: {proj_response.status_code}")
                continue
                
            proj_data = proj_response.json()
            linked_projects = proj_data.get("linked_projects", [])
            
            if debug:
                print(f"[DEBUG] Found {len(linked_projects)} linked projects.")
            
            has_target_workspace = False
            for index, project in enumerate(linked_projects):
                workspace = project.get("workspace", {})
                
                if debug:
                    print(f"[DEBUG] Project {index} Workspace JSON: {json.dumps(workspace, indent=2)}")
                
                name_val = workspace.get("name")
                default_val = workspace.get("default")
                
                if name_val == target_workspace or default_val == target_workspace:
                    has_target_workspace = True
                    break
                    
            if has_target_workspace:
                full_url = f"https://analysiscenter.veracode.eu/auth/index.jsp#{app_profile_url}"
                print(f'Application {profile_name} is linked to "{target_workspace}" workspace, please correct: {full_url}')
                
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
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug logging to see raw API responses."
    )
    
    args = parser.parse_args()
    check_veracode_workspaces(args.workspace, args.debug)
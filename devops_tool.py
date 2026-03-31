import argparse
import requests
import subprocess
import json
import os
import sys
from datetime import datetime

# -- API GitHub --------------------------------------

def github_repo(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 404:
        print(f"Repo '{owner}/{repo}' introuvable")
        sys.exit(1)
    return r.json()

def github_commits(owner, repo, n=5):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}
    r = requests.get(url, params={"per_page": n}, headers=headers, timeout=10)
    if r.status_code != 200:
        return[]
    return [{
        "sha":      c['sha'][:7],
        "message": c['commit']['message'].split('\n')[0][:60],
        "auteur":   c['commit']['author']['name'],
        "date":     c['commit']['author']['date'][:10]
    } for c in r.json()]

# -- Système ------------------------------------------

def system_info():
    def run(cmd):
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout.strip()
    
    disk = run(["df", "-h", "/"])
    disk_part = disk.split('\n')[1].split()

    # Mémoire via /proc/meminfo (disponible sur tout kernel Linux)
    mem_total = mem_available = "N/A"
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    mem_total = line.split()[1] + " kB"
                if line.startswith("MemAvailable"):
                    mem_available = line.split()[1] + " kB"
    except FileNotFoundError:
        pass

    # Uptime via /proc/uptime
    uptime = "N/A"
    try:
        with open("/proc/uptime") as f:
            seconds = float(f.read().split()[0])
            minutes = int(seconds // 60) % 60
            hours   = int(seconds // 3600) % 24
            days    = int(seconds // 86400)
            uptime  = f"up {days}d {hours}h {minutes}m"
    except FileNotFoundError:
        pass
    
    hostname = "N/A"
    try:
        with open ("/etc/hostname") as f:
            hostname = f.read().strip()
    except FileNotFoundError:
        pass

    return {
        "hostname": run(["hostname"]),
        "user":     os.environ.get("USER", "unknown"),
        "uptime":   uptime,
        "disk": {
            "total":    disk_part[1],
            "used":     disk_part[2],
            "dispo":    disk_part[3],
            "percent":  disk_part[4]
        },
        "memory": {
            "total":    mem_total,
            "available": mem_available
        }
    }

# -- Commandes ------------------------------------------

def cmd_github(args):
    owner, repo = args.owner, args.repo
    info    = github_repo(owner, repo)
    commits = github_commits(owner, repo, args.commits)

    rapport = {
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "repo":         f"{owner}/{repo}",
        "stats": {
            "etoiles":  info['stargazers_count'],
            "forks":    info['forks_count'],
            "issues":   info['open_issues_count'],
            "langue":   info['language'],
        },
        "derniers_commits": commits
    }

    print(json.dumps(rapport, indent=4, ensure_ascii=False))

    if args.save:
        nom = f"github_{owner}_{repo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(nom, "w") as f:
            json.dump(rapport, f, indent=4, ensure_ascii=False)
        print(f"\nSauvegardé : {nom}")

def cmd_system(args):
    info = system_info()
    info["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(json.dumps(info, indent=4, ensure_ascii=False))

    if args.save:
        nom = f"system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(nom, "w") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
        print(f"\nSauvegardé : {nom}")

# -- CLI --------------------------------------------------

parser = argparse.ArgumentParser(
    description="DevOps Tool - Surveillance Github et système"
)
subparser = parser.add_subparsers(dest="commande", required=True)

# Sous-commande : Github
p_github = subparser.add_parser("github", help="Surveiller un repo GitHub")

# Flags : GitHub
p_github.add_argument("--owner",    required=True, help="Propriétaire du repo")
p_github.add_argument("--repo",     required=True, help="Nom du repo")
p_github.add_argument("--commits",  type=int, default=5, help="Nombre de commits (par défaut : 5)")
p_github.add_argument("--save",     action="store_true", help="Sauvegarder en JSON")

# Sous-commande : Système
p_system = subparser.add_parser("system", help="Infos système")

# Flags : Système
p_system.add_argument("--save",     action="store_true", help="Sauvegarder en JSON")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.commande == "github":
        cmd_github(args)
    elif args.commande == "system":
        cmd_system(args)
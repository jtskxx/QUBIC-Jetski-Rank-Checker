import requests
import json
import time
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import logging

init(autoreset=True)
logging.basicConfig(filename='fetch_scores.log', level=logging.INFO, format='%(asctime)s %(message)s')

def get_epoch_times():
    now = datetime.utcnow()
    days_since_wednesday = (now.weekday() - 2) % 7 
    epoch_start = datetime(now.year, now.month, now.day, 12, 0, 0) - timedelta(days=days_since_wednesday)
    
    if now < epoch_start:
        epoch_start -= timedelta(days=7)

    epoch_end = epoch_start + timedelta(days=7)
    
    return epoch_start, epoch_end

def calculate_projected_avg(total_score, current_rate_per_hour, epoch_start, epoch_end, final_total_ids=676):
    now = datetime.utcnow()
    time_left_hours = (epoch_end - now).total_seconds() / 3600
    projected_score_increase = current_rate_per_hour * time_left_hours
    final_total_score = total_score + projected_score_increase
    projected_avg = final_total_score / final_total_ids
    return projected_avg, time_left_hours

def fetch_scores():
    rBody = {'userName': 'guest@qubic.li', 'password': 'guest13@Qubic.li', 'twoFactorCode': ''}
    rHeaders = {'Accept': 'application/json', 'Content-Type': 'application/json-patch+json'}

    try:
        r = requests.post('https://api.qubic.li/Auth/Login', data=json.dumps(rBody), headers=rHeaders, timeout=10)
        token = r.json().get('token')
        
        if token:
            rHeaders = {'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
            
            try:
                r = requests.get('https://api.qubic.li/Score/Get', headers=rHeaders, timeout=10)
                networkStat = r.json()
                
                current_solution_rate = networkStat.get('solutionsPerHourCalculated')  
                current_rate_per_hour = current_solution_rate
                
                scores = networkStat.get('scores', [])
                s = sorted(scores, key=lambda t: t['score'], reverse=True)

                rank = 1  # Start rank from 1 CHECK
                total_ids = len(s)
                computors_count = 0
                candidates_count = 0

                total_score = sum(comp['adminScore'] for comp in s if 'adminScore' in comp)

                max_score = max(comp['score'] for comp in s) if s else 0
                average_score = sum(comp['score'] for comp in s) / total_ids if total_ids > 0 else 0

                epoch_start, epoch_end = get_epoch_times()

                projected_avg, time_left_hours = calculate_projected_avg(
                    total_score, current_rate_per_hour, epoch_start, epoch_end, final_total_ids=676
                )

                identities_to_check = [ # ADD UR IDS TO CHECK
                    'BNXPHVIVQHQFJGDRHLNFTPKIDLODVMWKQHFZCPWGWAVPZNEOQUTVYGJFARED',
                    'DRZGNGZXLCECWAEBCTULXMHLJZVCLLOHNVAXZGPOHEOGYNRETYXLJFCBUXOE',
                    'MSZLCNGBOXQWRFLZANNELYOOKZRDZIXMYRKTITNUAESOJJOZFCZXWROCTKBK',
                    'YTTRDEMEFFZLDDAIDIKICNKVNQFBURZYPOQIFPTIECLYXPUQCGCWHIVFOULA'
                ]
                
                print(Fore.CYAN + Style.BRIGHT + r"""                            

                (        ) (      (               )     )            )               )     (    
           *   ))\ )  ( /( )\ )   )\ )   (     ( /(  ( /(     (   ( /(       (    ( /(     )\ ) 
   (  (  ` )  /(()/(  )\()(()/(  (()/(   )\    )\()) )\())    )\  )\())(     )\   )\())(  (()/( 
   )\ )\  ( )(_)/(_)|((_)\ /(_))  /(_)((((_)( ((_)\|((_)\   (((_)((_)\ )\  (((_)|((_)\ )\  /(_))
  ((_((_)(_(_()(_)) |_ ((_(_))   (_))  )\ _ )\ _((_|_ ((_)  )\___ _((_((_) )\___|_ ((_((_)(_))  
 _ | | __|_   _/ __|| |/ /|_ _|  | _ \ (_/_\(_| \| | |/ /  ((/ __| || | __((/ __| |/ /| __| _ \ 
| || | _|  | | \__ \  ' <  | |   |   /  / _ \ | .` | ' <    | (__| __ | _| | (__  ' < | _||   / 
 \__/|___| |_| |___/ _|\_\|___|  |_|_\ /_/ \_\|_|\_|_|\_\    \___|_||_|___| \___|_|\_\|___|_|_\                           
                """ + "="*60)
                for comp in s:
                    rank += 1 
                
                    if rank <= 500:
                        computors_count += 1
                    else:
                        candidates_count += 1

                    if comp['identity'] in identities_to_check:
                        if rank > 450:
                            color = Fore.RED + Style.BRIGHT
                            danger_message = Fore.RED + Style.BRIGHT + "DANGER! LOW RANK"
                        elif rank > 250:
                            color = Fore.LIGHTYELLOW_EX + Style.BRIGHT
                            danger_message = Fore.YELLOW + "Moderate Rank"
                        else:
                            color = Fore.GREEN + Style.BRIGHT
                            danger_message = Fore.GREEN + "Healthy Rank"

                        print(color + f"ID: {Fore.LIGHTCYAN_EX}{comp['identity']}")
                        print(f"Rank: {rank} | Score: {comp['score']} | {danger_message}")
                        print(Fore.BLUE + "-"*60)

                print(Fore.CYAN + f"\nTotal IDs: {total_ids}")
                print(Fore.GREEN + f"Computors: {computors_count}")
                print(Fore.YELLOW + f"Candidates: {candidates_count}")
                print(Fore.MAGENTA + f"Maximum Score: {max_score}")
                print(Fore.LIGHTMAGENTA_EX + f"Average Score: {average_score:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Projected Average: {projected_avg:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Current Solution Rate: {current_rate_per_hour}/h")
                print(Fore.LIGHTMAGENTA_EX + f"Time Left in Epoch (hours): {time_left_hours:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Total Score: {total_score}")  
                print(Fore.BLUE + "="*60)

            except requests.exceptions.Timeout as errt:
                print(Fore.RED + 'Time out Error:', errt)

        else:
            print(Fore.RED + "Authentication failed. No token received.")

    except requests.exceptions.Timeout as errt:
        print(Fore.RED + 'Time out Error:', errt)
    except requests.exceptions.RequestException as err:
        print(Fore.RED + "API lagging:", err)

while True:
    fetch_scores()
    print(Fore.LIGHTBLUE_EX + "\nNext update in 20 minutes... ⏳\n" + "="*60)
    time.sleep(1200)

import requests
import json
import time
from datetime import datetime, timedelta, timezone
from colorama import Fore, Style, init
import logging
import sys

init(autoreset=True)
logging.basicConfig(filename='fetch_scores.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Your IDs
YOUR_IDS = [
    'ID1',
    'ID2',
    'ID3',
    'ID4',
    'ID5'
]

def get_epoch_times():
    now = datetime.now(timezone.utc)
    days_since_wednesday = (now.weekday() - 2) % 7 
    epoch_start = datetime(now.year, now.month, now.day, 12, 0, 0, tzinfo=timezone.utc) - timedelta(days=days_since_wednesday)
    
    if now < epoch_start:
        epoch_start -= timedelta(days=7)

    epoch_end = epoch_start + timedelta(days=7)
    
    return epoch_start, epoch_end

def calculate_projected_avg(total_score, current_rate_per_hour, epoch_start, epoch_end, final_total_ids=676):
    now = datetime.now(timezone.utc)
    time_left_hours = (epoch_end - now).total_seconds() / 3600
    projected_score_increase = current_rate_per_hour * time_left_hours
    final_total_score = total_score + projected_score_increase
    projected_avg = final_total_score / final_total_ids
    return projected_avg, time_left_hours

def calculate_safe_id_count(your_total_rate, network_rate, your_lowest_rank):
    network_avg_rate = network_rate / 676
    your_avg_rate = your_total_rate / len(YOUR_IDS)
    performance_ratio = your_avg_rate / network_avg_rate
    
    base_safe_count = min(performance_ratio * 500, len(YOUR_IDS))
    
    safety_margins = {
        "20% Safety Margin": 0.8,
        "10% Safety Margin": 0.90,
        "0% Safety Margin": 1,
    }
    
    safe_counts = {}
    for margin_name, margin in safety_margins.items():
        if your_lowest_rank > 450:
            safe_count = max(1, base_safe_count * 0.5 * margin)
        elif your_lowest_rank > 250:
            safe_count = base_safe_count * 0.8 * margin
        else:
            safe_count = base_safe_count * margin
        safe_counts[margin_name] = round(safe_count)
    
    return safe_counts

def fetch_scores():
    rBody = {'userName': 'guest@qubic.li', 'password': 'guest13@Qubic.li', 'twoFactorCode': ''}
    rHeaders = {'Accept': 'application/json', 'Content-Type': 'application/json-patch+json'}

    try:
        r = requests.post('https://api.qubic.li/Auth/Login', data=json.dumps(rBody), headers=rHeaders, timeout=10)
        r.raise_for_status()
        token = r.json().get('token')
        
        if token:
            rHeaders = {'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
            
            try:
                r = requests.get('https://api.qubic.li/Score/Get', headers=rHeaders, timeout=10)
                r.raise_for_status()
                networkStat = r.json()
                
                current_solution_rate = networkStat.get('solutionsPerHourCalculated', 0)  
                current_rate_per_hour = current_solution_rate
                
                scores = networkStat.get('scores', [])
                s = sorted(scores, key=lambda t: t['score'], reverse=True)

                rank = 1
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

                # Logging key statistics
                logging.info(f"Total Score: {total_score}, Current Solution Rate: {current_rate_per_hour}, Projected Average: {projected_avg}")
                
                your_total_rate = 0
                your_scores = []
                your_lowest_rank = 0
                
                print(Fore.CYAN + Style.BRIGHT + r"""                            

                (        ) (      (               )     )            )               )     (    
           *   ))\ )  ( /( )\ )   )\ )   (     ( /(  ( /(     (   ( /(       (    ( /(     )\ ) 
   (  (  ` )  /(()/(  )\()(()/(  (()/(   )\    )\()) )\())    )\  )\())(     )\   )\())(  (()/( 
   )\ )\  ( )(_)/(_)|((_)\ /(_))  /(_)((((_)( ((_)\|((_)\   (((_)((_)\ )\  (((_)|((_)\ )\  /(_))
  ((_((_)(_(_()(_)) |_ ((_(_))   (_))  )\ _ )\ _((_|_ ((_)  )\___ _((_((_) )\___|_ ((_((_)(_))  
 _ | | __|_   _/ __|| |/ /|_ _|  | _ \ (_)_\(_| \| | |/ /  ((/ __| || | __((/ __| |/ /| __| _ \ 
| || | _|  | | \__ \  ' <  | |   |   /  / _ \ | .` | ' <    | (__| __ | _| | (__  ' < | _||   / 
 \__/|___| |_| |___/ _|\_\|___|  |_|_\ /_/ \_\|_|\_|_|\_\    \___|_||_|___| \___|_|\_\|___|_|_\                           
                """ + "="*60)
                
                print(Fore.YELLOW + f"\nCurrent Network Solution Rate: {current_rate_per_hour:.2f}/hour")
                print(Fore.YELLOW + f"Time Left in Epoch: {time_left_hours:.2f} hours")
                print(Fore.YELLOW + f"Estimated Solution Rate for 1 ID: {current_rate_per_hour / 676:.2f}/hour\n")
                
                print(Fore.CYAN + "Your IDs Performance:")
                for comp in s:
                    if comp['identity'] in YOUR_IDS:
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
                        rate = comp['score'] / time_left_hours
                        print(f"Estimated Solution Rate: {rate:.2f}/h")
                        print(Fore.BLUE + "-"*60)
                        
                        your_total_rate += rate
                        your_scores.append((comp['identity'], rank, comp['score'], rate))
                        your_lowest_rank = max(your_lowest_rank, rank)

                    if rank <= 500:
                        computors_count += 1
                    else:
                        candidates_count += 1

                    rank += 1

                print(Fore.CYAN + f"\nTotal IDs: {total_ids}")
                print(Fore.GREEN + f"Computors: {computors_count}")
                print(Fore.YELLOW + f"Candidates: {candidates_count}")
                print(Fore.MAGENTA + f"Maximum Score: {max_score}")
                print(Fore.LIGHTMAGENTA_EX + f"Average Score: {average_score:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Projected Average: {projected_avg:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Current Solution Rate: {current_rate_per_hour:.2f}/h")
                print(Fore.LIGHTMAGENTA_EX + f"Time Left in Epoch (hours): {time_left_hours:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Total Score: {total_score}")
                
                print(Fore.GREEN + f"\nYour Total Estimated Solution Rate: {your_total_rate:.2f}/hour")
                
                safe_id_counts = calculate_safe_id_count(your_total_rate, current_rate_per_hour, your_lowest_rank)
                print(Fore.MAGENTA + "\nRecommended number of IDs to run:")
                for margin, count in safe_id_counts.items():
                    print(f"{margin}: {count}")
                
                if min(safe_id_counts.values()) < len(YOUR_IDS):
                    print(Fore.YELLOW + "\nConsider running your top performing IDs only.")
                
                print(Fore.BLUE + "="*60)

            except requests.exceptions.Timeout as errt:
                logging.error(f"Timeout error during score fetching: {errt}")
                print(Fore.RED + 'Time out Error:', errt)

        else:
            logging.error("Authentication failed. No token received.")
            print(Fore.RED + "Authentication failed. No token received.")

    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout error during authentication: {errt}")
        print(Fore.RED + 'Time out Error:', errt)
    except requests.exceptions.RequestException as err:
        logging.error(f"API error: {err}")
        print(Fore.RED + "API error:", err)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(Fore.RED + f"Unexpected error: {e}")

def main():
    while True:
        try:
            fetch_scores()
            print(Fore.LIGHTBLUE_EX + "\nNext update in 10 minutes... ⏳\n" + "="*60)
            time.sleep(600)  # Sleep for 10 minutes before the next run
        except KeyboardInterrupt:
            print(Fore.RED + "Process interrupted. Exiting...")
            logging.info("Process interrupted by user.")
            sys.exit(0)  # Gracefully handle keyboard interruptions
        except Exception as e:
            logging.error(f"An error occurred in the main loop: {e}")
            print(Fore.RED + f"An error occurred: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()

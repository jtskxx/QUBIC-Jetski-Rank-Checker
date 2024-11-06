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
    'ID5',
    'ID6',
    'ID7'
]

# Add global variables for idle detection
last_total_score = None
last_score_change_time = None
IDLE_THRESHOLD = 25 * 60  # 25 minutes in seconds

def get_epoch_times():
    now = datetime.now(timezone.utc)
    days_since_wednesday = (now.weekday() - 2) % 7 
    epoch_start = datetime(now.year, now.month, now.day, 12, 0, 0, tzinfo=timezone.utc) - timedelta(days=days_since_wednesday)
    
    if now < epoch_start:
        epoch_start -= timedelta(days=7)

    epoch_end = epoch_start + timedelta(days=7)
    
    return epoch_start, epoch_end

def check_idle_status(current_total_score):
    global last_total_score, last_score_change_time
    current_time = time.time()
    
    if last_total_score is None:
        last_total_score = current_total_score
        last_score_change_time = current_time
        return True  # Start as idle
    
    if current_total_score != last_total_score:
        last_total_score = current_total_score
        last_score_change_time = current_time
        return False  # Not idle when score changes
    
    idle_time = current_time - last_score_change_time
    return idle_time >= IDLE_THRESHOLD

def calculate_projected_avg(total_score, current_rate_per_hour, epoch_start, epoch_end, final_total_ids=676):
    now = datetime.now(timezone.utc)
    time_left_hours = (epoch_end - now).total_seconds() / 3600
    projected_score_increase = current_rate_per_hour * time_left_hours
    final_total_score = total_score + projected_score_increase
    projected_avg = final_total_score / final_total_ids
    return projected_avg, time_left_hours

def calculate_safe_id_count(active_ids, network_average_score, total_ids=676):
    if not active_ids:
        return {}
    
    total_score = sum(score for _, _, score, _ in active_ids)
    possible_ids = int(total_score / network_average_score)
    
    recommendations = {
        "Conservative (Safe)": possible_ids,
        "Moderate": possible_ids if total_score < (possible_ids + 1) * network_average_score + 20 else possible_ids + 1,
        "Aggressive": possible_ids if total_score < (possible_ids + 1) * network_average_score else possible_ids + 1
    }
    
    return recommendations

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
                
                computors_count = sum(1 for comp in s if comp.get('isComputor', False))
                candidates_count = sum(1 for comp in s if not comp.get('isComputor', False))

                total_score = sum(comp['adminScore'] for comp in s if 'adminScore' in comp)
                
                # Check idle status
                is_idle = check_idle_status(total_score)
                idle_status = f"{Fore.GREEN}ON" if is_idle else f"{Fore.RED}OFF"

                max_score = max(comp['score'] for comp in s) if s else 0
                average_score = sum(comp['score'] for comp in s) / total_ids if total_ids > 0 else 0

                epoch_start, epoch_end = get_epoch_times()
                now = datetime.now(timezone.utc)
                time_elapsed = (now - epoch_start).total_seconds() / 3600
                time_left_hours = (epoch_end - now).total_seconds() / 3600

                projected_avg, _ = calculate_projected_avg(
                    total_score, current_rate_per_hour, epoch_start, epoch_end, final_total_ids=676
                )

                logging.info(f"Total Score: {total_score}, Current Solution Rate: {current_rate_per_hour}, Projected Average: {projected_avg}")
                
                your_active_ids = []
                
                print(Fore.CYAN + Style.BRIGHT + r"""                            

     ▄█    ▄████████     ███        ▄████████    ▄█   ▄█▄  ▄█          ▄███████▄  ▄██████▄   ▄██████▄   ▄█       
    ███   ███    ███ ▀█████████▄   ███    ███   ███ ▄███▀ ███         ███    ███ ███    ███ ███    ███ ███       
    ███   ███    █▀     ▀███▀▀██   ███    █▀    ███▐██▀   ███▌        ███    ███ ███    ███ ███    ███ ███       
    ███  ▄███▄▄▄         ███   ▀   ███         ▄█████▀    ███▌        ███    ███ ███    ███ ███    ███ ███       
    ███ ▀▀███▀▀▀         ███     ▀███████████ ▀▀█████▄    ███▌      ▀█████████▀  ███    ███ ███    ███ ███       
    ███   ███    █▄      ███              ███   ███▐██▄   ███         ███        ███    ███ ███    ███ ███       
    ███   ███    ███     ███        ▄█    ███   ███ ▀███▄ ███         ███        ███    ███ ███    ███ ███▌    ▄ 
█▄ ▄███   ██████████    ▄████▀    ▄████████▀    ███   ▀█▀ █▀         ▄████▀       ▀██████▀   ▀██████▀  █████▄▄██ 
▀▀▀▀▀▀                                          ▀                                                      ▀         
                          
                """ + "="*60)
                
                print(Fore.YELLOW + f"\nCurrent Network Solution Rate: {current_rate_per_hour:.2f}/hour")
                print(Fore.YELLOW + f"Time Left in Epoch: {time_left_hours:.2f} hours")
                print(Fore.YELLOW + f"Time Elapsed in Epoch: {time_elapsed:.2f} hours")
                print(Fore.YELLOW + f"Estimated Solution Rate for 1 ID: {current_rate_per_hour / 676:.2f}/hour")
                print(Fore.WHITE + f"IDLE: {idle_status}\n")
                
                print(Fore.CYAN + "Your Active IDs Performance:")
                for comp in s:
                    if comp['identity'] in YOUR_IDS and comp['score'] > 0:
                        score = comp['score']
                        rate = score / time_elapsed if time_elapsed > 0 else 0
                        
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
                        print(f"Rank: {rank} | Score: {score} | {danger_message}")
                        print(f"Computor Status: {'Yes' if comp.get('isComputor', False) else 'No'}")
                        print(f"Estimated Solution Rate: {rate:.2f}/h")
                        print(Fore.BLUE + "-"*60)
                        
                        your_active_ids.append((comp['identity'], rank, score, rate))

                    rank += 1

                if your_active_ids:
                    active_ranks = [rank for _, rank, _, _ in your_active_ids]
                    print(Fore.CYAN + "\nActive IDs Analysis:")
                    print(f"Total Active IDs: {len(your_active_ids)}")
                    print(f"Best Rank: {min(active_ranks)}")
                    print(f"Worst Rank: {max(active_ranks)}")
                    print(f"Average Rank: {sum(active_ranks) / len(active_ranks):.0f}")
                    
                    total_your_score = sum(score for _, _, score, _ in your_active_ids)
                    avg_your_score = total_your_score / len(your_active_ids)
                    print(f"Total Score: {total_your_score}")
                    print(f"Average Score: {avg_your_score:.2f}")
                    
                    safe_id_counts = calculate_safe_id_count(your_active_ids, average_score)
                    
                    print(Fore.MAGENTA + "\nRecommended number of IDs to run:")
                    for strategy, count in safe_id_counts.items():
                        if strategy == "Conservative (Safe)":
                            print(Fore.GREEN + f"{strategy}: {count} IDs")
                        elif strategy == "Moderate":
                            print(Fore.YELLOW + f"{strategy}: {count} IDs")
                        else:
                            print(Fore.RED + f"{strategy}: {count} IDs")

                print(Fore.CYAN + f"\nNetwork Statistics:")
                print(Fore.CYAN + f"Total IDs: {total_ids}")
                print(Fore.GREEN + f"Computors: {computors_count}")
                print(Fore.YELLOW + f"Candidates: {candidates_count}")
                print(Fore.MAGENTA + f"Maximum Score: {max_score}")
                print(Fore.LIGHTMAGENTA_EX + f"Average Score: {average_score:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Projected Average: {projected_avg:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Current Solution Rate: {current_rate_per_hour:.2f}/h")
                print(Fore.LIGHTMAGENTA_EX + f"Time Left in Epoch (hours): {time_left_hours:.2f}")
                print(Fore.LIGHTMAGENTA_EX + f"Total Score: {total_score}")
                
                if your_active_ids:
                    your_total_rate = sum(rate for _, _, _, rate in your_active_ids)
                    print(Fore.GREEN + f"\nYour Total Estimated Solution Rate: {your_total_rate:.2f}/hour")
                
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
            print(Fore.LIGHTBLUE_EX + "\nNext update in 5 minutes... ⏳\n" + "="*60)
            time.sleep(300)  # 5 minutes
        except KeyboardInterrupt:
            print(Fore.RED + "Process interrupted. Exiting...")
            logging.info("Process interrupted by user.")
            sys.exit(0)
        except Exception as e:
            logging.error(f"An error occurred in the main loop: {e}")
            print(Fore.RED + f"An error occurred: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()

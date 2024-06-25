import concurrent.futures
import subprocess
import os


def process_one(parameter : str):
    command = f'C:/Users/vojtech.kopal/AppData/Local/anaconda3/python.exe D:/Bachelor/existing_data/edge_cover.py "{parameter}"'
    subprocess.run(command, shell=True)

def main(): 
    prompts = []
    with open("prompts.txt", 'r', encoding='UTF-8') as f:
        for line in f:
            file = line.rstrip('\n')
            prompts.append(file)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_one, prompts) 

if __name__ == '__main__':
    main()
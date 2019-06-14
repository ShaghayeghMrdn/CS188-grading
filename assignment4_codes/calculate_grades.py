import sys, os, csv, subprocess
from typing import List, Dict, OrderedDict, Tuple
from collections import OrderedDict

ALL_REPOS_DIR: str = 'student_repos'
key_column = 'team_name'
run_tests_script: str = 'run_tests.sh'

#### specific to this assignment #####
columns: List[str] =['timestamp',
                     'email',
                     'team_name',
                     'user_names',
                     'discussion',
                     'link',
                     'hash']
shardmaster_tests = [
    ('TestBasic', ['1.Y8DvBKx3WM', '2.2yCOBMlwLg', '3.1CZkJCKZ0l', '4.a8tST0IbgX', '5.gXKLFrwSUp', '6.2Pqj35caiR', '7.BFOCXmoSzE'], 4),
    ('TestUnreliable', ['8.7z5GWWFXjo'], 8),
    ('TestFreshQuery', ['9.CmgIGk6B0f'], 8)
]

shardkv_tests = [
    ('TestBasic', ['1.GftAzhOgNq'], 7),
    ('TestMove', ['2.NWvmwc5du7'], 7),
    ('TestLimp', ['3.5c0Txxfqko'], 14),
    ('TestConcurrent', ['4.6izx3rOT6G'], 14),
    ('TestConcurrentUnreliable', ['5.0AGmdOzPVz'], 14)
]
### Also you need to modify calculate_grade function depending on the assignment. ###

def grade_part(tests, out_file) -> float:
    grade: float = 0
    """Returns the partial grade."""
    for test_tuple in tests:
        test_name: str = test_tuple[0]
        test_weight: int = test_tuple[2]
        for test_case in test_tuple[1]:
            test_number: str = test_case.split('.')[0]
            command: str = f'grep -FIR "{test_case}" {test_name}_*.out | wc -l'
            grepped = subprocess.run(command, shell=True, capture_output=True)
            if grepped.returncode != 0 :
                print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                print(f"ERROR grepping PASSED statement for {test_case} of {test_name}...")
            else:
                count: int = int(grepped.stdout.decode('UTF-8').strip())
                out_file.write(f'{test_name}-{test_number} (*{test_weight}): {count}'+'\n')

                if count == 5:
                    grade += test_weight
                elif (count > 0 and count < 5):
                    grade += test_weight*0.6
                # else nothing
    out_file.write('--------------------\n')
    return grade

def calculate_grade() -> None:
    if os.path.isfile('grading.out'): # if already exists, skip
        print('Skipping ... grading.out file already exits!')
        return

    if not os.path.isfile('running.out'): # running tests is not done yet!
        print('Ignoring ... running.out file is not there yet! -- Incomplete')
        return

    team_dir: str = os.getcwd()
    with open('grading.out', 'w') as grade_out:
        grade_out.write('Part I (shardmaster):\n')
        os.chdir(os.path.join(team_dir, 'src/shardmaster'))
        shardmaster_grade: float = grade_part(shardmaster_tests, grade_out)
        print(f'Part I grade: {shardmaster_grade}/44.0')

        grade_out.write('Part II (shardkv):\n')
        os.chdir(os.path.join(team_dir, 'src/shardkv'))
        shardkv_grade: float = grade_part(shardkv_tests, grade_out)
        print(f'Part II grade: {shardkv_grade}/56.0')
        grade_out.write(f'Total grade: {shardmaster_grade+shardkv_grade}'+'\n')

    print(f'Total grade: {shardmaster_grade+shardkv_grade}/100')
    os.chdir(team_dir)

def convert_to_ssh(github_link: str) -> str:
    result: str = github_link.replace('https://github.com/', 'git@github.com:')
    result += '.git'
    # print(result)
    return result

def run_tests() -> None:
    if os.path.isfile('running.out'): # if already exists, skip
        print('Skipping ... running.out file already exits!')
        return
    subprocess.run(['cp', run_tests_script, '.'], check=True)
    ran = subprocess.run('sh ./run_tests.sh',
                         stdout=subprocess.DEVNULL,
                         shell=True)
    print(ran)
    with open('running.out', 'w') as out:
        out.write("Done!")

def pull_commit(team: str, github_link: str, commit_hash: str) -> None:
    """Clones the GitHub link, checks out the code using the given commit hash.
    Then runs the grade_tests script for each repository (team).
    ** <team> should not contain any spaces.
    ** <github_link> should not have a trailing '/'.
    """
    last_wd: str = os.getcwd()
    print(f"Pulling the code for {team} from {github_link} at {commit_hash}")
    team_dir: str = os.path.join(last_wd,
                                 github_link.rsplit('/', 1)[-1]) # dir name

    # git clone
    if not os.path.isdir(team_dir):
        cloned = subprocess.run(['git', 'clone', convert_to_ssh(github_link)])
        if cloned.returncode != 0 :
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(f"ERROR cloning {github_link} for {team}! Check permissions!")
            os.chdir(last_wd)
            print('-----------------------------------------------------------')
            return
    else:
        print(f"{team}'s repo either is already cloned or directory exits ...")
    os.chdir(team_dir)
    print(f"Inside {team_dir} ...")

    # git checkout hash
    checked_out = subprocess.run(['git', 'checkout', commit_hash],
                                 stdout=subprocess.DEVNULL) # > /dev/null
    if checked_out.returncode != 0:
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(f"ERROR checking out {commit_hash}!")

    # run run_tests script
    run_tests()
    calculate_grade()
    os.chdir(last_wd)
    print('-----------------------------------------------------------')


#--------------main--------------
if len(sys.argv) < 3:
    print('Usage: python3 grading.py <csv_file_path> <2A/2B>')
    exit(1)

csv_file_path = sys.argv[1]
discussion = sys.argv[2]
if discussion != '2A' and discussion != '2B':
    print('Second argument to grading.py should be either 2A or 2B')
    exit(1)

run_tests_script = os.path.join(os.getcwd(), run_tests_script)
if not os.access(run_tests_script, os.X_OK):
    print(f"Need executable run_tests.sh script in this directory!")
    exit(1)

submissions: Dict[str, OrderedDict] = {}
total_rows = 0
with open(csv_file_path) as csv_file:
    reader = csv.DictReader(csv_file, fieldnames=columns)
    for row in reader:
        total_rows += 1
        team_name = row[key_column]
        if team_name != 'Team Name': # ignoring the header row
            submissions[team_name] = row

print(f"Removed {total_rows-len(submissions)-1} duplicate entries ...")
print(f"Total of {len(submissions)} last submissions.")

if not os.path.isdir(ALL_REPOS_DIR):
    print(f"Creating {ALL_REPOS_DIR} directory ...")
    subprocess.run(['mkdir', ALL_REPOS_DIR], check=True)
os.chdir(ALL_REPOS_DIR)

for one_submission in list(submissions.values()):
    if one_submission['discussion'] == discussion:
        # Removing the trailing '/' from github link.
        if one_submission['link'][-1] == '/':
            one_submission['link'] = one_submission['link'][:-1]
        pull_commit(one_submission['team_name'].replace(' ', '_'),
                    one_submission['link'],
                    one_submission['hash'])

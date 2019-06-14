import sys, os, csv, subprocess
from typing import List, Dict, OrderedDict
from collections import OrderedDict

ALL_REPOS_DIR: str = 'student_repos'
#### specific to this assignment #####
columns: List[str] =['timestamp',
                     'name',
                     'UID',
                     'discussion',
                     'link',
                     'hash']
grading_script: str = 'run_tests.sh'


def convert_to_ssh(github_link: str) -> str:
    result: str = github_link.replace('https://github.com/', 'git@github.com:')
    result += '.git'
    # print(result)
    return result

def run_grader(output_file: str) -> None:
    if os.path.isfile(output_file): #if already exists, skip
        print('Skipping ... since grading.out file already exits!')
        return
    subprocess.run(['cp', grading_script, '.'], check=True)
    with open(output_file, 'w') as out:
        graded = subprocess.run('sh ./run_tests.sh',
                               stdout=out,
                               shell=True,
                               check=True)

def pull_commit(name: str, github_link: str, commit_hash: str) -> None:
    """ Creates a directory with the given name, if does not exist already.
    Then goes to that directory and clones the GitHub link. Finally checks out
    the code at the given commit hash.
    ** <name> should not contain any spaces.
    ** <github_link> should not have a trailing '/'.
    """
    last_wd: str = os.getcwd()
    print(f"Pulling the code for {name} from {github_link} at {commit_hash}")
    if not os.path.isdir(name):
        subprocess.run(['mkdir', name], check=True)
    student_dir: str = os.path.join(last_wd, name)
    os.chdir(student_dir)

    grading_out_file: str = os.path.join(student_dir, 'grading.out')
    repo_dir: str = os.path.join(student_dir,
                                 github_link.rsplit('/', 1)[-1]) # url last part
    # git clone
    if not os.path.isdir(repo_dir):
        cloned = subprocess.run(['git', 'clone', convert_to_ssh(github_link)])
        if cloned.returncode != 0 :
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(f"ERROR cloning {github_link} for {name}! Check permissions!")
            os.chdir(last_wd)
            print('-----------------------------------------------------------')
            return
    else:
        print(f"{name}'s repo either is already cloned or directory exits ...")
    os.chdir(repo_dir)
    print(f"Inside {repo_dir} ...")

    # git checkout hash
    # checked_out = subprocess.run(['git', 'checkout', commit_hash],
    #                stdout=subprocess.DEVNULL) #directing stdout to /dev/null
    # if checked_out.returncode != 0:
    #     print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    #     print(f"ERROR checking out {commit_hash}!")
    # run grading script
    run_grader(grading_out_file)
    print(f"Grading output is in {grading_out_file} ...")
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

grading_script = os.path.join(os.getcwd(), grading_script)
if not os.access(grading_script, os.X_OK):
    print(f"Needs executable grading script in this directory ...")
    exit(1)

submissions: Dict[str, OrderedDict] = {}
total_rows = 0
with open(csv_file_path) as csv_file:
    reader = csv.DictReader(csv_file, fieldnames=columns)
    for row in reader:
        total_rows += 1
        uid = row['UID']
        if uid != 'UID':
            del row['UID']
            submissions[uid] = row
print(f"Removed {total_rows-len(submissions)-1} duplicate entries ...")
print(f"Total of {len(submissions)} last submissions.")

if not os.path.isdir(ALL_REPOS_DIR):
    print(f"Creating {ALL_REPOS_DIR} directory ...")
    subprocess.run(['mkdir', ALL_REPOS_DIR], check=True)
os.chdir(ALL_REPOS_DIR)

for one_submission in list(submissions.values()):
    if one_submission['discussion'] == discussion:
        if one_submission['link'][-1] == '/':
            one_submission['link'] = one_submission['link'][:-1]
        pull_commit(one_submission['name'].replace(' ', '_'),
                    one_submission['link'],
                    one_submission['hash'])

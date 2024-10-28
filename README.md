# mastermind

Please read the project description on Blackboard.

See main.py or examples.ipynb for example usages.

Example run of main.py:
`python3 main.py --board_length 4 --num_colors 6 --player_name RandomFolks --scsa_name InsertColors --num_rounds 100`

# How to run and test the code against different player baseline strategies and SCSA's

### How to run the code in this repo:
- Firstly use ```git clone``` in the command line to clone this repo into your local machine.
- Next use ```git switch your_branch_name``` to pull your remote branch to your local machine. 
- Use ```git branch``` to view which branch you are currently on, it will be highlighted in green.
- Use ```git branch -r``` to view all remote branches ```-l``` to see local branches, ```-a``` to see all branches.
- __DO NOT__ make any changes to the files while you are on the ```main``` branch. Please run ```git branch``` prior to making changes in order to check which branch you are on. 

### How to edit and test the code in this repo:

- Once you have pulled your branch and switched to it on your local machine, you may start making changes to the code.
- After ensuring you are on your branch, you may being making changes as you see fit. 
- When finished, use ```git add .``` to add all files to the staging area.
- Commit the changes with ```git commit -m "Your commit message here"``` to commit the changes.
- Push the committed changes to the remote branch with ```git push```.

### How to pull new code from other collaborators onto your branch.

- The ```main``` branch will occasionally have a "Pull Request" done from Github.com
- A Pull Request (PR) will pull the changes from a specified remote branch onto the remote main branch.
- This should only be done after the code from a collaborator's branch has been ensured to have no issues. 
- After the PR, you must update your local ```main``` branch and local ```your_branch_name```. 
- Run these steps in order:
1. ```git switch main``` To switch to your local main branch
2. ```git pull``` To pull the changes from the remote main branch onto your local main branch.
3. ```git switch your_branch_name``` To switch to your personal branch.
4. ```git merge main``` To merge your local main branch with your personal branch.
5. Resolve any merge conflicts to make sure none of the code you want to keep is lost. 

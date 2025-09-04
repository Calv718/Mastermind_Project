# Mastermind

This project was developed as part of an advanced Artificial Intelligence course and centers around building an intelligent and adaptive player for the code-breaking game commonly known as Mastermind. The core challenge is to design a player capable of solving any variation of the game across a wide range of secret code strategies, within strict time and guess constraints.


See main.py or examples.ipynb for example usages.
Example run of main.py:
`python3 main.py --board_length 4 --num_colors 6 --player_name RandomFolks --scsa_name InsertColors --num_rounds 100`


## Game Rules (Simplified)

- The game involves guessing the correct sequence of colored pegs (the "secret code").
- After each guess, the player receives feedback:
  1. Number of pegs that are the **correct color and in the correct position**
  2. Number of pegs that are the **correct color but in the wrong position**
  3. Number of guesses made so far
- The player has a maximum of **100 guesses per round**.

### Things to keep in mind

- We have two variables: p (pegs) and c (colors). Their values are both positive integers.
- Versions depend on how many pegs and colors we have (colors - pegs). 4 - 6 means there are 4 colors and 6 pegs
- Colors are represented by as distinct consecutive letters of the alphabet in lexical order. If c = 6, the colors will be A, B, C, D, E, F
- Size of the state space (the program's total possible codes) is colors^pegs
- A tournament has 100 rounds, 1 round is limited to 100 guesses, each guess has a time limit of 5 seconds
- Various Secret Code Selection Algorithms (SCSA) will be used to generate the secret code 


## Objective

To create a generalized, yet targeted player that can consistently win games of Mastermind by:

- Adapting dynamically to different secret code generation algorithms
- Guessing efficiently under both time (≤ 5 seconds/guess) and space constraints
- Maximizing win rate within a 100-round tournament competing against other teams
- Design and code a player that can accurately and efficiently guess the secret code through multiple game versions with unique patterns


## Complexity & Challenge

To increase difficulty and test algorithmic design skills, the professor and TA created multiple **Secret Code Selection Algorithms (SCSAs)**. Each SCSA follows its own logic to generate the secret code, such as:

- `TwoColor` - SCSA that generates codes containing only two randomly chosen colors
- `OnlyOnce` - SCSA that generates codes in which a color appears at most once
- `FirstLast` - SCSA that generates codes in which the first and last colors are the same
- `PreferFewer` - SCSA that generates codes with a preference for fewer colors

These variations force the player to reason strategically and adapt in real-time, making the problem exponentially harder as the number of pegs and colors increases. (state space is colors^pegs)
Our player was engineered to be both flexible and strategic, capable of adjusting to each SCSA without hardcoding for any one of them.

### Key Features

- **Dynamic Strategy Switching**  
  The player adjusts its guessing behavior based on inferred or known SCSA being used.

- **SCSA-Specific Search Space Reduction**  
  Applies customized filters for each SCSA to shrink the number of valid possibilities early.

- **Feedback-Consistent Filtering**  
  Ensures that every new guess is logically consistent with previous feedback.

- **Lightweight Heuristics**  
  Uses simple scoring methods to prioritize guesses that are likely to narrow the solution space most effectively.

- **Time-Aware Execution**  
  Incorporates a time buffer to ensure each guess is made in under 5 seconds, regardless of the board complexity.

## What This Demonstrates

This project is a showcase of:

- Efficient search-space pruning
- Adaptive and generalized algorithm design
- Balancing performance constraints (time & space) with solution accuracy
- Real-world application of heuristics, feedback loops, and domain-specific optimization


<details>
<summary>Click here to view running instructions </summary>

How to run and test the code against different player baseline strategies and SCSA's

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


### How to test the players on the command line.
- run ```python  main.py --board_length 6 --num_colors 4 --player_name Baseline3 --scsa_name InsertColors --num_rounds 100```
- "Baseline3" should be replaced by the player name you are trying to use.
- "InsertColors" should be replaced by the SCSA you would like to use.

</details>

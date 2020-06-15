# NCTU nphw3 demo scripts

## Directory structure
```
nctu_nphw3_demo/
├── testcase/
    ├── t1    ---- This file is for registration function test.   
    ├── t2    ---- This file is for login and board related function test.
    ├── t3    ---- This file is for create post function test.   
    ├── t4    ---- This file is for delete and update post function test.
    └── t5    ---- This file is for mail related function test.
├── answer/ 
    ├── t1/   ---- All correct outputs in test case 1.
        ├── user0  ---- correct output for user0 in test case 1.  
        ├── user1  ---- correct output for user1 in test case 1. 
        ├── user2  ---- correct output for user2 in test case 1.    
        └── user3  ---- correct output for user3 in test case 1.
    ├── t2/   ---- All correct outputs in test case 2.
        ├── user0  ---- correct output for user0 in test case 2.  
        ├── user1  ---- correct output for user1 in test case 2. 
        ├── user2  ---- correct output for user2 in test case 2.    
        └── user3  ---- correct output for user3 in test case 2.
    ├── t3/   ---- All correct outputs in test case 3.
        ├── user0  ---- correct output for user0 in test case 3.  
        ├── user1  ---- correct output for user1 in test case 3. 
        ├── user2  ---- correct output for user2 in test case 3.    
        └── user3  ---- correct output for user3 in test case 3.
    ├── t4/   ---- All correct outputs in test case 4.
        ...same as t1/ t2/ t3/... 
    └── t5/   ---- All correct outputs in test case 5.
        ...same as t1/ t2/ t3/...  
├── demo.sh        ---- Script for running all test cases and getting the outputs of your program.
├── run_test.sh    ---- Script for getting the test results.
└── compare.sh     ---- Script for comparing your output and answer.
```
## Details about the test case
The format of the test case is shown as follows:
```
0:register venus venus@nctu.edu.tw 11131
1:register apollo apollo@nctu.edu.tw 15313
2:register mars mars@nctu.edu.tw 11215
3:register mercury mercury@nctu.edu.tw 13154
2:register apollo apollo@nctu.edu.tw 15313
1:register mars mars@nctu.edu.tw 11215
0:exit
1:exit
2:exit
3:exit
```
The number before ':' represents the client (user) number. Because we will test 4 clients, the client (user) numbers are from 0 to 3. The string after ':' represents the command we test.
## Usage
### 1. Run your server first.
### 2. Change to directory ```nctu_nphw3_demo```
### 3. Install ```tmux``` and ```vim```
If you have installed these tools, you can skip this step. Otherwise, please install these tools.
```
sudo apt install tmux
sudo apt install vim
```
### 4. Run ```demo.sh```

- Every time you want to run this script, please clean your database or all files used to store metadata and Amazon S3 buckets and objects first.
- Please make sure your AWS credential does not expire before running this script.

This script will create an```output```directory to store your program output for each test case.

```
./demo.sh <command-to-run-your-client-program> <server-ip> <server-port>
```
e.g.,
```
./demo.sh ./client 127.0.0.1 7890
``` 
or 
```
./demo.sh python3 client.py 127.0.0.1 7890
```
It will take a few minutes for testing. After testing, you will see the following results. 

![](https://i.imgur.com/ACjYv0g.png=10x10)

There will be 5 tmux panes on your screen. Panes 0 to 3 are used to run your client program. Pane 0 represents user 0, pane 1 represents user 1, and so on.

Pane 4 will run the```run_test.sh``` script automatically to get the test results.
```
tmux usage
- Move to other pane: Hit <Ctrl-b> first and hit <Up/Down/Left/Right>
- Exit: Hit <Ctrl-b> first and hit <&>
- Scroll screen: Hit <Ctrl-b> first and hit <[>
- Exit scroll screen mode: Hit <q>
```

If you passed the test case, then you will see the following message.
```
Test case 1
===========
Test passed!
```
If failed, then you will see the following message. 
```
Test case 3
===========
user 0: 3 different lines!
user 3: 1 different lines!
```
It means that there are 3 different lines between your client program output and answer output for user 0 in test case 3. And, there are 1 different line between your client program output and answer output for user 3 in test case 3.

### 5. Run ```compare.sh``` to see the different lines.
Type ```./compare.sh <test case number> <user number>```

It will compare your program output for user \<user number\> with the answer output for user \<user number\> in test case \<test case number\>.

e.g.,
Run ```./compare.sh 3 3```. We can see the following results. There is one different line.

![](https://i.imgur.com/GAaygW3.png)

The left one is your output, and the right one is the answer. You can hit **\<F1\>** to exit this screen.


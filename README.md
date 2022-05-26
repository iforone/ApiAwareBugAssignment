# 🐞 Api-aware (A-BSBA) Bug Assignment
API-aware Bug Assignment is a novel developer assignment technique inspired by BSBA, L2R and L2R+.
This is my master's thesis project as part of the Web Science degree in University of Koblenz (Koblenz-Landau).
Here, we investigate the influence of APIs in assigning bug reports to appropriate developers. We developed an activity-based approach that considers history, code and API expertise for associating the bugs to profiles of developers in 2 open-source Java projects.


---
Official title: "The influence of API Experience on Bug Assignment".


You can access the thesis here:

LINK - not published yet.

The inital Exposé:

[Expose.pdf](extra/Expose-API-influence-BA-Amir-Dashti.pdf)

Futher deatails (on Software Languages Group):

https://olat.vcrp.de/auth/RepositoryEntry/2946663103/CourseNode/102851717515556/Message/3250259273

Notion Page (limited access):

https://www.notion.so/Master-Plan-3c42bc323bf4473da6c8d2dd3ddc5692

My Backups (limited access - on Google Drive):

https://drive.google.com/drive/folders/1Ry6aeCSu9hISKNjZd_pl0oG7kx0SlEsN?usp=sharing


Dataset (open source):

https://github.com/anonymous-programmers/BugReportAssignment

Mysql dump: 

https://github.com/anonymous-programmers/BugReportAssignment/blob/master/SQL_BugDatabase_Dump.7z

Alternative format: 

https://figshare.com/articles/dataset/The_dataset_of_six_open_source_Java_projects/951967?file=1656562

---
# 👩‍🎓 Acknowledgment

I thank Professor Dr. Ralf Lämmel and members of the Software Languages Team for supporting me in this thesis. If you are a researcher or just interested in the topic and needed access to further resources (jar files, datasets, etc.) let me know.

---
# 📞 Contact

Amir Reza Javaher Dashti:  

https://www.linkedin.com/in/amir-reza-javaher-dashti-b347bb114/

(via email: javaher@uni-koblenz.de, javaher21@gmail.com)

Professor Dr. R. Lämmel: 

https://www.uni-koblenz-landau.de/de/koblenz/fb4/ifi/AGLaemmel/staff/ralf-laemmel

Software Languages Group:

http://softlang.wikidot.com/

----
# 👩‍💻 Technical Notes

This work is uses Shell, Python, and Docker.

ℹ️ _An installed version of Python 3.9 (Anaconda) and Docker are required for this application._

---
### 🚀 How to run the project?

0- Please, install docker, and python (with virtualization mode).

1- Clone this repository to your machine.

2- Download the [database](https://github.com/anonymous-programmers/BugReportAssignment/blob/master/SQL_BugDatabase_Dump.7z), unzip it and put it to "/db" folder

3- Create a virtual Python environment (named ./venv) and connect it to your Python. This step can be done automatically in Pycharm:

![Alt text](extra/env.png?raw=true "Overall scheme")

ℹ️ see my other [Github project](https://github.com/walkingCommiter/flaky-tests-reproduction) for further help.

4- Run the bootstrapper. The rest of work is automatically handled by the boot shell file. 

This shell will download and create initial files that are needed only once if the database dump or data inputs are already provided to the folder it will ignore them and won't try to remake them. If you want to use a fresh copy again you have to remove contents of ./db and ./data/input folders and docker volumes.

```shell
# to initialize and run everything
zsh boot.sh

# if it asks permission or questions allow accordingly:

question 1: Which project should be selected?: jdt OR swt

question 2: Select extraction approach?: direct or indirect or ml

question 3: Which formula should be used for training-testing?: 'similar to BSBA' or 'similar to L2R and L2R+'

question 4: Should clean the imports? (it cleans up the imports in processed_code table): no or yes

# ⚠️ You can lock different parts of the logic (main, api, code, scanner) by putting an empty lock file in the ./input folder
```

---
### 🛼 Minimum Requirements:

Processor: 2.6 GHz 6-Core Intel Core i7 (or any equivalent chip)

RAM: 16GB

Storage: 10GB 

Preferred operating system: Mac OS Monterey v12 or above (there are no OS bindings)

---
### 📊 Results:


Visualizations of results are available at "[Results.ipynb](https://github.com/iforone/ApiAwareBugAssignment/blob/different-path2/app/Results.ipynb)".


Interesting observations:

None of the bug reports in JDT have more than one assignee so this is technically one assignee. The part of code that considers assignees is never used because the dataset did not have multi-assignees.

--- 
### 🚩 Visualized approach:

![Alt text](extra/approach.png?raw=true "Overall scheme")

----
### 🆘 Helpful notes and commands:

- Activating virtual environment:

```python
# reactivate the env (if forgotten)
deactivate
# create environment:
if [ -d "venv/ez_env/" ]; then
  echo 'env exists'
else
  python -m venv venv/ez_env
fi
source venv/ez_env/bin/activate
```


- Freeze requirements of a virtual python:

```python
pip3 freeze > requirements.txt
```

- Install a package within jupyter:
```
import sys
!{sys.executable} -m pip install plotly
```

- Writing all used APIs in to csv: 


```python
import csv

jdt = {'java.util': 471339.0, 'org.w3c.dom': 3502.0, 'java.lang': 5272.0, 'java.text': 5585.0, 'java.io': 72849.0, 'org.xml.sax': 1361.0, 'javax.xml': 2089.0, 'org.apache.xml': 243.0, 'java.net': 5175.0, 'junit.framework': 27285.0, 'sun.awt': 8.0, 'junit.extensions': 463.0, 'org.eclipse.core': 374.0, 'org.eclipse.jface': 300.0, 'org.eclipse.swt': 598.0, 'com.sun.jdi': 473.0, 'org.eclipse.ui': 99.0, 'junit.textui': 344.0, 'java.awt': 814.0, 'junit.util': 6.0, 'javax.swing': 380.0, 'java.security': 98.0, 'javax.naming': 1.0, 'org.omg.CORBA': 6.0, 'org.eclipse.debug': 23.0, 'sun.security': 16.0, 'org.apache.xerces': 6.0, 'org.eclipse.search': 3.0, 'java.beans': 1.0, 'java.math': 46.0, 'java.applet': 2.0, 'java.x': 43.0, 'javax.servlet': 10.0, 'org.apache.jasper': 189.0, 'junit.awtui': 27.0, 'org.osgi.framework': 684.0, 'java.sql': 381.0, 'java.nio': 81.0, 'org.osgi.service': 105.0, 'com.ibm.icu': 650.0, 'org.junit.runner': 230.0, 'junit.runner': 593.0, 'junit.tests': 23.0, 'org.junit.runners': 64.0, 'org.junit.Test': 34.0, 'org.junit.Ignore': 2.0, 'org.junit.Assert': 289.0, 'org.springframework.core': 20.0, 'org.apache.commons': 33.0, 'org.junit.Before': 2.0}

with open('jdt_apis.csv', 'w') as f:  
    writer = csv.writer(f)
    for k, v in jdt.items():
       writer.writerow([k, v])
        
swt= {'java.util': 133702.0, 'java.io': 25535.0, 'java.text': 844.0, 'java.awt': 2055.0, 'sun.awt': 133.0, 'java.net': 1067.0, 'java.lang': 2373.0, 'junit.framework': 30521.0, 'junit.textui': 781.0, 'org.eclipse.core': 22.0, 'org.eclipse.debug': 38.0, 'sun.dc': 4.0, 'org.apache.tools': 60.0, 'javax.swing': 265.0, 'org.osgi.framework': 29.0, 'java.applet': 8.0, 'org.lwjgl.opengl': 11.0, 'org.lwjgl.LWJGLException': 18.0, 'javax.media': 20.0, 'com.sun.org': 36.0, 'org.w3c.dom': 4032.0, 'javax.xml': 46.0, 'org.xml.sax': 14.0, 'org.lwjgl.util': 5.0, 'java.nio': 7.0, 'com.trolltech.qt': 40420.0, 'java.beans': 30.0, 'org.junit.Assert': 553.0}

with open('swt_apis.csv', 'w') as f:  
    writer = csv.writer(f)
    for k, v in swt.items():
       writer.writerow([k, v])
        
```

- Writing to a file:

```python
f = open('del/data/validations/all_imports-missing.txt', 'w')
for index_ in all_imports:
    f.write(index_ + '\n')
f.close()
```

- Manually unning the API Scanner _for single import_:

```python
from APIScanner import APIScanner


s = APIScanner('no')

# this will automatically find whether it is from a jar or java or is it a subclass, etc.
s.process_imports(['xx.xxx.xxxx'])
```

- Manually running the API Scanner _for an import from a jar_:

```python
from APIScanner import APIScanner

s = APIScanner('no')

s.scan_jar('org.eclipse.swt.widgets.Table', 'macosx-3.3.0-v3346.jar')
```

- Compiling a Java directory (in Alpine container):

```shell
# list all files 
javac -d build recreation/junit/tests/WasRun.java recreation/junit/util/Version.java
cd build
jar cvf YourJar.jar *
```

- Compiling single Java file or files in one folder (in Alpine container):

```shell
javac -d ./build *.java
cd build
jar cvf recreation .jar *
```

- To obtain APIs, for some packages we consider 2 prefixes and for some 3:

```sql
# 3 levels: com.eclipse.jdt.xxx
SELECT FROM scans 
WHERE not (importie like  'java%' or importie like 'junit%' or importie like  'sun%')

# 2 levels: java.sql.xxxx
SELECT FROM scans 
WHERE importie like  'java%' or importie like 'junit%' or importie like  'sun%'
```

Manually running Tokenizer (not used):

```python
tokens = word_tokenize('public static main() { okay(string int =231 ); x= x +1; r!;}')

filtered_words = [word for word in tokens if word not in self.stop_words]

print(filtered_words)
```

❓ QUERY: Finding assignment and resolution information for each bug based on the curated data by L2R+:

```SQL
SELECT baf.bug_id, *
FROM bug_commit
JOIN bug_and_files baf on bug_commit.bug_id = baf.bug_id
GROUP BY baf.bug_id
```
❓ QUERY: Authors that are assigned bug but do not have a commit that was merged to master at any point
for JDT: only one user: mhuebscher
```SQL
SELECT bug_commit.author
FROM bug_commit
JOIN bug_and_files baf on bug_commit.bug_id = baf.bug_id
WHERE bug_commit.author not in (SELECT author FROM processed_code group by author)
GROUP BY author
```

❓ QUERY: Commits that were assigned to a developer:

```SQL
SELECT bug_commit.*
FROM bug_commit
JOIN bug_and_files baf on bug_commit.bug_id = baf.bug_id
WHERE bug_commit.author = 'mhuebscher'
```

❓ QUERY: Developer commits:

The number of recorded file changes ever done by developer in all commits they pushed from the beginning of time until the 
report time of the last bug:
```SQL
SELECT author, count(*) as number_of_changes, username FROM processed_code group by author
```

- VCS Log:

```shell
 git log --before='2014-01-05 00:00:00' --after='1999-01-01 00:00:00' >> log.txt
```

 and then use revaluate() function in DeepProcess class to make sure no commit was missed


- Re-evaluate Deep-process (@deprecated):
```python
    deep_processor = DeepProcessor(project_name, builder_, db_)
    commits = deep_processor.re_evaluate()
    
    # definition of function
    def re_evaluate(self):
        # log_file = open(base.validation_of_vcs_jdt)
        # all_commits_in_vcs = [line.rstrip() for line in log_file.readlines()]
        # all_commits_in_vcs = [x for x in all_commits_in_vcs if x.startswith('commit ')]
        # all_commits_in_vcs = [x.replace('commit ', '') for x in all_commits_in_vcs]
        # log_file.close()
        # for commit_in_vcs in all_commits_in_vcs:
        #     found = False
        #     for key, commit in commits.items():
        #         if commit['hash'] == commit_in_vcs:
        #             found = True
        #             break
        #
        #     if not found:
        #         print(commit_in_vcs)

        commits = self.find_commits_between('2014-01-05 00:00:00', '1999-01-01 00:00:00')
        self.builder.execute("""
            SELECT commit_hash
            FROM processed_code
            ORDER BY commit_hash
        """)

        all_commit_hashes = pd.DataFrame(self.builder.fetchall(), columns={'hash'})
        for key, commit in commits.items():
            if commit['hash'] not in all_commit_hashes.values:
                print(commit['hash'])
```

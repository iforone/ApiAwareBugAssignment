# ApiAwareBugAssignment
API-aware Bug Assignment is a novel developer assigner technique inspired by BSBA, L2R and L2R+

This work is uses Python environment and Docker.

You need Python 3.9 installed and Docker running.

The rest of work is automatically handled by the boot shell file. This shell will download and create initial files that are needed only once if the database dump or data inputs are already provided to the folder it will ignore them and won't try to remake them. If you want to use a fresh copy again you have to remove contents of ./db and ./data/input folders and docker volumes.

```shell
# step 1: install python with virtualization mode

# step 2: run docker deamon

# step 3: to initialize and run everything
zsh boot.sh

# if it asks permission or questions allow accordingly
```


🆘 Helpful notes (for me):

- Freeze requirements of a virtual python:

```python
pip3 freeze > requirements.txt
```

- Write a file:

```python
    f = open('data/output/validations/all_imports-missing.txt', 'w')
for index_ in all_imports:
    f.write(index_ + '\n')
f.close()
```

- Running the API scanner for an import:

```python
s = APIScanner('no')
# this will automatically find whether it is from a jar or java or is it a subclass, etc
s.process_imports(['xx.xxx.xxxx'])
```

- Running the API scanner (separately) for an import from a jar:

```python
s = APIScanner('no')
s.scan_jar('org.eclipse.swt.widgets.Table', 'macosx-3.3.0-v3346.jar')
```

- Compiling a Java directory:

```shell
# list all files 
javac -d build recreation/junit/tests/WasRun.java recreation/junit/util/Version.java
cd build
jar cvf YourJar.jar *
```
- Compiling single Java file or files in one folder

```shell
javac -d ./build *.java
cd build
jar cvf recreation .jar *
```

- Get all imports in source code (unique) in a file:

```python
    # python read all imports old
old_imports_file = open('data/output/validations/all_imports_old.txt')
old_imports = [line.rstrip() for line in old_imports_file.readlines()]
old_imports_file.close()
f = open('data/output/validations/all_imports-missing.txt', 'w')
for old_import in old_imports:
    self.builder.execute("SELECT id FROM scans WHERE importie =  %s", [old_import])
    result = pd.DataFrame(self.builder.fetchall())
    if result.empty:
        f.write(old_import + '\n')
f.close()
```

- Some APIs consider 2 levels of import and some consider 3 levels of pacage name as API:
```sql
# 3 levels of pacakge name as API  com.eclipse.jdt.xxx
SELECT FROM scans 
WHERE not (importie like  'java%' or importie like 'junit%' or importie like  'sun%')

# 2 levels of pacakge name as API : java.sql.xxxx
SELECT FROM scans 
WHERE importie like  'java%' or importie like 'junit%' or importie like  'sun%'
```

keep this:
```python
builder_.execute("""
            SELECT id, packages, cleaned_packages
            FROM processed_code
            WHERE 1
        """)
        changes = pd.DataFrame(builder_.fetchall())
        all_imports = set()
        for index_, change in changes.iterrows():
            corrected_imports_split = change[2].split(',')
            for s in corrected_imports_split:
                all_imports.add(s)
        # python read all imports old
        old_imports_file = open('all_imports_old.txt')
        old_imports = [line.rstrip() for line in old_imports_file.readlines()]
        old_imports_file.close()
        f = open('all_imports-missing.txt', 'w')
        for old_import in old_imports:
            self.builder.execute("SELECT id FROM scans WHERE importie =  %s", [old_import])
            result = pd.DataFrame(self.builder.fetchall())
            if result.empty:
                f.write(old_import + '\n')
        f.close()
```

Try tokenizer:

```python
tokens = word_tokenize('public static main() { okay(string int =231 ); x= x +1; r!;}')
filtered_words = [word for word in tokens if word not in self.stop_words]
exit(filtered_words)
```


---
API usage statistics for Eclipse JDT project:

⚠️ Currently, I calculate the api usage only on code and NOT on the commit message but that might be helpful info as well.

```sql
SELECT api FROM scans WHERE 1 group by api; # JDT -> we have 51 unique apis from ± 502 imports 



How many times each api is used only on the codes in JDT?

{'java.util': 278294.1653, 'com.sun.jdi': 436.8666, 'java.io': 43854.46950000001, 'org.w3c.dom': 3816.000400000003, 'java.net': 5863.2192000000005, 'java.lang': 5570.5895999999975, 'java.text': 5353.537999999993, 'org.xml.sax': 1357.6837, 'javax.xml': 2542.9994999999985, 'org.apache.xml': 243.0, 'junit.framework': 28028.110000000044, 'sun.awt': 8.0, 'junit.extensions': 978.5216999999999, 'org.eclipse.jface': 312.9, 'org.eclipse.core': 334.0334, 'org.eclipse.swt': 505.90009999999995, 'org.eclipse.ui': 111.0, 'junit.textui': 398.7926, 'java.awt': 840.6444000000001, 'junit.util': 6.0, 'javax.swing': 463.2278, 'java.security': 139.42860000000002, 'javax.naming': 1.0, 'org.omg.CORBA': 6.0, 'org.eclipse.debug': 23.0, 'sun.security': 16.0, 'org.apache.xerces': 6.0, 'org.eclipse.search': 3.0, 'java.beans': 1.0, 'java.math': 71.49999999999999, 'java.x': 43.0, 'java.applet': 2.0, 'org.apache.jasper': 163.0, 'javax.servlet': 10.0, 'junit.awtui': 27.0, 'org.osgi.framework': 707.7166, 'java.sql': 343.6666, 'java.nio': 90.9834, 'org.osgi.service': 122.49999999999999, 'com.ibm.icu': 821.2001, 'org.junit.runner': 232.0, 'junit.tests': 23.0, 'junit.runner': 469.3429, 'org.junit.runners': 64.0, 'org.junit.Test': 47.0, 'org.junit.Ignore': 2.0, 'org.junit.Assert': 289.0, 'org.springframework.core': 472.5, 'org.apache.commons': 485.5, 'org.junit.Before': 2.0}

```
❓ Finding assignment and resolution information for each bug based on the curated data by L2R+:

```SQL
SELECT baf.bug_id, *
FROM bug_commit
JOIN bug_and_files baf on bug_commit.bug_id = baf.bug_id
GROUP BY baf.bug_id
```
❓  Authors that are assigned bug but do not have a commit that was merged to master at any point
for JDT: only one user: mhuebscher
```SQL
SELECT bug_commit.author
FROM bug_commit
JOIN bug_and_files baf on bug_commit.bug_id = baf.bug_id
WHERE bug_commit.author not in (SELECT author FROM processed_code group by author)
GROUP BY author
```

Commits that were assigned to a developer:

```SQL
SELECT bug_commit.*
FROM bug_commit
JOIN bug_and_files baf on bug_commit.bug_id = baf.bug_id
WHERE bug_commit.author = 'mhuebscher'
```

Verify developer commits:
ℹ️ Number of recorded file changes ever done by developer in all commits they pushed from the beginning of time until the 
report time of the last bug.
```SQL
SELECT author, count(*) as number_of_changes, username FROM processed_code group by author
```

- Make a log for validating VCS commit history:
 git log --before='2014-01-05 00:00:00' --after='1999-01-01 00:00:00' >> log.txt
 and then use revaluate() function in DeepProcess class to make sure no commit was missed


- DeepProcess re-evaluation:
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

# code_scanner = CodeScanner()
# code_scanner.analyze_commit_message('[41451]Something [Bug 213] copyrights (312) (1242).')
# exit(1)
# code_scanner.analyze_commit_message('[41451]Something copyrights.')
# exit(1)
#
# code_scanner.analyze_code(
#     '''
#     -/*
# - * (c) Copyright IBM Corp. 2000, 2001.
# - * All Rights Reserved.
# - */
# -package org.eclipse.jdt.internal.ui.refactoring.sef;
# -
# -import org.eclipse.jface.viewers.IStructuredSelection;
# -import org.eclipse.jface.wizard.WizardDialog;
# -
# -import org.eclipse.jdt.core.Flags;
# -import org.eclipse.jdt.core.IField;
# -
# -import org.eclipse.jdt.core.JavaModelException;
# -import org.eclipse.jdt.internal.ui.JavaPlugin;
# -import org.eclipse.jdt.internal.ui.refactoring.RefactoringWizardDialog;
# -import org.eclipse.jdt.internal.ui.refactoring.actions.RefactoringAction;
# -import org.eclipse.jdt.internal.ui.refactoring.actions.StructuredSelectionProvider;
# -import org.eclipse.jdt.internal.ui.util.SelectionUtil;
# -
# -public class SelfEncapsulateFieldAction extends RefactoringAction {
# -
# -	public SelfEncapsulateFieldAction(StructuredSelectionProvider provider) {
# -		super("Self Encapsulate", provider);
# -	}
# -	jasper-1; jasper_2; XML x; sa$s; t124; 2ds23; X= CSPO % 211;
# -	public void run() {
# -		IField field= (IField)SelectionUtil.getSingleElement(getStructuredSelection());
# -		SelfEncapsulateFieldWizard wizard= new SelfEncapsulateFieldWizard(field,
# -			JavaPlugin.getDefault().getCompilationUnitDocumentProvider());
# -		WizardDialog dialog= new RefactoringWizardDialog(JavaPlugin.getActiveWorkbenchShell(), wizard);
# -		dialog.open();
# -	}
# -
# -	public boolean canOperateOn(IStructuredSelection selection) {
# -		Object o= SelectionUtil.getSingleElement(selection);
# -		if (o instanceof IField)
# -			return true;
# -		return false;
# -	}
# -}
# -
#     '''
# )
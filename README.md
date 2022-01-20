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

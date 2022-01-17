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
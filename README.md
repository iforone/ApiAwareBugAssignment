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
    f = open('all_imports-missing.txt', 'w')
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
    fh = open('all_imports_old.txt')
    ax = [line.rstrip() for line in fh.readlines()]
    fh.close()
    f = open("all_imports-6-jan.txt", "a")
    for elexx in ax:
        if elexx in all_imports:
            print('✅' + elexx)
        else:
            print('❓' + elexx)
            f.write('NOT FOUND -' + elexx + '\n')
    f.close()
```
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


Helpful notes:

- Running the API scanner (separately):

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
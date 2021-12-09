# warning: please do not move this file
# warning: this file is provided with no guarantees as how it performs in your machine
# I ran it successfully on MacOS Monterey with Macbook Pro 2019

# reactivate the env (if forgotten)
deactivate
# create environment:
if [ -d "venv/ez_env/" ]; then
  echo 'env exists'
else
  python -m venv venv/ez_env
fi
source venv/ez_env/bin/activate

pip install --upgrade pip
pip --version
echo 'Installing requirements'
pip install -r requirements.txt
#pip install "textdistance[extras]" # for speed performance
echo 'DONE'

# remove temp files
echo "Deleting temp files"
#sudo rm -r 'data/temp/assignment2'

clone_projects() {
    echo "checking the project: $1"
    if [ -d "data/input/$1/" ]; then
      echo "Already exists -- skipped the cloning..."
    else
      echo "Cloning initial data; Please Wait..."
      cd  data/input
      git clone $2 $1
      cd ../../
    fi
}

#clone all original works into original
# obviously, you need to make an account in Eclipse foundation to be able to clone from their git
# and then add your public key to it
clone_projects jdt https://git.eclipse.org/r/jdt/eclipse.jdt.ui
clone_projects swt https://git.eclipse.org/r/platform/eclipse.platform.swt.git

# bring docker up and running
docker-compose up --detach

python app/maker.py
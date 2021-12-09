# This script will only work if you run it from the main not within the process folder
# this is a new version to initialization.sh from previous task

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

# clone all original works into original
#if [ -d "data/input/l2rp/" ]; then
#    echo "Already exists -- skipped the cloning..."
#else
#  echo "Cloning initial original data; Please Wait..."
#  cd  data/input
#  mkdir "l2rp/"
#  sudo chown -R "l2rp/"
#  sudo chmod -R g+rw "l2rp/"
#  cd "l2rp/"
#  git clone https://github.com/damorimRG/msr4flakiness.git
#  cd ../../../
#fi

# bring docker up and running
docker-compose up --detach

python app/maker.py
git checkout master
git fetch --all
git reset --hard origin/master
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/pip install --no-cache-dir --upgrade -r requirements.txt
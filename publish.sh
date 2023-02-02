if [ -n "$(git describe --tags --abbrev=0)" ]; then
  ver=$(python3 setup.py --version)
  name=$(python3 setup.py --name)
  package_cloud push segment/py-wheels/python dist/${name}-${ver}.tar.gz
else
  echo "skipping (no tag)"
fi
tag=$(git describe --tags --abbrev=0)
if [ -n "$tag" ]; then
  ver=$(python3 setup.py --version)
  name=$(python3 setup.py --name)
  if [ "$tag" = "v$ver" ]; then
    rm -fr ./dist/
    python3 setup.py sdist
  else
    echo "git tag doesn't match package version ($tag != v$ver)"
    exit 1
  fi
else
  echo "skipping (no tag)"
fi
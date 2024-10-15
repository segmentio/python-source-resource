if [ -n "$(git describe --tags --abbrev=0)" ]; then
  ver=$(git describe --tags --abbrev=0 | sed 's/^v//')
  name="segment_source_resource"
  echo "${name}-${ver}.tar.gz"
  package_cloud push segment/py-wheels/python dist/${name}-${ver}.tar.gz
else
  echo "skipping (no tag)"
fi
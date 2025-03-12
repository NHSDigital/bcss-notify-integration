pylint $(git ls-files '*.py' | grep -v '^tests/') || {
  echo "Pylint failed"
  exit 1
}

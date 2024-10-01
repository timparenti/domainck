import subprocess

import git
import pathlib

from . import helpers

# The GitCacheHandler class is a wrapper for basic on-disk caching (using a git
# repository) and comparison between runs.

class GitCacheHandler():
  cache_path = None

  def __init__(self, cache_dir):
    pathlib.Path(cache_dir).resolve().mkdir(parents=True, exist_ok=True)
    self.cache_path = pathlib.Path(cache_dir).resolve()

    # Create repo if it does not exist.
    try:
      git.Repo(self.cache_path)
    except git.exc.InvalidGitRepositoryError:
      git.Repo.init(self.cache_path, initial_branch="cache")

  def clear_working_dir(self):
    # Exclude the overarching directory with `-mindepth 1`.
    # Exclude everything that starts with '.git'.
    subprocess.call(["find", self.cache_path, "-mindepth", "1", "-not", "-path", f"{self.cache_path}/.git*", "-exec", "rm", "-rf", "{}", "+"])

  def write_file(self, filename, contents):
    with open(f"{self.cache_path}/{filename}", 'w') as file:
      file.write(contents)
      file.write('\n')

  def commit(self, msg=f"Update as of {helpers.now()}"):
    repo = git.Repo(self.cache_path)
    try:
      repo.git.add('-A')
      repo.git.commit('-m', msg)
      return True
    except git.exc.GitCommandError:
      # If nothing to commit, return False.
      return False

  def show_latest_diff(self):
    repo = git.Repo(self.cache_path)
    return repo.git.show()

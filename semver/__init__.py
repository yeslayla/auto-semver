import re
import subprocess
try: 
    from configparser import ConfigParser
except ImportError:
    # Python < 3
    from ConfigParser import ConfigParser

version = "1.0.5"

class SemVer(object):

    GET_COMMIT_MESSAGE = re.compile(r"Merge (branch|pull request) '?(.+)'? (into|from) ([\w/-]+)")
    # Merge pull request #1 from RightBrain-Networks/feature/PLAT-185-versioning

    def __init__(self):
        self.merged_branch = None
        self.main_branch = None
        self.version_type = None

        self.main_branches = self._setting_to_array('main_branches')
        self.major_branches = self._setting_to_array('major_branches')
        self.minor_branches = self._setting_to_array('minor_branches')
        self.patch_branches = self._setting_to_array('patch_branches')

    def _setting_to_array(self, setting):
        config = ConfigParser()
        config.read('./.bumpversion.cfg')
        value = config.get('semver', setting)
        # filter() removes empty string which is what we get if setting is blank
        return list(filter(bool, [v.strip() for v in value.split(',')]))

    # based on commit message see what branches are involved in the merge
    
    def get_branches(self):
        p = subprocess.Popen(['git', 'log', '-1'], stdout=subprocess.PIPE,
                             cwd='.')
        #check current branch
        b = subprocess.Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE,
                             cwd='.')
        message = str(p.stdout.read())
        br = b.stdout.read().decode('utf-8').rstrip()
        print('Main branch is ' + branch)
        matches = self.GET_COMMIT_MESSAGE.search(message)
        if matches:
            if str(matches.group(4)) == branch:
                self.merged_branch = matches.group(2)
            else:
                self.merged_branch = matches.group(4)
            self.main_branch = branch
        return bool(matches)

    # based on branches involved see what type of versioning should be done
    def get_version_type(self):
        print('Merged branch is ' + self.merged_branch)
        for prefix in self.major_branches:
            if self.merged_branch.startswith(prefix + '/'):
                self.version_type = 'major'
                return True
        for prefix in self.minor_branches:
            if self.merged_branch.startswith(prefix + '/'):
                self.version_type = 'minor'
                return True
        for prefix in self.patch_branches:
            if self.merged_branch.startswith(prefix + '/'):
                self.version_type = 'patch'
                return True
        return False

    # setup git settings so we can commit and tag
    def setup_git_user(self):
        # setup git user
        p = subprocess.Popen(['git', 'config', 'user.email',
                              '"versioner@semver.com"'],
                             cwd='.')
        p = subprocess.Popen(['git', 'config', 'user.name',
                              '"Semantic Versioner"'],
                             cwd='.')
        p.wait()
        return self

    # use bumpversion to increment the appropriate version type
    def version_repo(self):
        # version repo
        p = subprocess.Popen(['bumpversion', self.version_type],
                             cwd='.')
        p.wait()
        return self

    def commit_and_push(self):
        # push versioning commit
        p = subprocess.Popen(['git', 'push', 'origin', self.main_branch],
                             cwd='.')
        p.wait()

        # push versioning tag
        p = subprocess.Popen(['git', 'push', 'origin', '--tags'],
                             cwd='.')
        p.wait()
        return self

    # 1) get branches from last commit message
    # 2) see if we're merging into a main branch
    # 3) see what type of versioning we should do
    # 4) version the repo
    def run(self):
        if not self.get_branches():
            raise Exception('No merge found')
        if self.main_branch not in self.main_branches:
            raise Exception('Not merging into a main branch')
        if not self.get_version_type():
            raise Exception('No git flow branch found')
        self.setup_git_user()
        self.version_repo()
        self.commit_and_push()
        return self

def main():
    try:
        SemVer().run()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    try: main()
    except: raise

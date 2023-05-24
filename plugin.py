# Copyright (C) 2023 Gerard Roche
#
# This file is part of GitOpenModified.
#
# GitOpenModified is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GitOpenModified is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GitOpenModified.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import subprocess

from sublime import status_message
import sublime_plugin


class GitOpenModified(sublime_plugin.WindowCommand):

    def run(self):
        working_dir = _find_working_dir(self.window)
        if not working_dir:
            status_message('Git: working directory not found')
            return

        for modified_file in _get_modified_files(working_dir):
            path = os.path.join(working_dir, modified_file.strip('"'))
            if not os.path.isdir(path):
                self.window.open_file(path)


def _get_modified_files(cwd: str) -> list:
    git_status_output = subprocess.check_output(
        ["/usr/bin/env", "bash", "-c", "git status --short"],
        cwd=cwd,
        shell=False).decode('utf8')

    modified_files = re.findall('\\sM\\s(.+)\n', git_status_output)

    return modified_files


def _find_working_dir(window):
    if not window:
        return None

    folders = window.folders()
    if not folders:
        return None

    view = window.active_view()
    file_name = view.file_name() if view else None

    if not file_name and len(folders) == 1:
        return folders[0]

    if not file_name:
        return

    ancestor_folders = []
    common_prefix = os.path.commonprefix(folders)
    parent = os.path.dirname(file_name)
    while parent not in ancestor_folders and parent.startswith(common_prefix):
        ancestor_folders.append(parent)
        parent = os.path.dirname(parent)

    ancestor_folders.sort(reverse=True)

    for folder in ancestor_folders:
        if os.path.exists(os.path.join(folder, '.git')):
            return folder

    return None

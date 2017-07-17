#!/usr/bin/env python3

import os
import re
import datetime
import subprocess
import shutil
import urllib.parse

import pytest

from update_copyright import extract_urls, text_replace, hg_commit, main

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def create_repo(path):
    subprocess.check_call(['hg', 'init', path])
    with open(os.path.join(path, '.hg', 'hgrc'), 'w+') as hgrc:
        set_user = '[ui]\nusername = Test User <test@example.com>'
        hgrc.write(set_user)
    shutil.copy(os.path.join(data_path, 'sample_file.py'), path)
    subprocess.check_call(['hg', 'commit', '-Am', 'Initial commit',
                           '--repository', path])


@pytest.fixture()
def temp_dir(tmpdir):
    temp_dir = tmpdir.mkdir('temp_dir')
    return temp_dir


@pytest.fixture()
def temp_repo(tmpdir):
    """"Returns a path to a temporary repo containing one sample file"""
    temp_repo = tmpdir.mkdir('tmp_dir')
    create_repo(str(temp_repo))
    return temp_repo


@pytest.fixture()
def base_dir(tmpdir):
    """Returns a temporary directory that contains one html page and two
    repositories (one with push access, the other without)"""
    tmp_repo = tmpdir.mkdir('tmp_dir')
    temp_dir = str(tmp_repo)
    subprocess.check_call(['cp', os.path.join(data_path, 'hg_page.html'),
                           temp_dir])
    repo_1 = os.path.join(temp_dir, 'repo_1')
    repo_2 = os.path.join(temp_dir, 'repo_2')
    os.mkdir(repo_1)
    os.mkdir(repo_2)
    create_repo(repo_1)
    create_repo(repo_2)

    # Make repo_2 read-only
    with open(os.path.join(repo_2, '.hg/hgrc'), 'w') as hgrc:
        hook = '[hooks]\npretxnchangegroup = return True'
        hgrc.write(hook)
    return temp_dir


def test_extract_urls():
    data_url = urllib.parse.urljoin('file:///', data_path)
    urls = [data_url + '/repo_1/',
            data_url + '/repo_2/']
    assert urls == extract_urls(os.path.join(data_url, 'hg_page.html'))


def test_text_replacement(temp_repo):
    updated = 0
    filename = temp_repo.join('sample_file.py').strpath
    text_replace(temp_repo.strpath, filename)
    with open(filename) as file:
        text = file.read()
        pattern = re.compile(r'(copyright.*?\d{4})(?:-\d{4})?\s+eyeo gmbh',
                             re.I)
        for year in re.finditer(pattern, text):
            dates = re.search(r'(\d{4})-(\d{4})', year.group(0))
            if dates.group(2) == str(datetime.datetime.now().year):
                updated += 1

        # test that non-eyeo copyright information are left alone
        assert '2014 example' in text
    # test for copyright information in both strings and comments
    assert updated == 2


def test_hg_commit(temp_repo, temp_dir):
    directory = str(temp_dir)
    repo = str(temp_repo)
    subprocess.check_call(['hg', 'clone', repo, directory])
    open(os.path.join(directory, 'foo'), 'w').close()
    subprocess.check_call(['hg', 'add', '--repository', directory])
    hg_commit(directory, repo)

    # Make sure both files contain the commmit message from hg log
    log_1 = subprocess.run(['hg', 'log', '--repository', repo],
                           stdout=subprocess.PIPE)
    assert 'Noissue - Updated copyright year' in str(log_1.stdout)


def test_all(base_dir):
    main(urllib.parse.urljoin('file:///', os.path.join(
         base_dir, 'hg_page.html')), None)

    # assert hg log for repo_1
    log_1 = subprocess.run(['hg', 'log', '--repository',
                            os.path.join(base_dir, 'repo_1')],
                           stdout=subprocess.PIPE)
    assert 'Noissue - Updated copyright year' in str(log_1.stdout)

    # assert the .patch file for repo_2
    assert'Noissue - Updated copyright year' in open('repo_2.patch').read()
    subprocess.call(['rm', 'repo_2.patch'])  # cleanup

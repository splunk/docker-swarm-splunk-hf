import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('template-file')


def test_basic_template(host):
    # role parameters:
    # dest: template_test_output
    # src: single_file.txt

    # template layout:
    #  single_file.txt

    # the *contents* of src are templated directly into dest
    # in this case src is a file

    # expected output:
    # template_test_output/
    #  single_file.txt

    # resulting expected filename
    templated_filename = 'template_test_output/single_file.txt'

    # these are what we are going to test against
    # verify {{ inventory_hostname }} was templated with the hostname
    templated_content = 'This file was templated for template-file.\n'
    # the file on disk has u+rw only.  validate this was retained.
    templated_mode = 0o600

    f = host.file(templated_filename)

    assert f.exists
    assert f.content_string == templated_content
    assert f.mode == templated_mode

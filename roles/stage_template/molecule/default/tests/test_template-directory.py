import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('template-directory')


def test_basic_template(host):
    # role parameters:
    # dest: template_test_output
    # src: basic_test

    # template layout:
    # basic_test/
    #   basic_template

    # the *contents* of src are templated directly into dest
    # so the  src directory itself is not created in dest

    # expected output:
    # template_test_output/
    #  basic_template

    # resulting expected filename
    templated_filenames = [
        'template_test_output/basic_template',
        'template_test_output/anotherlayer/basic_template',
    ]

    # these are what we are going to test against
    # verify {{ inventory_hostname }} was templated with the hostname
    templated_content = 'This file was templated for template-directory.\n'
    # the file on disk has u+rw only.  validate this was retained.
    templated_mode = 0o600

    for templated_filename in templated_filenames:
        f = host.file(templated_filename)

        assert f.exists
        assert f.content_string == templated_content
        assert f.mode == templated_mode

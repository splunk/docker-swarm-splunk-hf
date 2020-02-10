import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('test_hosts')


def test_paths(host):
    host_vars = host.ansible.get_variables()
    test_vars = host_vars['_test_config']

    paths = test_vars['paths']

    print("testing host: {0}".format(host_vars['inventory_hostname']))
    for path in paths:
        print("Path: {0}".format(path))

        f = host.file(path)

        print("Path exists")
        assert f.exists
        print("Path is a file or directory")
        assert f.is_file or f.is_directory

        if f.is_file:
            print("File content")
            content = test_vars['file_contents']
            assert f.content_string == content
            # modes are string representations of octal integers, convert them
            mode = int(test_vars['mode'], 8)
            print("File mode")
            assert f.mode == mode
        else:
            print("Directory mode")
            # modes are string representations of octal integers, convert them
            directory_mode = int(test_vars['directory_mode'], 8)
            assert f.mode == directory_mode
